import time
import threading
from functools import wraps

# As ISTAT has put in place extreme restrictions (5 requests per minute otherwise the IP gets blacklisted for 7 days...),
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
                    print(f"{self.max_calls} requests limit reached. Waiting {self.time_to_pass} seconds...")
                    time.sleep(self.time_to_pass)
                    self.call_count = 0
                    self.last_reset_time = time.time()
                    print("Resuming work.")
                # Track the count
                self.call_count += 1
            # This is the wrapped function.
            return func(*args, **kwargs)
        return wrapper

rate_limiter = RateLimiter(max_calls=5, time_to_pass=70)