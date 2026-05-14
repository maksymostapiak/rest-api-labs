from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from api.endpoints import BookListResource, BookResource

def create_app():
    app = Flask(__name__)
    api = Api(app)


    app.config['SWAGGER'] = {
        'title': 'Library API (Layered Architecture)',
        'uiversion': 3,
        'description': 'API для управління книгами (Правильна архітектура)'
    }
    swagger = Swagger(app)


    api.add_resource(BookListResource, '/api/books')
    api.add_resource(BookResource, '/api/books/<int:book_id>')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)