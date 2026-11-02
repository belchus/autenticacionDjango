from django.shortcuts import get_object_or_404, redirect, render
from .models import Autor, Publicacion
from django.contrib.auth import login,logout
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


from .forms import AutorCreateForm, AutorForm, ComentarioForm, ContactoForm, PublicacionForm, RegistroForm

#VISTA DEL INICIO EN LA RAIZ / 
def inicio(request):
    return render(request, 'publicaciones/inicio.html')

#READ : Listar publicaciones
def lista_publicaciones(request):
    publicaciones = Publicacion.objects.all()
    busqueda = request.GET.get("buscar")
    if busqueda:
        publicaciones = publicaciones.filter(titulo__icontains = busqueda)
    estado = request.GET.get("estado")
    if estado:
        publicaciones= publicaciones.filter(estado=estado)
    orden = request.GET.get("orden","reciente")
    if orden == "antiguo":
        publicaciones = publicaciones.order_by("fecha_creacion")
    else: 
        publicaciones = publicaciones.order_by("-fecha_creacion")
    contexto = {"publicaciones": publicaciones,"busqueda":busqueda,"estado":estado,"orden":orden}
    return render(request,"publicaciones/lista_publicaciones.html", contexto)

def detalle_publicacion(request,id):
    publicacion = get_object_or_404(Publicacion,id=id)

    return render(request,"publicaciones/detalle_publicacion.html",{"publicacion":publicacion})

def lista_autores(request):
    autores = Autor.objects.all()
    busqueda = request.GET.get("buscar")
    if busqueda:
        autores = autores.filter(username__icontains = busqueda)
    return render(request,"autores/lista_autores.html",{"autores":autores})

def perfil_autor(request,autor_id):
    autor = get_object_or_404(Autor,id=autor_id)
    publicaciones = autor.publicaciones.all()

    return render(request,"autores/perfil_autor.html",{"autor":autor,"publicaciones":publicaciones})

@login_required
def editar_perfil(request,autor_id):
    autor = get_object_or_404(Autor,id = autor_id)
    if request.method == "POST":
        form = AutorForm(request.POST, instance=autor)
        if form.is_valid():
            form.save()
            return redirect("perfil_autor",autor_id=autor.id)
    else:
            form = AutorForm(instance=autor)
    return render(request,"autores/editar_perfil.html",{ "form":form,"autor":autor})

#CREATE : Crear publicaciones
@login_required
def crear_post(request):
    if request.method == "POST":
        titulo = request.POST["titulo"]
        descripcion = request.POST["descripcion"]
        autor = request.POST["autor"]
        estado = request.POST["estado"]

        Publicacion.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            autor=autor,
            estado=estado
        )
        return redirect("lista_publicaciones")
    return render(request,"publicaciones/crear_publicacion.html")

def crear_publicacion(request):
    if request.method == "POST":
        form = PublicacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_publicaciones")
    else:
        form = PublicacionForm()
    return render(request,"publicaciones/crear_publicacion.html",{"form":form})



def crear_autor(request):
    if request.method == "POST":
       form = AutorCreateForm(request.POST,request.FILES)
       if form.is_valid():
        form.save()
        return redirect("lista_autores")
    else:
        form = AutorCreateForm()
    return render(request,"autores/crear_autor.html",{"form":form})

@login_required
def dejar_comentario(request,publicacion_id):
    publicacion = get_object_or_404(Publicacion,id=publicacion_id)
    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.save()
            return redirect("detalle_publicacion",id=publicacion.id)
        else:
            form = ComentarioForm()
    return render(request,"publicaciones/comentar.html",{"form":form,"publicacion":publicacion})

#UPDATE: Actualizar una publicacion
@login_required
def editar_publicacion(request,id):
    publicacion = get_object_or_404(Publicacion,id=id)
    if request.method == "POST":
        publicacion.titulo= request.POST["titulo"]
        publicacion.descripcion = request.POST["descripcion"]
        publicacion.autor = request.POST["autor"]
        publicacion.estado = request.POST["estado"]

        publicacion.save()
        return redirect("lista_publicaciones")
    
    return render(request,"publicaciones/editar_publicacion.html",{"publicacion":publicacion})

#DELETE: Eliminar una publicacion
@login_required
def eliminar_publicacion(request,id):
    publicacion = get_object_or_404(Publicacion,id=id)
    if request.method == "POST":
        publicacion.delete()
    return redirect("lista_publicaciones")


#FROM publicaciones SELECT * 
# Publicacion.objects.all()
#CRUD - Create Read Updete Delete

def contacto(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)

        if form.is_valid():
            nombre = form.cleaned_data["nombre"]
            email = form.cleaned_data["email"]
            asunto = form.cleaned_data["asunto"]
            mensaje = form.cleaned_data["mensaje"]

            return render( request, "publicaciones/contacto.html",{
                "form": ContactoForm(),
                "enviado":True,
                "nombre": nombre
            },)
    else:
        form = ContactoForm()

    return render( request, "publicaciones/contacto.html", {"form": form})


# -------------------------------
# REGISTRO
# -------------------------------

def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST,request.FILES)
        if form.is_valid():
            usuario = form.save()
            login(request,usuario)
            return redirect("inicio")
    else:
        form = RegistroForm()
    return render(request,"autenticacion/registro.html",{"form":form})

# -------------------------------
# LOGIN
# -------------------------------

def iniciar_sesion(request):
    if request.method == "POST":
        form = AuthenticationForm(request,data =request.POST)

        if form.is_valid():
            usuario = form.get_user()
            login(request,usuario)
            return redirect("inicio")
    
    else:
        form = AuthenticationForm(request)
        
    return render(request,"autenticacion/login.html",{"form":form})


# -------------------------------
# LOGOUT
# -------------------------------

@require_POST

def cerrar_sesion(request):
    logout(request)

    return redirect("inicio")