from database import crear_tablas
from red_socialDB import RedSocial 

crear_tablas()
print(f"Inicializando Red Social :)")

red = RedSocial('UsuariosConquer')


usuario1 = red.registrar_usuario('premium','ignacio','ignacio@gmail.com')
usuario2 = red.registrar_usuario('estandar','Carlos Lopez','carlos@gmail.com')
usuario3 = red.registrar_usuario('empresa','Tech LATAM','tech_latam@gmail.com')
        
publicacion1 = red.crear_publicacion("video",usuario1,"Video de prueba 1 ",ruta_video = 'video1.mp4', duracion=120)
publicacion2 = red.crear_publicacion("imagen",usuario2,"Imagen de de prueba 1 ",ruta_video = 'imagen1.jpg')
publicacion3 = red.crear_publicacion("evento",usuario3,"Evento de prueba 1", fecha_evento = '15/12/2025', ubicacion="Online")
publicacion4 = red.crear_publicacion("anuncio",usuario3,"ANUNCIO DE PRUEBA!!!",publico_objetivo = "Tecnologia", frecuencia_publicacion="Diaria")



# #TODO
# comentario1 = red.comentar_publicacion()
# like1 = red.dar_like_publicacion()


red.seguir_usuario(usuario1,usuario2)
red.seguir_usuario(usuario1,usuario3)
red.seguir_usuario(usuario3,usuario2)
print(red.mostrar_estadisticas_generales())

print('NOTIFICACIONES:')
print(red.mostrar_notificaciones())