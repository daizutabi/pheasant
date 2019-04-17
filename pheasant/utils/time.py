def format_timedelta(timedelta) -> str:
    s = str(timedelta)
    if "day" in s:
        raise NotImplementedError
    h, m, s = s.split(":")
    if "." not in s:
        s += ".0"
    h = ("0" + h)[-2:]
    s = s[:4]
    return f"{h}:{m}:{s}"


def format_timedelta_human(timedelta) -> str:
    sec = timedelta.total_seconds()
    if sec >= 3600:
        return f"{sec//3600:.00f}h{sec//60%60:.00f}min{sec%3600%60:.00f}s"
    elif sec >= 60:
        return f"{sec//60:.00f}min{sec%60:.00f}s"
    elif sec >= 10:
        return f"{sec:0.1f}s"
    elif sec >= 1:
        return f"{sec:0.2f}s"
    elif sec >= 1e-1:
        return f"{sec*1e3:.00f}ms"
    elif sec >= 1e-2:
        return f"{sec*1e3:.01f}ms"
    elif sec >= 1e-3:
        return f"{sec*1e3:.02f}ms"
    elif sec >= 1e-6:
        return f"{sec*1e6:.00f}us"
    else:
        return f"<1us"
