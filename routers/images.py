from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os

router = APIRouter(prefix="/archivos-imagenes", tags=["Imagenes"])

IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

image_extensions = (".png", ".jpg", ".jpeg", ".gif")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def get_safe_path(relative_path: str) -> Path:
    """
    Devuelve una ruta segura dentro de IMAGES_DIR,
    evitando que alguien use '..' para salir de la carpeta.
    """
    full_path = IMAGES_DIR / relative_path
    try:
        full_path.resolve().relative_to(IMAGES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Ruta no permitida")
    return full_path


@router.get("/")
def list_images():
    result = []
    for file_path in IMAGES_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            relative_path = file_path.relative_to(IMAGES_DIR).as_posix()
            result.append({"name": file_path.name, "url": f"{BASE_URL}/archivos-imagenes/serve/{relative_path}"})
    return {"images": result}


@router.get("/serve/{path:path}")
def serve_image(path: str):
    file_path = get_safe_path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(file_path, headers={"Access-Control-Allow-Origin": "*"})


@router.post("/")
async def upload_image(file: UploadFile = File(...), folder: str = Form("")):
    save_dir = get_safe_path(folder)
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename
    if not filename.lower().endswith(image_extensions):
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

    save_path = save_dir / filename
    if save_path.exists():
        raise HTTPException(status_code=400, detail="Archivo ya existe")

    try:
        contents = await file.read()
        save_path.write_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando la imagen: {str(e)}")

    relative_path = save_path.relative_to(IMAGES_DIR).as_posix()
    return {"message": "Imagen subida", "url": f"{BASE_URL}/archivos-imagenes/serve/{relative_path}"}


@router.put("/rename")
def rename_image(old_path: str = Form(...), new_name: str = Form(...)):
    old_full_path = get_safe_path(old_path)
    if not old_full_path.exists() or not old_full_path.is_file():
        raise HTTPException(status_code=404, detail="Imagen original no encontrada")

    if not new_name.lower().endswith(image_extensions):
        raise HTTPException(status_code=400, detail="Nuevo nombre debe tener extensión válida")

    new_full_path = old_full_path.parent / new_name
    if new_full_path.exists():
        raise HTTPException(status_code=400, detail="Ya existe un archivo con el nuevo nombre")

    old_full_path.rename(new_full_path)
    relative_path = new_full_path.relative_to(IMAGES_DIR).as_posix()
    return {"message": "Imagen renombrada", "url": f"{BASE_URL}/archivos-imagenes/serve/{relative_path}"}


@router.delete("/")
def delete_image(path: str):
    full_path = get_safe_path(path)
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    full_path.unlink()
    return {"message": f"Imagen '{path}' eliminada"}


class DeleteImagesRequest(BaseModel):
    paths: List[str]


@router.post("/delete-multiple")
def delete_multiple_images(request: DeleteImagesRequest):
    eliminadas = []
    no_encontradas = []

    for path in request.paths:
        full_path = get_safe_path(path)
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            eliminadas.append(path)
        else:
            no_encontradas.append(path)

    return {"eliminadas": eliminadas, "no_encontradas": no_encontradas}
