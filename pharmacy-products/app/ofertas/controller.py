from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ofertas.dto import OfertaCreate, OfertaUpdate, OfertaResponse
from app.ofertas.service import (
    crear_oferta, obtener_oferta, obtener_ofertas,
    actualizar_oferta, eliminar_oferta
)

router = APIRouter(
    prefix="/ofertas",
    tags=["Ofertas"]
)

@router.post("/crear", response_model=OfertaResponse, status_code=status.HTTP_201_CREATED)
def crear(oferta: OfertaCreate, db: Session = Depends(get_db)):
    return OfertaResponse.from_orm(crear_oferta(db, oferta))

@router.get("/all", response_model=list[OfertaResponse])
def listar(db: Session = Depends(get_db)):
    return [OfertaResponse.from_orm(o) for o in obtener_ofertas(db)]

@router.get("/{oferta_id}", response_model=OfertaResponse)
def obtener(oferta_id: int, db: Session = Depends(get_db)):
    return OfertaResponse.from_orm(obtener_oferta(db, oferta_id))

@router.put("/{oferta_id}", response_model=OfertaResponse)
def actualizar(oferta_id: int, oferta_update: OfertaUpdate, db: Session = Depends(get_db)):
    return OfertaResponse.from_orm(actualizar_oferta(db, oferta_id, oferta_update))

@router.delete("/{oferta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(oferta_id: int, db: Session = Depends(get_db)):
    eliminar_oferta(db, oferta_id)