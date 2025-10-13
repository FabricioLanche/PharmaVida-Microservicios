from sqlalchemy.orm import Session
from app.productos.repository import (
    get_by_id, get_by_nombre, get_all, create, update, delete,
    get_by_tipo, get_stock_bajo, get_con_receta, get_sin_receta, update_stock
)
from app.productos.dto import ProductoCreate, ProductoUpdate

from fastapi import HTTPException, status, Query

def crear_producto(db: Session, producto: ProductoCreate):
    if get_by_nombre(db, producto.nombre):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un producto con este nombre")
    data = producto.dict()
    data["requiere_receta"] = 1 if data["requiere_receta"] else 0
    return create(db, data)

def obtener_productos(db: Session, skip=0, limit=100, tipo=None, stock_minimo=None):
    return get_all(db, skip, limit, tipo, stock_minimo)

def obtener_producto(db: Session, producto_id: int):
    producto = get_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

def actualizar_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    producto = get_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    update_data = producto_update.dict(exclude_unset=True)
    return update(db, producto, update_data)

def eliminar_producto(db: Session, producto_id: int):
    producto = get_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    delete(db, producto)

def actualizar_stock_producto(db: Session, producto_id: int, nuevo_stock: int):
    producto = get_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if nuevo_stock < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="nuevo_stock debe ser un número mayor o igual a 0")
    return update_stock(db, producto, nuevo_stock)

def obtener_productos_por_tipo(db: Session, tipo: str):
    return get_by_tipo(db, tipo)

def obtener_productos_stock_bajo(db: Session, minimo: int):
    return get_stock_bajo(db, minimo)

def obtener_productos_con_receta(db: Session):
    return get_con_receta(db)

def obtener_productos_sin_receta(db: Session):
    return get_sin_receta(db)

def paginar_query(query: Query, page: int, pagesize: int):
    total = query.count()
    skip = (page - 1) * pagesize
    items = query.offset(skip).limit(pagesize).all()
    return total, items

def obtener_productos_paginados(db: Session, page: int = 1, pagesize: int = 25):
    query = db.query(get_by_id.__globals__['ProductoDB'])
    return paginar_query(query, page, pagesize)

def obtener_productos_por_tipo_paginados(db: Session, tipo: str, page: int = 1, pagesize: int = 25):
    query = db.query(get_by_id.__globals__['ProductoDB']).filter(get_by_id.__globals__['ProductoDB'].tipo.ilike(f"%{tipo}%"))
    return paginar_query(query, page, pagesize)

def obtener_productos_stock_bajo_paginados(db: Session, minimo: int, page: int = 1, pagesize: int = 25):
    query = db.query(get_by_id.__globals__['ProductoDB']).filter(get_by_id.__globals__['ProductoDB'].stock < minimo)
    return paginar_query(query, page, pagesize)

def obtener_productos_por_receta_paginados(db: Session, requiere_receta: bool, page: int = 1, pagesize: int = 25):
    query = db.query(get_by_id.__globals__['ProductoDB']).filter(get_by_id.__globals__['ProductoDB'].requiere_receta.is_(requiere_receta))
    return paginar_query(query, page, pagesize)

def obtener_productos_por_nombre_paginados(db: Session, nombre: str, page: int = 1, pagesize: int = 25):
    ProductoDB = get_by_id.__globals__['ProductoDB']
    query = db.query(ProductoDB).filter(ProductoDB.nombre.ilike(f"%{nombre}%"))
    return paginar_query(query, page, pagesize)