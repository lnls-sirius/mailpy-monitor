import typing


class Condition(object):
    """Alarm  conditions"""

    OutOfRange = "out of range"
    SuperiorThan = "superior than"
    InferiorThan = "inferior than"
    IncreasingStep = "increasing step"
    DecreasingStep = "decreasing step"

    @staticmethod
    def get_conditions() -> typing.List:
        return [
            {
                "name": Condition.OutOfRange,
                "desc": "Must remain within the specified range.",
            },
            {"name": Condition.SuperiorThan, "desc": "Must remain superior than."},
            {"name": Condition.InferiorThan, "desc": "Must remain inferior than."},
            {
                "name": Condition.IncreasingStep,
                "desc": "Each increasing step triggers an alarm.",
            },
            {
                "name": Condition.DecreasingStep,
                "desc": "Each decreasing step triggers an alarm.",
            },
        ]
