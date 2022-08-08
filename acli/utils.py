from math import modf


def calc_time(hours: float) -> tuple[int, float | int]:
    """Calculate hours and minutes given an hour float"""
    (minutes, hours) = modf(hours)
    return (round(hours), round(60 * minutes))


def format_time(hours: float) -> str:
    """Convert time into `XXh XXm` format"""
    (hours, minutes) = calc_time(hours)

    return f"{hours:2d}h {minutes:02}m"
