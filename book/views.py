from django.shortcuts import render, redirect, HttpResponse

from book.forms import CategoryForm, BookForm
from book.models import Book, Category


# search/views.py
from django.shortcuts import render
from py2neo import Graph, Node, Relationship
from django.db.models import Q


def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(name__icontains=query) |  # поиск по названию книги
        Q(category__name__icontains=query)  # поиск по категории
    )
    return render(request, 'book/search.html', {'books': books, 'query': query})


def search_page(request):
    return render(request, 'book/search.html')


def search_books_and_authors(query):
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "11111111"))

    cypher_query = f"MATCH (b:Book)-[:WRITTEN_BY]-(a:Author) WHERE b.title CONTAINS '{query}' OR a.name CONTAINS '{query}' RETURN b, a LIMIT 20"

    result = graph.run(cypher_query)

    search_results = [record.data() for record in result]

    return search_results


def search_books_view(request):
    query = request.GET.get('query')
    results = search_books_and_authors(query)
    if results:
        return render(request, 'book/search.html', {'results': results, 'query': query})
    else:
        result = "NOT FOUND"
        return render(request, 'book/search.html', {'result': result})


def add_graph(request):
    if request.method == 'POST':
        title = request.POST['title']
        authors = request.POST['authors']
        average_rating = request.POST['average_rating']
        language_code = request.POST['language_code']
        num_pages = request.POST['num_pages']
        ratings_count = request.POST['ratings_count']
        text_reviews_count = request.POST['text_reviews_count']
        publication_date = request.POST['publication_date']

        # Выполняйте необходимые проверки и преобразования данных, если это необходимо

        add_book_to_database(title, authors, average_rating, language_code, num_pages, ratings_count, text_reviews_count, publication_date)

        return redirect('/search_page/')

    return render(request, 'book/search.html')


def add_book_to_database(title, authors, average_rating, language_code, num_pages, ratings_count, text_reviews_count, publication_date):
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "11111111"))

    # Получение текущего максимального bookID
    max_book_id_query = "MATCH (b:Book) RETURN MAX(b.bookID) AS max_book_id"
    result = graph.run(max_book_id_query)
    max_book_id = result.evaluate() or 0

    # Увеличение текущего максимального bookID на единицу
    new_book_id = max_book_id + 1

    create_book_query = f"""
        MERGE (b:Book {{
            bookID: {new_book_id},
            title: '{title}',
            average_rating: {average_rating},
            language_code: '{language_code}',
            num_pages: {num_pages},
            ratings_count: {ratings_count},
            text_reviews_count: {text_reviews_count},
            publication_date: '{publication_date}'
        }})
        WITH b, split('{authors}', '/') AS authors
        UNWIND authors AS author
        MERGE (a:Author {{name: author}})
        MERGE (a)-[:WRITTEN_BY]->(b)
        """

    graph.run(create_book_query)

#end_search_function


def index(request):
    books = Book.objects.all()
    category = Category.objects.all()

    return render(request, 'book/index.html', {'books': books, 'category': category})


def book_lists(request):
    books = Book.objects.all()
    category = Category.objects.all()
    return render(request, 'book/book_lists.html', {'books': books, 'category': category})


def admin(request):
    authenticated = False

    user = {
        'username': 'admin',
        'password': '1234'
    }

    if request.method == "POST":
        if user['username'] == request.POST['username'] and user['password'] == request.POST['password']:
            authenticated = True
        else:
            warning = "Wrong password"
            return render(request, 'book/login.html', {'error': warning})
    if authenticated:
        category_form = CategoryForm()
        book_form = BookForm()
        category_list = Category.objects.all()
        book_list = Book.objects.all()
        return render(request, 'book/admin-page.html', {
            "category_form": category_form,
            "book_form": book_form,
            "category_list": category_list,
            "book_list": book_list,
        })
    else:
        return render(request, 'book/login.html')


def admin_list(request):
    book = Book.objects.all()
    book_form = BookForm()
    return render(request, 'book/admin-lists.html', {'book': book, 'book_form': book_form})


def books(request):
    book = Book.objects.all()
    return render(request, 'book/book_lists.html', {'books': book})


def directions(request, pk):
    book = Book.objects.filter(category=pk)
    book_pdf = Book.objects.all()
    if book:
        return render(request, 'book/book_lists.html', {'books': book})
    else:
        test = "NOT FOUND"
        return render(request, 'book/book_lists.html', {'test': test})


def admin_sort(request, pk):
    book = Book.objects.filter(category=pk)
    book_pdf = Book.objects.all()
    if book:
        return render(request, 'book/admin-lists.html', {'book': book})
    else:
        test = "NOT FOUND"
        return render(request, 'book/admin-lists.html', {'test': test})


def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/admin-page/')
        else:
            return redirect('/admin-page/')


def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/admin-lists/')
        else:
            print(form.errors)
            return redirect('/admin-lists/')


def delete_category(request, pk):
    if request.method == "POST":
        cat = Category.objects.get(id=pk)
        book = Book.objects.filter(category=cat)
        cat.delete()
        book.delete()

        return redirect('/admin-page/')


def delete_book(request, pk):
    if request.method == "POST":
        book = Book.objects.get(id=pk)
        book.delete()

        return redirect('/admin-lists/')



"""
new_book_data = {
    "bookID": 3,
    "title": "New Book Title",
    "authors": "Author3/Author4",
    "average_rating": 4.5,
    "language_code": "eng",
    "num_pages": 400,
    "ratings_count": 1200,
    "text_reviews_count": 70,
    "publication_date": "2/1/2023"
}

# Создание узла книги
new_book_node = Node("Book", **new_book_data)
graph.create(new_book_node)

# Создание узла автора и отношения "АВТОР_КНИГИ"
author_names = new_book_data["authors"].split("/")
for author_name in author_names:
    author_node = Node("Author", name=author_name)
    graph.merge(author_node, "Author", "name")
   graph.create(Relationship(author_node, "AUTHOR_OF", new_book_node))
"""