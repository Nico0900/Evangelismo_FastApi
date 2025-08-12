from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from routers import images, user, faq

app = FastAPI()

# Lista de orígenes permitidos (puedes poner "*" para todos)
origins = [
    "http://127.0.0.1:5501",  # tu frontend local
    "http://localhost:5501"   # a veces el navegador usa localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # o ["*"] si no quieres restricciones
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, PUT, DELETE...
    allow_headers=["*"],
)

IMAGES_DIR = "images"
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(user.router)   # prefijo cambiado en user.py
app.include_router(faq.router)    # prefijo cambiado en faq.py
app.include_router(images.router) # prefijo cambiado en images.py


handler = Mangum(app)