import os
import json
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

# Import routers
from routers import summon  # Assuming summon.py contains the router instance

# --- IP Whitelisting for Docs (same logic as before) ---
ALLOWED_DOCS_IPS_STR = os.environ.get("ALLOWED_DOCS_IPS", "")
ALLOWED_DOCS_IPS = [ip.strip() for ip in ALLOWED_DOCS_IPS_STR.split(',') if ip.strip()]


def verify_ip_for_docs(request: Request):
    source_ip = None
    if "aws.event" in request.scope and request.scope["aws.event"].get("requestContext", {}).get("http"):
        source_ip = request.scope["aws.event"]["requestContext"]["http"].get("sourceIp")
    elif request.client:
        source_ip = request.client.host
    
    print(f"Docs access attempt from IP: {source_ip}. Allowed: {ALLOWED_DOCS_IPS}")  # Replace with logger

    if not ALLOWED_DOCS_IPS:
        print("WARN: ALLOWED_DOCS_IPS is not set. Denying docs access.")
        raise HTTPException(status_code=403, detail="Documentation access is disabled.")
    if source_ip not in ALLOWED_DOCS_IPS:
        print(f"WARN: Forbidden docs access for IP: {source_ip}")
        raise HTTPException(status_code=403, detail="Access to documentation is restricted.")
    return True
# --- End IP Whitelisting ---


app = FastAPI(
    title="Automated Taskmaster API",
    version="0.2.0", # Updated version example
    description="Provides TTRPG utilities like monster summoning.",
    docs_url=None, redoc_url=None, openapi_url=None # Disable defaults
)

# --- Custom Documentation Routes (same logic) ---
@app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(verify_ip_for_docs)])
async def custom_openapi_endpoint():
    return get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)

@app.get("/docs", include_in_schema=False, dependencies=[Depends(verify_ip_for_docs)])
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title + " - Swagger UI")

@app.get("/redoc", include_in_schema=False, dependencies=[Depends(verify_ip_for_docs)])
async def custom_redoc_html():
    return get_redoc_html(openapi_url="/openapi.json", title=app.title + " - ReDoc")

# Include routers
app.include_router(summon.router) # This adds routes from routers/summon.py (e.g., /taskmaster/summon-monster)
# app.include_router(loot.router) # Example for another router

@app.get("/taskmaster/health", include_in_schema=False, tags=["health"]) # Example health check on base path
async def health_check():
    return {"status": "ok", "message": "Automated Taskmaster is operational!"}

# Mangum adapter for AWS Lambda
# The handler in Lambda configuration will be 'handler.lambda_handler_asgi' (or your chosen name)
lambda_handler_asgi = Mangum(app, lifespan="off")
