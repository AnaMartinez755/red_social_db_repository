from typing import List, Dict
from datetime import datetime
from usuarios import Usuario, UsuarioEmpresa, UsuarioEstandar, UsuarioPremium
from publicaciones import Publicacion, PublicacionImagen, PublicacionVideo, Evento, Anuncio

class RedSocial:
    #Clase principal que gestiona usuarios y publicaciones (interaccion).
    def __init__(self, nombre):
        self.nombre = nombre
        self.usuarios : List[Usuario]=[]
        self.publicaciones : List[Publicacion] = []
        self._estadisticas= {
            "total_usuarios":0,
            "total_publicaciones" : 0,
            "total_comentarios":0,
            "total_likes":0,
            "total_clics":0
        }
        self._notificaciones=[]
    def registrar_usuario(self, tipo:str, nombre:str, email:str , **kwargs)-> Usuario:
        usuario = None
        if tipo.lower() =='estandar':
            usuario = UsuarioEstandar(nombre,email)
        elif tipo.lower() == 'premium':
            usuario = UsuarioPremium(nombre,email)
        elif  tipo.lower() == 'empresa':
            industria = kwargs.get('industria','General')
            usuario = UsuarioEmpresa( nombre,email,industria)
        if usuario is None:
            raise ValueError("Tipo de usuario no existente")
        
        self.usuarios.append(usuario)
        self._estadisticas['total_usuarios'] += 1
        self._agregar_notificacion(f"Bienvenido {nombre} a {self.nombre}!!!")
        print(f"Usuario {nombre} registrado exitosamente como {tipo}")

        return usuario
    def crear_publicacion(self,tipo: str, autor:Usuario, contenido:str , **kwargs) -> Publicacion:
        #Validacion de registro 
        if autor not in self.usuarios:
            raise ValueError("Debes registrarte antes de crear una publicacion")
        #Crear publicaciones -> validacion de permisos
        if tipo.lower() =='evento' and not autor.puede_crear_evento():
            raise ValueError(f"{autor.nombre} no tiene permisos para eventos")
        if tipo.lower() =='anuncio' and not autor.puede_crear_anuncio():
            raise ValueError(f"{autor.nombre} no tiene permisos para anucios")
        
        publicacion = None #Inicializacion de publicacion

        if tipo.lower() =="imagen":
            ruta_imagen = kwargs.get('ruta_imagen','default.jpg')
            publicacion = PublicacionImagen(contenido,autor,ruta_imagen)
        elif tipo.lower() =="video":
            ruta_video = kwargs.get('ruta_video','default.mp4')
            duracion = kwargs.get('duracion',60)
            publicacion = PublicacionVideo(contenido,autor,ruta_video,duracion)
        elif tipo.lower() =="evento":
            fecha_evento = kwargs.get('fecha_evento','12/24/2025')
            ubicacion = kwargs.get('ubicacion', 'Online')
            publicacion = Evento(contenido,autor,fecha_evento,ubicacion)
        elif tipo.lower() =="anuncio":
            publico_objetivo = kwargs.get('publico_objetivo','General')
            frecuencia_publicacion = kwargs.get('frecuencia_publicacion','Diaria')
            publicacion = Anuncio(contenido,autor,publico_objetivo,frecuencia_publicacion)
        else:
            raise ValueError(f"Tipo de publicacion {tipo} no valida")
        
        self.publicaciones.append(publicacion) # Agrego publicacion a la red social
        autor.crear_publicaciones(publicacion) # Creo publicacion para el usuario 

        #Actualiza estadisticas 
        self._estadisticas['total_publicaciones'] +=1
        self._agregar_notificacion(f"{autor.nombre} creo una nueva publicacion!!!")
    def dar_like_publicacion(self, id_publicacion, usuario):
        for publicacion in self.publicaciones:
            if publicacion.id == id_publicacion:
                self._estadisticas['total_likes'] +=1
                self._agregar_notificacion(f"{usuario.nombre} le dio like a una publicacion")
                return publicacion.dar_like()
        return "Publicacion no econtrada"
    def comentar_publicacion(self, id_publicacion, comentario, usuario):
        for publicacion in self.publicaciones:
            if publicacion.id == id_publicacion:
                self._estadisticas["total_comentarios"] +=1
                resultado = publicacion.agregar_comentario(comentario, usuario)
                self._agregar_notificacion(f"{usuario.nombre} comento una publicacion")
                return resultado
        return "Publicacion no encontrada"
    def seguir_usuario(self,usuario:Usuario, usuario2:Usuario):
        if usuario not in self.usuarios or usuario2 not in self.usuarios:
            return "Usuario no encontrado"
        resultado = usuario.seguir(usuario2)
        self._agregar_notificacion(f"{usuario.nombre} empezo a seguir a {usuario2.nombre}")
        return resultado
    
    def mostrar_estadisticas_generales(self):
        total_comentarios = sum(len(p.comentarios) for p in self.publicaciones)
        return(
            f"\nESTADISTICAS DE {self.nombre.upper()}\n"
            f"Usuarios registrados: {self._estadisticas['total_usuarios']}\n"
            f"Publicaciones totales: {self._estadisticas['total_publicaciones']}\n"
            f"Likes totales: {self._estadisticas['total_likes']}\n"
            f"Comentarios totales: {self._estadisticas['total_comentarios']}\n"
            f"Notificaciones recientes: {len(self._notificaciones)}"
        )

    #FUNCIONES AGREGADAS
    def mostrar_notificaciones(self):
        return self._notificaciones[-10:]
    def _agregar_notificacion(self, mensaje):
        timestamp = datetime.now()
        self._notificaciones.append(f"[{timestamp}] {mensaje}")


red = RedSocial('UsuariosMeta')
usuario1 = red.registrar_usuario('premium','ignacio','ignacio@gmail.com')
usuario2 = red.registrar_usuario('estandar','Carlos Lopez','carlos@gmail.com')
usuario3 = red.registrar_usuario('empresa','Tech LATAM','tech_latam@gmail.com')
        
publicacion1 = red.crear_publicacion("video",usuario1,"Video de prueba 1 ",ruta_video = 'video1.mp4', duracion=120)
publicacion2 = red.crear_publicacion("imagen",usuario2,"Imagen de de prueba 1 ",ruta_video = 'imagen1.jpg')
publicacion3 = red.crear_publicacion("evento",usuario3,"Evento de prueba 1", fecha_evento = '15/12/2025', ubicacion="Online")
publicacion4 = red.crear_publicacion("anuncio",usuario3,"ANUNCIO DE PRUEBA!!!",publico_objetivo = "Tecnologia", frecuencia_publicacion="Diaria")

red.seguir_usuario(usuario1,usuario2)
red.seguir_usuario(usuario1,usuario3)
red.seguir_usuario(usuario3,usuario2)
print(red.mostrar_estadisticas_generales())

print('NOTIFICACIONES:')
print(red.mostrar_notificaciones())