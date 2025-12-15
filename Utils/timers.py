# Countdown Timers that use delta_time

class Timer:
    # Start Time in seconds
    def __init__(self, start_time):
        self.timer = start_time
        self.timer_max = start_time

    def tick(self, delta_time):
        if self.timer <= 0: return
        self.timer -= delta_time

    def reset(self):
        self.timer = self.timer_max

    def get_percentage(self):
        return self.timer / self.timer_max
    
    def is_active(self):
        return self.timer > 0