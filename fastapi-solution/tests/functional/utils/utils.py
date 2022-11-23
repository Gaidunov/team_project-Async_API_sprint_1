from functools import wraps
from time import sleep
from typing import Callable, Optional


def backoff(
    exception_to_check,
    max_tries: Optional[int] = 7,
    delay: Optional[int] = 0.1,
    border_sleep_time: Optional[int] = 15,
    factor: Optional[int] = 2,
    logger=None
) -> Callable:
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            actual_tries, actual_delay = max_tries, delay
            while max_tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    msg = "%s, Retrying in %f seconds..." % (str(e), actual_delay)
                    if logger:
                        logger.warning(msg)

                    sleep(actual_delay)
                    actual_tries -= 1
                    actual_delay = min(actual_delay * 2**factor, border_sleep_time)

            return func(*args, **kwargs)

        return inner

    return func_wrapper
