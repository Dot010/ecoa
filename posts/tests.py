from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from posts.models import Comment, Post


def criar_usuario(username):
    return User.objects.create_user(
        username=username, email=f"{username}@exemplo.com", password="Senha-forte-123"
    )


class BaseApiTest(APITestCase):
    def setUp(self):
        self.ana = criar_usuario("ana")
        self.bruno = criar_usuario("bruno")
        self.carla = criar_usuario("carla")

    def entrar_como(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


class FollowApiTest(BaseApiTest):
    def test_seguir_e_deixar_de_seguir(self):
        self.entrar_como(self.ana)
        url = reverse("user-follow", args=["bruno"])

        self.assertEqual(self.client.post(url).status_code, status.HTTP_200_OK)
        self.assertIn(self.bruno, self.ana.following.all())

        self.assertEqual(self.client.delete(url).status_code, status.HTTP_200_OK)
        self.assertNotIn(self.bruno, self.ana.following.all())

    def test_nao_segue_a_si_mesmo(self):
        self.entrar_como(self.ana)
        response = self.client.post(reverse("user-follow", args=["ana"]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lista_seguidores(self):
        self.ana.following.add(self.bruno)
        response = self.client.get(reverse("user-followers", args=["bruno"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["username"], "ana")


class PostApiTest(BaseApiTest):
    def test_anonimo_nao_publica(self):
        response = self.client.post(
            reverse("post-list"), {"content": "Oi"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publica_como_o_usuario_logado(self):
        self.entrar_como(self.ana)
        response = self.client.post(
            reverse("post-list"), {"content": "Meu primeiro post"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.get().author, self.ana)

    def test_rejeita_post_com_mais_de_280_caracteres(self):
        self.entrar_como(self.ana)
        response = self.client.post(
            reverse("post-list"), {"content": "a" * 281}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_so_o_autor_apaga(self):
        post = Post.objects.create(author=self.ana, content="Post da Ana")
        self.entrar_como(self.bruno)
        response = self.client.delete(reverse("post-detail", args=[post.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=post.id).exists())


class FeedApiTest(BaseApiTest):
    def test_feed_mostra_so_quem_eu_sigo(self):
        Post.objects.create(author=self.bruno, content="Post do Bruno")
        Post.objects.create(author=self.carla, content="Post da Carla")
        self.ana.following.add(self.bruno)
        self.entrar_como(self.ana)

        response = self.client.get(reverse("feed"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        textos = [post["content"] for post in response.data["results"]]
        self.assertEqual(textos, ["Post do Bruno"])

    def test_feed_exige_login(self):
        response = self.client.get(reverse("feed"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InteracaoApiTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.bruno, content="Post do Bruno")

    def test_curtir_e_descurtir(self):
        self.entrar_como(self.ana)
        url = reverse("post-like", args=[self.post.id])

        self.assertEqual(self.client.post(url).data["likes_count"], 1)
        self.assertEqual(self.client.post(url).data["likes_count"], 1)
        self.assertEqual(self.client.delete(url).data["likes_count"], 0)

    def test_mostra_se_eu_curti(self):
        self.post.likes.add(self.ana)
        self.entrar_como(self.ana)
        response = self.client.get(reverse("post-detail", args=[self.post.id]))

        self.assertTrue(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 1)

    def test_comentar_post_de_outra_pessoa(self):
        self.entrar_como(self.ana)
        url = reverse("post-comments", args=[self.post.id])
        response = self.client.post(url, {"content": "Boa!"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.get().author, self.ana)
        self.assertEqual(self.client.get(url).data[0]["content"], "Boa!")

    def test_anonimo_nao_comenta(self):
        url = reverse("post-comments", args=[self.post.id])
        response = self.client.post(url, {"content": "Oi"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
