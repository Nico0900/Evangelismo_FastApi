from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union

router = APIRouter(prefix="/users", tags=["users"])

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

# Persona que puede ser Usuario o Administrador
class Persona(BaseModel):
    usuario: Optional[Usuario] = None
    administrador: Optional[Administrador] = None

# "Base de datos" simulada en memoria
usuarios_db: List[Union[Usuario, Administrador]] = []

@router.post("/register", response_model=Persona)
def register_persona(persona: Persona):
    # Validar que venga uno solo (usuario o administrador)
    if (persona.usuario is None and persona.administrador is None) or \
       (persona.usuario is not None and persona.administrador is not None):
        raise HTTPException(status_code=400, detail="Debe enviar solo usuario o administrador")

    if persona.usuario:
        if any(u.id == persona.usuario.id for u in usuarios_db):
            raise HTTPException(status_code=400, detail="ID de usuario ya registrado")
        if any(u.email == persona.usuario.email for u in usuarios_db):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        usuarios_db.append(persona.usuario)
        return {"usuario": persona.usuario}

    if persona.administrador:
        if any(u.id == persona.administrador.id for u in usuarios_db):
            raise HTTPException(status_code=400, detail="ID de administrador ya registrado")
        if any(u.email == persona.administrador.email for u in usuarios_db):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        usuarios_db.append(persona.administrador)
        return {"administrador": persona.administrador}

@router.get("/")
def list_all_users():
    return usuarios_db

# Nuevo endpoint para filtrar usuarios o administradores
@router.get("/filter")
def filter_users(tipo: str = Query(..., regex="^(usuario|administrador)$", description="Filtrar por usuario o administrador")):
    if tipo == "usuario":
        return [u for u in usuarios_db if isinstance(u, Usuario)]
    elif tipo == "administrador":
        return [u for u in usuarios_db if isinstance(u, Administrador)]

# POST

# Usuario
# {
#   "usuario": {
#     "id": 1,
#     "usuario": "juanperez",
#     "contraseña": "123456",
#     "email": "juan@example.com",
#     "iglesia": "Iglesia Central"
#   }
# }

# Admin
# {
#   "administrador": {
#     "id": 2,
#     "rol": "admin",
#     "usuario": "admin01",
#     "contraseña": "adminpass",
#     "email": "admin@example.com",
#     "iglesia": "Iglesia Central",
#     "cargo_iglesia": "Pastor",
#     "cargo_zonal": "Coordinador",
#     "cargo_nacional": "Líder"
#   }
# }

