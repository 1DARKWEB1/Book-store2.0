from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    category_img = models.ImageField(upload_to='category_img/', null=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cover = models.ImageField(upload_to='book_covers/')
    book_pdf = models.FileField(upload_to='book_pdfs/')
