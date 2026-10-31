import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.models import User
from posts.models import Comment, Post

MEDIA_TESTE = tempfile.mkdtemp()


def criar_usuario(username):
    return User.objects.create_user(
        username=username, email=f"{username}@exemplo.com", password="Senha-forte-123"
    )


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class TelasTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.ana = criar_usuario("ana")
        self.bruno = criar_usuario("bruno")
        self.carla = criar_usuario("carla")

    def test_feed_exige_login(self):
        response = self.client.get(reverse("timeline"))

        self.assertRedirects(
            response, reverse("entrar") + "?next=" + reverse("timeline")
        )

    def test_cadastro_ja_entra_logado(self):
        data = {
            "name": "Diego",
            "username": "diego",
            "email": "diego@exemplo.com",
            "password1": "Senha-forte-123",
            "password2": "Senha-forte-123",
        }
        response = self.client.post(reverse("cadastro"), data)

        self.assertRedirects(response, reverse("timeline"))
        self.assertTrue(User.objects.filter(username="diego").exists())

    def test_feed_mostra_so_quem_eu_sigo(self):
        Post.objects.create(author=self.bruno, content="Post do Bruno")
        Post.objects.create(author=self.carla, content="Post da Carla")
        self.ana.following.add(self.bruno)
        self.client.force_login(self.ana)

        response = self.client.get(reverse("timeline"))

        self.assertContains(response, "Post do Bruno")
        self.assertNotContains(response, "Post da Carla")

    def test_publicar(self):
        self.client.force_login(self.ana)
        self.client.post(reverse("publicar"), {"content": "Olá, Ecoa!"})

        self.assertEqual(Post.objects.get().author, self.ana)

    def test_curtir_e_descurtir(self):
        post = Post.objects.create(author=self.bruno, content="Post do Bruno")
        self.client.force_login(self.ana)

        self.client.post(reverse("curtir", args=[post.id]))
        self.assertIn(self.ana, post.likes.all())

        self.client.post(reverse("curtir", args=[post.id]))
        self.assertNotIn(self.ana, post.likes.all())

    def test_comentar(self):
        post = Post.objects.create(author=self.bruno, content="Post do Bruno")
        self.client.force_login(self.ana)
        self.client.post(reverse("comentar", args=[post.id]), {"content": "Boa!"})

        self.assertEqual(Comment.objects.get().author, self.ana)

    def test_so_o_autor_apaga(self):
        post = Post.objects.create(author=self.bruno, content="Post do Bruno")
        self.client.force_login(self.ana)
        response = self.client.post(reverse("apagar_post", args=[post.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_seguir_e_deixar_de_seguir(self):
        self.client.force_login(self.ana)

        self.client.post(reverse("seguir", args=["bruno"]))
        self.assertIn(self.bruno, self.ana.following.all())

        self.client.post(reverse("seguir", args=["bruno"]))
        self.assertNotIn(self.bruno, self.ana.following.all())

    def test_perfil_mostra_seguidores(self):
        self.ana.following.add(self.bruno)
        response = self.client.get(
            reverse("perfil", args=["bruno"]) + "?aba=seguidores"
        )

        self.assertContains(response, "@ana")

    def test_editar_so_o_nome(self):
        self.client.force_login(self.ana)
        self.client.post(
            reverse("configuracoes"), {"name": "Ana Souza", "salvar_perfil": ""}
        )

        self.ana.refresh_from_db()
        self.assertEqual(self.ana.name, "Ana Souza")
        self.assertEqual(self.ana.bio, "")

    def test_enviar_foto(self):
        imagem = BytesIO()
        Image.new("RGB", (10, 10), "teal").save(imagem, "PNG")
        foto = SimpleUploadedFile(
            "foto.png", imagem.getvalue(), content_type="image/png"
        )
        self.client.force_login(self.ana)
        self.client.post(
            reverse("configuracoes"), {"avatar": foto, "salvar_perfil": ""}
        )

        self.ana.refresh_from_db()
        self.assertTrue(self.ana.avatar.name.startswith("avatars/"))

    def test_trocar_senha(self):
        self.client.force_login(self.ana)
        self.client.post(
            reverse("configuracoes"),
            {
                "old_password": "Senha-forte-123",
                "new_password1": "Outra-senha-456",
                "new_password2": "Outra-senha-456",
                "trocar_senha": "",
            },
        )

        self.ana.refresh_from_db()
        self.assertTrue(self.ana.check_password("Outra-senha-456"))
