from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from auth_utils import hash_password, require_admin, get_current_user
import models

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioOut], summary="Listar todos los usuarios")
def get_usuarios(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    return db.query(models.Usuario).all()


@router.get("/{user_id}", response_model=UsuarioOut, summary="Obtener usuario por ID")
def get_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario")
def create_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    if db.query(models.Usuario).filter(models.Usuario.user == data.user).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    nuevo = models.Usuario(
        nombres  =data.nombres,
        apellidos=data.apellidos,
        email    =data.email,
        user     =data.user,
        password =hash_password(data.password),
        rol      =data.rol.value
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{user_id}", response_model=UsuarioOut, summary="Actualizar usuario")
def update_usuario(
    user_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value.value if hasattr(value, "value") else value)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar usuario")
def delete_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
