def clamp(value, min, max):
        if value > max: return max
        elif value < min: return min
        else: return value

# Loop a number between a min and max
#   Reverse clamp
def loop(value, min, max):
      if value > max: return min
      elif value < min: return max
      else: return value