from django.contrib import admin
from .models import BlogPost, BlogComment, UserRole, Noticias_ultima, Noticias_destacada, Juego_ranking, Plataforma, Genero, Captura, Redactor, Video, EventoCalendario

class CapturaInline(admin.TabularInline):
    model = Captura
    extra = 1

class JuegoRankingAdmin(admin.ModelAdmin):
    inlines = [CapturaInline]
    # Permitir cambiar el ID después de creado
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return []
        return []
admin.site.register(UserRole)
admin.site.register(Noticias_ultima)
admin.site.register(Noticias_destacada)
admin.site.register(BlogPost)
admin.site.register(BlogComment)
admin.site.register(Juego_ranking, JuegoRankingAdmin)
admin.site.register(Plataforma)
admin.site.register(Genero)
admin.site.register(Captura)
admin.site.register(Redactor)
admin.site.register(Video)
admin.site.register(EventoCalendario)