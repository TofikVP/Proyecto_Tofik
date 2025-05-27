from django.core.management.base import BaseCommand
from vandalproy.models import (
    Noticias_ultima, Noticias_destacada, BlogPost,
    Juego_ranking, Redactor, Genero
)
from googletrans import Translator

class Command(BaseCommand):
    help = 'Traduce automáticamente todos los textos relevantes al inglés'

    def handle(self, *args, **kwargs):
        translator = Translator()

        # Traduce Noticias_ultima
        for noticia in Noticias_ultima.objects.all():
            changed = False
            if hasattr(noticia, 'titulo_en') and not noticia.titulo_en:
                noticia.titulo_en = translator.translate(noticia.titulo, dest="en").text
                changed = True
            if hasattr(noticia, 'resumen_en') and not noticia.resumen_en:
                noticia.resumen_en = translator.translate(noticia.resumen, dest="en").text
                changed = True
            if hasattr(noticia, 'contenido_en') and not noticia.contenido_en:
                noticia.contenido_en = translator.translate(noticia.contenido, dest="en").text
                changed = True
            if changed:
                noticia.save()
                self.stdout.write(self.style.SUCCESS(f"Traducida noticia_ultima: {noticia.titulo}"))

        # Traduce Noticias_destacada
        for noticia in Noticias_destacada.objects.all():
            changed = False
            if hasattr(noticia, 'titulo_en') and not noticia.titulo_en:
                noticia.titulo_en = translator.translate(noticia.titulo, dest="en").text
                changed = True
            if hasattr(noticia, 'resumen_en') and not noticia.resumen_en:
                noticia.resumen_en = translator.translate(noticia.resumen, dest="en").text
                changed = True
            if hasattr(noticia, 'contenido_en') and not noticia.contenido_en:
                noticia.contenido_en = translator.translate(noticia.contenido, dest="en").text
                changed = True
            if changed:
                noticia.save()
                self.stdout.write(self.style.SUCCESS(f"Traducida noticia_destacada: {noticia.titulo}"))

        # Traduce BlogPost
        for post in BlogPost.objects.all():
            changed = False
            if hasattr(post, 'title_en') and not post.title_en:
                post.title_en = translator.translate(post.title, src="es", dest="en").text
                changed = True
            if hasattr(post, 'content_en') and not post.content_en:
                post.content_en = translator.translate(post.content, src="es", dest="en").text
                changed = True
            if changed:
                post.save()
                self.stdout.write(self.style.SUCCESS(f"Traducido blogpost: {post.title}"))

        # Traduce Juegos del ranking
        for juego in Juego_ranking.objects.all():
            changed = False
            if hasattr(juego, 'titulo_en') and not juego.titulo_en:
                juego.titulo_en = translator.translate(juego.titulo, dest="en").text
                changed = True
            if hasattr(juego, 'resumen_en') and not juego.resumen_en:
                juego.resumen_en = translator.translate(juego.resumen, dest="en").text
                changed = True
            if changed:
                juego.save()
                self.stdout.write(self.style.SUCCESS(f"Traducido juego ranking: {juego.titulo}"))

        # Traduce Generos (solo una vez por género)
        for genero in Genero.objects.all():
            changed = False
            if hasattr(genero, 'nombre_en') and not genero.nombre_en:
                genero.nombre_en = translator.translate(genero.nombre, dest="en").text
                changed = True
            if changed:
                genero.save()
                self.stdout.write(self.style.SUCCESS(f"Traducido género: {genero.nombre}"))

        # Traduce Redactores (equipo)
        for redactor in Redactor.objects.all():
            changed = False
            if hasattr(redactor, 'nombre_en') and not redactor.nombre_en:
                redactor.nombre_en = translator.translate(redactor.nombre, dest="en").text
                changed = True
            if hasattr(redactor, 'resumen_en') and not redactor.resumen_en:
                redactor.resumen_en = translator.translate(redactor.resumen, dest="en").text
                changed = True
            if changed:
                redactor.save()
                self.stdout.write(self.style.SUCCESS(f"Traducido redactor: {redactor.nombre}"))

        self.stdout.write(self.style.SUCCESS("Traducción automática completada."))