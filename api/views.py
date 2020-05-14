from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import TitleFilter
from .mixins import ReviewCommentMixin
from .models import Category, Comment, Genre, Review, Title
from .permissions import IsAdmin, IsAdminUserOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer)
from .utils import email_is_valid, generate_mail

User = get_user_model()


class CDLViewSet(mixins.CreateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `destroy()`
    and `list()` actions.
    """
    pass


class GenreViewSet(CDLViewSet):
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]


class CategoryViewSet(CDLViewSet):
    permission_classes = [IsAdminUserOrReadOnly, ]
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUserOrReadOnly, ]
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer

        return TitleWriteSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser | IsAdmin]
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me', url_name='me')
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid()
            serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    email = request.data.get('email')
    if email is None:
        message = 'Email is required'
    else:
        if email_is_valid(email):
            user = get_object_or_404(User, email=email)
            confirmation_code = default_token_generator.make_token(user)
            generate_mail(email, confirmation_code)
            user.confirmation_code = confirmation_code
            message = email
            user.save()
        else:
            message = 'Valid email is required'
    return Response({'email': message})


class ReviewViewSet(ReviewCommentMixin):
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        queryset = Review.objects.filter(title__id=self.kwargs.get('title_id'))

        return queryset


class CommentViewSet(ReviewCommentMixin):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        queryset = Comment.objects.filter(
            review__id=self.kwargs.get('review_id')
        )
        return queryset
