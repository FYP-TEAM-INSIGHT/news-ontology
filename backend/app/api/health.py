from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Simple endpoint to check if the server is running.
    """
    return {"status": "OK", "message": "Server is running"}
