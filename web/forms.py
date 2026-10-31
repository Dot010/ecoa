from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import User
from posts.models import Comment, Post


class CadastroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "email"]
        labels = {"name": "Nome", "username": "Nome de usuário", "email": "E-mail"}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        labels = {"content": "O que está acontecendo?"}
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Escreva algo para quem te segue"}
            )
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = {"content": "Comentário"}
        widgets = {
            "content": forms.TextInput(attrs={"placeholder": "Escreva um comentário"})
        }


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "name", "bio"]
        labels = {"avatar": "Foto de perfil", "name": "Nome", "bio": "Bio"}
        widgets = {"avatar": forms.FileInput(attrs={"accept": "image/*"})}
