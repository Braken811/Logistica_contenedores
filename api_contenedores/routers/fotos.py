import os
import shutil
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from datetime import date

from schemas import FotoOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/fotos", tags=["Fotos de Contenedor"])

UPLOAD_DIR = "uploads/fotos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/contenedor/{contenedor_id}", response_model=List[FotoOut],
            summary="Fotos de un contenedor")
def get_fotos(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == contenedor_id for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    fotos = load_data("fotos.json")
    return [f for f in fotos if f["id_contenedor"] == contenedor_id]


@router.post("/contenedor/{contenedor_id}", response_model=FotoOut,
             status_code=status.HTTP_201_CREATED, summary="Subir foto")
def upload_foto(contenedor_id: int, file: UploadFile = File(...)):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == contenedor_id for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    ext = os.path.splitext(file.filename)[1]
    filename = f"contenedor_{contenedor_id}_{date.today()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    fotos = load_data("fotos.json")
    nueva_foto = {
        "id_foto": get_next_id(fotos, "id_foto"),
        "id_contenedor": contenedor_id,
        "ruta_imagen": filepath,
        "fecha_subida": date.today().isoformat()
    }
    fotos.append(nueva_foto)
    save_data("fotos.json", fotos)
    return nueva_foto


@router.delete("/{foto_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar foto")
def delete_foto(foto_id: int):
    fotos = load_data("fotos.json")
    foto = next((f for f in fotos if f["id_foto"] == foto_id), None)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    if os.path.exists(foto["ruta_imagen"]):
        os.remove(foto["ruta_imagen"])

    fotos.remove(foto)
    save_data("fotos.json", fotos)
