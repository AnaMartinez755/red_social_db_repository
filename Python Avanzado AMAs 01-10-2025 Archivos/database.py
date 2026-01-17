from  sqlalchemy import create_engine, Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship   
import uuid
from datetime import datetime
from  dotenv import load_dotenv
import os

load_dotenv()

# Obtener desde .env con las variables de TU LOCAL (MYSQL)

config = {
    "usuario":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "host":os.getenv("DB_HOST"),
    "port":os.getenv("DB_PORT"),
    "nombre_db":os.getenv("DB_NAME")
}


DATABASE_URL = f"mysql+pymysql://{config['usuario']}:{config['password']}@{config['host']}:{config['port']}/{config['nombre_db']}"

# DATABASE_URL = "sqlite:///red_social.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base() # Clase padre para la inicializacion de los modelos 
Session = sessionmaker(bind=engine) #Sesion link -> engine (motor de base de datos)

class UsuariosBD(Base):
    __tablename__ = 'usuarios'

    id = Column(String(8) , primary_key = True, default= lambda : str(uuid.uuid4())[:8] )
    nombre = Column( String(100) , nullable=False)
    email =  Column(String(100), nullable= False, unique=True)
    tipo =  Column(String(20), nullable=False)
    industria =  Column(String(100), nullable=True)
    fecha_registro =  Column(DateTime , default=  datetime.now())

    #Relaciones
    publicaciones = relationship("PublicacionesDB" , backref="autor_rel" , cascade="all, delete-orphan")
    comentarios = relationship("ComentariosDB" , backref="usuario_rel" , cascade="all, delete-orphan")
    seguidor_rel = relationship("Seguidor" ,foreign_keys= "Seguidor.usuario_id",  backref= "usuario_rel")
    seguidos_rel = relationship("Seguidor" ,foreign_keys="Seguidor.seguidor_id", backref="seguidor_rel")

    
class Seguidor(Base):
    __tablename__="seguidores"

    id = Column(Integer , primary_key = True, autoincrement=True)
    usuario_id = Column(String(8) , ForeignKey('usuarios.id'), nullable=False)
    seguidor_id = Column(String(8) , ForeignKey('usuarios.id'), nullable=False)
    fecha_seguimiento =  Column(DateTime , default=  datetime.now())

class PublicacionesDB(Base):
    __tablename__ = "publicaciones"

    id = Column(String(8) , primary_key = True, default= lambda : str(uuid.uuid4())[:8] )
    tipo = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    autor_id = Column(String(8), ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion= Column(DateTime , default=datetime.now())
    likes = Column(Integer,default=0)

    #cAMPOS ESPECIFICOS POR TIPO
    ruta_imagen = Column(String(200), nullable=True)
    ruta_video = Column(String(200),nullable=True)
    duracion = Column(Integer, nullable=True)
    fecha_evento = Column(DateTime, nullable=True)
    ubicacion = Column(String(200), nullable=True)
    asistentes =Column(Text, nullable=True)
    publico_objetivo = Column(String(100),nullable=True)
    frecuencia_publicacion = Column(String(50), nullable=True)
    clics = Column(Integer, default=0)

    #RELACIONES
    comentarios = relationship("ComentariosDB" , backref="publicaciones_rel" , cascade="all, delete-orphan")



class ComentariosDB(Base):
    __tablename__ = "comentarios"

    id = Column(String(8) , primary_key = True, default= lambda : str(uuid.uuid4())[:8] )
    fecha = Column(DateTime, default = datetime.now())
    contenido = Column(Text , nullable=False)
    usuario_id = Column(String(8) , ForeignKey('usuarios.id'), nullable=False)
    publicacion_id = Column( String(8), ForeignKey('publicaciones.id'), nullable=False)


class EstadisticasDB(Base):
    __tablename__ = "estadisticas"

    id = Column(Integer, primary_key=True , autoincrement=True)
    fecha = Column(DateTime, default = datetime.now())
    total_usuarios= Column(Integer, default= 0 )
    total_publicaciones = Column(Integer, default= 0 )
    total_comentarios= Column(Integer, default= 0 )
    total_likes = Column(Integer, default= 0 )
    total_clics= Column(Integer, default= 0 )
    

class NotificacionesDB(Base):
    __tablename__ = "notificaciones"

    id = Column( Integer, primary_key=True, autoincrement=True)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default = datetime.now())
    leida = Column(Boolean , default=False)


def crear_tablas():
    Base.metadata.create_all(engine)
    print("Tablas creadas exitosamente")

def obtener_sesion():
    return Session()
