from fastapi import FastAPI

app = FastAPI(
    title="WhatsApp Chatbot API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "WhatsApp Chatbot API is running 🚀"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }