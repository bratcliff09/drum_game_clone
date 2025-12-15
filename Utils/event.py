# Observer Pattern
class Event:
    def __init__(self):
        self.listeners = []

    def observe(self, callback_func):
        self.listeners.append(callback_func)

    def notify(self):
        for listener in self.listeners:
            try:
                listener() # Requires the callback function to have (self) in the definition
            except Exception as e:
                print(e)

    def notify_args(self, arg = None):
        for listener in self.listeners:
            try:
                if (arg != None):
                    listener(arg) # Requires the callback function to have (self) in the definition
                else:
                    listener()
            
            except Exception as e:
                print(e)
    
    def clear(self):
        self.listeners.clear()
    