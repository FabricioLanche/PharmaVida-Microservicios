from datetime import datetime

from sqlalchemy.orm import Session
from app.productos.domain import ProductoDB

def get_by_id(db: Session, producto_id: int):
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

def get_by_nombre(db: Session, nombre: str):
    return db.query(ProductoDB).filter(ProductoDB.nombre == nombre).first()

def get_all(db: Session, skip=0, limit=100, tipo=None, stock_minimo=None):
    query = db.query(ProductoDB)
    if tipo:
        query = query.filter(ProductoDB.tipo.ilike(f"%{tipo}%"))
    if stock_minimo is not None:
        query = query.filter(ProductoDB.stock >= stock_minimo)
    return query.offset(skip).limit(limit).all()

def get_by_tipo(db: Session, tipo: str):
    return db.query(ProductoDB).filter(ProductoDB.tipo.ilike(f"%{tipo}%")).all()

def get_stock_bajo(db: Session, minimo: int):
    return db.query(ProductoDB).filter(ProductoDB.stock < minimo).all()

def get_con_receta(db: Session):
    return db.query(ProductoDB).filter(ProductoDB.requiere_receta.is_(True)).all()

def get_sin_receta(db: Session):
    return db.query(ProductoDB).filter(ProductoDB.requiere_receta.is_(False)).all()

def create(db: Session, producto: dict):
    db_producto = ProductoDB(**producto)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def update(db: Session, producto, update_data: dict):
    for field, value in update_data.items():
        setattr(producto, field, value)
    producto.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(producto)
    return producto

def update_stock(db: Session, producto, nuevo_stock: int):
    producto.stock = nuevo_stock
    producto.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(producto)
    return producto

def delete(db: Session, producto):
    db.delete(producto)
    db.commit()