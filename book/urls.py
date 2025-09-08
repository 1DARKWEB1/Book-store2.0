from django.urls import path
from django.http import HttpResponseNotFound
from haystack.views import SearchView
from book.views import (index, admin, add_category, add_book, delete_category, delete_book, admin_list, book_lists,
                        directions, admin_sort, search_books_view, search_page, add_graph, search_books)

urlpatterns = [
    path('', index, name="index"),
    path('admin-page/', admin, name="admin"),
    path('admin-lists/', admin_list, name="lists"),
    path('book-lists/', book_lists, name='books'),
    path('directions/<int:pk>/', directions),
    path('admin_sort/<int:pk>/', admin_sort),
    path('add-category/', add_category),
    path('add-book/', add_book),
    path('delete-book/<int:pk>/', delete_book),
    path('delete-category/<int:pk>/', delete_category),

    #serach function
    path('search/', search_books, name='search_books'),

    path('search_page/', search_page, name='search_page'),
    #path('search/', search_books_view, name='search'),
    path('search_add/', add_graph, name='add_graph'),
    #path('search/ajax/', search_books_view, name='search_ajax'),
]

urlpatterns += [
    path('docs/5.2/', lambda request: HttpResponseNotFound(), name='docs-placeholder'),
]
