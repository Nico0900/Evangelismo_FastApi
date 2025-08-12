from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/preguntas-frecuentes", tags=["FAQ"])

class FAQ(BaseModel):
    id: int
    pregunta: str
    descripcion: str

faq_db: List[FAQ] = []

@router.post("/", response_model=FAQ)
def create_faq(faq: FAQ):
    if any(item.id == faq.id for item in faq_db):
        raise HTTPException(status_code=400, detail="ID ya existe")
    faq_db.append(faq)
    return faq

@router.get("/", response_model=List[FAQ])
def list_faq():
    return faq_db

@router.get("/{faq_id}", response_model=FAQ)
def get_faq(faq_id: int):
    for item in faq_db:
        if item.id == faq_id:
            return item
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")

@router.put("/{faq_id}", response_model=FAQ)
def update_faq(faq_id: int, faq_update: FAQ):
    for index, item in enumerate(faq_db):
        if item.id == faq_id:
            faq_db[index] = faq_update
            return faq_update
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")

@router.delete("/{faq_id}")
def delete_faq(faq_id: int):
    for index, item in enumerate(faq_db):
        if item.id == faq_id:
            del faq_db[index]
            return {"message": "Pregunta frecuente eliminada"}
    raise HTTPException(status_code=404, detail="Pregunta frecuente no encontrada")

from pydantic import BaseModel
from typing import List

class DeleteFAQRequest(BaseModel):
    ids: List[int]

@router.post("/delete-multiple")
def delete_multiple_faq(request: DeleteFAQRequest):
    ids_a_eliminar = set(request.ids)
    eliminados = []
    no_encontrados = []

    global faq_db
    restantes = []

    for faq in faq_db:
        if faq.id in ids_a_eliminar:
            eliminados.append(faq.id)
        else:
            restantes.append(faq)

    no_encontrados = list(ids_a_eliminar - set(eliminados))

    faq_db.clear()
    faq_db.extend(restantes)

    return {
        "eliminados": eliminados,
        "no_encontrados": no_encontrados
    }
