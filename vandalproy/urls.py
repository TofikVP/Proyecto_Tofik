from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic import TemplateView
from .views import dashboard, user_dashboard, CommentDeleteView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Panel administrador
    path('admin/', admin.site.urls),
    # Paginas del portal
    path('', views.home, name='home'),
    path('legal/', TemplateView.as_view(template_name='portal/legal.html'), name='legal'),
    path('error/', TemplateView.as_view(template_name='portal/error.html'), name='error'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_post_view, name='blog_post'),
    path('comentario/<int:pk>/eliminar/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comentario/<int:comment_id>/rate/', views.rate_comment, name='rate_comment'),
    path('noticias_destacada/<int:pk>/', views.detalle_noticia_destacada, name='detalle_noticia_destacada'),
    path('noticias_ultima/<int:pk>/', views.detalle_noticia_ultima, name='detalle_noticia_ultima'),
    path('calendario/', TemplateView.as_view(template_name='portal/calendario.html'), name='calendario'),
    path('contacto/', TemplateView.as_view(template_name='portal/contacto.html'), name='contacto'),
    path('ranking/', TemplateView.as_view(template_name='portal/ranking.html'), name='ranking'),
    path('ranking/<int:pk>/', views.detalle_ranking_juego, name='detalle_ranking_juego'),    path('redactores/', TemplateView.as_view(template_name='portal/redactores.html'), name='redactores'),
    path('videos/', TemplateView.as_view(template_name='portal/videos.html'), name='videos'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', dashboard, name='error'),
    path('dashboard/admin/', admin.site.urls, name='dashboard_admin'),
    path('dashboard/<str:role>/', user_dashboard, name='dashboard_view'),
    path('dashboard/colaborador/', user_dashboard, name='dashboard_colaborador'),
    path('dashboard/redactor/', user_dashboard, name='dashboard_redactor'),
    path('dashboard/suscriptor/', user_dashboard, name='dashboard_suscriptor'),
    path('dashboard/comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('dashboard/suscriptor/change-password/', views.change_password, name='change_password'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
