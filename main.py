from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from routers import images, user, faq
import uvicorn
import os

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir según necesidad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Evangelismo API funcionando correctamente"}

# Archivos estáticos
app.mount("/images", StaticFiles(directory="images"), name="images")

# Rutas
app.include_router(user.router)
app.include_router(faq.router)
app.include_router(images.router)

# Handler Lambda
handler = Mangum(app)

# Iniciar servidor en 0.0.0.0
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Usa variable PORT si está definida
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
