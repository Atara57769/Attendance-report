from datetime import time

# Time boundaries configuration
TIME_MIN = time(6, 0)   # 06:00 - earliest allowed
TIME_MAX = time(23, 59) # 23:59 - latest allowed

# Variation constraints
MAX_VARIATION_MINUTES = 20  # Maximum allowed change in minutes
BREAK_TIME_TARGET = 30      # Target break time in minutes
BREAK_TIME_TOLERANCE = 20    # Tolerance in minutes (+/-)
