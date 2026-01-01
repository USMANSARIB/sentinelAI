
import os
import time
from filelock import FileLock, Timeout

class BrowserLock:
    def __init__(self, lock_file="browser_session.lock", timeout=60):
        self.lock_file = lock_file
        self.timeout = timeout
        self.lock = FileLock(f"{lock_file}")

    def acquire(self):
        print(f"[LOCK] Attempting to acquire browser lock...")
        try:
            self.lock.acquire(timeout=self.timeout)
            print(f"[LOCK] Access Granted.")
            return True
        except Timeout:
            print(f"[LOCK] BUSY. Could not acquire lock after {self.timeout}s.")
            return False

    def release(self):
        self.lock.release()
        print(f"[LOCK] Released.")

    def __enter__(self):
        result = self.acquire()
        if not result:
            raise TimeoutError("Could not acquire browser lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
