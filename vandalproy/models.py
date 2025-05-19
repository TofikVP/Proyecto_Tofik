from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('redactor', 'Redactor'), ('colaborador', 'Colaborador'), ('suscriptor', 'Suscriptor')])

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    content_en = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    def __str__(self):
        return f"{self.user.username} en {self.post.title if self.post else 'General'}"

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    titulo_en = models.CharField(max_length=200, blank=True)
    resumen = models.TextField()
    resumen_en = models.TextField(blank=True)
    contenido = models.TextField()
    contenido_en = models.TextField(blank=True)
    fecha_publicacion = models.DateField()
    imagen = models.ImageField(upload_to='noticias/')

    def __str__(self):
        return self.titulo
