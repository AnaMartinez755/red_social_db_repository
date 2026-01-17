from abc import ABC, abstractmethod
from typing import List
import uuid
from datetime import datetime
from publicaciones import Publicacion

class Usuario(ABC):
    def __init__(self, nombre: str, email: str):
        self.id = str(uuid.uuid4())[:8]  # id unico abreviado
        self.nombre = nombre
        self.email = email
        self.seguidores: List["Usuario"] = []
        self.fecha_registro = datetime.now()
        self._publicaciones = []  # atributo protegido (no accesible fuera de la clase)

    @abstractmethod
    def puede_crear_anuncio(self) -> bool:
        # Metodo para verificar si puede crear anuncios
        pass

    @abstractmethod
    def puede_crear_evento(self) -> bool:
        # Metodo para verificar si puede crear eventos
        pass

    def seguir(self, usuario2: "Usuario") -> str:
        if usuario2 not in self.seguidores:
            self.seguidores.append(usuario2)
            return f"{self.nombre} ahora sigue a {usuario2.nombre}"
        return f"Ya sigues a {usuario2.nombre}"

    def dejar_seguir(self, usuario2: "Usuario") -> str:
        if usuario2 in self.seguidores:
            self.seguidores.remove(usuario2)
            return f"{self.nombre} dejo de seguir a {usuario2.nombre}"
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
    def puede_crear_anuncio(self) -> bool:
        return False

    def puede_crear_evento(self) -> bool:
        return False


class UsuarioPremium(Usuario):
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
