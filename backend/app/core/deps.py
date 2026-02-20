"""FastAPI dependencies: auth guard and ID helpers."""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.db import get_db
from app.core.security import decode_access_token

# Shows the "Authorize 🔒" button in Swagger UI
_bearer = HTTPBearer()


async def get_current_instructor(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Decode JWT from Authorization header and return the instructor dict.
    Raises 401 if the token is missing, invalid, or expired."""
    instructor_id = decode_access_token(credentials.credentials)
    if not instructor_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    db = get_db()
    try:
        instructor = db.instructors.find_one({"_id": ObjectId(instructor_id)})
    except (InvalidId, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if not instructor:
        raise HTTPException(status_code=401, detail="Instructor not found")

    return {
        "id": str(instructor["_id"]),
        "name": instructor["name"],
        "email": instructor["email"],
    }


def to_object_id(id_str: str) -> ObjectId:
    """Convert a string to a BSON ObjectId, raising 400 if the format is bad."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {id_str}")
