from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.service.register import router as register_router
from src.service.user import router as user_router
from src.service.friendship import router as friendship_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Tu URL del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

# Incluir rutas desde routes.py
app.include_router(register_router, tags=["Register"]) 
app.include_router(user_router, tags=["User"])
app.include_router(friendship_router, tags=["Friendship"])

# Handler requerido por Vercel
def handler(req, context):
    return app

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/favicon.ico")
def favicon():
    return {"message": "This is the favicon placeholder"}