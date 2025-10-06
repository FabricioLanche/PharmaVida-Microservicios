from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.productos.dto import ProductosPaginadosResponse
from app.productos.dto import (
    ProductoCreate, ProductoUpdate, ProductoResponse
)
from app.productos.service import (
    crear_producto, obtener_producto,
    actualizar_producto, eliminar_producto,
    obtener_productos_paginados,
    obtener_productos_por_receta_paginados,
    obtener_productos_por_tipo_paginados,
    obtener_productos_stock_bajo_paginados,
    obtener_productos_por_nombre_paginados
)

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.get("/paged", response_model=ProductosPaginadosResponse)
def listar_paginado(
    page: int = Query(1, ge=1),
    pagesize: int = Query(25, gt=0),
    db: Session = Depends(get_db)
):
    total, productos = obtener_productos_paginados(db, page, pagesize)
    return ProductosPaginadosResponse(
        total=total,
        page=page,
        pagesize=pagesize,
        productos=[ProductoResponse.from_orm(p) for p in productos]
    )

@router.get("/nombre", response_model=ProductosPaginadosResponse)
def buscar_por_nombre(
    nombre: str = Query(..., description="Texto a buscar en el nombre del producto"),
    page: int = Query(1, ge=1),
    pagesize: int = Query(25, gt=0),
    db: Session = Depends(get_db)
):
    total, productos = obtener_productos_por_nombre_paginados(db, nombre, page, pagesize)
    return ProductosPaginadosResponse(
        total=total,
        page=page,
        pagesize=pagesize,
        productos=[ProductoResponse.from_orm(p) for p in productos]
    )

@router.get("/receta", response_model=ProductosPaginadosResponse)
def listar_por_receta(
    requiere_receta: bool = Query(..., description="True para productos que requieren receta, False para los que no"),
    page: int = Query(1, ge=1),
    pagesize: int = Query(25, gt=0),
    db: Session = Depends(get_db)
):
    total, productos = obtener_productos_por_receta_paginados(db, requiere_receta, page, pagesize)
    return ProductosPaginadosResponse(
        total=total,
        page=page,
        pagesize=pagesize,
        productos=[ProductoResponse.from_orm(p) for p in productos]
    )

@router.get("/tipo", response_model=ProductosPaginadosResponse)
def listar_por_tipo(
    tipo: str = Query(..., description="Tipo de producto"),
    page: int = Query(1, ge=1),
    pagesize: int = Query(25, gt=0),
    db: Session = Depends(get_db)
):
    total, productos = obtener_productos_por_tipo_paginados(db, tipo, page, pagesize)
    return ProductosPaginadosResponse(
        total=total,
        page=page,
        pagesize=pagesize,
        productos=[ProductoResponse.from_orm(p) for p in productos]
    )

@router.get("/stock-bajo", response_model=ProductosPaginadosResponse)
def listar_stock_bajo(
    minimo: int = Query(10, ge=0, description="Stock mínimo"),
    page: int = Query(1, ge=1),
    pagesize: int = Query(25, gt=0),
    db: Session = Depends(get_db)
):
    total, productos = obtener_productos_stock_bajo_paginados(db, minimo, page, pagesize)
    return ProductosPaginadosResponse(
        total=total,
        page=page,
        pagesize=pagesize,
        productos=[ProductoResponse.from_orm(p) for p in productos]
    )

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    return ProductoResponse.from_orm(obtener_producto(db, producto_id))

@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear(producto: ProductoCreate, db: Session = Depends(get_db)):
    return ProductoResponse.from_orm(crear_producto(db, producto))

@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar(producto_id: int, producto_update: ProductoUpdate, db: Session = Depends(get_db)):
    return ProductoResponse.from_orm(actualizar_producto(db, producto_id, producto_update))

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    eliminar_producto(db, producto_id)


