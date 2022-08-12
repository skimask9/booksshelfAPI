from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Book,UserBookRelation


class BookUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username','first_name','last_name')




class BooksSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3,decimal_places=2,read_only=True)
    price_with_discount = serializers.DecimalField(max_digits=7, decimal_places=2 )
    owner = serializers.CharField(read_only=True)
    readers = BookUserSerializer(many=True, read_only=True)
    class Meta:
        model = Book
        fields = ('id','name','price','author_name','annotated_likes','rating','price_with_discount','owner','readers')


class UserBookRelationSerializer(ModelSerializer):

    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate', )