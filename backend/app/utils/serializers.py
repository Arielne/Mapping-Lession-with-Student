from datetime import datetime
from typing import Any

from bson import ObjectId


def serialize_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    return value


def serialize_document(document: dict) -> dict:
    output = {key: serialize_value(value) for key, value in document.items()}
    output["id"] = str(document["_id"])
    output.pop("_id", None)
    output.pop("password_hash", None)
    return output

