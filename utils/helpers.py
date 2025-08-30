def azimuth_to_direction(degrees):
    """
    Convert azimuth degrees → one of 8 cardinal directions (N, NE, E, ...).
    Mirrors your original helper.
    """
    directions = [
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West"
    ]
    # robust if degrees is not a number
    try:
        idx = round(float(degrees) / 45) % 8
    except Exception:
        idx = 0
    return directions[idx]
