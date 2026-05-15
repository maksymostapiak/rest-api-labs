from flask import request, jsonify
from flask_restful import Resource
import uuid

from database import SessionLocal
from book_service import BookService

class BookListResource(Resource):
    def get(self):
        """
        Отримати список книг (з пагінацією)
        ---
        tags:
          - Books
        parameters:
          - name: limit
            in: query
            type: integer
            default: 10
            description: Кількість записів на сторінку
          - name: cursor
            in: query
            type: string
            description: ID останньої книги з попередньої сторінки (UUID)
          - name: status
            in: query
            type: string
            enum: ['наявні в бібліотеці', 'видані комусь']
          - name: author
            in: query
            type: string
        responses:
          200:
            description: Список книг та курсор
        """
        db = SessionLocal()
        try:
            service = BookService(db)
            limit = int(request.args.get('limit', 10))
            cursor = request.args.get('cursor')
            status = request.args.get('status')
            author = request.args.get('author')

            books = service.get_all_books(limit=limit, cursor=cursor, status=status, author=author)
            
            next_cursor = books[-1]['id'] if books and len(books) == limit else None
            
            return jsonify({"items": books, "next_cursor": next_cursor})
        except Exception as e:
            return {"message": str(e)}, 400
        finally:
            db.close()

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
              required:
                - title
                - author
                - year
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
                status:
                  type: string
                  enum: ['наявні в бібліотеці', 'видані комусь']
                  default: 'наявні в бібліотеці'
        responses:
          201:
            description: Книгу успішно додано
          400:
            description: Помилка валідації
        """
        data = request.get_json()
        db = SessionLocal()
        try:
            service = BookService(db)
            new_book, errors = service.create_book(data)
            
            if errors:
                return {"message": "Помилка валідації даних", "errors": errors}, 400
                
            return new_book, 201
        except Exception as e:
            return {"message": str(e)}, 400
        finally:
            db.close()


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
            type: string
            required: true
            description: Унікальний ідентифікатор книги (UUID)
        responses:
          200:
            description: Дані про книгу
          404:
            description: Книгу не знайдено
        """
        db = SessionLocal()
        try:
            service = BookService(db)
            book = service.get_book_by_id(book_id)
            if book:
                return book, 200
            return {"message": "Книгу не знайдено"}, 404
        finally:
            db.close()

    def put(self, book_id):
        """
        Оновити дані існуючої книги
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            type: string
            required: true
            description: Унікальний ідентифікатор книги (UUID)
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
        db = SessionLocal()
        try:
            service = BookService(db)
            book = service.update_book(book_id, data)
            if book:
                return book, 200
            return {"message": "Книгу не знайдено"}, 404
        finally:
            db.close()

    def delete(self, book_id):
        """
        Видалити книгу
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            type: string
            required: true
            description: Унікальний ідентифікатор книги (UUID)
        responses:
          200:
            description: Книгу успішно видалено
          404:
            description: Книгу не знайдено
        """
        db = SessionLocal()
        try:
            service = BookService(db)
            success = service.delete_book(book_id)
            if success:
                return {"message": "Книгу видалено"}, 200
            return {"message": "Книгу не знайдено"}, 404
        finally:
            db.close()