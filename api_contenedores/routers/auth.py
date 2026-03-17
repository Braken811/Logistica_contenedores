from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import LoginRequest, TokenResponse
from auth_utils import verify_password, create_access_token
import models

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve un JWT.
    - **user**: nombre de usuario
    - **password**: contraseña en texto plano
    """
    usuario = db.query(models.Usuario).filter(
        models.Usuario.user == credentials.user
    ).first()

    if not usuario or not verify_password(credentials.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    token = create_access_token({"sub": str(usuario.id_usuario), "rol": usuario.rol})

    return TokenResponse(
        access_token=token,
        rol=usuario.rol,
        nombres=usuario.nombres
    )
