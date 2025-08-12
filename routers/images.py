from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/archivos-imagenes", tags=["Imagenes"])

IMAGES_DIR = "images"
image_extensions = (".png", ".jpg", ".jpeg", ".gif")

@router.get("/")
def list_images():
    result = []
    for root, dirs, files in os.walk(IMAGES_DIR):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, IMAGES_DIR).replace("\\", "/")
                result.append({"name": file, "url": f"http://localhost:8000/images/{relative_path}"})
    return {"images": result}

@router.get("/serve/{path:path}")
def serve_image(path: str):
    file_path = os.path.join(IMAGES_DIR, path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(file_path, headers={"Access-Control-Allow-Origin": "*"})

@router.post("/")
async def upload_image(file: UploadFile = File(...), folder: str = Form("")):
    save_dir = os.path.join(IMAGES_DIR, folder)
    os.makedirs(save_dir, exist_ok=True)

    filename = file.filename
    if not filename.lower().endswith(image_extensions):
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

    save_path = os.path.join(save_dir, filename)
    if os.path.exists(save_path):
        raise HTTPException(status_code=400, detail="Archivo ya existe")

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    relative_path = os.path.relpath(save_path, IMAGES_DIR).replace("\\", "/")
    return {"message": "Imagen subida", "url": f"http://localhost:8000/images/{relative_path}"}

@router.put("/rename")
def rename_image(old_path: str = Form(...), new_name: str = Form(...)):
    old_full_path = os.path.join(IMAGES_DIR, old_path)
    if not os.path.exists(old_full_path):
        raise HTTPException(status_code=404, detail="Imagen original no encontrada")

    if not new_name.lower().endswith(image_extensions):
        raise HTTPException(status_code=400, detail="Nuevo nombre debe tener extensión válida")

    new_full_path = os.path.join(os.path.dirname(old_full_path), new_name)
    if os.path.exists(new_full_path):
        raise HTTPException(status_code=400, detail="Ya existe un archivo con el nuevo nombre")

    os.rename(old_full_path, new_full_path)
    relative_path = os.path.relpath(new_full_path, IMAGES_DIR).replace("\\", "/")
    return {"message": "Imagen renombrada", "url": f"http://localhost:8000/images/{relative_path}"}

@router.delete("/")
def delete_image(path: str):
    full_path = os.path.join(IMAGES_DIR, path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    os.remove(full_path)
    return {"message": f"Imagen '{path}' eliminada"}

class DeleteImagesRequest(BaseModel):
    paths: List[str]

@router.post("/delete-multiple")
def delete_multiple_images(request: DeleteImagesRequest):
    eliminadas = []
    no_encontradas = []

    for path in request.paths:
        full_path = os.path.join(IMAGES_DIR, path)
        if os.path.exists(full_path):
            os.remove(full_path)
            eliminadas.append(path)
        else:
            no_encontradas.append(path)

    return {
        "eliminadas": eliminadas,
        "no_encontradas": no_encontradas
    }
