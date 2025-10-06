from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del motor de base de datos
engine_config = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 10,
    "max_overflow": 20,
    "echo": False
}

# Crear el motor con configuración específica para MySQL
engine = create_engine(settings.DATABASE_URL, **engine_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db():
    max_retries = 60
    retry_count = 0

    while retry_count < max_retries:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Conexión a la base de datos establecida exitosamente")
            return True
        except Exception as e:
            retry_count += 1
            logger.warning(f"Intento {retry_count}/{max_retries} - Error conectando a la base de datos: {e}")
            if retry_count < max_retries:
                time.sleep(3)

    logger.error("No se pudo establecer conexión con la base de datos después de varios intentos")
    return False