import time
import threading
from functools import wraps
from ._logging import logger

# As ISTAT has put in place some restrictions (5 requests per minute otherwise the IP gets blacklisted for 1 to 2 days),
# this decorator prevents that by tracking the number of requests and pausing them if needed. 

class RateLimiter:
    def __init__(self, max_calls, time_to_pass):
        self.call_count = 0
        self.last_reset_time = time.time()
        self.lock = threading.Lock()
        self.max_calls = max_calls
        self.time_to_pass = time_to_pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                if time.time() - self.last_reset_time > self.time_to_pass:
                    self.call_count = 0
                    self.last_reset_time = time.time()
                # Reset counter
                if self.call_count + 1 > self.max_calls:
                    logger.warning("%s requests limit reached. Waiting %s seconds before resuming.", self.max_calls, self.time_to_pass)
                    time.sleep(self.time_to_pass)
                    self.call_count = 0
                    self.last_reset_time = time.time()
                    logger.info("Resuming work.")
                # Track the count
                self.call_count += 1
                logger.debug("Rate limiter counter: %s/%s", self.call_count, self.max_calls)
            # This is the wrapped function.
                # print(f"Wrapper engaged. Counter: {self.call_count}. Time passed: {time.time()-self.last_reset_time}...")
                time.sleep(1) ### Safeguard
                return func(*args, **kwargs)
        return wrapper

rate_limiter = RateLimiter(max_calls=5, time_to_pass=60)