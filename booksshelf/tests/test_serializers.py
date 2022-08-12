from django.contrib.auth.models import User
from django.db.models import Count,Case,When,Avg,F
from rest_framework.test import APITestCase

from booksshelf.models import Book,UserBookRelation
from booksshelf.serializers import BooksSerializer


class BookSerializerTestCase(APITestCase):
    def test_ok(self):
        user = User.objects.create(username="username_test1")
        user2 = User.objects.create(username="username_test2")
        user3 = User.objects.create(username="username_test3")
        book_1 = Book.objects.create(name="Test book 1",price=25,author_name="test", discount=5, owner = user)
        book_2 = Book.objects.create(name="Test book 2",price=55,author_name="test", discount = 10)

        UserBookRelation.objects.create(user=user, book=book_1, like = True,rate=5)
        UserBookRelation.objects.create(user=user2,book=book_1,like=True,rate=5)
        UserBookRelation.objects.create(user=user3,book=book_1,like=True,rate=4)

        UserBookRelation.objects.create(user=user,book=book_2,like=True,rate=3)
        UserBookRelation.objects.create(user=user2,book=book_2,like=True,rate=4)
        UserBookRelation.objects.create(user=user3,book=book_2,like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like = True, then=1))),
            price_with_discount = F('price') - F('discount')
        )
        # books_test = Book.objects.all().annotate(
        #     annotated_likes = Count("userbookrelation__like")
        # )
        data = BooksSerializer(books,many=True).data
        print(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name' : 'test',
                'annotated_likes': 3,
                'annotated_rates': '4.67',
                'price_with_discount': '20.00',
                'owner':'username1'
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'test',
                'annotated_likes': 2,
                'annotated_rates': '3.50',
                'price_with_discount': '45.00',
                'owner': ''
            }
        ]
        print(expected_data)
        self.assertEqual(expected_data,data)
