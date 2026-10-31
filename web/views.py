from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.models import User
from posts.models import Comment, Post
from posts.views import posts_com_contadores
from web.forms import CadastroForm, ComentarioForm, PerfilForm, PostForm


def voltar(request, padrao="timeline"):
    destino = request.POST.get("next") or request.GET.get("next")
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}
    ):
        return redirect(destino)
    return redirect(padrao)


def com_comentarios(posts):
    return posts.prefetch_related(
        Prefetch("comments", queryset=Comment.objects.select_related("author"))
    )


def contexto_dos_posts(request, posts):
    pagina = Paginator(com_comentarios(posts), 10).get_page(request.GET.get("page"))
    curtidos = set()
    if request.user.is_authenticated:
        curtidos = set(request.user.liked_posts.values_list("id", flat=True))
    return {"pagina": pagina, "curtidos": curtidos, "comentario_form": ComentarioForm()}


def inicio(request):
    return redirect("timeline" if request.user.is_authenticated else "entrar")


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("timeline")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request, "Conta criada! Siga algumas pessoas para montar o seu feed."
        )
        return redirect("timeline")
    return render(request, "web/cadastro.html", {"form": form})


@login_required
def feed(request):
    posts = posts_com_contadores().filter(author__in=request.user.following.all())
    sugestoes = (
        User.objects.exclude(pk=request.user.pk)
        .exclude(pk__in=request.user.following.all())
        .order_by("?")[:5]
    )
    contexto = contexto_dos_posts(request, posts)
    contexto.update({"post_form": PostForm(), "sugestoes": sugestoes})
    return render(request, "web/feed.html", contexto)


@login_required
@require_POST
def publicar(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Publicado!")
    else:
        messages.error(request, "O post precisa ter de 1 a 280 caracteres.")
    return voltar(request)


@login_required
@require_POST
def curtir(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return voltar(request)


@login_required
@require_POST
def comentar(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.post = post
        comentario.author = request.user
        comentario.save()
    else:
        messages.error(request, "O comentário precisa ter de 1 a 280 caracteres.")
    return voltar(request)


@login_required
@require_POST
def apagar_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("Você só pode apagar os seus próprios posts.")
    post.delete()
    messages.success(request, "Post apagado.")
    return voltar(request)


def perfil(request, username):
    usuario = get_object_or_404(User, username=username)
    aba = request.GET.get("aba", "posts")
    contexto = {
        "usuario": usuario,
        "aba": aba,
        "eu_sigo": request.user.is_authenticated
        and request.user.following.filter(pk=usuario.pk).exists(),
    }
    if aba == "seguidores":
        contexto["pessoas"] = usuario.followers.order_by("username")
    elif aba == "seguindo":
        contexto["pessoas"] = usuario.following.order_by("username")
    else:
        contexto.update(
            contexto_dos_posts(request, posts_com_contadores().filter(author=usuario))
        )
    return render(request, "web/perfil.html", contexto)


@login_required
@require_POST
def seguir(request, username):
    alvo = get_object_or_404(User, username=username)
    if alvo == request.user:
        messages.error(request, "Você não pode seguir a si mesmo.")
    elif request.user.following.filter(pk=alvo.pk).exists():
        request.user.following.remove(alvo)
    else:
        request.user.following.add(alvo)
    return voltar(request)


@login_required
def configuracoes(request):
    perfil_form = PerfilForm(instance=request.user)
    senha_form = PasswordChangeForm(request.user)

    if request.method == "POST" and "salvar_perfil" in request.POST:
        perfil_form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if perfil_form.is_valid():
            perfil_form.save()
            messages.success(request, "Perfil atualizado.")
            return redirect("configuracoes")

    if request.method == "POST" and "trocar_senha" in request.POST:
        senha_form = PasswordChangeForm(request.user, request.POST)
        if senha_form.is_valid():
            user = senha_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada.")
            return redirect("configuracoes")

    return render(
        request,
        "web/configuracoes.html",
        {"perfil_form": perfil_form, "senha_form": senha_form},
    )
