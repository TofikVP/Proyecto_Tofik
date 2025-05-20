from .models import Noticias_ultima, Noticias_destacada, UserRole, BlogPost
from googletrans import Translator


def user_role(request):
    if request.user.is_authenticated:
        try:
            role = UserRole.objects.get(user=request.user).role
        except UserRole.DoesNotExist:
            role = None
    else:
        role = None
    return {"role": role}


translator = Translator()

for noticia in Noticias_ultima.objects.all():
    if not noticia.titulo_en:
        noticia.titulo_en = translator.translate(noticia.titulo, dest="en").text
    if not noticia.resumen_en:
        noticia.resumen_en = translator.translate(noticia.resumen, dest="en").text
    if not noticia.contenido_en:
        noticia.contenido_en = translator.translate(noticia.contenido, dest="en").text
    noticia.save()

for noticia in Noticias_destacada.objects.all():
    if not noticia.titulo_en:
        noticia.titulo_en = translator.translate(noticia.titulo, dest="en").text
    if not noticia.resumen_en:
        noticia.resumen_en = translator.translate(noticia.resumen, dest="en").text
    if not noticia.contenido_en:
        noticia.contenido_en = translator.translate(noticia.contenido, dest="en").text
    noticia.save()

for post in BlogPost.objects.all():
    if not post.title_en:
        post.title_en = translator.translate(post.title, src="es", dest="en").text
    if not post.content_en:
        post.content_en = translator.translate(post.content, src="es", dest="en").text
    post.save()
