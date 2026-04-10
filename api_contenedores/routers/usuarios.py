from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from auth.hashing import hash_password
from auth.dependencies import get_current_user, only_admin

from schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioOut], summary="Listar todos los usuarios")
def get_usuarios(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{user_id}", response_model=UsuarioOut, summary="Obtener usuario por ID")
def get_usuario(user_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario




@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario")
def create_usuario(data: UsuarioCreate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.user == data.user).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    datos = data.model_dump()
    datos["password"] = hash_password(datos["password"])
    nuevo = Usuario(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/public", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear PRIMER usuario admin (bootstrap público, solo si no existe admin)")
def create_usuario_public(data: UsuarioCreate, db: Session = Depends(get_db)):
    # Solo si no existe ningún admin
    if db.query(Usuario).filter(Usuario.rol == "admin").first():
        raise HTTPException(status_code=403, detail="Admin ya existe. Use /usuarios/ con autenticación.")

    if db.query(Usuario).filter(Usuario.user == data.user).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    # Forzar rol admin para bootstrap
    datos = data.model_dump()
    datos["rol"] = "admin"
    datos["password"] = hash_password(datos["password"])
    nuevo = Usuario(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo



@router.put("/{user_id}", response_model=UsuarioOut, summary="Actualizar usuario")
def update_usuario(user_id: int, data: UsuarioUpdate, admin=Depends(only_admin), db: Session = Depends(get_db)):
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
def delete_usuario(user_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()