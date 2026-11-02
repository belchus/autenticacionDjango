from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from publicaciones.models import Autor, Comentario, Publicacion

User = get_user_model()

class ContactoForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Correo Electronico")
    asunto = forms.CharField(label="Asunto", max_length=150)
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)


#forms.ModelForm

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
    
        fields = [
            "titulo",
            "descripcion",
            "autor",
            "estado",
            "url_imagen"
        ]

        labels = {
            "titulo":"Titulo de la publicacion",
            "descripcion":"Descipcion de la publicacion",
            "autor":"Selecciona un autor",
            "estado":"Estado de la publicacion",
            "url_imagen":"URL de la imagen de la publicacion"
        }

        widgets = {
            "titulo":forms.TextInput(attrs={"class":"form-control","placeholder":"Escribi tu titulo"}),
            "descripcion":forms.Textarea(attrs={"class":"form-control","placeholder":"Escribi el contenido"}),
            "autor":forms.Select(attrs={"class":"form-control"}),
            "estado":forms.Select(attrs={"class":"form-select"}),
           
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario

        fields = ["contenido"]

        labels = {
            "contenido" :"Escribi un comentario"
        }

        widgets = {
            "contenido" : forms.Textarea(attrs={
                "class":"form-control",
                "rows":3,
                "placeholder":"Deja tu comentario"
            })
        }

class AutorCreateForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = [
            "nombre",
            "apellido",
            "email",
            "username",
            "imagen"

        ]

        def clean_email(self):
            email = self.cleaned_data["email"]

            if Autor.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("Este email ya esta en uso")
            return email
        

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor

        fields = [
            "nombre",
            "apellido",
            "email",
            
        ]
        labels = {
            "nombre":"Nombre",
            "apellido":"Apellido",
            "email":"Email"
        }

        widgets = {
            "nombre": forms.TextInput(attrs={"class":"form-control"}),
            "apellido": forms.TextInput(attrs={"class":"form-control"}),
            "email": forms.EmailInput(attrs={"class":"form-control"})
        }

class RegistroForm(UserCreationForm):

    first_name = forms.CharField(max_length=150, label="Nombre")
    last_name = forms.CharField(max_length=150, label="Apellido")
    email = forms.EmailField(label="Tu correo electrónico")
    avatar = forms.ImageField(required=False, label="Tu foto de perfil")

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email"
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]

        if Autor.objects.filter(username=username).exists():
            raise ValidationError(
                "Ese nombre de usuario ya está en uso"
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if Autor.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "Este correo electrónico ya está en uso"
            )

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.first_name = self.cleaned_data["first_name"]
        usuario.last_name = self.cleaned_data["last_name"]
        usuario.email = self.cleaned_data["email"]

        if commit:
            usuario.save()

            Autor.objects.create(
                usuario=usuario,
                nombre=usuario.first_name,
                apellido=usuario.last_name,
                email=usuario.email,
                username=usuario.username,
                imagen=self.cleaned_data.get("avatar")
            )

        return usuario