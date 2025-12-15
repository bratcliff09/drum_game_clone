from CustomEnums.input_type import InputType

# Responsible for knowing which notes are to be played at each beat
class Composer:
    def __init__(self, notes, sub_note):
        self.queue = self.generate_queue(notes, sub_note)
        self.index = 0

    # Get every note that should be played
    def generate_queue(self, notes, sub_note):
        # Defaults
        time_sig = (4, 4) # 4/4
        arr = []

        curr_beat = 1
        for measure in notes:
            if "end" in measure: break
            
            if "time_sig" in measure:
                time_sig = measure['time_sig'].split('/')
                time_sig = (int(time_sig[0]), int(time_sig[1])) 
            
            row = measure["notes"]
            if row.strip() == "," or row.strip() == "": 
                curr_beat += int(sub_note * time_sig[0])
                continue

            row = list(row)
            for n in row:
                if n == '1':
                    key = InputType.DON
                elif n == '2':
                    key = InputType.KAT

                if n != "0":
                    arr.append({'beat': curr_beat, 'key': key})
                curr_beat += 1
        return arr

    def get_next_note(self):
        if len(self.queue) == 0: return {'beat': -1}
        self.index += 1
        if self.index >= len(self.queue): return {'beat': -1}
        return self.queue[self.index]
    
    def get_curr_note(self):
        if len(self.queue) == 0: return -1
        return self.queue[self.index]

    # Returns whether or not there's a note to be played on the current beat
    def debug(self, curr_beat):
        if len(self.queue) == 0: return False
        if self.index >= len(self.queue): return False
        if curr_beat > self.queue[self.index]: return False
        return self.queue[self.index] == curr_beat