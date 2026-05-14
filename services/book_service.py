from repository.book_repo import BookRepository
from models.book_model import BookModel
from schemas.book_schema import BookSchema

class BookService:
    @staticmethod
    def get_all_books():
        books = BookRepository.get_all()
        return BookSchema.serialize_list(books)

    @staticmethod
    def get_book_by_id(book_id):
        book = BookRepository.get_by_id(book_id)
        return BookSchema.serialize(book)

    @staticmethod
    def create_book(data):

        validation_errors = BookSchema.validate_create(data)
        if validation_errors:
            return None, validation_errors

        new_id = BookRepository.get_next_id()
        new_book = BookModel(new_id, data['title'], data['author'], data['year'])
        
        created_book = BookRepository.add(new_book)
        return BookSchema.serialize(created_book), None

    @staticmethod
    def update_book(book_id, data):
        updated_book = BookRepository.update(book_id, data)
        return BookSchema.serialize(updated_book)

    @staticmethod
    def delete_book(book_id):
        return BookRepository.delete(book_id)