from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trendsapi import router as trends_router
from analyzeapi import router as analyze_router

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)