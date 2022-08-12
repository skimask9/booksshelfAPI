import json

from django.contrib.auth.models import User
from django.db.models import When,Case,Count,Avg,F
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from booksshelf.models import Book,UserBookRelation
from booksshelf.serializers import BooksSerializer,UserBookRelationSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="username_test")
        self.book_1 = Book.objects.create(name="Test book 1",price=25,author_name='Author 1',owner=self.user,discount=5)
        self.book_2 = Book.objects.create(name="Test book 2",price=55,author_name='Buthor 5',discount=10)
        self.book_3 = Book.objects.create(name="Test book Author ",price=55,author_name='Cuthor 2',discount=15)

        UserBookRelation.objects.create(user=self.user, book = self.book_1, like = True, rate =5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes = Count(Case(When(userbookrelation__like = True, then = 1))),
            price_with_discount=F('price') - F('discount')
        )
        serializer_data = BooksSerializer(books,many=True).data
        print(serializer_data)
        print(response.data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.assertEqual(serializer_data,response.data)
    #
    # def test_get_detail(self):
    #     url = reverse('book-detail',args=(self.book_1.id,))
    #     response = self.client.get(url)
    #     self.client.force_login(self.user)
    #     books = Book.objects.filter(id__in=[self.book_1.id,]).annotate(
    #         annotated_likes=Count(Case(When(userbookrelation__like=True,then=1)))
    #     )
    #     serializer_data = BooksSerializer(books,).data
    #     print(serializer_data)
    #     print(response.data)
    #     self.assertEqual(status.HTTP_200_OK,response.status_code)
    #     self.assertEqual(serializer_data,response.data)

    def test_get_detail_readonly(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK,response.status_code)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url,data={'search': 'Author'})
        books = Book.objects.filter(id__in=[self.book_1.id,self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True,then=1))),
            price_with_discount=F('price') - F('discount')
        )
        serializer_data = BooksSerializer(books,many=True).data
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.assertEqual(serializer_data,response.data)

    # def test_get_ordering_by_name(self):
    #     url = reverse('book-list')
    #     response = self.client.get(url,data={'ordering': "author_name"})
    #     books = Book.objects.all().annotate(
    #         annotated_likes=Count(Case(When(userbookrelation__like=True,then=1))),
    #         annotated_rates=Avg("userbookrelation__rate"),
    #         price_with_discount=F('price') - F('discount')
    #     )
    #     serializer_data = BooksSerializer(books,many=True).data
    #     self.assertEqual(status.HTTP_200_OK,response.status_code)
    #     self.assertEqual(serializer_data,response.data)

    # def test_get_ordering_by_discount(self):
    #     url = reverse('book-list')
    #     response = self.client.get(url,data={'ordering': "price_with_discount"})
    #     books = Book.objects.all().annotate(
    #         annotated_likes=Count(Case(When(userbookrelation__like=True,then=1))),
    #         annotated_rates=Avg("userbookrelation__rate"),
    #         price_with_discount=F('price') - F('discount')
    #     )
    #     serializer_data = BooksSerializer(books,many=True).data
    #     print(serializer_data)
    #     print(response.data)
    #     self.assertEqual(status.HTTP_200_OK,response.status_code)
    #     self.assertEqual(serializer_data,response.data)


    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url,data={'price': 55})
        books = Book.objects.filter(price__in=[self.book_2.price]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True,then=1))),
            price_with_discount=F('price') - F('discount')
        )
        serializer_data = BooksSerializer(books,many=True).data
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.assertEqual(serializer_data,response.data)

    def test_post_create(self):
        url = reverse('book-list')
        data = {
            "name": "Test Post",
            "price": 150.00,
            "author_name": "Test Author"
        }
        # json_data = json.dumps(data)
        # print(json_data)
        self.client.force_login(self.user)
        response = self.client.post(url,data=data)
        print(response)
        self.assertEqual(status.HTTP_201_CREATED,response.status_code)
        self.assertEqual(4,Book.objects.all().count())
        self.assertEqual(self.user,Book.objects.last().owner)

    def test_post_create_notlogin(self):
        url = reverse('book-list')
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST,response.status_code)

    def test_post_update(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        self.client.force_login(self.user)
        response = self.client.put(url,data=data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575,self.book_1.price)

    def test_post_update_notowner(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        self.user2 = User.objects.create(username="username_test2")
        self.client.force_login(self.user2)
        response = self.client.put(url,data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN,response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(25,int(self.book_1.price))

    # def test_post_update_notowner_but_stuff(self):
    #     url = reverse('book-detail',args=(self.book_1.id,))
    #     data = {
    #         "price": 575,
    #     }
    #     self.user2 = User.objects.create(username="username_test2",is_staff=True)
    #     self.client.force_login(self.user2)
    #     response = self.client.put(url,data=data)
    #     self.book_1.refresh_from_db()
    #     self.assertEqual(575,int(self.book_1.price))

    def test_post_update_notlogin(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        response = self.client.put(url,data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN,response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(25,self.book_1.price)

    def test_post_delete(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT,response.status_code)
        self.assertEqual(2,Book.objects.all().count())

    def test_post_delete_notowner(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        self.user2 = User.objects.create(username="username_test2")
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN,response.status_code)
        self.assertEqual(3,Book.objects.all().count())

    def test_post_delete_notlogin(self):
        url = reverse('book-detail',args=(self.book_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN,response.status_code)
        self.assertEqual(3,Book.objects.all().count())




class UserBookRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="username_test")
        self.user2 = User.objects.create(username="username_test2")
        self.book_1 = Book.objects.create(name="Test book 1",price=25,author_name='Author 1',owner=self.user)
        self.book_2 = Book.objects.create(name="Test book 2",price=55,author_name='Buthor 5')

    def test_post_patch_like(self):
        url = reverse('userbookrelation-detail',args=(self.book_1.id,))
        data = {
            "like" : True,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url,data=data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,book=self.book_1)
        self.assertTrue(relation.like)

    def test_post_patch_dislike(self):
        url = reverse('userbookrelation-detail',args=(self.book_1.id,))
        data = {
            "like" : True,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url,data=data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            "like": False,
        }
        response = self.client.patch(url,data=data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,book=self.book_1)
        self.book_1.refresh_from_db()
        self.assertFalse(relation.like)

    def test_post_patch_in_bookmark(self):
        url = reverse('userbookrelation-detail',args=(self.book_1.id,))
        data = {
            "in_bookmarks": True,
        }
        self.client.force_login(self.user)
        response = self.client.patch(url,data=data)
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail',args=(self.book_1.id,))

        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url,data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3,relation.rate)