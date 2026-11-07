
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Avg, Count
from django.views.decorators.http import require_POST

from .models import Autor, Calificacion, Publicacion
from .forms import (
    AutorCreateForm,
    AutorForm,
    CalificacionForm,
    ComentarioForm,
    ContactoForm,
    PublicacionForm,
    RegistroForm
)


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

    if request.method == "POST":

        titulo = request.POST["titulo"]
        descripcion = request.POST["descripcion"]
        estado = request.POST["estado"]

        Publicacion.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            autor=autor,
            estado=estado
        )

        messages.success(
            request,
            "La publicación fue creada correctamente."
        )

        return redirect("lista_publicaciones")

    return render(
        request,
        "publicaciones/crear_publicacion.html"
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
        publicacion.autor_id = request.POST["autor"]
        publicacion.estado = request.POST["estado"]

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
