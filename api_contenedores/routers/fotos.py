import os
import shutil
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, status, Depends
from datetime import date
from sqlalchemy.orm import Session

from schemas import FotoOut
from database import get_db
from models import Foto, Contenedor
from auth.dependencies import get_current_user

router = APIRouter(prefix="/fotos", tags=["Fotos de Contenedor"])

UPLOAD_DIR = "uploads/fotos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/contenedor/{contenedor_id}", response_model=List[FotoOut],
            summary="Fotos de un contenedor")
def get_fotos(contenedor_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    return db.query(Foto).filter(Foto.id_contenedor == contenedor_id).all()


@router.post("/contenedor/{contenedor_id}", response_model=FotoOut,
             status_code=status.HTTP_201_CREATED, summary="Subir foto")
def upload_foto(contenedor_id: int, current=Depends(get_current_user), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    ext = os.path.splitext(file.filename)[1]
    filename = f"contenedor_{contenedor_id}_{date.today()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    nueva_foto = Foto(id_contenedor=contenedor_id, ruta_imagen=filepath, fecha_subida=date.today())
    db.add(nueva_foto)
    db.commit()
    db.refresh(nueva_foto)
    return nueva_foto


@router.delete("/{foto_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar foto")
def delete_foto(foto_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    foto = db.query(Foto).filter(Foto.id_foto == foto_id).first()
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    if os.path.exists(foto.ruta_imagen):
        os.remove(foto.ruta_imagen)

    db.delete(foto)
    db.commit()
