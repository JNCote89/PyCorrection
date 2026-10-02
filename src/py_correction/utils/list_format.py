def semester_sorting_key(semester: str) -> tuple[int, int]:
    if not semester or not isinstance(semester, str):
        return 0, 0

    season_order = {"H": 1, "E": 2, "A": 3}

    season = semester[0]  # type: ignore
    year = int(semester[1:])

    season_priority = season_order.get(season, 4)

    return year, season_priority


def enumeration_join(items: list):
    if len(items) == 1:
        return str(items[0])
    return f"{', '.join(str(i) for i in items[:-1])} et {items[-1]}"
