from django.contrib import admin

# Register your models here.

from .models import Autor, Publicacion

admin.site.register(Autor)

@admin.register(Publicacion)

class PublicacionAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "autor",
        "fecha_creacion",
        "estado"
    )

    search_fields =(
        "titulo",
        "descripcion",
        "autor"
    )

    list_filter =(
        "estado",
        "fecha_creacion"
    )

    list_editable = ("estado",)

admin.site.site_header = "Administracion de Glup"
admin.site.site_title = "Panel del blog"
admin.site.index_title = "Gestion de publicaciones"