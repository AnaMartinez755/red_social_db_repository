from  sqlalchemy import create_engine, Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship   
import uuid
from datetime import datetime

DATABASE_URL = "mysql+pymysql://usuario:Thisisthepart9.@localhost/red_social_db"
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


    # FALTA : LINK A SEGUIDORES PUBLICACIONES, COMENTARIOS
class Seguidor(Base):
    __tablename__="seguidores"

    id = Column(Integer , primary_key = True, autoincrement=True)
    usuario_id = Column(String(8) , ForeignKey('usuarios.id'), nullable=False)
    seguidor_id = Column(String(8) , ForeignKey('usuarios.id'), nullable=False)
    fecha_seguimiento =  Column(DateTime , default=  datetime.now())

    #RELACIONES: usuarios seguidor

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

    #RELACIONES: AUTOR , COMENTARIOS

# POR HACER: CREAR TABLAS (CLASES) PARA: 
#comentarios 
#estadisticas
#notificaciones
