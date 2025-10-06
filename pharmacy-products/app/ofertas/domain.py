from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class OfertaDB(Base):
    __tablename__ = "ofertas"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_vencimiento = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())
    detalles = relationship("OfertaDetalleDB", cascade="all, delete-orphan", back_populates="oferta")

class OfertaDetalleDB(Base):
    __tablename__ = "ofertas_detalle"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    oferta_id = Column(Integer, ForeignKey("ofertas.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    descuento = Column(Float, nullable=False)
    oferta = relationship("OfertaDB", back_populates="detalles")