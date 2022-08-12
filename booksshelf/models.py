from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7,decimal_places=2)
    discount = models.PositiveIntegerField(null=True,blank=True)
    # discount_active = models.BooleanField()
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='my_book',blank=True    )
    readers = models.ManyToManyField(User,through="UserBookRelation",related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)


    def __str__(self):
        return self.name

    @property
    def discount_active(self):
        if self.discount > 0:
            discount_price = self.price - self.discount
        return discount_price

class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1,'So-So'),
        (2,'Mehh'),
        (3,'Decent'),
        (4,'Amazing'),
        (5,'NICE'),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES,null=True)

    def __str__(self):
        return f"{self.user.username}: {self.book}, {self.rate}"


    def save(self, *args, **kwargs):
        from booksshelf.logic import set_rating

        creating = not self.pk

        old_rate = self.rate

        super().save(*args,**kwargs)
        new_rating = self.rate
        if old_rate != new_rating or creating:
            set_rating(self.book)