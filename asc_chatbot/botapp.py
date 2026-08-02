import uvicorn
from main import app  # reuse the same app, but we can also run separately
# This is just a convenience entry point for local testing.
# We'll use the /bot endpoints.

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)