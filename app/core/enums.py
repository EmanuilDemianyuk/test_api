from enum import IntEnum, Enum


class StatusEnum(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SortByEnum(str, Enum):
    NAME = "name"
    PRICE = "price"
    CATEGORY = "category"
    DATE_ADDED = "date_added"


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"