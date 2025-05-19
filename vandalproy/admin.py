from django.contrib import admin

#Register your models here.
from .models import BlogPost, BlogComment
from .models import UserRole
from .models import Noticia

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    list_filter = ('nombre',)
    ordering = ('nombre',)
    list_per_page = 10
    list_editable = ('nombre',)
    fieldsets = (
        (None, {
            'fields': ('nombre',)
        }),
    )

class PaginaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'imagen', 'fecha_creacion', 'fecha_modificacion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    search_fields = ('nombre',)
    list_filter = ('categoria',)
    ordering = ('nombre',)
    list_per_page = 10
    list_editable = ('nombre', 'categoria', 'imagen')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'imagen')
        }),
    )

admin.site.register(UserRole)
admin.site.register(Noticia)
admin.site.register(BlogPost)
admin.site.register(BlogComment)
