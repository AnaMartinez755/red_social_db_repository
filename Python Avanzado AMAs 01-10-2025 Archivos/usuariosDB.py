from abc import ABC, abstractmethod
from typing import List
import uuid
from datetime import datetime
from publicaciones import Publicacion
from database import obtener_sesion, UsuariosBD, Seguidor

class Usuario(ABC):
    def __init__(self, nombre: str, email: str):
        self.id = str(uuid.uuid4())[:8]  # id unico abreviado
        self.nombre = nombre
        self.email = email
        self.seguidores: List["Usuario"] = []
        self.fecha_registro = datetime.now()
        self._publicaciones = []  # atributo protegido (no accesible fuera de la clase)
        self._session = obtener_sesion()
        self._db_usuario = None

    @abstractmethod
    def puede_crear_anuncio(self) -> bool:
        # Metodo para verificar si puede crear anuncios
        pass

    @abstractmethod
    def puede_crear_evento(self) -> bool:
        # Metodo para verificar si puede crear eventos
        pass
    
    #POST
    def _guardar_en_db(self,tipo_usuario, industria): 
        #Guardar el usuario en la base de datos 
        try:
            db_usuario = UsuariosBD(
                id = self.id,
                nombre = self.nombre,
                email= self.email,
                tipo = tipo_usuario,
                industria = industria,
                fecha_registro = self.fecha_registro
            )
            self._session.add(db_usuario)
            self._session.commit()
            self._db_usuario = db_usuario
            return True
        except Exception as e:
            self._session.rollback() # Retorno de accion
            print("Error al guardar usuario", e)
            return False
    
    #GET
    def _traer_usuarios_desde_bd(self):
        try:
            db_usuario= self._session.query(UsuariosBD).filter(id = self.id).first()
            if db_usuario:
                self.nombre = db_usuario.nombre
                self.email = db_usuario.email
                self.fecha_registro = db_usuario.fecha_registro
                self._db_usuario = db_usuario
                return True
        except Exception as e:
            print("Error al traer usuario", e)
            return False
    def traer_seguidores_desde_db(self):
        try:
            seguidores_bd = self._session.query(Seguidor).filter_by(usuario_id = self.id).all()
            self.seguidores = [seguidor.seguidor_id for seguidor in seguidores_bd]
            print(f"Seguidores cargados: {len(self.seguidores)}")

        except Exception as e:
            print(f"Error al traer seguidores: {e}")
   
    def seguir(self, usuario2: "Usuario") -> str:
        if usuario2 not in self.seguidores:
            self.seguidores.append(usuario2)
            try:
                seguidor = Seguidor(
                    usuario_id = usuario2.id,
                    seguidor_id = self.id
                ) #Preparo
                self._session.add(seguidor) # agrego 
                self._session.commit() #envio
                return f"{self.nombre} ahora sigue a {usuario2.nombre}"
            except Exception as e:
                print(f"Error al seguir {e}")
        return f"Ya sigues a {usuario2.nombre}"

    def dejar_seguir(self, usuario2: "Usuario") -> str:
        if usuario2 in self.seguidores:
            self.seguidores.remove(usuario2)
            try:
                seguidor = self._session.query(Seguidor).filter_by(usuario_id = usuario2.id,
                                                                   seguidor_id = self.id).first()
                if seguidor:
                    self._session.delete(seguidor)
                    self._session.commit()
                return f"{self.nombre} dejo de seguir a {usuario2.nombre}"
            except Exception as e:
                self._session.rollback()
                print(f"Error al dejar de seguir {e}")
        return f"No sigue a {usuario2.nombre}"
    
    # Encapsulacion
    def crear_publicaciones(self, publicacion:Publicacion) -> None:
        # Funcion que orquesta la creacion de publicaciones (setter)
        self._publicaciones.append(publicacion)

    def mostrar_perfil(self) -> str:
        return (
            f"Perfil de {self.nombre} \n"
            f"Email: {self.email}\n"
            f"Seguidores: {len(self.seguidores)}\n"
            f"Publicaciones: {len(self._publicaciones)}\n"
            f"Tipo: {self.__class__.__name__}"
        )


class UsuarioEstandar(Usuario):
    def __init__(self, nombre,email):
        super().__init__(nombre,email)
        self._guardar_en_db('estandar',industria=None)

    def puede_crear_anuncio(self) -> bool:
        return False

    def puede_crear_evento(self) -> bool:
        return False


class UsuarioPremium(Usuario):
    def __init__(self, nombre,email):
        super().__init__(nombre,email)
        self._guardar_en_db('premium', industria=None)

    def puede_crear_anuncio(self) -> bool:
        return False

    def puede_crear_evento(self) -> bool:
        return True

    def mostrar_perfil(self):
        perfil_base = super().mostrar_perfil()
        return f"{perfil_base} \n Beneficios: Eventos ilimitados"


class UsuarioEmpresa(Usuario):
    def __init__(self, nombre, email, industria: str):
        super().__init__(nombre, email)
        self.industria = industria
        self.anuncios_creados = 0
        self._guardar_en_db('empresa', industria)

    def puede_crear_anuncio(self) -> bool:
        return True

    def puede_crear_evento(self) -> bool:
        return True

    # Polimorfismo
    def crear_anuncio(self, contenido: str):
        self.anuncios_creados += 1
        return f"Anuncio creado por {self.nombre} con contenido {contenido}"

    def mostrar_perfil(self):
        perfil_base = super().mostrar_perfil()
        return (
            f"{perfil_base} \n"
            f"Industria: {self.industria}"
            f"Anuncios creados: {self.anuncios_creados}"
            f"Beneficios: Eventos/Anuncios ilimitados"
        )

# usuario_testeo = UsuarioEmpresa('test2', "test2@gmail.com", "Tecnologia")
