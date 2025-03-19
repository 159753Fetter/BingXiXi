import time

def get_time_now(unit="seconds", value=0):
    current_timestamp = int(time.time())
    if unit == "seconds":
        new_timestamp = current_timestamp + value
    elif unit == "minutes":
        new_timestamp = current_timestamp + (value * 60)
    elif unit == "hours":
        new_timestamp = current_timestamp + (value * 3600)
    elif unit == "days":
        new_timestamp = current_timestamp + (value * 86400)
    else:
        raise ValueError("Unsupported time unit")
    return new_timestamp