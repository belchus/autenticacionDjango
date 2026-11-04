from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to="avatars/",blank=True,null=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                   null=True,blank =True,related_name="perfil_autor")

    def __str__(self):
        #return self.titulo
        return f"{self.nombre} - {self.apellido}"
    
class Publicacion(models.Model):
    ESTADOS = [("borrador","Borrador"),("publicado","Publicado"),("archivado","Archivado")]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    #Arreglar aca para que tambien relacionar con el autor
    autor = models.ForeignKey(Autor,on_delete=models.CASCADE,related_name="publicaciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    url_imagen = models.ImageField(upload_to="posts/",blank=True,null=True)
   

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        #return self.titulo
        return f"{self.titulo} - {self.autor}"

class Comentario(models.Model):
    contenido = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    publicacion = models.ForeignKey(Publicacion,on_delete=models.CASCADE,related_name="comentarios")
    autor = models.ForeignKey(Autor,on_delete=models.CASCADE,null=True,blank=True,related_name="comentarios")
    def __str__(self):
        return f"Comentario en {self.publicacion.titulo}"
    

class Calificacion(models.Model):
    publicacion = models.ForeignKey(
        Publicacion, on_delete= models.CASCADE, related_name="calificaciones")
    autor = models.ForeignKey(Autor,on_delete=models.CASCADE,related_name="calificaciones")
    estrellas = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion","autor"],
                name= "una_calificacion_por_usuario"

            ),
            models.CheckConstraint(
                condition = models.Q(estrellas__gt=1) &
                models.Q(estrellas__gt=5) ,
                name= "calificacion_entre_1_y_5"


            )
        ]

    def __str__(self):
        return f"{self.autor}-{self.estrellas}estrellas"