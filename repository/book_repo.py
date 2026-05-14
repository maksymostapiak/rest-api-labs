from models.book_model import BookModel

_books_db = [
    BookModel(1, "1984", "George Orwell", 1949),
    BookModel(2, "Кобзар", "Тарас Шевченко", 1840)
]

class BookRepository:
    @staticmethod
    def get_all():
        return _books_db

    @staticmethod
    def get_by_id(book_id):
        return next((b for b in _books_db if b.id == book_id), None)

    @staticmethod
    def add(book: BookModel):
        _books_db.append(book)
        return book

    @staticmethod
    def update(book_id, data):
        book = BookRepository.get_by_id(book_id)
        if book:
            if 'title' in data: book.title = data['title']
            if 'author' in data: book.author = data['author']
            if 'year' in data: book.year = data['year']
        return book

    @staticmethod
    def delete(book_id):
        global _books_db
        book = BookRepository.get_by_id(book_id)
        if book:
            _books_db.remove(book)
            return True
        return False

    @staticmethod
    def get_next_id():
        return max([b.id for b in _books_db]) + 1 if _books_db else 1