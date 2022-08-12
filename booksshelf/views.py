from django.db.models import Count,Case,When,Avg,F,CharField,Value,Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter,SearchFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet,GenericViewSet

from booksshelf.models import Book,UserBookRelation
from booksshelf.permissions import IsOwnerOrStaffOrReadOnly
from booksshelf.serializers import BooksSerializer,UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.annotate(
        annotated_likes=Count(Case(When(userbookrelation__like = True, then =1))),
        price_with_discount=F('price') - F('discount'),
        # owner_name = F('owner__username')
    ).prefetch_related('readers').select_related('owner')
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['price',]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    search_fields = ['name','author_name']
    ordering_fields = ['price','author_name','price_with_discount']

    def perform_create(self,serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationViewSet(GenericViewSet,UpdateModelMixin):
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'book'

    def get_object(self):
        obj,_ = UserBookRelation.objects.get_or_create(user=self.request.user,book_id=self.kwargs['book'])

        return obj


def index(request):
    booksprice = Book.objects.annotate(status=Case(When(Q(price__lte=100),then=Value("cheap")),
                                                   When(Q(price__gte=100) & Q(price__lte=500),then=Value("middle")),
                                                   When(Q(price__gte=500),then=Value("expensive")),
                                                   output_field=CharField()))
    return render(request,"booksshelf/index.html",{"booksprice":booksprice})
