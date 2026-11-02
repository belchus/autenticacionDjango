"""
URL configuration for red_social project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from publicaciones import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('publicaciones/', views.lista_publicaciones, name='lista_publicaciones'),
    path('publicacion/<int:id>',views.detalle_publicacion, name= "detalle_publicacion"),
    path('crear/',views.crear_publicacion, name="crear_publicacion"),
    path('editar/<int:id>',views.editar_publicacion, name= "editar_publicacion"),
    path('eliminar/<int:id>',views.eliminar_publicacion, name="eliminar_publicacion"),
    path('autor/crear/',views.crear_autor,name="crear_autor"),
    path('autores/',views.lista_autores,name="lista_autores"),
    path('autor/<int:autor_id>/',views.perfil_autor,name="perfil_autor"),
    path('autor/<int:autor_id>/editar',views.editar_perfil,name="editar_perfil"),
    path("contacto/", views.contacto, name="contacto"),
    path('publicacion/<int:publicacion_id>/comentar',views.dejar_comentario, name= "dejar_comentario"),
    path('registro/',views.registro, name="registro"),
    path('login/',views.iniciar_sesion, name="login"),
    path('logout/',views.cerrar_sesion, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )
