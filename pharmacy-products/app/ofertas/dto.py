from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OfertaDetalleIn(BaseModel):
    producto_id: int
    descuento: float

class OfertaCreate(BaseModel):
    detalles: List[OfertaDetalleIn]
    fecha_vencimiento: datetime

class OfertaUpdate(BaseModel):
    detalles: Optional[List[OfertaDetalleIn]] = None
    fecha_vencimiento: Optional[datetime] = None

class OfertaDetalleResponse(OfertaDetalleIn):
    id: int

class OfertaResponse(BaseModel):
    id: int
    fecha_vencimiento: datetime
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    detalles: List[OfertaDetalleResponse]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            fecha_vencimiento=obj.fecha_vencimiento,
            fecha_creacion=obj.fecha_creacion,
            fecha_actualizacion=obj.fecha_actualizacion,
            detalles=[OfertaDetalleResponse(
                id=d.id,
                producto_id=d.producto_id,
                descuento=d.descuento
            ) for d in obj.detalles]
        )

    class Config:
        orm_mode = True