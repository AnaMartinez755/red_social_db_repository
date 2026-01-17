from abc import ABC, abstractmethod
from typing import List, Dict
import uuid
from datetime import datetime
from database import obtener_sesion, PublicacionesDB, ComentariosDB
import json

class Publicacion(ABC):
    def __init__(self, contenido: str, autor, db_id=None):
        self.id = db_id or str(uuid.uuid4())[:8]  # id unico abreviado
        self.autor = autor
        self.contenido = contenido
        self.fecha_creacion = datetime.now()
        self.likes = 0
        self.comentarios: List[Dict] = [] # Arreglo de diccionarios 
        self._visibilidad = "publico"
        self._session = obtener_sesion()
        self._db_publicacion = None
    @abstractmethod
    def tipo(self):
        pass
    def _guardar_en_db(self,**kwargs):
        try:
            asistentes_json = None
            if hasattr(self,'asistentes') and self.asistentes:
                asistentes_json = json.dump([
                    asistente.id for asistente in self.asistentes
                ])
            db_publicacion = PublicacionesDB( #Preparo
                id = self.id,
                tipo = self.tipo,
                contenido = self.contenido,
                autor_id = self.autor.id,
                fecha_creacion=self.fecha_creacion,
                likes = self.likes,
                ruta_imagen = kwargs.get('ruta_imagen'),
                ruta_video = kwargs.get('ruta_video'),
                duracion = kwargs.get('duracion'),
                fecha_evento =kwargs.get('fecha_evento'),
                ubicacion =kwargs.get('ubicacion'),
                asistentes = asistentes_json,            
                publico_objetivo = kwargs.get('publico_objetivo'),
                frecuencia_publicacion =kwargs.get('frecuencia_publicacion'),
                clics = kwargs.get('clics',0))
            
            self._session.add(db_publicacion) # agrego 
            self._session.commit() #envio
            self._db_publicacion = db_publicacion # actualizar mi variable local
            return True
    
        except Exception as e:
            self._session.rollback() 
            print(f"Error al guardar publicacion: {e}")
            return False
        


    def _traer_pubicaciones_desde_bd(self):
        try: 
            comentarios_db = self._session.query(ComentariosDB).filter_by(
publicacion_id = self.id
            ).all()
            self.comentarios = []
            for comentario_db in comentarios_db:
                comentario_dict_local = {
                    "id":
                    comentario_db.id,
                    "usuario" : comentario_db.usuario_id,
                    "contenido":comentario_db.contenido,
                    "fecha": comentario_db.fecha
                }
                self.comentarios.append(comentario_dict_local)
        except Exception as e:
            print(f"Error al cargar el comentario: {e}")

    def dar_like(self):
        self.likes += 1
        try: 
           db_publicacion =  self._session.query(PublicacionesDB).filter_by(id = self.id).first() 
           if db_publicacion:
               db_publicacion.likes = self.likes
               self._session.commit()
        except Exception as e:
            self._session.rollback() 
            print(f"Error al actualizar likes: {e}")

        return f"Like :) agregado a la publicacion de {self.autor}"

    def agregar_comentario(self, comentario: str, usuario):
        comentario_id = str(uuid.uuid4())[:8] 
        comentario_dict = {
            "usuario": usuario.nombre,
            "contenido": comentario,
            "fecha": datetime.now(),
            "id": comentario_id
        }
        self.comentarios.append(comentario_dict)

        try: 
            db_comentario = ComentariosDB(
                id =comentario_id,
                contenido = comentario,
                usuario_id = usuario.id,
                publicacion_id = self.id
                )
            self._session.add(db_comentario) # agrego 
            self._session.commit() #envio
        except Exception as e:
            self._session.rollback() 
            print(f"Error al guardar comentario")

        return f"Comentario agregado por {usuario.nombre}"
    
    
    def eliminar_comentario(self,id_comentario:str)->bool:
        for i, comentario in enumerate(self.comentarios):
            if comentario['id'].lower() == id_comentario.lower():
                self.comentarios.pop(i)
                try:
                    db_comentario =  self._session.query(ComentariosDB).filter_by(id = id_comentario).first() 
                    if db_comentario :
                        self._session.delete(db_comentario)
                        self._session.commit()
                        return True
                except Exception as e:
                    self._session.rollback() 
                    print(f"Error al eliminar comentario: {e}")
                    return False
        return False
    
    def actualizar_comentario(self, id_comentario:str, nuevo_contenido)->bool:
        for comentario in self.comentarios:
            if comentario['id'].lower() == id_comentario.lower():
                comentario['contenido'] = nuevo_contenido
                
                try: 
                    db_comentario =  self._session.query(ComentariosDB).filter_by(id = id_comentario).first() 
                    if db_comentario:
                        db_comentario.contenido = nuevo_contenido
                        self._session.commit()
                        return True
                except Exception as e:
                    self._session.rollback() 
                    print(f"Error al actualizar el comentario: {e}")
                    return False        
        return False
    
    def mostrar_publicacion(self):
        comentarios_str = ""
        for comentario in self.comentarios:
            fecha_comentario = comentario['fecha']
            comentarios_str += f"\n - {comentario['usuario']} ({fecha_comentario}): {comentario['contenido']}"
        
        return (
            f"\n {self.tipo()} de {self.autor.nombre}\n"
            f"fecha de creacion: {self.fecha_creacion}"
            f"contenido: {self.contenido}\n"
            f"likes: {self.likes} \n"
            f"comentarios: ({len(self.comentarios)}):{comentarios_str if self.comentarios else 'No hay comentarios'}"
        )
    def buscar_comentario_usuario(self, nombre_usuario:str )-> List[Dict]:
        return [comentario for comentario in self.comentarios if comentario['usuario'].lower() == nombre_usuario.lower()]
    


    
class PublicacionImagen(Publicacion):
    def __init__(self, contenido, autor, ruta_imagen,db_id=None):
        super().__init__(contenido, autor,db_id)
        self.ruta_imagen = ruta_imagen
        self._guardar_en_db(ruta_imagen = ruta_imagen)

    def tipo(self):
        return "Publicacion de Imagen"
    
    def mostrar_publicacion(self):
        base=  super().mostrar_publicacion()
        return f" {base}\n Imagen: {self.ruta_imagen}"
    
    


class PublicacionVideo(Publicacion):
    def __init__(self, contenido, autor, ruta_video, duracion,db_id=None):
        super().__init__(contenido, autor,db_id)
        self.ruta_video = ruta_video
        self.duracion= duracion
        self._guardar_en_db(ruta_video= ruta_video, duracion = duracion)

    def tipo(self):
        return "Publicacion de Video"
    
    def mostrar_publicacion(self):
        base=  super().mostrar_publicacion()
        return f" {base}\n Video: {self.ruta_video} ({self.duracion}s)"
    
    

class Evento(Publicacion):
    def __init__(self, contenido, autor, fecha_evento:str, ubicacion:str,db_id=None):
        super().__init__(contenido, autor,db_id=None)
        self.fecha_evento = fecha_evento
        self.ubicacion = ubicacion
        self.asistentes : List[str] = []
        self._guardar_en_db( fecha_evento= fecha_evento, ubicacion=ubicacion)

    def tipo(self):
        return 'Evento'
    
    def confirmar_asistencia(self,usuario):
        if usuario not in self.asistentes:
            self.asistentes.append(usuario)
            try: 
                db_publicacion = self._session.query(PublicacionesDB).filter_by(id = self.id) .first()
                if db_publicacion: 
                    asistentes_lista = json.loads(db_publicacion.asistentes) if db_publicacion.asistentes else [] # json -> python object
                    asistentes_lista.append(usuario.id)
                    db_publicacion.asistentes = json.dump(asistentes_lista)  # python object -> json 
                    self._session.commit()
            except Exception as e:
                self._session.rollback()
                print(f"Error al confirmar asistencia: {e}")

            return f"{usuario} confirmo su asistencia"
        return f"{usuario} ya esta confirmado"
    def mostrar_publicacion(self):
        base = super().mostrar_publicacion()
        return f"{base}\n Fecha del evento: {self.fecha_evento}\n Ubicacion: {self.ubicacion}"
    
    

class Anuncio(Publicacion):
    def __init__(self, contenido, autor, publico_objetivo:str, frecuencia_publicacion,db_id=None):
        super().__init__(contenido, autor,db_id=None)
        self.publico_objetivo =publico_objetivo
        self.clics = 0
        self.frecuencia_publicacion = frecuencia_publicacion
        self._guardar_en_db(publico_objetivo = publico_objetivo, frecuencia_publicacion=frecuencia_publicacion)

    def tipo(self):
        return "Anuncio"
    

    def registrar_clic(self):
        self.clics += 1 
        try: 
            db_publicacion =  self._session.query(PublicacionesDB).filter_by(id = self.id).first() 
            if db_publicacion:
                db_publicacion.clics = self.clicsa
        except Exception as e:
            self._session.rollback() 
            print("Error al registrar el clic")
            
        return "Alguien se intereso en tu anuncio :)"
    
    def  mostrar_publicacion(self):
        base =  super().mostrar_publicacion()
        return f'{base}\n Publico objetivo: {self.publico_objetivo}\n Frecuencia de publicacion: {self.frecuencia_publicacion}'
    
