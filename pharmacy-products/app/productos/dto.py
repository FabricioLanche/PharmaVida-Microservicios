from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    requiere_receta: bool = Field(default=False)

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    requiere_receta: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            nombre=obj.nombre,
            tipo=obj.tipo,
            precio=obj.precio,
            stock=obj.stock,
            requiere_receta=obj.requiere_receta,
            fecha_creacion=obj.fecha_creacion,
            fecha_actualizacion=obj.fecha_actualizacion,
        )

    class Config:
        from_attributes = True


class ProductosPaginadosResponse(BaseModel):
    total: int
    page: int
    pagesize: int
    productos: List[ProductoResponse]
