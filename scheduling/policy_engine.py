def apply_policy(hour, low_hours):
    if hour in low_hours:
        return "EXECUTE_NOW"
    return "DELAY_TASK"
