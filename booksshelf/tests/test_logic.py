from django.contrib.auth.models import User
from django.test import TestCase


from booksshelf.logic import set_rating
from booksshelf.models import Book,UserBookRelation


class SetRatingTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username="username_test1")
        user2 = User.objects.create(username="username_test2")
        user3 = User.objects.create(username="username_test3")
        self.book_1 = Book.objects.create(name="Test book 1",price=25,author_name="test",discount=5)
        self.book_2 = Book.objects.create(name="Test book 2",price=55,author_name="test",discount=10)

        UserBookRelation.objects.create(user=user,book=self.book_1,like=True,rate=5)
        UserBookRelation.objects.create(user=user2,book=self.book_1,like=True,rate=5)
        UserBookRelation.objects.create(user=user3,book=self.book_1,like=True,rate=4)

        UserBookRelation.objects.create(user=user,book=self.book_2,like=True,rate=3)
        UserBookRelation.objects.create(user=user2,book=self.book_2,like=True,rate=4)
        UserBookRelation.objects.create(user=user3,book=self.book_2,like=False)


    def test_ok(self):
        set_rating(self.book_1)
        set_rating(self.book_2)
        self.assertEqual(float(4.67),round(self.book_1.rating,2))
        self.assertEqual(float(3.5),round(self.book_2.rating,2))