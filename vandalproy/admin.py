from django.contrib import admin

# Register your models here.
from .models import BlogPost, BlogComment, UserRole, Noticias_ultima, Noticias_destacada, Juego_ranking, Plataforma, Genero, Captura

class CapturaInline(admin.TabularInline):
    model = Captura
    extra = 1

class JuegoRankingAdmin(admin.ModelAdmin):
    inlines = [CapturaInline]

admin.site.register(UserRole)
admin.site.register(Noticias_ultima)
admin.site.register(Noticias_destacada)
admin.site.register(BlogPost)
admin.site.register(BlogComment)
admin.site.register(Juego_ranking)
admin.site.register(Plataforma)
admin.site.register(Genero)
admin.site.register(Captura)