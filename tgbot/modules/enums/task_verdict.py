from enum import Enum

__all__ = [
    "TaskVerdict"
]

TaskVerdict = Enum('TaskVerdict', ["PENDING", "ACCEPTED", "TLE", "DECLINED", "RE", "MLE", "CE", "WA", "SERVER_ERROR"])
