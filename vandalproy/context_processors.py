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