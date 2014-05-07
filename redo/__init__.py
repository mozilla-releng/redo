# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

import time
from functools import wraps
from contextlib import contextmanager
import logging
log = logging.getLogger(__name__)


def retry(action, attempts=5, sleeptime=60, max_sleeptime=5 * 60,
          retry_exceptions=(Exception,), cleanup=None, args=(), kwargs={}):
    """Call `action' a maximum of `attempts' times until it succeeds,
    defaulting to 5. `sleeptime' is the number of seconds to wait
    between attempts, defaulting to 60 and doubling each retry attempt, to
    a maximum of `max_sleeptime'.  `retry_exceptions' is a tuple of
    Exceptions that should be caught. If exceptions other than those
    listed in `retry_exceptions' are raised from `action', they will be
    raised immediately. If `cleanup' is provided and callable it will
    be called immediately after an Exception is caught. No arguments
    will be passed to it. If your cleanup function requires arguments
    it is recommended that you wrap it in an argumentless function.
    `args' and `kwargs' are a tuple and dict of arguments to pass onto
    to `callable'.

    Example usage:
    def maybe_raises(foo, bar=1):
        ...
        return 1

    def cleanup():
        os.rmtree("/tmp/dirtydir")
   
    ret = retry(maybe_raises, retry_exceptions=(HTTPError,),
                cleanup=cleanup, args=1, kwargs={"bar": 2})
    """
    assert callable(action)
    assert not cleanup or callable(cleanup)
    if max_sleeptime < sleeptime:
        log.debug("max_sleeptime %d less than sleeptime %d" % (
            max_sleeptime, sleeptime))
    n = 1
    while n <= attempts:
        try:
            log.info("retry: Calling %s with args: %s, kwargs: %s, "
                     "attempt #%d" % (action, str(args), str(kwargs), n))
            return action(*args, **kwargs)
        except retry_exceptions:
            log.debug("retry: Caught exception: ", exc_info=True)
            if cleanup:
                cleanup()
            if n == attempts:
                log.info("retry: Giving up on %s" % action)
                raise
            if sleeptime > 0:
                log.info("retry: Failed, sleeping %d seconds before retrying" %
                         sleeptime)
                time.sleep(sleeptime)
                sleeptime = sleeptime * 2
                if sleeptime > max_sleeptime:
                    sleeptime = max_sleeptime
            continue
        finally:
            n += 1


def retriable(*retry_args, **retry_kwargs):
    """A decorator for retry(). Example usage:
    @retriable()
    def foo()
        ...

    @retriable(attempts=100, sleeptime=10)
    def bar():
        ...
    """

    def _retriable_factory(func):
        @wraps(func)
        def _retriable_wrapper(*args, **kwargs):
            return retry(func, args=args, kwargs=kwargs, *retry_args,
                         **retry_kwargs)
        return _retriable_wrapper
    return _retriable_factory


@contextmanager
def retrying(func, *retry_args, **retry_kwargs):
    """A context manager that returns a retrying version of `func'. Mostly
    useful to allow more natural invocation of retrying methods.
    Example usage:
    def foo(a, b):
        ...

    with retrying(foo, retry_exceptions=(HTTPError,)) as retrying_foo:
        # retries on any HTTPError
        r = retrying_foo(1, 3)
    """

    @wraps(func)
    def retry_it(*args, **kwargs):
        return retry(func, args=args, kwargs=kwargs, *retry_args,
                     **retry_kwargs)
    yield retry_it
