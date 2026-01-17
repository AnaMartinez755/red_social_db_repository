from abc import ABC, abstractmethod
from typing import List, Dict
import uuid
from datetime import datetime


class Publicacion(ABC):
    def __init__(self, contenido: str, autor):
        self.id = str(uuid.uuid4())[:8]  # id unico abreviado
        self.autor = autor
        self.contenido = contenido
        self.fecha_creacion = datetime.now()
        self.likes = 0
        self.comentarios: List[Dict] = [] # Arreglo de diccionarios 
        self._visibilidad = "publico"
    @abstractmethod
    def tipo(self):
        pass

    def dar_like(self):
        self.likes += 1
        return f"Like :) agregado a la publicacion de {self.autor}"

    def agregar_comentario(self, comentario: str, usuario):
        comentario_dict = {
            "usuario": usuario.nombre,
            "contenido": comentario,
            "fecha": datetime.now(),
            "id":  str(uuid.uuid4())[:8] 
        }
        
        self.comentarios.append(comentario_dict)
        return f"Comentario agregado por {usuario.nombre}"
    def eliminar_comentario(self,id_comentario:str)->bool:
        for i, comentario in enumerate(self.comentarios):
            if comentario['id'].lower() == id_comentario.lower():
                self.comentarios.pop(i)
            return True
        return False
    def actualizar_comentario(self, id_comentario:str, nuevo_contenido)->bool:
        for i, comentario in enumerate(self.comentarios):
            if comentario['id'].lower() == id_comentario.lower():
                self.comentarios[id_comentario] = nuevo_contenido
                return True
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
    def __init__(self, contenido, autor, ruta_imagen):
        super().__init__(contenido, autor)
        self.ruta_imagen = ruta_imagen

    def tipo(self):
        return "Publicacion de Imagen"
    
    def mostrar_publicacion(self):
        base=  super().mostrar_publicacion()
        return f" {base}\n Imagen: {self.ruta_imagen}"
    
    


class PublicacionVideo(Publicacion):
    def __init__(self, contenido, autor, ruta_video, duracion):
        super().__init__(contenido, autor)
        self.ruta_video = ruta_video
        self.duracion= duracion
    def tipo(self):
        return "Publicacion de Video"
    
    def mostrar_publicacion(self):
        base=  super().mostrar_publicacion()
        return f" {base}\n Video: {self.ruta_video} ({self.duracion}s)"
    
    

class Evento(Publicacion):
    def __init__(self, contenido, autor, fecha_evento:str, ubicacion:str):
        super().__init__(contenido, autor)
        self.fecha_evento = fecha_evento
        self.ubicacion = ubicacion
        self.asistentes : List[str] = []
    def tipo(self):
        return 'Evento'
    
    def confirmar_asistencia(self,usuario):
        if usuario not in self.asistentes:
            self.asistentes.append(usuario)
            return f"{usuario} confirmo su asistencia"
        return f"{usuario} ya esta confirmado"
    def mostrar_publicacion(self):
        base = super().mostrar_publicacion()
        return f"{base}\n Fecha del evento: {self.fecha_evento}\n Ubicacion: {self.ubicacion}"
    
    

class Anuncio(Publicacion):
    def __init__(self, contenido, autor, publico_objetivo:str, frecuencia_publicacion):
        super().__init__(contenido, autor)
        self.publico_objetivo =publico_objetivo
        self.clics = 0
        self.frecuencia_publicacion = frecuencia_publicacion

    def tipo(self):
        return "Anuncio"
    

    def registrar_clic(self):
        self.clics += 1 
        return "Alguien se intereso en tu anuncio :)"
    
    def  mostrar_publicacion(self):
        base =  super().mostrar_publicacion()
        return f'{base}\n Publico objetivo: {self.publico_objetivo}\n Frecuencia de publicacion: {self.frecuencia_publicacion}'
    
