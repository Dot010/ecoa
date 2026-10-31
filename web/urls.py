from django.contrib.auth import views as auth_views
from django.urls import path

from web import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "entrar/",
        auth_views.LoginView.as_view(
            template_name="web/entrar.html", redirect_authenticated_user=True
        ),
        name="entrar",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="sair"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("feed/", views.feed, name="timeline"),
    path("posts/novo/", views.publicar, name="publicar"),
    path("posts/<int:post_id>/curtir/", views.curtir, name="curtir"),
    path("posts/<int:post_id>/comentar/", views.comentar, name="comentar"),
    path("posts/<int:post_id>/apagar/", views.apagar_post, name="apagar_post"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
    path("u/<str:username>/", views.perfil, name="perfil"),
    path("u/<str:username>/seguir/", views.seguir, name="seguir"),
]
