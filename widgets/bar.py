import tkinter as tk
import datetime

class Bar:
    def __init__(self, window, settings):
        self.window = window
        self.bar_colors = settings.get_settings(['colors'])

        self.bar_canvas = None
        self.bar_text = None
        self.bar = None

        self.color_done = False

        self.update_bar_thread = None
        self.is_running_bar = False
        self.update_timestamp_thread = None
        self.is_running_timestamp = False

    def update_bar(self, time, full_time):
        fill_done = (full_time - 1 < time) and (full_time > time)
        if (not self.color_done) and fill_done:
                self.bar_canvas.itemconfig(self.bar, fill=self.bar_colors['fill_done'])
                self.color_done = True
        elif not fill_done:
            self.bar_canvas.itemconfig(self.bar, fill=self.bar_colors['fill'])
            self.color_done = False
        fill = 1 + (round((time - full_time) * 1000) % 1000) / 2.5
        self.bar_canvas.coords(self.bar, 1, 1, fill, 42)

    def update_timestamp(self, time):
        # Make a timestamp from the current server time and place it onto the
        # bar
        string = datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
        self.bar_canvas.itemconfig(self.bar_text, text=string)

    def setup_window(self):
        self.bar_canvas = tk.Canvas(self.window, width=400, height=40, background=self.bar_colors['background'])

        # Colored loading bar
        self.bar = self.bar_canvas.create_rectangle(1, 1, 201, 42, fill=self.bar_colors['fill'], width=0)
        self.bar_text = self.bar_canvas.create_text((200, 20), font="calibri 20 bold", width=300)

        return self.bar_canvas

    # Update the bar every 1/60th of a second
    # TODO: Fix running at steady 60fps
    def run_bar(self, entries_ref, clock_ref):
        time = clock_ref[0].time_ms()
        self.update_bar(time, entries_ref[0])

        if self.is_running_bar:
            self.update_bar_thread = self.window.after(10, self.run_bar, entries_ref, clock_ref)

    # Update the timestamp every 1000 milliseconds
    def run_timestamp(self, clock_ref):
        time = clock_ref[0].time_ms()
        self.update_timestamp(time)

        if self.is_running_timestamp:
            # time = timesync.clock[0].time_ms()
            self.update_timestamp_thread = self.window.after(1000 - (round(time * 1000) % 1000), self.run_timestamp, clock_ref)

    # Start the bar
    def start_bar(self, entries_ref, clock_ref):
        if not self.is_running_bar:
            self.is_running_bar = True
            self.run_bar(entries_ref, clock_ref)

    def start_timestamp(self, clock_ref):
        if not self.is_running_timestamp:
            self.is_running_timestamp = True
            self.run_timestamp(clock_ref)

    def stop_bar(self):
        if not self.is_running_bar:
            self.window.after_cancel(self.update_bar_thread)
            self.update_bar_thread = None
            self.is_running_bar = False

    def stop_timestamp(self):
        if not self.is_running_timestamp:
            self.window.after_cancel(self.update_timestamp_thread)
            self.update_timestamp_thread = None
            self.is_running_timestamp = False

    def start(self, entries_ref, clock_ref):
        self.start_timestamp(clock_ref)
        self.start_bar(entries_ref, clock_ref)

    def stop(self):
        self.stop_timestamp()
        self.stop_bar()
