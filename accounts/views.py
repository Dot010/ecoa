from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import (
    ChangePasswordSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)
from posts.serializers import PostSerializer
from posts.views import posts_com_contadores


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        return Response({"token": token.key})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    lookup_field = "username"

    def get_queryset(self):
        return User.objects.order_by("username")

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def follow(self, request, username=None):
        alvo = self.get_object()
        if alvo == request.user:
            return Response(
                {"detail": "Você não pode seguir a si mesmo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            request.user.following.add(alvo)
        else:
            request.user.following.remove(alvo)
        return Response(UserSerializer(alvo).data)

    @action(detail=True, methods=["get"])
    def followers(self, request, username=None):
        usuario = self.get_object()
        pagina = self.paginate_queryset(usuario.followers.order_by("username"))
        return self.get_paginated_response(UserSerializer(pagina, many=True).data)

    @action(detail=True, methods=["get"])
    def following(self, request, username=None):
        usuario = self.get_object()
        pagina = self.paginate_queryset(usuario.following.order_by("username"))
        return self.get_paginated_response(UserSerializer(pagina, many=True).data)

    @action(detail=True, methods=["get"])
    def posts(self, request, username=None):
        usuario = self.get_object()
        pagina = self.paginate_queryset(posts_com_contadores().filter(author=usuario))
        serializer = PostSerializer(pagina, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
