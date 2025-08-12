from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Union

router = APIRouter(prefix="/personas", tags=["Usuarios"])

# MODELOS
class UsuarioBase(BaseModel):
    id: Optional[int] = None  # Ignorado en creación, mostrado en respuesta
    usuario: str
    apellido: str
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

    @model_validator(mode="after")
    def check_only_one(cls, values):
        usuario = values.usuario
        administrador = values.administrador
        if (usuario is None and administrador is None) or (usuario is not None and administrador is not None):
            raise ValueError("Debe enviar solo uno: usuario o administrador")
        return values

class DeleteUsersRequest(BaseModel):
    ids: List[int]

# DB simulada
usuarios_db: List[Union[Usuario, Administrador]] = []
id_counter = 1  # Autoincremental

# ENDPOINTS

@router.get("/")
def list_all_users():
    return usuarios_db

@router.get("/filter")
def filter_users(tipo: str = Query(..., pattern="^(usuario|administrador)$")):
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

@router.post("/", response_model=Persona)
def create_persona(persona: Persona):
    global id_counter

    nuevo = persona.usuario or persona.administrador

    # Validar email único
    if any(u.email == nuevo.email for u in usuarios_db):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Asignar ID automático, ignorando el id que venga en la request
    nuevo_dict = nuevo.dict(exclude={"id"})
    nuevo_dict["id"] = id_counter
    id_counter += 1

    if isinstance(nuevo, Usuario):
        nuevo_obj = Usuario(**nuevo_dict)
    else:
        nuevo_obj = Administrador(**nuevo_dict)

    usuarios_db.append(nuevo_obj)
    return {"usuario": nuevo_obj} if isinstance(nuevo_obj, Usuario) else {"administrador": nuevo_obj}

@router.put("/{user_id}")
def update_user(user_id: int, persona: Persona):
    if (persona.usuario is None and persona.administrador is None) or \
       (persona.usuario is not None and persona.administrador is not None):
        raise HTTPException(status_code=400, detail="Debe enviar solo usuario o administrador")

    for i, u in enumerate(usuarios_db):
        if u.id == user_id:
            nuevo = persona.usuario or persona.administrador

            # Validar email único excepto el usuario que se actualiza
            if any(existing.email == nuevo.email and existing.id != user_id for existing in usuarios_db):
                raise HTTPException(status_code=400, detail="Email ya registrado por otro usuario")

            nuevo_dict = nuevo.dict(exclude={"id"})
            nuevo_dict["id"] = user_id  # Mantener mismo ID

            if isinstance(nuevo, Usuario):
                usuarios_db[i] = Usuario(**nuevo_dict)
            else:
                usuarios_db[i] = Administrador(**nuevo_dict)
            return usuarios_db[i]

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(usuarios_db):
        if u.id == user_id:
            del usuarios_db[i]
            return {"message": "Usuario eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/delete-multiple")
def delete_multiple_users(
    ids: Optional[List[int]] = Query(None, description="IDs a eliminar (pueden enviarse por query)"),
    request: Optional[DeleteUsersRequest] = Body(None)
):
    if not ids and request:
        ids = request.ids

    if not ids:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un ID para eliminar")

    ids_a_eliminar = set(ids)
    eliminados = []
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
