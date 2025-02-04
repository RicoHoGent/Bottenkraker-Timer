import datetime
from threading import Timer

import ntplib

# Class imported from https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
# This class can run a function every n seconds, on its own thread.
class ThreadedTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.first = True
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            if self.first:
                self.first = False
                self._timer = Timer(0, self._run)
            else:
                self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self.is_running:
            self._timer.cancel()
            self.is_running = False
# End of code imported from stackoverflow
#


class Clock:
    def __init__(self, st_delay, server, delay, interval=30):
        self.client = ntplib.NTPClient()

        # The delay for the system time (datetime.datetime.now())
        self.st_delay = st_delay
        # Adress of the timeserver
        self.address = server
        # The delay for the server time
        self.delay = delay
        # The interval for when the clock tries to sync with the server
        self.interval = interval

        # Sync the time with the system time
        self.server_time = datetime.datetime.now().timestamp() + (self.st_delay / 1000)
        self.system_time = datetime.datetime.now().timestamp()
        self.last_synced = None
        self.server_sync = None

        # Thread to keep retrieving the server time
        self.sync_thread = None

    def get_time(self):
        # Server is given, retrieve the corresponding server time
        if self.address != 'standard':
            try:
                print("getting", self.address)
                start = datetime.datetime.now().timestamp()
                response = self.client.request(self.address)
                end = datetime.datetime.now().timestamp()

                # Add the round trip time and the delay to the retrieved
                # server time
                # NOTE: This still needs to be implemented correctly. See
                # https://stackoverflow.com/questions/51390551/what-are-all-the-fields-in-a-python-ntplib-response-and-how-are-they-used
                trip_time = (end - start) / 2
                self.server_time = response.tx_time + trip_time + (self.delay / 1000)
                print(self.server_time)
                self.system_time = datetime.datetime.now().timestamp()

                self.last_synced = self.server_time
                self.server_sync = self.address
            except Exception:
                print('Could not sync with time server.')
        # No server is given, resync with the current system time
        else:
            self.server_time = datetime.datetime.now().timestamp() + (self.st_delay / 1000)
            self.system_time = datetime.datetime.now().timestamp()
            self.last_synced = self.system_time
            self.server_sync = 'standard'

    def time_ms(self):
        return self.server_time + (datetime.datetime.now().timestamp() - self.system_time)

    def start(self):
        self.sync_thread = ThreadedTimer(self.interval, self.get_time)

    def stop(self):
        if self.sync_thread:
            self.sync_thread.stop()
            self.sync_thread = None
