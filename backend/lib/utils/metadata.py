import os
from lib.utils.dynamodb import put_item, get_item

METADATA_TABLE = os.environ.get("METADATA_TABLE", "Metadata")
PLANS_STALE_KEY = "META#plans"


def mark_plans_stale() -> None:
    put_item(METADATA_TABLE, {"key": PLANS_STALE_KEY, "plans_stale": True})


def mark_plans_fresh() -> None:
    put_item(METADATA_TABLE, {"key": PLANS_STALE_KEY, "plans_stale": False})


def get_plans_stale() -> bool:
    item = get_item(METADATA_TABLE, {"key": PLANS_STALE_KEY})
    return bool(item and item.get("plans_stale"))
