from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import BlogPost, BlogComment, UserRole, Noticia
from .forms import CommentForm, PostForm
from django.contrib.auth.backends import ModelBackend
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import BlogComment, UserRole
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_backends

logger = logging.getLogger(__name__)

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

@login_required
def dashboard(request):
    try:
        user_role = UserRole.objects.get(user=request.user).role
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'message': 'No tienes un rol asignado. Contacta al administrador.'})


@login_required
def user_dashboard(request, role):
    # 1) Instanciar el formulario de cambio de contraseña
    pwd_form = PasswordChangeForm(user=request.user)

    # 2) Procesar envíos de formulario (POST)
    if request.method == 'POST':
        # 2.a) Cambio de contraseña
        if 'password_submit' in request.POST:
            pwd_form = PasswordChangeForm(user=request.user, data=request.POST)
            if pwd_form.is_valid():
                user = pwd_form.save()
                update_session_auth_hash(request, user)
                return redirect(f'/')
        # 2.b) Subida de archivo (colaborador/redactor)
        if 'upload' in request.POST and role in ['colaborador', 'redactor']:
            fs = FileSystemStorage(location='static/uploads/')
            fs.save(request.FILES['file'].name, request.FILES['file'])
            return redirect(f'dashboard_{role}')
        if 'post_submit' in request.POST and role in ['colaborador', 'redactor']:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect(f'dashboard_{role}')
        if 'noticia_submit' in request.POST and role == 'redactor':
            titulo = request.POST.get('titulo')
            resumen = request.POST.get('resumen')
            contenido = request.POST.get('contenido')
            imagen = request.FILES.get('imagen')

            # Crear noticia sin 'autor', usando fecha actual
            from datetime import date
            Noticia.objects.create(
                titulo=titulo,
                resumen=resumen,
                contenido=contenido,
                imagen=imagen,
                fecha_publicacion=date.today()
            )

            return redirect(f'dashboard_{role}')

    # 3) Construir contexto **fuera** del POST, para GET y POST invalidados
    comments = BlogComment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'comments': comments,
        'password_form': pwd_form,
    }

    # 4) Añadir posts si corresponde
    if role in ['colaborador', 'redactor']:
        context['posts'] = BlogPost.objects.filter(author=request.user)

    # 5) Renderizar siempre (GET o POST), retornando HttpResponse
    templates = {
        'redactor':   'usuarios/dashboard_redactor.html',
        'colaborador':'usuarios/dashboard_colaborador.html',
        'suscriptor': 'usuarios/dashboard_suscriptor.html',
    }
    return render(request, templates[role], context)

    # Vista de listado de posts
    # Actualización para ordenar comentarios de más recientes a más antiguos





    # post = get_object_or_404(BlogPost.objects.prefetch_related('comments'), id=post_id)
    # form = CommentForm(request.POST or None)

    # if request.method == 'POST' and request.user.is_authenticated and form.is_valid():
    #     comment = form.save(commit=False)
    #     comment.post = post
    #     comment.user = request.user
    #     comment.save()
    #     return redirect('blog_post', post_id=post.id)

    # comments = post.comments.all().order_by('-created_at')
    # return render(request, 'portal/blog.html', {
    #     'post': post,
    #     'comments': comments,
    #     'form': form,
    # })

# Vistas de autenticación
def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('/')
        return render(request, 'usuarios/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'usuarios/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmar')

        error = None
        if password != confirm_password:
            error = 'Las contraseñas no coinciden'
        elif User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            error = 'El usuario o email ya está registrado'
        else:
            # 1) Crear el usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            # 2) Autenticarlo en la sesión
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # ahora no da error porque user.backend ya está definido
                # 3) Redirigir al home
                return redirect('/')  # :contentReference[oaicite:1]{index=1}

        # Si hay error, volver a mostrar el formulario
        return render(request, 'usuarios/login.html', {'error': error})

    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

    
@login_required
def change_password(request):
    role = UserRole.objects.get(user=request.user).role
    if role != 'suscriptor':
        return redirect('/')  # o página de error

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return render(request, 'usuarios/password_change_done.html')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'usuarios/dashboard_suscriptor.html', {
        'role': role,
        'password_form': form,
    })


# Vista de lista de posts del blog
def blog_list_view(request):
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and request.user.is_authenticated and form.is_valid():
        comment = form.save(commit=False)
        post_id = request.POST.get('post_id')
        comment.post = get_object_or_404(BlogPost, id=post_id) if post_id else None
        comment.user = request.user
        comment.save()
        return redirect('blog_list')

    posts = BlogPost.objects.prefetch_related('comments').all().order_by('-created_at')
    page_comments = BlogComment.objects.filter(post__isnull=True).order_by('-created_at')
    return render(request, 'portal/blog_list.html', {
        'posts': posts,
        'form': form,
        'page_comments': page_comments,
    })

# Vista de detalle de post con comentarios
# Actualización para ordenar comentarios de más recientes a más antiguos
def blog_post_view(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and request.user.is_authenticated:
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = BlogComment.objects.get(id=parent_id)
            comment.save()
            return redirect('blog_post', post_id=post.id)

    # solo los comentarios principales (no respuestas)
    top_comments = post.comments.filter(parent__isnull=True).order_by('created_at')
    return render(request, 'portal/blog_detalle.html', {
        'post': post,
        'comments': top_comments,
        'form': form,
    })

# Vista para enviar comentarios desde el blog
def submit_comment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        comment_content = request.POST.get('comment')
        post_id = request.POST.get('post_id')
        if comment_content and post_id:
            try:
                post = BlogPost.objects.get(id=post_id)
                BlogComment.objects.create(
                    user=request.user,
                    content=comment_content,
                    post=post
                )
            except BlogPost.DoesNotExist:
                return HttpResponseRedirect(reverse('blog'))
        return HttpResponseRedirect(reverse('blog'))
    return HttpResponseRedirect(reverse('login'))

# Noticias
def detalle_noticia(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    return render(request, 'portal/noticia_detalle.html', {'noticia': noticia})

def home(request):
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')
    return render(request, 'common/home.html', {'noticias': noticias})

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogComment
    template_name = 'usuarios/confirm_delete_comment.html'
    success_url = reverse_lazy('home')  # redirige al panel

    def test_func(self):
        role = UserRole.objects.get(user=self.request.user).role
        if role == 'admin':
            return True
        if role == 'redactor':
            return self.get_object().user == self.request.user
        return False
