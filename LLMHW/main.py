from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from api.routes import router

app = FastAPI(
    title="Smart Librarian API",
    description="AI chatbot care recomanda carti si oefera rezumate detaliate",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # <– important pentru preflight
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return RedirectResponse("/docs")