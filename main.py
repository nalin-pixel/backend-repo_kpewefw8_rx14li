import os
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Event as EventSchema

app = FastAPI(title="College Event Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EventCreate(BaseModel):
    title: str
    description: str
    event_date: date
    event_time: str
    location: str
    category: str
    cover_image: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False


@app.get("/")
def read_root():
    return {"message": "College Event Management Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Utility: Seed a few sample events for demo if collection empty
SAMPLE_EVENTS = [
    {
        "title": "Tech Symposium 2025",
        "description": "A showcase of cutting-edge projects, keynote talks, and hackathon finals.",
        "event_date": date.today().replace(day=min(28, date.today().day)),
        "event_time": "10:00 AM",
        "location": "Main Auditorium",
        "category": "Tech",
        "cover_image": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=80&w=1600&auto=format&fit=crop",
        "tags": ["ai", "robotics", "talks"],
        "is_featured": True,
    },
    {
        "title": "Cultural Night Fiesta",
        "description": "An evening of performances, fashion show, and food stalls.",
        "event_date": date.today(),
        "event_time": "06:30 PM",
        "location": "Open Air Theatre",
        "category": "Cultural",
        "cover_image": "https://images.unsplash.com/photo-1515165562835-c3b8c0b1a3b0?q=80&w=1600&auto=format&fit=crop",
        "tags": ["dance", "music", "food"],
        "is_featured": True,
    },
    {
        "title": "Data Science Workshop",
        "description": "Hands-on bootcamp on Python, pandas, and ML pipelines.",
        "event_date": date.today(),
        "event_time": "02:00 PM",
        "location": "Lab Complex - 204",
        "category": "Workshop",
        "cover_image": "https://images.unsplash.com/photo-1555949963-aa79dcee981d?q=80&w=1600&auto=format&fit=crop",
        "tags": ["python", "ml", "workshop"],
        "is_featured": False,
    },
]


def ensure_seed():
    try:
        if db is None:
            return
        count = db["event"].count_documents({})
        if count == 0:
            for ev in SAMPLE_EVENTS:
                create_document("event", ev)
    except Exception:
        # Silently ignore seeding errors to avoid breaking app start
        pass


def serialize_event(d: dict) -> dict:
    out = dict(d)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    # Map storage keys to API keys expected by frontend
    if "event_date" in out:
        try:
            out["date"] = out["event_date"].isoformat() if hasattr(out["event_date"], "isoformat") else str(out["event_date"])
        except Exception:
            out["date"] = str(out["event_date"])
    if "event_time" in out:
        out["time"] = out["event_time"]
    # Convert timestamps
    for ts in ("created_at", "updated_at"):
        if ts in out and hasattr(out[ts], "isoformat"):
            out[ts] = out[ts].isoformat()
    return out


@app.get("/api/events")
def list_events(category: Optional[str] = None, featured: Optional[bool] = None):
    ensure_seed()
    filt = {}
    if category:
        filt["category"] = category
    if featured is not None:
        filt["is_featured"] = featured
    try:
        docs = get_documents("event", filt)
        return {"events": [serialize_event(d) for d in docs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events", status_code=201)
def create_event(event: EventCreate):
    try:
        # Validate using schema
        _ = EventSchema(**event.model_dump())
        inserted_id = create_document("event", event.model_dump())
        return {"id": inserted_id, "message": "Event created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
