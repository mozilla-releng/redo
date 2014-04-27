import mock
import unittest

from retry import retry, retriable, retrying

ATTEMPT_N = 1


def _succeedOnSecondAttempt(foo=None, exception=Exception):
    global ATTEMPT_N
    if ATTEMPT_N == 2:
        ATTEMPT_N += 1
        return
    ATTEMPT_N += 1
    raise exception("Fail")


def _alwaysPass():
    global ATTEMPT_N
    ATTEMPT_N += 1
    return True


def _mirrorArgs(*args, **kwargs):
    return args, kwargs


def _alwaysFail():
    raise Exception("Fail")


class NewError(Exception):
    pass


class OtherError(Exception):
    pass


def _raiseCustomException():
    return _succeedOnSecondAttempt(exception=NewError)


class TestRetry(unittest.TestCase):
    def setUp(self):
        global ATTEMPT_N
        ATTEMPT_N = 1

    def testRetrySucceed(self):
        # Will raise if anything goes wrong
        retry(_succeedOnSecondAttempt, attempts=2, sleeptime=0)

    def testRetriableSucceed(self):
        func = retriable(attempts=2, sleeptime=0)(_succeedOnSecondAttempt)
        func()

    def testRetryFailWithoutCatching(self):
        self.assertRaises(Exception, retry, _alwaysFail, sleeptime=0,
                          exceptions=())

    def testRetriableFailWithoutCatching(self):
        func = retriable(sleeptime=0)(_alwaysFail)
        self.assertRaises(Exception, func, retry_exceptions=())

    def testRetryFailEnsureRaisesLastException(self):
        self.assertRaises(Exception, retry, _alwaysFail, sleeptime=0)

    def testRetriableFailEnsureRaisesLastException(self):
        func = retriable(sleeptime=0)(_alwaysFail)
        self.assertRaises(Exception, func)

    def testRetrySelectiveExceptionSucceed(self):
        retry(_raiseCustomException, attempts=2, sleeptime=0,
              retry_exceptions=(NewError,))

    def testRetriableSelectiveExceptionSucceed(self):
        func = retriable(attempts=2, sleeptime=0,
                         retry_exceptions=(NewError,))(_raiseCustomException)
        func()

    def testRetrySelectiveExceptionFail(self):
        self.assertRaises(NewError, retry, _raiseCustomException, attempts=2,
                          sleeptime=0, retry_exceptions=(OtherError,))

    def testRetriableSelectiveExceptionFail(self):
        func = retriable(attempts=2, sleeptime=0,
                         retry_exceptions=(OtherError,))(_raiseCustomException)
        self.assertRaises(NewError, func)

    # TODO: figure out a way to test that the sleep actually happened
    def testRetryWithSleep(self):
        retry(_succeedOnSecondAttempt, attempts=2, sleeptime=1)

    def testRetriableWithSleep(self):
        func = retriable(attempts=2, sleeptime=1)(_succeedOnSecondAttempt)
        func()

    def testRetryOnlyRunOnce(self):
        """Tests that retry() doesn't call the action again after success"""
        global ATTEMPT_N
        retry(_alwaysPass, attempts=3, sleeptime=0)
        # ATTEMPT_N gets increased regardless of pass/fail
        self.assertEquals(2, ATTEMPT_N)

    def testRetriableOnlyRunOnce(self):
        global ATTEMPT_N
        func = retriable(attempts=3, sleeptime=0)(_alwaysPass)
        func()
        # ATTEMPT_N gets increased regardless of pass/fail
        self.assertEquals(2, ATTEMPT_N)

    def testRetryReturns(self):
        ret = retry(_alwaysPass, sleeptime=0)
        self.assertEquals(ret, True)

    def testRetriableReturns(self):
        func = retriable(sleeptime=0)(_alwaysPass)
        ret = func()
        self.assertEquals(ret, True)

    def testRetryCleanupIsCalled(self):
        cleanup = mock.Mock()
        retry(_succeedOnSecondAttempt, cleanup=cleanup, sleeptime=0)
        self.assertEquals(cleanup.call_count, 1)

    def testRetriableCleanupIsCalled(self):
        cleanup = mock.Mock()
        func = retriable(cleanup=cleanup, sleeptime=0)(_succeedOnSecondAttempt)
        func()
        self.assertEquals(cleanup.call_count, 1)

    def testRetryArgsPassed(self):
        args = (1, 'two', 3)
        kwargs = dict(foo='a', bar=7)
        ret = retry(_mirrorArgs, args=args, kwargs=kwargs.copy(), sleeptime=0)
        self.assertEqual(ret[0], args)
        self.assertEqual(ret[1], kwargs)

    def testRetriableArgsPassed(self):
        args = (1, 'two', 3)
        kwargs = dict(foo='a', bar=7)
        func = retriable(sleeptime=0)(_mirrorArgs)
        ret = func(*args, **kwargs)
        self.assertEqual(ret[0], args)
        self.assertEqual(ret[1], kwargs)

    def test_retrying_id(self):
        """Make sure that the context manager doesn't change the original
        callable"""
        def wrapped():
            pass
        before = id(wrapped)
        with retrying(wrapped) as w:
            within = id(w)
        after = id(wrapped)
        self.assertEqual(before, after)
        self.assertNotEqual(before, within)

    def test_retrying_call_retry(self):
        """Make sure to distribute retry and function args/kwargs properly"""
        def wrapped(*args, **kwargs):
            pass
        with mock.patch("retry.retry") as mocked_retry:
            with retrying(wrapped, 1, x="y") as w:
                w("a", b=1, c="a")
            mocked_retry.assert_called_once_with(
                wrapped, 1, x='y', args=('a',), kwargs={'c': 'a', 'b': 1})
