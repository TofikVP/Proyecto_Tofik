from django.contrib import admin

# Register your models here.
from .models import BlogPost, BlogComment, UserRole, Noticias_ultima, Noticias_destacada

admin.site.register(UserRole)
admin.site.register(Noticias_ultima)
admin.site.register(Noticias_destacada)
admin.site.register(BlogPost)
admin.site.register(BlogComment)
