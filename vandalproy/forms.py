from django import forms
from .models import BlogComment, BlogPost


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "Escribe tu comentario aquí..."}
        ),
        label="",
    )

    class Meta:
        model = BlogComment
        fields = ["content"]


class PostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
