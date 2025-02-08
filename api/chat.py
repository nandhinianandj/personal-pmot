from fastapi import APIRouter, HTTPException
import ollama
import httpx
import json
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "llama2"

class ChatResponse(BaseModel):
    response: str
    model: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Format messages for Ollama
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": request.model,
                    "messages": formatted_messages
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="LLM service error")
            
            result = response.json()
            return ChatResponse(
                response=result["message"]["content"],
                model=request.model
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))