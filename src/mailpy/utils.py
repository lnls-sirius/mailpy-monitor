import typing


def check_required_fields(obj, fields: typing.List[str]):
    if not fields:
        return

    missing = []
    for field in fields:
        if getattr(obj, field, None) is None:
            missing.append(field)
    if missing:
        raise ValueError(f"Required fields '{missing}' are missing from object {obj}")
