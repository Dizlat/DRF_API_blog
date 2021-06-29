from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet

from .models import *
from .permissions import IsAuthorPerm
from .serializers import *


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return self.serializer_class

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorPerm() ]
        elif self.action in ['create_comment', 'create']:
            return [IsAuthenticated() ]
        return []

    @action(detail=True, methods=['POST'])
    def create_comment(self, request, pk):
        data = request.data.copy()
        data['post'] = pk
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostImageViewSet(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPerm, ]
        else:
            permissions = []
        return [permission() for permission in permissions]


# class CommentViewSet(mixins.CreateModelMixin,
#                      mixins.UpdateModelMixin,
#                      mixins.DestroyModelMixin,
#                      GenericViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#
#     def get_permissions(self):
#         if self.action == 'create':
#             return [IsAuthenticated, ]
#         return [IsAuthorPerm, ]




