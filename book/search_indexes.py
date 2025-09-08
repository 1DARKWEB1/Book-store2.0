from haystack import indexes
from .models import Book


class BookIndex(indexes.SearchIndex, indexes.Indexable):
    # Поле для документа
    text = indexes.CharField(document=True, use_template=True)  # Используется шаблон для текста

    # Поля для индексации
    name = indexes.CharField(model_attr='name')
    category = indexes.CharField(model_attr='category__name')  # Индексация поля category.name

    def get_model(self):
        return Book
