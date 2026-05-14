class BookSchema:
    @staticmethod
    def serialize(book):
        """Серіалізація об'єкта SQLAlchemy у словник (для JSON)"""
        if not book:
            return None
        return {
            "id": str(book.id),
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "status": book.status
        }

    @staticmethod
    def serialize_list(books):
        """Серіалізація списку об'єктів"""
        return [BookSchema.serialize(book) for book in books]

    @staticmethod
    def validate_create(data):
        """Валідація вхідних даних при створенні"""
        errors = {}
        if not data:
            return {"error": "Тіло запиту порожнє"}
        if "title" not in data or not isinstance(data["title"], str):
            errors["title"] = "Поле 'title' обов'язкове (рядок)"
        if "author" not in data or not isinstance(data["author"], str):
            errors["author"] = "Поле 'author' обов'язкове (рядок)"
        if "year" not in data or not isinstance(data["year"], int):
            errors["year"] = "Поле 'year' обов'язкове (число)"
        return errors if errors else None