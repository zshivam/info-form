from bson import ObjectId
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

def record_helper(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a MongoDB document (_id ObjectId) to JSON-compatible dictionary with 'id' string."""
    if not doc:
        return {}
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "address": doc.get("address", ""),
        "contact": doc.get("contact", ""),
        "email": doc.get("email"),
        "category": doc.get("category", "General"),
        "notes": doc.get("notes"),
        "image": doc.get("image", ""),
        "created_at": doc.get("created_at")
    }

class RecordModel(BaseModel):
    name: str
    address: Optional[str] = ""
    contact: int
    email: Optional[str] = None
    category: Optional[str] = "General"
    notes: Optional[str] = None
    image: str
    created_at: Optional[str] = None
