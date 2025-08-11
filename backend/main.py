from fastapi import FastAPI

# This creates the main application instance
app = FastAPI(
    title="KnowUrBite API",
    description="API for real-time food adulteration reporting and risk mapping.",
    version="0.1.0"
)

# This defines a "route" for the root URL
@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the KnowUrBite API!"}

# A health check endpoint to verify service status
@app.get("/health")
def health_check():
    """Returns the operational status of the API."""
    return {"status": "ok", "message": "API is healthy"}