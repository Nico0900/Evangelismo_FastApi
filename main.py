from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import images, user

app = FastAPI()

IMAGES_DIR = "images"
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(images.router)
app.include_router(user.router)
