import time
import threading
from functools import wraps

# As ISTAT has put in place extreme restrictions (5 requests per minute otherwise the IP gets blacklisted for 7 days...),
# this decorator prevents that by tracking the number of requests and pausing them if needed. 
   
call_count = 0
last_reset_time = time.time()
rate_limit_lock = threading.Lock()
# These variables set the count and handle multithreading (probably not useful)

def rate_limit_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global call_count, last_reset_time
        with rate_limit_lock:
            # Reset counter
            if time.time() - last_reset_time > 61:
                call_count = 0
                last_reset_time = time.time()

            # Put in place in the evenience there is the need to add 2 to the counter instead of 1
            increment_by = 1

            # Set limit; 61 seconds for peace of mind.
            if call_count + increment_by > 5:
                print("5 requests limit reached. Waiting 60 seconds before resuming...")
                time.sleep(61)
                call_count = 0
                last_reset_time = time.time()

            # Track the count
            call_count += increment_by
            # print(f"Chiamata {call_count}/5. Eseguo: {func.__name__} (incremento: {increment_by})")

        # This is the wrapped function.
        return func(*args, **kwargs)
    return wrapper