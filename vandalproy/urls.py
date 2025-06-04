from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import *


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Panel administrador
    path('admin/', admin.site.urls),
    # Paginas del portal
    path('', home, name='home'),
    path('legal/', TemplateView.as_view(template_name='portal/legal.html'), name='legal'),
    path('error/', TemplateView.as_view(template_name='portal/error.html'), name='error'),
    #Blog y posts
    path('blog/', blog_list_view, name='blog_list'),
    path('blog/<int:post_id>/', blog_post_view, name='blog_post'),
    #Comentarios del blog
    path('comentario/<int:pk>/eliminar/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comentario/<int:comment_id>/rate/', rate_comment, name='rate_comment'),
    #Noticias
    path('noticias_destacada/<int:pk>/', detalle_noticia_destacada, name='detalle_noticia_destacada'),
    path('noticias_ultima/<int:pk>/', detalle_noticia_ultima, name='detalle_noticia_ultima'),
    #Página del calendario
    path('calendario/', calendario, name='calendario'),
    #Página de contacto
    path('contacto/', TemplateView.as_view(template_name='portal/contacto.html'), name='contacto'),
    #Página del ranking y sus juegos
    path('ranking/', ranking, name='ranking'),
    path('ranking/<int:pk>/', detalle_ranking_juego, name='detalle_ranking_juego'),
    path('api/streams/', obtener_streams, name='obtener_streams'),
    #Página de redactores
    path('redactores/', redactores, name='redactores'),
    #Página de videos
    path('videos/', video, name='videos'),
    #Formularios de acceso
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    #Paneles
    path('dashboard/', dashboard, name='error'),
    path('dashboard/admin/', admin.site.urls, name='dashboard_admin'),
    path('dashboard/<str:role>/', user_dashboard, name='dashboard_view'),
    path('dashboard/colaborador/', user_dashboard, name='dashboard_colaborador'),
    path('dashboard/redactor/', user_dashboard, name='dashboard_redactor'),
    path('dashboard/suscriptor/', user_dashboard, name='dashboard_suscriptor'),
    path('dashboard/comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('dashboard/suscriptor/change-password/', change_password, name='change_password'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
