from app.ofertas.domain import OfertaDB, OfertaDetalleDB
from sqlalchemy.orm import Session
from datetime import datetime

def get_by_id(db: Session, oferta_id: int):
    return db.query(OfertaDB).filter(OfertaDB.id == oferta_id).first()

def get_all(db: Session):
    return db.query(OfertaDB).all()

def create(db: Session, oferta: dict):
    detalles = oferta.pop("detalles", [])
    db_oferta = OfertaDB(**oferta)
    db.add(db_oferta)
    db.flush()  # get oferta id

    for detalle in detalles:
        db_detalle = OfertaDetalleDB(oferta_id=db_oferta.id, **detalle)
        db.add(db_detalle)
    db.commit()
    db.refresh(db_oferta)
    return db_oferta

def update(db: Session, oferta, update_data: dict):
    if "fecha_vencimiento" in update_data:
        oferta.fecha_vencimiento = update_data["fecha_vencimiento"]
    if "detalles" in update_data and update_data["detalles"] is not None:
        for d in oferta.detalles:
            db.delete(d)
        db.flush()
        for detalle in update_data["detalles"]:
            db_detalle = OfertaDetalleDB(oferta_id=oferta.id, **detalle)
            db.add(db_detalle)
    oferta.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(oferta)
    return oferta

def delete(db: Session, oferta):
    db.delete(oferta)
    db.commit()