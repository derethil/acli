from math import modf


def calc_time(time: float) -> tuple[int, float | int]:
    (minutes, hours) = modf(time)
    return (round(hours), round(60 * minutes))


def format_time(time: float) -> str:
    (hours, minutes) = calc_time(time)
    return f"{hours}h {minutes}m"
