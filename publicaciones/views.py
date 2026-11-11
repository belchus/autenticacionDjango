
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Avg, Count,Q
from django.db import models
from django.views.decorators.http import require_POST

from .models import Autor, Calificacion, Mensaje, Publicacion
from .forms import (
    AutorCreateForm,
    AutorForm,
    CalificacionForm,
    ComentarioForm,
    ContactoForm,
    MensajeForm,
    PublicacionForm,
    RegistroForm
)

# ==========================================
# ADMINISTRADOR
# ==========================================


def es_administrador(user):
    return user.is_staff


@login_required
@user_passes_test(es_administrador)

def publicaciones_pendientes(request):

    publicaciones = Publicacion.objects.filter(estado = "borrador").order_by("-fecha_creacion")
    return render(request,"publicaciones/publicaciones_pendientes.html",{"publicaciones":publicaciones})

@login_required
@user_passes_test(es_administrador)

def revisar_publicacion(request,publicacion_id):
    publicacion = get_object_or_404(Publicacion,id=publicacion_id,estado = "borrador")

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "aprobar":
            publicacion.estado = "publicado"
            publicacion.save()

            messages.success(request,"Publicacion aprobada y publicada")
            print("ESTADO",publicacion.estado)

        elif accion == "rechazar":
            publicacion.estado = "archivado"
            publicacion.save()

            messages.success(request,"Publicacion rechazada")
        
        else: 
            messages.error(request,"Accion no valida")
            return redirect("publicaciones_pendientes")

    print("ESTADO",publicacion.estado)
    return redirect("publicaciones_pendientes")


# ==========================================
# INICIO
# ==========================================

def inicio(request):
    print("USUARIO:", request.user)
    print("AUTENTICADO:", request.user.is_authenticated)

    return render(request, "publicaciones/inicio.html")


# ==========================================
# LISTAR PUBLICACIONES
# ==========================================


from django.db.models import Avg, Count

def lista_publicaciones(request):

    publicaciones = Publicacion.objects.all()

    # Buscador por título
    busqueda = request.GET.get("buscar")

    if busqueda:
        publicaciones = publicaciones.filter(
            titulo__icontains=busqueda
        )

    # Filtro por estado
    estado = request.GET.get("estado")

    if estado:
        publicaciones = publicaciones.filter(
            estado=estado
        )

    # Ordenar publicaciones
    orden = request.GET.get("orden", "reciente")

    if orden == "antiguo":
        publicaciones = publicaciones.order_by("fecha_creacion")
    else:
        publicaciones = publicaciones.order_by("-fecha_creacion")

    # Calcular promedio y cantidad de calificaciones
    publicaciones = publicaciones.annotate(
        promedio_calificacion=Avg("calificaciones__estrellas"),
        cantidad_calificaciones=Count("calificaciones")
    )

    contexto = {
        "publicaciones": publicaciones,
        "busqueda": busqueda,
        "estado": estado,
        "orden": orden
    }

    return render(
        request,
        "publicaciones/lista_publicaciones.html",
        contexto
    )


# ==========================================
# DETALLE DE UNA PUBLICACIÓN
# ==========================================

def detalle_publicacion(request, publicacion_id):

    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id
    )

    # Buscamos los comentarios de la publicación
    comentarios = publicacion.comentarios.select_related(
        "autor"
    ).order_by("-fecha")

    # Calculamos el promedio y la cantidad de calificaciones
    datos_calificacion = publicacion.calificaciones.aggregate(
        promedio=Avg("estrellas"),
        cantidad=Count("id")
    )

    promedio = datos_calificacion["promedio"] or 0
    cantidad = datos_calificacion["cantidad"]

    # Redondeamos el promedio para mostrar las estrellas
    estrellas = int(round(promedio))

    # Buscamos si el usuario autenticado ya calificó
    calificacion_usuario = None

    if request.user.is_authenticated:

        autor = Autor.objects.filter(
            usuario=request.user
        ).first()

        if autor:
            calificacion_usuario = Calificacion.objects.filter(
                publicacion=publicacion,
                autor=autor
            ).first()

    # CalificacionForm es un forms.Form, por eso no lleva instance
    form_calificacion = CalificacionForm()

    # Formulario para agregar comentarios
    form_comentario = ComentarioForm()

    contexto = {
        "publicacion": publicacion,
        "comentarios": comentarios,
        "promedio": promedio,
        "cantidad": cantidad,
        "estrellas": estrellas,
        "calificacion_usuario": calificacion_usuario,
        "form_calificacion": form_calificacion,
        "form_comentario": form_comentario
    }

    return render(
        request,
        "publicaciones/detalle_publicacion.html",
        contexto
    )


# ==========================================
# LISTAR AUTORES
# ==========================================

def lista_autores(request):

    autores = Autor.objects.all()

    busqueda = request.GET.get("buscar")

    if busqueda:
        autores = autores.filter(
            username__icontains=busqueda
        )

    return render(
        request,
        "autores/lista_autores.html",
        {"autores": autores}
    )


# ==========================================
# PERFIL DE UN AUTOR
# ==========================================

def perfil_autor(request, autor_id):

    autor = get_object_or_404(
        Autor,
        id=autor_id
    )

    publicaciones = autor.publicaciones.all()

    return render(
        request,
        "autores/perfil_autor.html",
        {
            "autor": autor,
            "publicaciones": publicaciones
        }
    )


# ==========================================
# EDITAR PERFIL
# ==========================================

@login_required
def editar_perfil(request, autor_id):

    autor = get_object_or_404(
        Autor,
        id=autor_id
    )

    if request.method == "POST":

        form = AutorForm(
            request.POST,
            request.FILES,
            instance=autor
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Tu perfil fue actualizado correctamente."
            )

            return redirect(
                "perfil_autor",
                autor_id=autor.id
            )

    else:

        form = AutorForm(instance=autor)

    return render(
        request,
        "autores/editar_perfil.html",
        {
            "form": form,
            "autor": autor
        }
    )


# ==========================================
# CREAR PUBLICACIÓN
# ==========================================

@login_required
def crear_post(request):

    autor = get_object_or_404(
        Autor,
        usuario=request.user
    )

    # Inicializamos el formulario
    form = PublicacionForm()

    if request.method == "POST":
        form = PublicacionForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            publicacion = form.save(commit=False)

            publicacion.autor = autor
            publicacion.estado = "borrador"

            publicacion.save()

            messages.success(
                request,
                "Tu publicación está pendiente de aprobación"
            )

            return redirect("lista_publicaciones")

    return render(
        request,
        "publicaciones/crear_publicacion.html",
        {"form": form}
    )


# ==========================================
# CREAR AUTOR
# ==========================================

def crear_autor(request):

    if request.method == "POST":

        form = AutorCreateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect("lista_autores")

    else:

        form = AutorCreateForm()

    return render(
        request,
        "autores/crear_autor.html",
        {"form": form}
    )


# ==========================================
# DEJAR COMENTARIO
# ==========================================

@login_required
def dejar_comentario(request, publicacion_id):

    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id
    )

    autor = get_object_or_404(
        Autor,
        usuario=request.user
    )

    if request.method == "POST":

        form = ComentarioForm(request.POST)

        if form.is_valid():

            # Creamos el comentario sin guardarlo todavía
            comentario = form.save(commit=False)

            # Asignamos la publicación y el autor
            comentario.publicacion = publicacion
            comentario.autor = autor

            # Guardamos el comentario completo
            comentario.save()

            messages.success(
                request,
                "¡Tu comentario se publicó exitosamente!"
            )

        else:

            messages.error(
                request,
                "No se pudo publicar el comentario."
            )

    return redirect(
        "detalle_publicacion",
        publicacion_id=publicacion.id
    )


# ==========================================
# CALIFICAR PUBLICACIÓN
# ==========================================

@login_required
def calificar_publicacion(request, publicacion_id):

    # Buscamos la publicación
    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id
    )

    # Buscamos el perfil del usuario autenticado
    autor = get_object_or_404(
        Autor,
        usuario=request.user
    )

    if request.method == "POST":

        # Recibimos los datos del formulario
        form = CalificacionForm(request.POST)

        if form.is_valid():

            # Convertimos las estrellas a un número entero
            estrellas = int(
                form.cleaned_data["estrellas"]
            )

            print("ESTRELLAS RECIBIDAS:", estrellas)
            print("TIPO:", type(estrellas))

            # Comprobamos que esté entre 1 y 5
            if estrellas < 1 or estrellas > 5:

                messages.error(
                    request,
                    "La calificación debe estar entre 1 y 5."
                )

            else:

                # Creamos o actualizamos la calificación
                calificacion, creada = Calificacion.objects.update_or_create(

                    publicacion=publicacion,

                    autor=autor,

                    defaults={
                        "estrellas": estrellas
                    }
                )

                if creada:

                    messages.success(
                        request,
                        "¡Gracias por calificar esta publicación!"
                    )

                else:

                    messages.success(
                        request,
                        "Tu calificación fue actualizada."
                    )

        else:

            print("ERRORES DEL FORMULARIO:", form.errors)

            messages.error(
                request,
                "No se pudo guardar tu calificación."
            )

    return redirect(
        "detalle_publicacion",
        publicacion_id=publicacion.id
    )


# ==========================================
# EDITAR PUBLICACIÓN
# ==========================================

@login_required

def editar_publicacion(request, id):

    publicacion = get_object_or_404(
        Publicacion,
        id=id
    )

    if request.method == "POST":

        publicacion.titulo = request.POST["titulo"]
        publicacion.descripcion = request.POST["descripcion"]

        nueva_imagen = request.FILES.get("url_imagen")

        if nueva_imagen:
            publicacion.url_imagen = nueva_imagen

        publicacion.save()

        messages.success(
            request,
            "La publicación fue actualizada correctamente."
        )

        return redirect("lista_publicaciones")

    return render(
        request,
        "publicaciones/editar_publicacion.html",
        {"publicacion": publicacion}
    )

# ==========================================
# ELIMINAR PUBLICACIÓN
# ==========================================

@login_required
def eliminar_publicacion(request, id):

    publicacion = get_object_or_404(
        Publicacion,
        id=id
    )

    if request.method == "POST":

        publicacion.delete()

        messages.success(
            request,
            "La publicación fue eliminada."
        )

    return redirect("lista_publicaciones")


# ==========================================
# CONTACTO
# ==========================================

def contacto(request):

    if request.method == "POST":

        form = ContactoForm(request.POST)

        if form.is_valid():

            nombre = form.cleaned_data["nombre"]
            email = form.cleaned_data["email"]
            asunto = form.cleaned_data["asunto"]
            mensaje = form.cleaned_data["mensaje"]

            return render(
                request,
                "publicaciones/contacto.html",
                {
                    "form": ContactoForm(),
                    "enviado": True,
                    "nombre": nombre
                }
            )

    else:

        form = ContactoForm()

    return render(
        request,
        "publicaciones/contacto.html",
        {"form": form}
    )


# ==========================================
# REGISTRO
# ==========================================

def registro(request):

    if request.method == "POST":

        form = RegistroForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            usuario = form.save()

            login(request, usuario)

            return redirect("inicio")

    else:

        form = RegistroForm()

    return render(
        request,
        "autenticacion/registro.html",
        {"form": form}
    )


# ==========================================
# INICIAR SESIÓN
# ==========================================

def iniciar_sesion(request):

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            usuario = form.get_user()

            login(request, usuario)

            return redirect("inicio")

    else:

        form = AuthenticationForm(request)

    return render(
        request,
        "autenticacion/login.html",
        {"form": form}
    )


# ==========================================
# CERRAR SESIÓN
# ==========================================

@require_POST
def cerrar_sesion(request):

    logout(request)

    return redirect("lista_publicaciones")

# ==========================================
# MENSAJES
# ==========================================
@login_required
def lista_mensajes(request):

    autor_actual = get_object_or_404(
        Autor,
        usuario=request.user
    )

    autores = Autor.objects.exclude(id=autor_actual.id)

    # Mantener la lógica para iniciar una conversación
    if request.method == "GET":
        remitente_id = request.GET.get("remitente")
        destinatario_id = request.GET.get("destinatario")

        if remitente_id and destinatario_id:
            remitente = get_object_or_404(Autor, id=remitente_id)
            destinatario = get_object_or_404(Autor, id=destinatario_id)

            if remitente == autor_actual and remitente != destinatario:
                return redirect(
                    "conversacion",
                    autor1_id=remitente_id,
                    autor2_id=destinatario_id
                )

    # Buscar las conversaciones existentes
    conversaciones = []

    for autor in autores:

        ultimo_mensaje = Mensaje.objects.filter(
            Q(remitente=autor_actual, destinatario=autor) |
            Q(remitente=autor, destinatario=autor_actual)
        ).order_by("-fecha_envio", "-id").first()

        if ultimo_mensaje:

            mensajes_sin_leer = Mensaje.objects.filter(
                remitente=autor,
                destinatario=autor_actual,
                visto=False
            ).count()

            conversaciones.append({
                "autor": autor,
                "ultimo_mensaje": ultimo_mensaje,
                "mensajes_sin_leer": mensajes_sin_leer
            })

    # Ordenar por el mensaje más reciente
    conversaciones.sort(
        key=lambda x: x["ultimo_mensaje"].fecha_envio,
        reverse=True
    )

    return render(
        request,
        "mensajes/lista_mensajes.html",
        {
            "autores": autores,
            "autor_actual": autor_actual,
            "conversaciones": conversaciones
        }
    )

@login_required
def conversacion(request,autor_id):
    autor_actual= get_object_or_404(Autor,usuario = request.user)
    destinatario = get_object_or_404(Autor,id= autor_id)

    if autor_actual == destinatario:
        return redirect("lista_mensajes")

    mensajes = Mensaje.objects.filter(
        models.Q(remitente=autor_actual,destinatario=destinatario)|
        models.Q(remitente=destinatario,destinatario=autor_actual)
    ).order_by("fecha_envio")



    if request.method == "POST":
        contenido = request.POST.get("contenido","").strip()

        if contenido:
            Mensaje.objects.create(
                remitente = autor_actual,
                destinatario= destinatario,
                contenido = contenido
            )
            return redirect("conversacion",autor_id=destinatario.id)
    mensajes.filter(destinatario= autor_actual,visto = False).update(visto = True)
    
    return render(request,"mensajes/conversacion.html",{"autor_actual":autor_actual,"destinatario":destinatario,"mensajes":mensajes})