import requests
from django.conf import settings

from django.db.models import Q

from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy


from django.views.generic import DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from django.utils.translation import get_language

from django.core.paginator import Paginator

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    BlogPost,
    BlogComment,
    UserRole,
    Noticias_ultima,
    Noticias_destacada,
    CommentRating,
    Juego_ranking,
    Redactor,
    Video,
    EventoCalendario,
)
from .forms import CommentForm, PostForm
import logging

logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

#Paneles de usuario

@login_required
def user_dashboard(request, role):
    # 1) Instanciar el formulario de cambio de contraseña
    pwd_form = PasswordChangeForm(user=request.user)

    # 2) Procesar envíos de formulario (POST)
    if request.method == "POST":
        # 2.a) Cambio de contraseña
        if "password_submit" in request.POST:
            pwd_form = PasswordChangeForm(user=request.user, data=request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                return redirect(f"/")
        # 2.b) Subida de archivo (admin/colaborador/redactor)
        if "upload" in request.POST and role in ["admin", "colaborador", "redactor"]:
            fs = FileSystemStorage(location="static/uploads/")
            fs.save(request.FILES["file"].name, request.FILES["file"])
            return redirect(f"dashboard_{role}")
        if "post_submit" in request.POST and role in [
            "admin",
            "colaborador",
            "redactor",
        ]:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect(f"dashboard_{role}")
        if "noticia_submit" in request.POST and role == "redactor" or role == "admin":
            titulo = request.POST.get("titulo")
            resumen = request.POST.get("resumen")
            contenido = request.POST.get("contenido")
            imagen = request.FILES.get("imagen")

            # Crear noticia sin 'autor', usando fecha actual
            from datetime import date

            Noticias_ultima.objects.create(
                titulo=titulo,
                resumen=resumen,
                contenido=contenido,
                imagen=imagen,
                fecha_publicacion=date.today(),
            )

            return redirect(f"dashboard_{role}")

    # 3) Construir contexto **fuera** del POST, para GET y POST invalidados
    comments = BlogComment.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "comments": comments,
        "password_form": pwd_form,
    }

    # 4) Añadir posts si corresponde
    if role in ["colaborador", "redactor"]:
        context["posts"] = BlogPost.objects.filter(author=request.user)

    # 5) Renderizar siempre (GET o POST), retornando HttpResponse
    templates = {
        "redactor": "usuarios/dashboard_redactor.html",
        "colaborador": "usuarios/dashboard_colaborador.html",
        "suscriptor": "usuarios/dashboard_suscriptor.html",
    }
    return render(request, templates[role], context)


# Vistas de autenticación
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("/")
        return render(
            request, "usuarios/login.html", {"error": "Credenciales inválidas"}
        )
    return render(request, "usuarios/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("nombre")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmar")

        error = None
        if password != confirm_password:
            error = "Las contraseñas no coinciden"
        elif (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            error = "El usuario o email ya está registrado"
        else:
            # 1) Crear el usuario
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            # 2) Asignar rol de suscriptor automáticamente
            UserRole.objects.create(user=user, role="suscriptor")
            # 3) Autenticarlo en la sesión
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # 4) Redirigir al home
                return redirect("/")

        # Si hay error, volver a mostrar el formulario
        return render(request, "usuarios/login.html", {"error": error})

    return render(request, "usuarios/login.html")


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def change_password(request):
    role = UserRole.objects.get(user=request.user).role
    if role != "suscriptor":
        return redirect("/") 

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return render(request, "usuarios/password_change_done.html")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(
        request,
        "usuarios/dashboard_suscriptor.html",
        {
            "role": role,
            "password_form": form,
        },
    )


#Blog

# Lista de posts del blog
def blog_list_view(request):
    form = CommentForm(request.POST or None)

    if request.method == "POST" and request.user.is_authenticated and form.is_valid():
        comment = form.save(commit=False)
        post_id = request.POST.get("post_id")
        comment.post = get_object_or_404(BlogPost, id=post_id) if post_id else None
        comment.user = request.user
        comment.save()
        return redirect("blog_list")

    posts_list = (
        BlogPost.objects.prefetch_related("comments").all().order_by("-created_at")
    )
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    comments = BlogComment.objects.filter(parent__isnull=True).order_by("-created_at")

    return render(
        request,
        "portal/blog_list.html",
        {
            "posts": posts,
            "form": form,
            "comments": comments,
        },
    )


# Posts del blog y sus comentarios
def blog_post_view(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    form = CommentForm(request.POST or None)
# Ordenar comentarios de más recientes a más antiguos
    if request.method == "POST" and request.user.is_authenticated:
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = BlogComment.objects.get(id=parent_id)
            comment.save()
            return redirect("blog_post", post_id=post.id)

    # solo los comentarios principales (no respuestas)
    top_comments = post.comments.filter(parent__isnull=True).order_by("created_at")
    # Obtener el rol del usuario autenticado
    role = None
    if request.user.is_authenticated:
        try:
            role = UserRole.objects.get(user=request.user).role
        except UserRole.DoesNotExist:
            role = None

    # Obtener el siguiente post (por ID mayor)
    next_post = BlogPost.objects.filter(id__gt=post.id).order_by("id").first()

    return render(
        request,
        "portal/blog_detalle.html",
        {
            "post": post,
            "comments": top_comments,
            "form": form,
            "role": role,
            "next_post": next_post,
        },
    )

class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'usuarios/confirm_delete_post.html'
    success_url = reverse_lazy('blog_list')

    def test_func(self):
        post = self.get_object()
        role = UserRole.objects.get(user=self.request.user).role
        return role in ['redactor', 'admin'] or post.author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        return context

class BlogPostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    fields = ['title', 'title_en', 'content', 'content_en', 'image']
    template_name = 'portal/blog_detalle_editar.html'
    success_url = reverse_lazy('blog_list')

    def test_func(self):
        user = self.request.user
        # Permitir solo admin o redactor
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

# Vista para enviar comentarios desde el blog
def submit_comment(request):
    if request.method == "POST" and request.user.is_authenticated:
        comment_content = request.POST.get("comment")
        post_id = request.POST.get("post_id")
        if comment_content and post_id:
            try:
                post = BlogPost.objects.get(id=post_id)
                BlogComment.objects.create(
                    user=request.user, content=comment_content, post=post
                )
            except BlogPost.DoesNotExist:
                return HttpResponseRedirect(reverse("blog"))
        return HttpResponseRedirect(reverse("blog"))
    return HttpResponseRedirect(reverse("login"))

#Puntuar comentarios
@require_POST
@login_required
def rate_comment(request, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id)
    stars = int(request.POST.get("stars", 0))
    if 1 <= stars <= 5:
        rating, created = CommentRating.objects.update_or_create(
            comment=comment, user=request.user, defaults={"stars": stars}
        )
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("blog_post", post_id=comment.post.id)

#Borrar comentarios del blog
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogComment
    template_name = "usuarios/confirm_delete_comment.html"
    success_url = reverse_lazy("home")  # redirige al panel

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        comment = self.get_object()
        if comment.post:
            return reverse("blog_post", args=[comment.post.id])
        return reverse("home")

    def test_func(self):
        role = UserRole.objects.get(user=self.request.user).role
        if role == "redactor" or role == "admin":
            return role in ["redactor", "admin"]
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.object
        return context

#Borrar respuestas a comentarios
def reply_delete_view(request, pk):
    reply = get_object_or_404(BlogComment, pk=pk)
    # Solo admin/redactor puede borrar
    if getattr(request.user, 'userrole', None) and request.user.userrole.role in ['admin', 'redactor']:
        reply.delete()
    # Redirige al post original
    return redirect('blog_post', post_id=reply.post.id)


#Redactores


#Redactores del medio
def redactores(request):
    redactores = Redactor.objects.all()
    return render(request, 'portal/redactores.html', {'redactores': redactores})

# Noticias

# Vista para la página de inicio
def home(request):
    query = request.GET.get('q', '')

    # Buscar en noticias destacadas
    destacadas_qs = Noticias_destacada.objects.all().order_by("-titulo")
    if query:
        destacadas_qs = destacadas_qs.filter(
            Q(titulo__icontains=query) |
            Q(titulo_en__icontains=query) |
            Q(resumen__icontains=query) |
            Q(resumen_en__icontains=query) |
            Q(contenido__icontains=query) |
            Q(contenido_en__icontains=query)
        )

    paginator_destacadas = Paginator(destacadas_qs, 3)
    page_number_destacadas = request.GET.get('page')
    noticias_destacadas = paginator_destacadas.get_page(page_number_destacadas)

    # Buscar en noticias ultimas
    ultimas_qs = Noticias_ultima.objects.all().order_by("-fecha_publicacion")
    if query:
        ultimas_qs = ultimas_qs.filter(
            Q(titulo__icontains=query) |
            Q(titulo_en__icontains=query) |
            Q(resumen__icontains=query) |
            Q(resumen_en__icontains=query) |
            Q(contenido__icontains=query) |
            Q(contenido_en__icontains=query)
        )

    paginator_ultimas = Paginator(ultimas_qs, 3)
    page_number_ultimas = request.GET.get('ultimas_page')
    ultimas_noticias = paginator_ultimas.get_page(page_number_ultimas)

    return render(
        request,
        "portal/home.html",
        {
            "noticias_destacadas": noticias_destacadas,
            "ultimas_noticias": ultimas_noticias,
            "query": query,
        },
    )

#Noticias destacadas
def detalle_noticia_destacada(request, pk):
    noticia = get_object_or_404(Noticias_destacada, pk=pk)
    return render(request, "portal/noticia_detalle.html", {"noticia": noticia, "tipo_noticia": "destacada"})
#Editar noticia destacada
class EditarNoticiaDestacadaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Noticias_destacada
    fields = ['titulo', 'titulo_en', 'resumen', 'resumen_en', 'contenido', 'contenido_en', 'imagen']
    template_name = 'portal/noticia_destacada_editar.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

#Noticias ultimas
def detalle_noticia_ultima(request, pk):
    noticia = get_object_or_404(Noticias_ultima, pk=pk)
    return render(request, "portal/noticia_detalle.html", {"noticia": noticia, "tipo_noticia": "ultima"})
#Editar noticia ultima
class EditarNoticiaUltimaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Noticias_ultima
    fields = ['titulo', 'titulo_en', 'resumen', 'resumen_en', 'contenido', 'contenido_en', 'fecha_publicacion', 'imagen']
    template_name = 'portal/noticia_ultima_editar.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

#Ranking

def ranking(request):
    juegos = Juego_ranking.objects.all().order_by('-nota')
    return render(request, 'portal/ranking.html', {'Juego_ranking': juegos})

# Detalle de un juego en el ranking
def detalle_ranking_juego(request, pk):
    juego = get_object_or_404(Juego_ranking, pk=pk)
    capturas = juego.capturas.all()
    # Obtener anterior y siguiente por ID
    anterior = Juego_ranking.objects.filter(id__lt=juego.id).order_by('-id').first()
    siguiente = Juego_ranking.objects.filter(id__gt=juego.id).order_by('id').first()
    return render(request, 'portal/ranking_detalle.html', {
        'juego': juego,
        'capturas': capturas,
        'juego_anterior': anterior,
        'juego_siguiente': siguiente,
    })

#Editar un juego del ranking
class EditarRankingJuegoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Juego_ranking
    fields = ['titulo', 'titulo_en', 'resumen', 'resumen_en', 'nota', 'generos', 'plataformas_de_lanzamiento', 'portada']
    template_name = 'portal/ranking_detalle_editar.html'
    success_url = reverse_lazy('ranking')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

#Twitch API
def get_twitch_app_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

#Obtener streams de Twitch por nombre de juego
@csrf_exempt
@require_GET
def obtener_streams(request):
    game_name = request.GET.get('game', '')
    if not game_name:
        return JsonResponse({'error': 'Missing game name'}, status=400)

    # Paso 1: obtener access_token
    token_url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    token_res = requests.post(token_url, data=data)
    if token_res.status_code != 200:
        return JsonResponse({'error': 'Token failed', 'detail': token_res.text}, status=token_res.status_code)
    
    access_token = token_res.json()['access_token']

    # Paso 2: obtener game_id
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    search_url = f'https://api.twitch.tv/helix/search/categories?query={game_name}'
    game_res = requests.get(search_url, headers=headers)
    if game_res.status_code != 200:
        return JsonResponse({'error': 'Game search failed'}, status=500)

    data = game_res.json().get('data', [])
    if not data:
        return JsonResponse({'error': 'No game found'}, status=404)

    game_id = data[0]['id']

    # Paso 3: obtener streams
    streams_url = f'https://api.twitch.tv/helix/streams?game_id={game_id}&first=10'
    stream_res = requests.get(streams_url, headers=headers)
    if stream_res.status_code != 200:
        return JsonResponse({'error': 'Stream fetch failed'}, status=500)

    return JsonResponse({'streams': stream_res.json().get('data', [])})

#Videos

def video(request):
    idioma = get_language()
    video = Video.objects.all().order_by('-fecha_subida')
    return render(request, 'portal/videos.html', {'video': video, 'idioma': idioma})


#Calendario

def calendario(request):
    eventos = EventoCalendario.objects.all().order_by('fecha')
    return render(request, 'portal/calendario.html', {'eventos': eventos})

# Detalle de un evento del calendario
class CalendarioDetailView(UpdateView):
    model = EventoCalendario
    template_name = 'portal/calendario_detalle.html'
    context_object_name = 'evento'
    fields = ['nombre', 'nombre_en', 'fecha', 'descripcion', 'descripcion_en', 'imagen']

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

# Borrar evento del calendario
class CalendarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = EventoCalendario
    template_name = 'portal/calendario_confirm_delete.html'
    success_url = reverse_lazy('calendario')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']

#Editar evento del calendario
class EditarCalendarioView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EventoCalendario
    fields = ['nombre', 'nombre_en', 'fecha', 'descripcion', 'descripcion_en', 'imagen']
    template_name = 'portal/calendario_editar.html'
    success_url = reverse_lazy('calendario')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'userrole') and user.userrole.role in ['admin', 'redactor']