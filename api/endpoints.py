from flask import request
from flask_restful import Resource
from services.book_service import BookService

class BookListResource(Resource):
    def get(self):
        """
        Отримати список всіх книг
        ---
        tags:
          - Books
        responses:
          200:
            description: Список всіх книг у бібліотеці
        """
        books = BookService.get_all_books()
        return books, 200

    def post(self):
        """
        Додати нову книгу
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: "Тіні забутих предків"
                author:
                  type: string
                  example: "Михайло Коцюбинський"
                year:
                  type: integer
                  example: 1911
        responses:
          201:
            description: Книгу успішно додано
          400:
            description: Помилка валідації
        """
        data = request.get_json()
        new_book, errors = BookService.create_book(data)
        
        if errors:
            return {"message": "Помилка валідації даних", "errors": errors}, 400
            
        return new_book, 201


class BookResource(Resource):
    def get(self, book_id):
        """
        Отримати книгу за ID
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
            description: Унікальний ідентифікатор книги
        responses:
          200:
            description: Дані про книгу
          404:
            description: Книгу не знайдено
        """
        book = BookService.get_book_by_id(book_id)
        if book:
            return book, 200
        return {"message": "Книгу не знайдено"}, 404

    def put(self, book_id):
        """
        Оновити дані існуючої книги
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                author:
                  type: string
                year:
                  type: integer
        responses:
          200:
            description: Книгу успішно оновлено
          404:
            description: Книгу не знайдено
        """
        data = request.get_json()
        book = BookService.update_book(book_id, data)
        if book:
            return book, 200
        return {"message": "Книгу не знайдено"}, 404

    def delete(self, book_id):
        """
        Видалити книгу
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            type: integer
            required: true
        responses:
          200:
            description: Книгу успішно видалено
          404:
            description: Книгу не знайдено
        """
        success = BookService.delete_book(book_id)
        if success:
            return {"message": "Книгу видалено"}, 200
        return {"message": "Книгу не знайдено"}, 404