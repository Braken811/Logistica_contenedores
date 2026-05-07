import os
import shutil
import random
import string
import logging as _logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session

from auth.hashing import hash_password
from auth.dependencies import get_current_user, only_admin
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioSelfUpdate, UsuarioOut
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
_logger = _logging.getLogger(__name__)

AVATAR_DIR = "uploads/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)

ALLOWED_IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


# ── /me (ANTES de /{user_id} para evitar colisión de rutas) ──────────────────

@router.get("/me", response_model=UsuarioOut, summary="Obtener mi perfil")
def get_me(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return current["user"]


@router.put("/me", response_model=UsuarioOut, summary="Actualizar mi perfil")
def update_me(
    data: UsuarioSelfUpdate,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuario = current["user"]
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        if update_data["password"]:
            update_data["password"] = hash_password(update_data["password"])
        else:
            del update_data["password"]
    for field, value in update_data.items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/me/avatar", summary="Subir foto de perfil")
def upload_avatar(
    file: UploadFile = File(...),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuario = current["user"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMG_EXTS:
        raise HTTPException(status_code=400, detail="Formato de imagen no válido. Use JPG, PNG, GIF o WEBP.")

    filename = f"avatar_{usuario.id_usuario}_{int(datetime.utcnow().timestamp())}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if usuario.ruta_imagen and os.path.exists(usuario.ruta_imagen):
        try:
            os.remove(usuario.ruta_imagen)
        except OSError:
            pass

    url = f"/uploads/avatars/{filename}"
    usuario.ruta_imagen = url
    db.commit()
    return {"url": url}


# ── Verificación de email ────────────────────────────────────────────────────

@router.post("/solicitar-verificacion", summary="Solicitar código de verificación por email")
def solicitar_verificacion(current=Depends(get_current_user), db: Session = Depends(get_db)):
    usuario = current["user"]
    if usuario.email_verificado:
        raise HTTPException(status_code=400, detail="El email ya está verificado")

    codigo = "".join(random.choices(string.digits, k=6))
    usuario.verification_token = codigo
    db.commit()

    _logger.info(f"📧 CÓDIGO DE VERIFICACIÓN PARA {usuario.email}: {codigo}")
    return {"mensaje": f"Código enviado al email {usuario.email}. Revisa los logs del servidor."}


@router.post("/verificar-email", summary="Verificar email con código")
def verificar_email(token: str, current=Depends(get_current_user), db: Session = Depends(get_db)):
    usuario = current["user"]
    if usuario.email_verificado:
        raise HTTPException(status_code=400, detail="Ya verificado")
    if not usuario.verification_token or usuario.verification_token != token:
        raise HTTPException(status_code=400, detail="Código incorrecto")

    usuario.email_verificado = True
    usuario.verification_token = None
    db.commit()
    return {"mensaje": "Email verificado correctamente"}


# ── Bootstrap público ────────────────────────────────────────────────────────

@router.post("/public", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED,
             summary="Crear PRIMER usuario admin (bootstrap público)")
def create_usuario_public(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.rol == "admin").first():
        raise HTTPException(status_code=403, detail="Admin ya existe. Use /usuarios/ con autenticación.")
    if db.query(Usuario).filter(Usuario.user == data.user).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    datos = data.model_dump()
    datos["rol"] = "admin"
    datos["password"] = hash_password(datos["password"])
    nuevo = Usuario(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── CRUD estándar (Admin) ────────────────────────────────────────────────────

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


@router.put("/{user_id}", response_model=UsuarioOut, summary="Actualizar usuario (admin)")
def update_usuario(
    user_id: int,
    data: UsuarioUpdate,
    admin=Depends(only_admin),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        if update_data["password"]:
            update_data["password"] = hash_password(update_data["password"])
        else:
            del update_data["password"]
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
