from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[
            ("admin", "Admin"),
            ("redactor", "Redactor"),
            ("colaborador", "Colaborador"),
            ("suscriptor", "Suscriptor"),
        ],
    )

    def __str__(self):
        return f"{self.user.username} - Rol: {self.get_role_display()}"


class BlogPost(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    content_en = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to="blog/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlogComment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def __str__(self):
        return f"{self.user.username} en {self.post.title if self.post else 'General'}"

class CommentRating(models.Model):
    comment = models.ForeignKey('BlogComment', related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('comment', 'user')

#Equipo de redactores
class Redactor(models.Model):
    nombre = models.CharField(max_length=100)
    resumen = models.CharField(max_length=255)
    resumen_en = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.ImageField(upload_to='images/Redactores/')
    icono_twitter = models.ImageField(upload_to='images/Redactores/Iconos/', blank=True, null=True)
    icono_linkedin = models.ImageField(upload_to='images/Redactores/Iconos/', blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Noticias_ultima(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    titulo_en = models.CharField(max_length=200, blank=True)
    resumen = models.TextField()
    resumen_en = models.TextField(blank=True)
    contenido = models.TextField()
    contenido_en = models.TextField(blank=True)
    fecha_publicacion = models.DateField()
    imagen = models.ImageField(upload_to="noticias/ultimas/")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noticias_ultimas", null=True, blank=True)


    def __str__(self):
        return self.titulo


class Noticias_destacada(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    titulo_en = models.CharField(max_length=200, blank=True)
    resumen = models.TextField()
    resumen_en = models.TextField(blank=True)
    contenido = models.TextField()
    contenido_en = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="noticias/destacadas/")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noticias_destacadas", null=True, blank=True)

    def __str__(self):
        return self.titulo


# Videojuegos del ranking

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    nombre_en = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.nombre
    
class Plataforma(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

def captura_upload_to(instance, filename):
    # Guarda en juegos_ranking/capturas/<id_juego>/<nombre_archivo>
    return f"juegos_ranking/capturas/{instance.juego.id}/{filename}"

class Captura(models.Model):
    juego = models.ForeignKey('Juego_ranking', related_name='capturas', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=captura_upload_to)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Captura de {self.juego.titulo}"

class Juego_ranking(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    titulo = models.CharField(max_length=200)
    titulo_en = models.CharField(max_length=200, blank=True)
    resumen = models.TextField()
    resumen_en = models.TextField(blank=True)
    generos = models.ManyToManyField(Genero)
    nota = models.PositiveSmallIntegerField(default=0)
    plataformas_de_lanzamiento = models.ManyToManyField(Plataforma)
    portada = models.ImageField(upload_to="juegos_ranking/portadas/")

    def __str__(self):
        return self.titulo
    
class Video(models.Model):
    titulo = models.CharField(max_length=200)
    titulo_en = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True)
    descripcion_en = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='videos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class EventoCalendario(models.Model):
    nombre = models.CharField(max_length=200)
    nombre_en = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField()
    descripcion = models.TextField()
    descripcion_en = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='Calendario/')

    def __str__(self):
        return f"{self.nombre} ({self.fecha})"