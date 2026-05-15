import uuid
from repository.book_repo import BookRepository
from schemas.book_schemas import BookSchema


class BookService:
    def __init__(self, db_session):
        self.repo = BookRepository(db_session)

    def get_all_books(self, limit=100, cursor=None, status=None, author=None):
        books = self.repo.get_all(limit, cursor, status, author)
        return BookSchema.serialize_list(books)

    def get_book_by_id(self, book_id_str):
        try:
            book_id = uuid.UUID(book_id_str)
        except ValueError:
            return None 
            
        book = self.repo.get_by_id(book_id)
        return BookSchema.serialize(book)

    def create_book(self, data):
        validation_errors = BookSchema.validate_create(data)
        if validation_errors:
            return None, validation_errors


        book_data = {
            "title": data['title'],
            "author": data['author'],
            "year": data['year'],
            "status": data.get('status', 'available')
        }
        
        created_book = self.repo.add(book_data)
        return BookSchema.serialize(created_book), None

    def update_book(self, book_id_str, data):
        try:
            book_id = uuid.UUID(book_id_str)
        except ValueError:
            return None
            
        updated_book = self.repo.update(book_id, data)
        return BookSchema.serialize(updated_book)

    def delete_book(self, book_id_str):
        try:
            book_id = uuid.UUID(book_id_str)
        except ValueError:
            return False
            
        return self.repo.delete(book_id)