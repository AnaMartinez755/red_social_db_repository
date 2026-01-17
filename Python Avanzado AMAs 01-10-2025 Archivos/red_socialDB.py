from typing import List
from datetime import datetime
from usuariosDB import Usuario, UsuarioEmpresa, UsuarioEstandar, UsuarioPremium
from publicacionesDB import Publicacion, PublicacionImagen, PublicacionVideo, Evento, Anuncio
from database import obtener_sesion, EstadisticasDB, UsuariosBD, PublicacionesDB, NotificacionesDB

class RedSocial:
    #Clase principal que gestiona usuarios y publicaciones (interaccion).
    def __init__(self, nombre):
        self.nombre = nombre
        self.usuarios : List[Usuario]=[]
        self.publicaciones : List[Publicacion] = []
        self._session = obtener_sesion()
        self._notificaciones : List[str] = []

        #Cargar ESTADISTICAS 
        self._cargar_estadisticas_desde_bd()
        self._cargar_usuarios_desde_bd()
        self._cargar_publicaciones_desde_bd()

    def _cargar_estadisticas_desde_bd(self):
        try:
            estadisticas_ultimas = self._session.query(EstadisticasDB).order_by(EstadisticasDB.fecha.desc()).first()
            if estadisticas_ultimas:
                self._estadisticas = {
                    "total_usuarios" : estadisticas_ultimas.total_usuarios,
                    "total_publicaciones": estadisticas_ultimas.total_publicaciones,
                    "total_comentarios":estadisticas_ultimas.total_comentarios,
                    "total_likes":estadisticas_ultimas.total_likes,
                    "total_clics":estadisticas_ultimas.total_clics
                }
            else:
                self._estadisticas = {
                    "total_usuarios" : 0,
                    "total_publicaciones": 0,
                    "total_comentarios":0,
                    "total_likes":0,
                    "total_clics":0
                }
        except Exception as e:
            print(f"Error al cargar estadisticas: {e}")
            self._estadisticas = {
                    "total_usuarios" : 0,
                    "total_publicaciones": 0,
                    "total_comentarios":0,
                    "total_likes":0,
                    "total_clics":0
                }
    def _cargar_usuarios_desde_bd(self):
        try: 
            usuarios_db = self._session.query(UsuariosBD).all()

            for usuario_db in usuarios_db:
                if usuarios_db.tipo == "estandar":
                    usuario_local = UsuarioEstandar(usuario_db.nombre, usuario_db.email)
                elif usuarios_db.tipo == "premium":
                    usuario_local = UsuarioPremium(usuario_db.nombre, usuario_db.email)
                elif usuarios_db.tipo == "empresa":
                    usuario_local = UsuarioEmpresa(usuario_db.nombre, usuario_db.email, usuario_db.industria or "General")
                
                usuario_local.id = usuario_db.id
                usuario_local.fecha_registro = usuario_db.fecha_registro
                self.usuarios.append(usuario_local)
        except Exception as e:
            print("Error al cargar usuarios: {e}")

    def _cargar_publicaciones_desde_bd(self):
        try: 
            publicaciones_db = self._session.query(PublicacionesDB).all()

            for  pub_db in publicaciones_db:
                autor = next((usuario for usuario in self.usuarios if usuario.id == pub_db.autor.id ),None)

                if not autor:
                    continue

                if pub_db.tipo ==  "Publicacion de Imagen":
                    publicacion_local = PublicacionImagen(pub_db.contenido, autor, pub_db.ruta_imagen, pub_db.id)
                elif pub_db.tipo == "Publicacion de Video":
                    publicacion_local = PublicacionVideo(pub_db.contenido, autor, pub_db.ruta_video,pub_db.duracion or 60, pub_db.id)
                elif pub_db.tipo == "Evento":
                    publicacion_local = Evento(pub_db.contenido, autor, pub_db.fecha_evento, pub_db.ubicacion,pub_db.id)
                elif pub_db.tipo == "Anuncio":
                    publicacion_local = Anuncio(pub_db.contenido, autor, pub_db.publico_objetivo, pub_db.frecuencia_publicacion,pub_db.id)
                    publicacion_local.clics = pub_db.clics or 0 
                else:
                    continue

                publicacion_local.fecha_creacion = pub_db.fecha_creacion
                publicacion_local.likes = pub_db.likes or 0 

                publicacion_local._cargar_comentarios_desde_db()

                self.publicaciones.append(publicacion_local)
                autor.crear_publicaciones(publicacion_local)
        except Exception as e:
            print(f"Error al cargar publicaciones: {e}")

    
    def _guardar_estadisticas_en_bd(self):
        try: 
            estadisticas_locales = EstadisticasDB(
                total_usuarios =  self._estadisticas['total_usuarios'],
                total_publicaciones =  self._estadisticas['total_publicaciones'],
                total_comentarios =  self._estadisticas['total_comentarios'],
                total_likes =  self._estadisticas['total_likes'],
                total_clics =  self._estadisticas['total_clics']
            )

            self._session.add(estadisticas_locales)
            self._session.commit()
            print(f"Estadisticas guardadas existosamente")
            
        except Exception as e:
            self._session.rollback() 
            print(f"{estadisticas_locales} Error al subir en la tabla {EstadisticasDB.__tablename__} : {e}")
            print(f"Error al guardar estadisticas: {e}")
    
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
        self._guardar_estadisticas_en_bd()
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
        self._guardar_estadisticas_en_bd()
        self._agregar_notificacion(f"{autor.nombre} creo una nueva publicacion!!!")

        return publicacion


    def dar_like_publicacion(self, id_publicacion, usuario):
        for publicacion in self.publicaciones:
            if publicacion.id == id_publicacion:
                resultado = publicacion.dar_like()
                self._estadisticas['total_likes'] +=1
                self._guardar_estadisticas_en_bd()
                self._agregar_notificacion(f"{usuario.nombre} le dio like a una publicacion")
                return resultado
        return "Publicacion no econtrada"
    
    def comentar_publicacion(self, id_publicacion, comentario, usuario):
        for publicacion in self.publicaciones:
            if publicacion.id == id_publicacion:
                resultado = publicacion.agregar_comentario(comentario, usuario)
                self._estadisticas["total_comentarios"] +=1
                self._guardar_estadisticas_en_bd()
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
        print(total_comentarios)
        return(
            f"\nESTADISTICAS DE {self.nombre.upper()}\n"
            f"Usuarios registrados: {self._estadisticas['total_usuarios']}\n"
            f"Publicaciones totales: {self._estadisticas['total_publicaciones']}\n"
            f"Likes totales: {self._estadisticas['total_likes']}\n"
            f"Comentarios totales: {self._estadisticas['total_comentarios']}\n"
            f"Notificaciones recientes: {len(self._notificaciones)}"
        )
  

    def mostrar_notificaciones(self):
      try: 
            notificaciones_db = self._session.query(NotificacionesDB).order_by(NotificacionesDB.fecha.desc()).limit(10).all()
            return [f"[{notificacion.fecha}] {notificacion.mensaje}" for notificacion in notificaciones_db]
      except Exception as e:
          print(f"Error al cargar notificaciones {e}")

    def _agregar_notificacion(self, mensaje):
        timestamp = datetime.now()
        self._notificaciones.append(f"[{timestamp}] {mensaje}")
        try:  
            notificacion = NotificacionesDB(
                mensaje =mensaje
                )
            self._session.add(notificacion)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            print(f"Error al guardar notificacion")
