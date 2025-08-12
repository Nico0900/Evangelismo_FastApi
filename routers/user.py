from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union

router = APIRouter(prefix="/personas", tags=["personas"])

# Modelos Pydantic
class UsuarioBase(BaseModel):
    id: int
    usuario: str
    contraseña: str
    email: EmailStr
    iglesia: str
    cargo_iglesia: Optional[str] = None
    cargo_zonal: Optional[str] = None
    cargo_nacional: Optional[str] = None

class Usuario(UsuarioBase):
    pass

class Administrador(UsuarioBase):
    rol: str = Field(..., description="Rol del administrador")

class Persona(BaseModel):
    usuario: Optional[Usuario] = None
    administrador: Optional[Administrador] = None

usuarios_db: List[Union[Usuario, Administrador]] = []

@router.post("/", response_model=Persona)
def create_persona(persona: Persona):
    if (persona.usuario is None and persona.administrador is None) or \
       (persona.usuario is not None and persona.administrador is not None):
        raise HTTPException(status_code=400, detail="Debe enviar solo usuario o administrador")

    nuevo = persona.usuario or persona.administrador
    if any(u.id == nuevo.id for u in usuarios_db):
        raise HTTPException(status_code=400, detail="ID ya registrado")
    if any(u.email == nuevo.email for u in usuarios_db):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    usuarios_db.append(nuevo)
    return persona

@router.get("/")
def list_all_users():
    return usuarios_db

@router.get("/filter")
def filter_users(tipo: str = Query(..., regex="^(usuario|administrador)$")):
    if tipo == "usuario":
        return [u for u in usuarios_db if isinstance(u, Usuario)]
    else:
        return [u for u in usuarios_db if isinstance(u, Administrador)]

@router.get("/{user_id}")
def get_user(user_id: int):
    for u in usuarios_db:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.put("/{user_id}")
def update_user(user_id: int, persona: Persona):
    if (persona.usuario is None and persona.administrador is None) or \
       (persona.usuario is not None and persona.administrador is not None):
        raise HTTPException(status_code=400, detail="Debe enviar solo usuario o administrador")

    for i, u in enumerate(usuarios_db):
        if u.id == user_id:
            nuevo = persona.usuario or persona.administrador

            if any(existing.email == nuevo.email and existing.id != user_id for existing in usuarios_db):
                raise HTTPException(status_code=400, detail="Email ya registrado por otro usuario")

            usuarios_db[i] = nuevo
            return nuevo

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(usuarios_db):
        if u.id == user_id:
            del usuarios_db[i]
            return {"message": "Usuario eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

from pydantic import BaseModel
from typing import List

class DeleteUsersRequest(BaseModel):
    ids: List[int]

@router.post("/delete-multiple")
def delete_multiple_users(request: DeleteUsersRequest):
    ids_a_eliminar = set(request.ids)
    eliminados = []
    no_encontrados = []

    global usuarios_db
    usuarios_restantes = []

    for usuario in usuarios_db:
        if usuario.id in ids_a_eliminar:
            eliminados.append(usuario.id)
        else:
            usuarios_restantes.append(usuario)

    no_encontrados = list(ids_a_eliminar - set(eliminados))

    usuarios_db.clear()
    usuarios_db.extend(usuarios_restantes)

    return {
        "eliminados": eliminados,
        "no_encontrados": no_encontrados
    }
