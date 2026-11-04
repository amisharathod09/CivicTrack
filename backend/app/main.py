from fastapi import FastAPI

from app.routes.department_routes import router as department_router
from app.routes.category_routes import router as category_router
from app.routes.location_routes import router as location_router
from app.routes.service_request_routes import router as service_request_router
from app.routes.assignment_routes import router as assignment_router
from app.routes.status_history_routes import router as status_history_router
from app.routes.feedback_routes import router as feedback_router
from app.routes.attachment_routes import router as attachment_router


# Create FastAPI application
app = FastAPI(
    title="CivicTrack API",
    description="AI-Powered Smart Public Service Request & Operations Analytics Platform",
    version="1.0.0"
)


# Register API routers
app.include_router(department_router)
app.include_router(category_router)
app.include_router(location_router)
app.include_router(service_request_router)
app.include_router(assignment_router)
app.include_router(status_history_router)
app.include_router(feedback_router)
app.include_router(attachment_router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to CivicTrack API!",
        "status": "Backend is running successfully"
    }