# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "boipotro_final"
mongo = PyMongo(app, config_prefix="MONGO")


class Books(Resource):
    def __init__(self):
        self.collection = mongo.db.boipotro_info_new
        self.data = []
        self.categories_in_store = []

    def get(self, category_books=None, sub_category=None, book_id=None, categories=None ):
        if category_books:
            cursor = self.collection.find({"category": category_books})

            for book in cursor:
                book_id = book.pop("_id")
                book["book_id"] = str(book_id)
                self.data.append(book)

            return jsonify({"categories": category_books, "response": self.data})



        elif categories:

            cursor = self.collection.find({"store": categories})

            for book in cursor:
                if book['category'] not in self.data:
                    self.data.append(book['category'])
                    book_id = book.pop("_id")
                    book["book_id"] = str(book_id)
                    self.data.append(book)


            return jsonify({"Store": categories, "response": self.data})


        elif sub_category:
            cursor = self.collection.find({"sub_category": sub_category})
            for book in cursor:
                book_id = book.pop("_id")
                book["book_id"] = str(book_id)
                self.data.append(book)

            return jsonify({"sub_category": sub_category, "response": self.data})



        elif book_id:
            id = ObjectId(book_id)
            cursor = self.collection.find_one({"_id": id}, {"_id": 0})

            self.data.append(cursor)

            return jsonify({"Book Name": book_id, "response": self.data})



        else:
            cursor = self.collection.find({})

            for book in cursor:

                book_id = book.pop("_id")
                book["book_id"] = str(book_id)
                self.data.append(book)


            return jsonify({"response": self.data})





class Index(Resource):
    def get(self):
        return redirect(url_for("boipotro_info_new"))


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Books, "/api", endpoint="boipotro_info_new")
api.add_resource(Books, "/api/<string:category_books>", endpoint="category_books")
api.add_resource(Books, "/api/store/<string:categories>", endpoint="categories")

api.add_resource(Books, "/api/sub/<string:sub_category>", endpoint="sub_category")
api.add_resource(Books, "/api/book/<string:book_id>", endpoint="book_id")

if __name__ == "__main__":
    app.run(debug=True)