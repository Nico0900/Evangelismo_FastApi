from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/list", tags=["images"])

IMAGES_DIR = "images"
image_extensions = (".png", ".jpg", ".jpeg", ".gif")

def find_images(base_path):
    result = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, IMAGES_DIR)
                result.append(relative_path.replace("\\", "/"))
    return result

def find_images_in_path(relative_path: str):
    full_path = os.path.join(IMAGES_DIR, relative_path)
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return None
    return find_images(full_path)

@router.get("/")
def list_all_images():
    files = find_images(IMAGES_DIR)
    images = [{"name": f.split("/")[-1], "url": f"http://localhost:8000/images/{f}"} for f in files]
    return {"images": images}

@router.get("/{folder1}")
def list_images_in_folder1(folder1: str):
    files = find_images_in_path(folder1)
    if files is None:
        raise HTTPException(status_code=404, detail=f"Carpeta '{folder1}' no encontrada")
    images = [{"name": f.split("/")[-1], "url": f"http://localhost:8000/images/{f}"} for f in files]
    return {"folder": folder1, "images": images}

@router.get("/{folder1}/{folder2}")
def list_images_in_folder2(folder1: str, folder2: str):
    relative_path = os.path.join(folder1, folder2)
    files = find_images_in_path(relative_path)
    if files is None:
        raise HTTPException(status_code=404, detail=f"Carpeta '{relative_path}' no encontrada")
    images = [{"name": f.split("/")[-1], "url": f"http://localhost:8000/images/{f}"} for f in files]
    return {"folder": relative_path, "images": images}


