from django.db.models import Count
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import CommentSerializer, PostSerializer


def posts_com_contadores():
    return (
        Post.objects.select_related("author")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .order_by("-created_at")
    )


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return posts_com_contadores()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method == "POST":
            post.likes.add(request.user)
        else:
            post.likes.remove(request.user)
        return Response({"likes_count": post.likes.count()})

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            serializer = CommentSerializer(
                post.comments.select_related("author"), many=True
            )
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return posts_com_contadores().filter(
            author__in=self.request.user.following.all()
        )
