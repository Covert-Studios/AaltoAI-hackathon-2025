from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trendsapi import router as trends_router
from analyzeapi import router as analyze_router
from analyze_db import router as analyze_db_router
from ainewsapi import router as ainews_router

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trends_router)
app.include_router(analyze_router)
app.include_router(analyze_db_router)
app.include_router(ainews_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)