from fastapi import APIRouter, HTTPException
from app.content.founder_stories import get_founder_story

router = APIRouter(prefix="/api/content", tags=["content"])

@router.get("/founder-story/{business}")
def founder_story(business: str):
    story = get_founder_story(business)
    if not story:
        raise HTTPException(status_code=404, detail="No story found for this business")
    return {"business": business, "cards": story}