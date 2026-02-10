from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from modeling import chat_reply, generate_description, generate_suggestions, generate_completion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hrms-420.netlify.app",
        "http://127.0.0.1:63601"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------- REQUEST MODELS -------- #

class RequestBody(BaseModel):
    title: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]



@app.post("/generate")
def generate(req: RequestBody):
    return {
        "description": generate_description(req.title)
    }


@app.get("/suggest")
def suggest(q: str):
    return {"suggestions": generate_suggestions(q)}


@app.get("/autocomplete")
def autocomplete(q: str):
    return {"completion": generate_completion(q)}


@app.options("/chat")
def chat_options():
    return Response(status_code=200)


@app.post("/chat")
def chat(req: ChatRequest):
    reply = chat_reply([m.dict() for m in req.messages])
    return {"reply": reply}
