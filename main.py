from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from models.database import SessionLocal, engine, Base
from api.books import BookListResource, BookResource
from services.book_service import BookService

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
api = Api(app)

app.config['SWAGGER'] = {
    'title': 'Library API',
    'uiversion': 3
}
swagger = Swagger(app)

api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True)