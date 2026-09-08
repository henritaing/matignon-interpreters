'''Timestamp parsing and formatting.'''

def parse_timestamp(value: str) -> float:
    """Parse 'H:MM:SS', 'MM:SS', 'HH:MM:SS,mmm' or 'HH:MM:SS.mmm' to seconds."""
    text = str(value).strip().replace(",", ".")
    parts = text.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = "0", parts[0], parts[1]
    else:
        raise ValueError(f"unparseable timestamp: {value!r}")
    return int(h) * 3600 + int(m) * 60 + float(s)


def format_timestamp(seconds: float) -> str:
    total = int(round(seconds))
    return f"{total // 3600}:{(total % 3600) // 60:02d}:{total % 60:02d}"


def seconds_to_english(seconds: int) -> str:
    """Reproduce the human-readable duration string used by the transcript subtitle format."""
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    parts = []
    if h:
        parts.append(f"{h} hour" + ("s" if h > 1 else ""))
    if m:
        parts.append(f"{m} minute" + ("s" if m > 1 else ""))
    if s:
        parts.append(f"{s} second" + ("s" if s > 1 else ""))
    return ", ".join(parts) if parts else "0 seconds"
