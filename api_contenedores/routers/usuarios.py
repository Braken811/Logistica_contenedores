from typing import List
from fastapi import APIRouter, HTTPException, status

from schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioOut], summary="Listar todos los usuarios")
def get_usuarios():
    return load_data("usuarios.json")


@router.get("/{user_id}", response_model=UsuarioOut, summary="Obtener usuario por ID")
def get_usuario(user_id: int):
    usuarios = load_data("usuarios.json")
    usuario = next((u for u in usuarios if u["id_usuario"] == user_id), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario")
def create_usuario(data: UsuarioCreate):
    usuarios = load_data("usuarios.json")
    if any(u["user"] == data.user for u in usuarios):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    nuevo = {
        "id_usuario": get_next_id(usuarios, "id_usuario"),
        "nombres": data.nombres,
        "apellidos": data.apellidos,
        "email": data.email,
        "user": data.user,
        "rol": data.rol.value
    }
    usuarios.append(nuevo)
    save_data("usuarios.json", usuarios)
    return nuevo


@router.put("/{user_id}", response_model=UsuarioOut, summary="Actualizar usuario")
def update_usuario(user_id: int, data: UsuarioUpdate):
    usuarios = load_data("usuarios.json")
    usuario = next((u for u in usuarios if u["id_usuario"] == user_id), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):
            usuario[field] = value.value
        else:
            usuario[field] = value

    save_data("usuarios.json", usuarios)
    return usuario


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar usuario")
def delete_usuario(user_id: int):
    usuarios = load_data("usuarios.json")
    usuario = next((u for u in usuarios if u["id_usuario"] == user_id), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuarios.remove(usuario)
    save_data("usuarios.json", usuarios)
