from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/faq", tags=["FAQ"])

# Modelo Pydantic
class FAQ(BaseModel):
    id: int
    pregunta: str
    descripcion: str

# "Base de datos" en memoria
faq_db: List[FAQ] = []

# Crear nueva pregunta frecuente
@router.post("/", response_model=FAQ)
def create_faq(faq: FAQ):
    if any(item.id == faq.id for item in faq_db):
        raise HTTPException(status_code=400, detail="ID ya existe")
    faq_db.append(faq)
    return faq

# Listar todas las preguntas frecuentes
@router.get("/", response_model=List[FAQ])
def list_faq():
    return faq_db

# Obtener una pregunta frecuente por ID
@router.get("/{faq_id}", response_model=FAQ)
def get_faq(faq_id: int):
    for item in faq_db:
        if item.id == faq_id:
            return item
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")

# Actualizar una pregunta frecuente
@router.put("/{faq_id}", response_model=FAQ)
def update_faq(faq_id: int, faq_update: FAQ):
    for index, item in enumerate(faq_db):
        if item.id == faq_id:
            faq_db[index] = faq_update
            return faq_update
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")

# Eliminar una pregunta frecuente
@router.delete("/{faq_id}")
def delete_faq(faq_id: int):
    for index, item in enumerate(faq_db):
        if item.id == faq_id:
            del faq_db[index]
            return {"message": "Pregunta frecuente eliminada"}
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")
