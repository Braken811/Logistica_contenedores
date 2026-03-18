from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas import TipoContenedorCreate, TipoContenedorOut
from database import get_db
from models import TipoContenedor

router = APIRouter(prefix="/tipos-contenedores", tags=["Tipos de Contenedores"])


@router.get("/", response_model=List[TipoContenedorOut], summary="Listar tipos")
def get_tipos(db: Session = Depends(get_db)):
    return db.query(TipoContenedor).all()


@router.get("/{tipo_id}", response_model=TipoContenedorOut)
def get_tipo(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.query(TipoContenedor).filter(TipoContenedor.id_tipo == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    return tipo


@router.post("/", response_model=TipoContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear tipo de contenedor")
def create_tipo(data: TipoContenedorCreate, db: Session = Depends(get_db)):
    nuevo = TipoContenedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.query(TipoContenedor).filter(TipoContenedor.id_tipo == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    db.delete(tipo)
    db.commit()
