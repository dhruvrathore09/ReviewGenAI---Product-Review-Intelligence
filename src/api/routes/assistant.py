"""FastAPI router for AI Review Intelligence Assistant."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.api.schemas.assistant import ChatRequest, ChatResponse, StarterPrompt
from src.api.services.assistant_service import AssistantService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Assistant"])


@router.post("/assistant/chat", response_model=ChatResponse, summary="Send message to AI Review Intelligence Assistant")
def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Processes conversational questions regarding products, failure modes, comparisons, and aspect analytics."""
    try:
        return AssistantService.handle_chat(db, request)
    except Exception as exc:
        logger.error("Error in chat_with_assistant: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant processing error: {str(exc)}"
        )


@router.get("/assistant/starter-prompts", response_model=List[StarterPrompt], summary="Get suggested starter prompts")
def get_starter_prompts() -> List[StarterPrompt]:
    """Returns curated starter prompts for new conversations."""
    return AssistantService.get_starter_prompts()


@router.get("/assistant/status", summary="Check AI Assistant service health")
def get_assistant_status(db: Session = Depends(get_db)):
    """Health check for AI assistant engine."""
    return {
        "status": "active",
        "engine": "Grounded Review Intelligence (PostgreSQL RAG)",
        "model": "Review Intelligence GPT",
        "version": "2.4.0",
        "capabilities": [
            "Head-to-Head Product Comparisons",
            "Defect & Critical Flaw Extraction",
            "Debiased Product Recommendations",
            "Aspect Sentiment Deep Dives",
            "Multi-Turn Conversation Memory"
        ]
    }


@router.get("/qa/status", summary="Legacy Level 7 status check")
def get_qa_status():
    """Endpoint for Level 7 activation verification."""
    return {
        "status": "online",
        "level": 7,
        "feature": "Review Intelligence Assistant",
        "ready": True
    }
