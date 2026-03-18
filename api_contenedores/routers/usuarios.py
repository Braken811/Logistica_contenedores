from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioOut], summary="Listar todos los usuarios")
def get_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{user_id}", response_model=UsuarioOut, summary="Obtener usuario por ID")
def get_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario")
def create_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.user == data.user).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    nuevo = Usuario(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{user_id}", response_model=UsuarioOut, summary="Actualizar usuario")
def update_usuario(user_id: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar usuario")
def delete_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
