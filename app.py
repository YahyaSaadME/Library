from flask import Flask,request, jsonify,render_template
from bson.objectid import ObjectId
from datetime import datetime
app = Flask(__name__,template_folder='src')
import pymongo
from bson.json_util import dumps
import os
import json
# Establish a connection to the MongoDB server
client = pymongo.MongoClient("mongodb://yahyasaadme:#Y1a2h3y4a5@ac-8kep9r2-shard-00-00.er1hajy.mongodb.net:27017,ac-8kep9r2-shard-00-01.er1hajy.mongodb.net:27017,ac-8kep9r2-shard-00-02.er1hajy.mongodb.net:27017/library?ssl=true&replicaSet=atlas-z7zirc-shard-0&authSource=admin&retryWrites=true&w=majority")
database = client["library"]
collection = database["users"]
book_collection = database["books"]
# User GET Requests

@app.route('/', methods=['GET'])
def Home():
    return render_template("index.html")

@app.route('/user/signup', methods=['GET'])
def Signup():
    return render_template("signup.html")
@app.route('/user/login', methods=['GET'])
def Login():
    return render_template("login.html")
@app.route('/user/profile', methods=['GET'])
def Profile():
    return render_template("profile.html")

# User POST Requests

@app.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        regno = data.get('regno')
        password = data.get('password')

        if not regno or not password or regno == "" or password == "":
            return jsonify({"msg": "Fill in all details"})

        user = collection.find_one({'regno': regno})
        if user:
            if password == user["password"]:
                return jsonify({"msg": {"name": user['name'], "regno": user['regno'], "password": user["password"],
                                        "_id": str(user['_id'])}})
            else:
                return jsonify({"msg": "regno or password is wrong"})
        else:
            return jsonify({"msg": "regno or password is wrong"}), 401

    except Exception as e:
        return jsonify({"msg": "SMO"}), 500

@app.route('/user/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        regno = data.get('regno')
        password = data.get('password')
        name = data.get('name')

        if not password or not regno or not name:
            return jsonify({"msg": "Fill in all details"})

        # Check if user already exists
        user = collection.find_one({'regno':regno})
        if user!= None:
            return jsonify({"msg": {"created": False, "msg": "User Already Exists"}})
        else:
            user = collection.insert_one({"name":name,"regno":regno,"password":password})
            if user.inserted_id:
                return jsonify({"msg": {"created": True,"name":name,"regno":regno,"password":password,"_id": str(user.inserted_id)}})
            else:
                return jsonify({"msg": {"created": False, "msg": "SMO"}})

    except Exception as e:
        return jsonify({"msg": "SMO"}), 500

@app.route('/user/check', methods=['POST'])
def check_user():
    try:
        id = request.json.get('id')
        user = collection.find_one({'_id':ObjectId(id)})
        if user != None or user:
            return jsonify(dumps({"msg":user})), 200
        else:
            return jsonify(dumps({"msg":"User not exists"})), 200
    except Exception as e:
        return jsonify(dumps({"msg":"SMO"})), 500

@app.route('/user/addbook', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        user_id = data.get('id')
        title = data.get('title')
        author = data.get('author')

        user = collection.find_one({'_id': ObjectId(user_id)})

        added = collection.update_one({'_id': ObjectId(user_id)}, {'$push': {'mybooks': {'title': title, 'date': datetime.now(), 'author': author}}})
        if added:
          return jsonify({'msg': 'Added'}), 200
        else:
            return jsonify({'msg': 'Not Added'}), 404

    except Exception as e:
        return jsonify({'msg': 'Server Error'}), 500

@app.route('/user/removebook', methods=['POST'])
def removebook():
    try:
        data = request.get_json()
        user_id = data.get('id')
        title = data.get('title')

        result = collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$pull': {'mybooks': {'title': title}}}
        )
        if result:
            return jsonify({'msg': 'Book removed'}), 200
        else:
            return jsonify({'msg': 'Book not found or not removed'}), 404

    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500


# Admin GET Requests

@app.route('/admin/yahyasaad', methods=['GET'])
def admin():
    return render_template("admin-index.html")
@app.route('/admin/addbook', methods=['GET'])
def admin_add_book():
    return render_template("add-book.html")

# Admin POST Requests

@app.route('/admin/addbook', methods=['POST'])
def admin_add_book_POST():
    try:
        data = request.get_json()
        title = data.get('title')
        genre = data.get('genre')
        content = data.get('content')
        author = data.get('author')

        added = book_collection.insert_one({'title':title,'genre':genre,'content':content,'author':author})

        if added.inserted_id:
            return jsonify({'msg':"Added"})
        else:
            return jsonify({'msg':"SMO"})


    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

@app.route('/admin/delete', methods=['POST'])
def delete():
    try:
        data = request.get_json()
        book_id = data.get('id')

        result = book_collection.delete_one(
            {'_id': ObjectId(book_id)},
        )
        if result.deleted_count > 0:
            return jsonify({'msg': 'Book removed'}), 200
        else:
            return jsonify({'msg': 'Book not found or not removed'}), 404

    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

@app.route('/admin/update', methods=['POST'])
def updatebooks():
    try:
        data = request.get_json()
        book_id = data.get('id')
        title = data.get('title')
        author = data.get('author')
        content = data.get('content')
        genre = data.get('genre')

        result = book_collection.update_one(
            {'_id': ObjectId(book_id)},
            {'$set':{"title":title,'author':author,"content":content,"genre":genre}}
        )
        if result.modified_count > 0:
            return jsonify({'msg': 'updated'}), 200
        else:
            return jsonify({'msg': 'Book not found or not removed'}), 404

    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500


# Common GET Requests

@app.route('/book', methods=['GET'])
def get_books():
    try:
        books = list(book_collection.find({}))
        # Convert the BSON document to JSON
        books_json = dumps(books)
        return jsonify(dumps({"msg":books})), 200
    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

@app.route('/book/genre', methods=['GET'])
def get_genres():
    try:
        data = book_collection.distinct("genre")  # Assuming BookModal is a MongoDB model
        response_data = {'msg': data}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500


# Common POST Requests

@app.route('/book/search', methods=['POST'])
def search_books():
    try:
        q = request.json.get('q')
        data = book_collection.find({"$text":{"$search":q}})  # Assuming BookModal is a MongoDB model
        all = []
        for i in data:
            all.append(i)

        return jsonify(dumps({'msg':all})), 200
    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

@app.route('/book/bygenre', methods=['POST'])
def get_books_by_genre():
    try:
        q = request.json.get('q')
        data = book_collection.find({"genre":q})  # Assuming BookModal is a MongoDB model

        return jsonify(dumps({'msg':data})), 200
    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

if __name__ == "__main__":
    app.run()