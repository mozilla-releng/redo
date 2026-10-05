import functools
import logging

import mock
import pytest

from redo import calculate_sleep_time, retriable_async, retry_async

retry_count = {}


async def always_fail(*args, **kwargs):
    global retry_count
    retry_count.setdefault("always_fail", 0)
    retry_count["always_fail"] += 1
    raise Exception("fail")


async def fail_first(*args, **kwargs):
    global retry_count
    retry_count["fail_first"] += 1
    if retry_count["fail_first"] < 2:
        raise Exception("first")
    return "yay"


async def fake_sleep(*args, **kwargs):
    pass


class AsyncCallable:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        return await self.func(*args, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("callable_factory", [functools.partial, AsyncCallable])
async def test_retry_async_callable_recovers(callable_factory, caplog):
    calls = []

    async def action(value, *, suffix):
        calls.append((value, suffix))
        if len(calls) == 1:
            raise ValueError("retry")
        return value + suffix

    func = callable_factory(action)
    sleep_time = mock.Mock(return_value=0)
    with caplog.at_level(logging.DEBUG, logger="redo"):
        result = await retry_async(
            func,
            retry_exceptions=ValueError,
            sleeptime_callback=sleep_time,
            args=("hello",),
            kwargs={"suffix": " world"},
        )

    assert result == "hello world"
    assert calls == [("hello", " world"), ("hello", " world")]
    sleep_time.assert_called_once_with(2)
    assert "{}: sleeping 0 seconds before retry".format(func) in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("callable_factory", [functools.partial, AsyncCallable])
@pytest.mark.parametrize("attempts", [1, 3])
async def test_retry_async_callable_preserves_final_exception(callable_factory, attempts, caplog):
    calls = []
    error = ValueError("failed action")

    async def action():
        calls.append(None)
        raise error

    func = callable_factory(action)
    sleep_time = mock.Mock(return_value=0)
    with pytest.raises(ValueError) as exc:
        await retry_async(func, attempts=attempts, retry_exceptions=ValueError, sleeptime_callback=sleep_time)

    assert exc.value is error
    assert len(calls) == attempts
    assert sleep_time.call_args_list == [mock.call(attempt) for attempt in range(2, attempts + 1)]
    assert "{}: too many retries!".format(func) in caplog.text


@pytest.mark.asyncio
async def test_retry_async_fail_first():
    global retry_count
    retry_count["fail_first"] = 0
    status = await retry_async(fail_first, sleeptime_kwargs={"delay_factor": 0})
    assert status == "yay"
    assert retry_count["fail_first"] == 2


@pytest.mark.asyncio
async def test_retry_async_always_fail():
    global retry_count
    retry_count["always_fail"] = 0
    with mock.patch("asyncio.sleep", new=fake_sleep):
        with pytest.raises(Exception):
            status = await retry_async(always_fail, sleeptime_kwargs={"delay_factor": 0})
            assert status is None
    assert retry_count["always_fail"] == 5


@pytest.mark.asyncio
async def test_retriable_async_fail_first():
    global retry_count

    @retriable_async(sleeptime_kwargs={"delay_factor": 0})
    async def decorated_fail_first(*args, **kwargs):
        return await fail_first(*args, **kwargs)

    retry_count["fail_first"] = 0
    status = await decorated_fail_first()
    assert status == "yay"
    assert retry_count["fail_first"] == 2


@pytest.mark.asyncio
async def test_retriable_async_always_fail_async():
    global retry_count

    @retriable_async(sleeptime_kwargs={"delay_factor": 0})
    async def decorated_always_fail(*args, **kwargs):
        return await always_fail(*args, **kwargs)

    retry_count["always_fail"] = 0
    with mock.patch("asyncio.sleep", new=fake_sleep):
        with pytest.raises(Exception):
            await decorated_always_fail()

    assert retry_count["always_fail"] == 5


@pytest.mark.parametrize("attempt", (-1, 0))
def test_calculate_no_sleep_time(attempt):
    assert calculate_sleep_time(attempt) == 0


@pytest.mark.parametrize(
    "attempt,kwargs,min_expected,max_expected",
    (
        (
            1,
            {"delay_factor": 5.0, "randomization_factor": 0, "max_delay": 15},
            5.0,
            5.0,
        ),
        (
            2,
            {"delay_factor": 5.0, "randomization_factor": 0.25, "max_delay": 15},
            10.0,
            12.5,
        ),
        (
            3,
            {"delay_factor": 5.0, "randomization_factor": 0.25, "max_delay": 10},
            10.0,
            10.0,
        ),
    ),
)
def test_calculate_sleep_time(attempt, kwargs, min_expected, max_expected):
    assert min_expected <= calculate_sleep_time(attempt, **kwargs) <= max_expected
