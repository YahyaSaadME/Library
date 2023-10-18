from flask import Flask,render_template,request,make_response, jsonify
from bson.objectid import ObjectId
from datetime import datetime
app = Flask(__name__)
import pymongo
from bson.json_util import dumps
import os
# Establish a connection to the MongoDB server

# Establish a connection to the MongoDB server
client = pymongo.MongoClient(os.environ['MONGODB_URI'])
database = client["library"]
collection = database["users"]

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

        if 'mybooks' in user:
            if len(user['mybooks']) < 3:
                book = {'title': title, 'date': datetime.now(), 'author': author}
                collection.update_one({'_id': ObjectId(user_id)}, {'$push': {'mybooks': book}})
                data = book_collection.update_one({'title':title},{"$set":{'taken': True}})
                return jsonify({'msg': 'Added'}), 200
            elif user:
                return jsonify({'msg': '3'}), 200
        elif 'mybooks' not in user:
            collection.update_one({'_id': ObjectId(user_id)}, {'$push': {'mybooks': {'title': title, 'date': datetime.now(), 'author': author}}})
            data = book_collection.update_one({'title': title}, {"$set": {'taken': True}})
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
        if result.modified_count > 0:
            book_collection.update_one({'title': title}, {"$set":{'taken': False}})
            return jsonify({'msg': 'Book removed'}), 200
        else:
            return jsonify({'msg': 'Book not found or not removed'}), 404

    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

@app.route('/', methods=['GET'])
def Home():
    return '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
  </head>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Lexend", sans-serif;
    }
    .search {
      width: 100%;
      flex-wrap: wrap;
      display: flex;
    }
    .search-in-1 {
      width: 100%;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      flex-direction: row;
      margin: 10px 10%;
      border-radius: 5px;
    }
    .search-nav {
      margin-top: -10px;
      /* position: fixed; */
      background-color: white;
    }
    #btn {
      border: none;
      background-color: white;
      outline: none;
      margin-top: 5px;
      margin-right: 10px;
    }
    .ntf {
      width: 300px;
      height: 300px;
    }
    .ntf-div {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }
    .opt {
      border: none;
      outline: none;
      border-radius: 2px;
    }
    .inpts {
      padding: 10px 10px;
      border-radius: 3px;
      border: none;
      font-size: 15px;
      margin: 2px;
      display: inline-block;
      margin: 5px;
      outline: none;
    }
    .head {
      font-size: x-large;
      padding-top: 20px;
      padding-bottom: 10px;
      text-align: center;
    }
    .card {
      padding: 15px;
      box-shadow: 0px 0px 2px -1px black;
    }
  </style>
  <link
    href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
    rel="stylesheet"
  />
  <body>
    <div class="p-5 flex justify-between items-center">
      <h1
        onclick="home()"
        style="text-align: center; cursor: pointer"
        class="text-3xl font-bold tracking-tight text-gray-900"
      >
        Library Manager
      </h1>
      <div id="profile">
        <h5
          onclick="login() "
          style="
            align-self: end;
            background-color: black;
            padding-right: 7px;
            padding-left: 7px;
            cursor: pointer;
          "
          class="p-1 text-white"
        >
          Login
        </h5>
      </div>
    </div>
    <div id="alert"></div>

    <div class="search mt-6 mb-6">
      <div class="search-in-1 shadow">
        <select name="select" id="sel" class="inpts" style="width: 30%">
          <option class="opt" value="categ">Genre</option>
        </select>

        <input
          id="inpts-1"
          class="inpts"
          style="width: 50%"
          type="text"
          placeholder="Enter your value"
        />
        <button id="btn" onclick="searchele()">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-search"
            viewBox="0 0 16 16"
          >
            <path
              d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="flex justify-center lg:justify-left">
      <div
        id="body"
        class="p-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        <div
          onclick="searchele('card-1')"
          href="#"
          class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
        >
          <h5
            class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
          >
            Noteworthy technology acquisitions 2021
          </h5>
          <p class="font-normal text-gray-700 dark:text-gray-400">
            Here are the biggest enterprise technology acquisitions of 2021 so
            far, in reverse chronological order.
          </p>
        </div>
      </div>
      <div id="open"></div>
    </div>

    <script>
    window.onbeforeunload = (e)=>{
        e.preventDefault();
        window.reload()
    }
      const profile = () => {
        window.location.replace("/user/profile");
      };
      function home() {
        window.location.replace("/");
      }
      function login() {
        window.location.replace("/user/login");
      }
      function getCookie(cookieName) {
        const name = cookieName + "=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(";");
        for (let i = 0; i < cookieArray.length; i++) {
          let cookie = cookieArray[i];
          while (cookie.charAt(0) === " ") {
            cookie = cookie.substring(1);
          }
          if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
          }
        }
        return null;
      }
      const user = getCookie("library");
      if (user == null || user == undefined || user == "undefined") {
        window.location.replace("/user/login");
      } else {
        fetch("/user/check", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: user }),
        })
          .then((e) => {
            return e.json();
          })
          .then((e) => {
          e = JSON.parse(e) 
          console.log(e.msg)
          console.log(e.msg != "User not exists" )
          if (e.msg != "User not exists" || e.msg != "SMO"){
            document.getElementById("profile").innerHTML = `
              <h5 onclick="profile()" style="align-self: end; background-color: black; padding-right: 7px; padding-left: 7px; cursor: pointer;" class="p-1 text-white">${e.msg.name}</h5>
                `;
            }
          });
      }
      const allBooks = async () => {
        document.getElementById("body").style.display = null;
        document.getElementById("open").style.display = "none";

        document.getElementById("body").innerHTML = "";

        const books = await fetch("/book", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        let data = JSON.parse(await books.json())
        data.msg.map((e, i) => {
          document.getElementById("body").innerHTML += `
                    <a  onclick='openbook("${e.title}")' href="#title=${
            e.title
          }" class="block max-w-sm p-6 md:p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                      e.title
                    }</h5>
                    <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                    <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                      e.author
                    }</h5>
                    <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                      0,
                      75
                    )}...</p>

                    </a>

                    `;
        });
      };

      async function genre() {
        const data = await fetch("/book/genre", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const e = await data.json();
        e.msg.map((e, i) => {
          document.getElementById("sel").innerHTML += `
                <option class="opt" value=${e}>${e}</option>
                  `;
        });
      }
      genre();

      const searchele = async (e) => {
        if (document.getElementById("inpts-1").value == "") {
          allBooks();
        } else {
          document.getElementById("body").style.display = null;
          document.getElementById("open").style.display = "none";

          const data = await fetch("/book/search", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              q: document.getElementById("inpts-1").value,
            }),
          });
          const e = JSON.parse(await data.json());
          if (e.msg.length == 0) {
            document.getElementById("body").innerHTML = `
                  <h2>No books found</h2>
              `;
          } else {
            e.msg.map((e, i) => {
              document.getElementById("body").innerHTML = "";
              document.getElementById("body").innerHTML += `
                          <a  onclick='openbook("${e.title}")' href="#title=${
                e.title
              }" class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.title
                          }</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.author
                          }</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                            0,
                            75
                          )}...</p>
                      </a>

                          `;
            });
          }
        }
      };

      document.getElementById("sel").addEventListener("change", async (e) => {
        if (document.getElementById("sel").value !== "categ") {
          document.getElementById("body").style.display = null;
          document.getElementById("open").style.display = "none";
          const data = await fetch("/book/bygenre", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ q: document.getElementById("sel").value }),
          });
          const res = JSON.parse(await data.json());
          
          document.getElementById("body").innerHTML = "";
          res.msg.map((e, i) => {
            document.getElementById("body").innerHTML += `
                          <a onclick='openbook("${e.title}")' href="#title=${
              e.title
            }" class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.title
                          }</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.author
                          }</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                            0,
                            75
                          )}...</p>
                          </a>

                          `;
          });
        } else {
          document.getElementById("body").innerHTML = "";
          allBooks();
        }
      });

      document.getElementById("inpts-1").addEventListener("change", (e) => {
        searchele();
      });

      const openbook = async (title) => {
        const data = await fetch("/book/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ q: title }),
        });
        const e = JSON.parse(await data.json());
        document.getElementById("body").style.display = "none";
        document.getElementById("open").style.display = null;
        e.msg.map((e, i) => {
          document.getElementById("open").innerHTML = `
                      <div class='p-8'>
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${e.title}</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${e.author}</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content}</p>
                          ${e.taken==true?"<p class='font-normal text-red-700'>Sorry this book has been already taken</p>":`<button onclick='getbook("${e.title}","${e.author}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700 mt-5">Get Book</button>`}
                          </div>
                          `;
          return;
        });
      };
      allBooks();
      document.getElementById("alert").style.display = null;
      async function getbook(title, author) {
        const res = await fetch("/user/addbook", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: user, title, author }),
        });
        const data = await res.json();
        if (data.msg == "Added") {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                  <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
        <span class="font-medium">Book Added successfully!</span>
      </div>  `;
        } else if (data.msg == "3") {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
        <span class="font-medium">You can't Add more than three books</span>
      </div> `;
        } else {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
        <span class="font-medium">Book Not Added!</span>
      </div> `;
        }
      }
    </script>
  </body>
</html>

'''

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
@app.route('/admin/yahyasaad', methods=['GET'])
def admin():
    return '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
  </head>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Lexend", sans-serif;
    }
    .search {
      width: 100%;
      flex-wrap: wrap;
      display: flex;
    }
    .search-in-1 {
      width: 100%;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      flex-direction: row;
      margin: 10px 10%;
      border-radius: 5px;
    }
    .search-nav {
      margin-top: -10px;
      /* position: fixed; */
      background-color: white;
    }
    #btn {
      border: none;
      background-color: white;
      outline: none;
      margin-top: 5px;
      margin-right: 10px;
    }
    .ntf {
      width: 300px;
      height: 300px;
    }
    .ntf-div {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }
    .opt {
      border: none;
      outline: none;
      border-radius: 2px;
    }
    .inpts {
      padding: 10px 10px;
      border-radius: 3px;
      border: none;
      font-size: 15px;
      margin: 2px;
      display: inline-block;
      margin: 5px;
      outline: none;
    }
    .head {
      font-size: x-large;
      padding-top: 20px;
      padding-bottom: 10px;
      text-align: center;
    }
    .card {
      padding: 15px;
      box-shadow: 0px 0px 2px -1px black;
    }
  </style>
  <link
    href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
    rel="stylesheet"
  />
  <body>
      <h1
        onclick="home()"
        style="text-align: center; cursor: pointer"
        class="text-3xl font-bold tracking-tight text-gray-900 mt-4"
      >
        Library Manager Admin
      </h1>
    <div id="alert"></div>

<div id="alert-2" class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
</div>
    <div class="search mt-6 mb-6">
      <div class="search-in-1 shadow">
        <select name="select" id="sel" class="inpts" style="width: 30%">
          <option class="opt" value="categ">Genre</option>
        </select>

        <input
          id="inpts-1"
          class="inpts"
          style="width: 50%"
          type="text"
          placeholder="Enter your value"
        />
        <button id="btn" onclick="searchele()">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-search"
            viewBox="0 0 16 16"
          >
            <path
              d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"
            />
          </svg>
        </button>
      </div>
    </div>
        <div class="search mt-6 mb-6 flex justify-center">
            <button type="button" onclick="addbookfunc()" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Add New Book</button>
    </div>
    <div class="flex justify-center lg:justify-left">
      <div
        id="body"
        class="p-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8"
      >
      </div>
      <div id="open" style="width:100%"></div>
    </div>

    <script>
      
      function home() {
        window.location.replace("/admin/yahyasaad");
      }
      function addbookfunc(){
        window.location.replace("/admin/addbook");      
      }
      const allBooks = async () => {
        document.getElementById("body").style.display = null;
        document.getElementById("open").style.display = "none";

        document.getElementById("body").innerHTML = "";

        const books = await fetch("/book", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        let data = JSON.parse(await books.json())
        data.msg.map((e, i) => {
          document.getElementById("body").innerHTML += `
                    <a class="block max-w-sm p-6 md:p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                      e.title
                    }</h5>
                    <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                    <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                      e.author
                    }</h5>
                    <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                      0,
                      75
                    )}...</p>
                    <div class="mt-4">
                    <button onclick='openbook("${e.title}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Edit</button>
                    <button onclick='deletebook("${e._id.$oid}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Delete</button>
                    </div>
                    </a>

                    `;
        });
      };


      async function genre(d) {
        const data = await fetch("/book/genre", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const e = await data.json();
        e.msg.map((e, i) => {
            if(e!=null){
          document.getElementById(d).innerHTML += `
                <option class="opt" value=${e}>${e}</option>
                  `;}
        });
      }
      genre("sel");

      const searchele = async (e) => {
        if (document.getElementById("inpts-1").value == "") {
          allBooks();
        } else {
          document.getElementById("body").style.display = null;
          document.getElementById("open").style.display = "none";

          const data = await fetch("/book/search", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              q: document.getElementById("inpts-1").value,
            }),
          });
          const e = JSON.parse(await data.json());
          if (e.msg.length == 0) {
            document.getElementById("body").innerHTML = `
                  <h2>No books found</h2>
              `;
          } else {
            e.msg.map((e, i) => {
              document.getElementById("body").innerHTML = "";
              document.getElementById("body").innerHTML += `
                          <a  onclick='openbook("${e.title}")' href="#title=${
                e.title
              }" class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.title
                          }</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.author
                          }</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                            0,
                            75
                          )}...</p>
                    <div class="mt-4">
                    <button onclick='openbook("${e.title}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Edit</button>
                    <button onclick='deletebook("${e._id.$oid}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Delete</button>
                    </div>
                      </a>

                          `;
            });
          }
        }
      };

      document.getElementById("sel").addEventListener("change", async (e) => {
        if (document.getElementById("sel").value !== "categ") {
          document.getElementById("body").style.display = null;
          document.getElementById("open").style.display = "none";
          const data = await fetch("/book/bygenre", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ q: document.getElementById("sel").value }),
          });
          const res = JSON.parse(await data.json());

          document.getElementById("body").innerHTML = "";
          res.msg.map((e, i) => {
            document.getElementById("body").innerHTML += `
                          <a onclick='openbook("${e.title}")' href="#title=${
              e.title
            }" class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.title
                          }</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                            e.author
                          }</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content.slice(
                            0,
                            75
                          )}...</p>
                          <div class="mt-4">
                    <button onclick='openbook("${e.title}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Edit</button>
                    <button onclick='deletebook("${e._id.$oid}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Delete</button>
                    </div>
                          </a>
                    
                          `;
          });
        } else {
          document.getElementById("body").innerHTML = "";
          allBooks();
        }
      });

      document.getElementById("inpts-1").addEventListener("change", (e) => {
        searchele();
      });

      const openbook = async (title) => {
     
        const data = await fetch("/book/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ q: title }),
        });
        const e = JSON.parse(await data.json());
        document.getElementById("body").style.display = "none";
        document.getElementById("open").style.display = null;
        e.msg.map((e, i) => {
          document.getElementById("open").innerHTML = `
                    <div class='p-8'>
                        <div class="mb-6">
                            <label for="default-input" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Title</label>
                            <input type="text" value="${e.title}" id="title-${e._id.$oid}" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </div>
                        <div class="mb-6">
                        <select name="select" id="sel2" class="inpts">
                            <option class="opt" value="categ">Genre</option>
                        </select>
                        </div>
                        <div class="mb-6">
                            <label for="default-input" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Author</label>
                            <input type="text"  value="${e.author}" id="author-${e._id.$oid}" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </div>
                        <div class="mb-6">
                            <label for="default-input" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Content</label>
                            <textarea type="text" id="content-${e._id.$oid}" rows="10" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        ${e.content}</textarea>
                        </div>                              
                        <button type="button"  onclick='updatebook("${e._id.$oid}")' class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700">Update</button>
                    </div>
                          `;
                          
          return;
        });
         genre("sel2");
      };
        document.getElementById(`alert-2`).style.display = "none"
      
      async function updatebook(id){
      const title = document.getElementById(`title-${id}`).value
      const content = document.getElementById(`content-${id}`).value
      const genre = document.getElementById(`sel2`).value
      const author = document.getElementById(`author-${id}`).value
      const res = await fetch("/admin/update", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: id,title,content,author,genre}),
        });
        const data = await res.json();
        if(data.msg == "updated"){
        document.getElementById(`alert-2`).style.display = null
             document.getElementById(`alert-2`).innerHTML=`
  <span class="font-medium">Updated Successfully!</span>
             `
            
        }else{
        document.getElementById(`alert`).style.display = null
            document.getElementById(`alert`).innerHTML=`
  <span class="font-medium">Not Updated </span>
             `           
        }
      
      }
      allBooks();
      document.getElementById("alert").style.display = null;
      async function getbook(title, author) {
        const res = await fetch("/user/addbook", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: user, title, author }),
        });
        const data = await res.json();
        if (data.msg == "Added") {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                  <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
        <span class="font-medium">Book Added successfully!</span>
      </div>  `;
        } else if (data.msg == "3") {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
        <span class="font-medium">You can't Add more than three books</span>
      </div> `;
        } else {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
        <span class="font-medium">Book Not Added!</span>
      </div> `;
        }
      }
      
          async function deletebook(id){
        const data = await fetch("/admin/delete", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body:JSON.stringify({"id":id})
        });
        const e = await data.json();
        if(e.msg == "Book removed"){
            window.location.reload()
        }else{
            document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
        <span class="font-medium">Book Not Deleted!</span>`
        }
            
    }
      
    </script>
  </body>
</html>

'''

@app.route('/user/signup', methods=['GET'])
def Signup():
    return '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login</title>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
      * {
        font-family: "Lexend", sans-serif;
      }
    </style>
    <link
      href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
      rel="stylesheet"
    />
  </head>
  <body>
    <div
      style="
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        width: 100%;
        height: 100vh;
      "
    >
      <div
        id="alert"
        class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400"
        role="alert"
      >
        <span class="font-medium">Danger alert!</span> Change a few things up
        and try submitting again.
      </div>
      <div
        class="w-full m-2 max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-6 md:p-8 dark:bg-gray-800 dark:border-gray-700"
      >
        <h5 class="text-xl font-medium text-gray-900 dark:text-white">
          Sign Up to Library Manager
        </h5>
        <div>
            <label
              for="name"
              class="block mt-5 mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >
              Your Name
            </label>
            <input
              type="text"
              id="name"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
              placeholder="Ex. Joe"
            />
          </div>
        <div>
          <label
            for="regno"
            class="block mt-5 mb-2 text-sm font-medium text-gray-900 dark:text-white"
          >
            Your Register No
          </label>
          <input
            type="text"
            id="regno"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
            placeholder="RA•••••••••"
          />
        </div>

        <div>
          <label
            for="password"
            class="block mb-2 mt-5 text-sm font-medium text-gray-900 dark:text-white"
          >
            Your password
          </label>
          <input
            type="password"
            id="password"
            placeholder="••••••••"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <button
          onclick="submit()"
          class="w-full mt-5 text-white bg-gray-700 hover:bg-gray-800 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-gray-600 dark:hover:bg-gray-700 dark:focus:ring-gray-800"
        >
          Sign up to your account
        </button>
        <div class="text-sm mt-3 font-medium text-gray-500 dark:text-gray-300">
          Already registered?
          <a
            href="/user/login"
            class="text-gray-700 hover:underline dark:text-gray-500"
          >
            Log in
          </a>
        </div>
      </div>
    </div>
    <script>
    document.title = "Sign Up"
      document.getElementById("alert").style.display = "none";
      const submit = async (e) => {
       try {
          const res = await fetch("/user/signup", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              regno: document.getElementById("regno").value,
              password: document.getElementById("password").value,
              name: document.getElementById("name").value,
            }),
          });
          let data =  await res.json()
          if(data.msg.created == true ){
                    function setCookie(cookieName, cookieValue, daysToExpire) {
    const date = new Date();
    date.setTime(date.getTime() + (daysToExpire * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + "; " + expires + "; path=/";
}
                setCookie('library', data.msg._id, 7);
                window.location.replace("/")
          }else{
          document.getElementById("alert").style.display = null;

            document.getElementById("alert").innerHTML = `
                <span class="font-medium">${data.msg.msg}</span>
                `;
          }
        } catch (error) {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <span class="font-medium">Something Worng</span>
                
                `;
        }
      };
    </script>
  </body>
</html>

    
    '''

@app.route('/user/login', methods=['GET'])
def Login():
    return '''

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login</title>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
      * {
        font-family: "Lexend", sans-serif;
      }
    </style>
    <link
      href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
      rel="stylesheet"
    />
  </head>
  <body>
    <div
      style="
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        width: 100%;
        height: 100vh;
      "
    >
      <div
        id="alert"
        class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400"
        role="alert"
      >
        <span class="font-medium">Danger alert!</span> Change a few things up
        and try submitting again.
      </div>
      <div
        class="w-full m-2 max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-6 md:p-8 dark:bg-gray-800 dark:border-gray-700"
      >
        <h5 class="text-xl font-medium text-gray-900 dark:text-white">
          Login to Library Manager
        </h5>
        <div>
          <label
            for="regno"
            class="block mt-5 mb-2 text-sm font-medium text-gray-900 dark:text-white"
          >
            Your Register No
          </label>
          <input
            type="regno"
            id="regno"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
            placeholder="RA•••••••••"
          />
        </div>
        <div>
          <label
            for="password"
            class="block mb-2 mt-5 text-sm font-medium text-gray-900 dark:text-white"
          >
            Your password
          </label>
          <input
            type="password"
            id="password"
            placeholder="••••••••"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white"
          />
        </div>

        <button
          onclick="submit()"
          class="w-full mt-5 text-white bg-gray-700 hover:bg-gray-800 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-gray-600 dark:hover:bg-gray-700 dark:focus:ring-gray-800"
        >
          Login to your account
        </button>
        <div class="text-sm mt-3 font-medium text-gray-500 dark:text-gray-300">
          Not registered?
          <a
            href="/user/signup"
            class="text-gray-700 hover:underline dark:text-gray-500"
          >
            Create account
          </a>
        </div>
      </div>
    </div>
    <script>
      document.getElementById("alert").style.display = "none";
      const submit = async (e) => {
       try {
          const res = await fetch("/user/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              regno: document.getElementById("regno").value,
              password: document.getElementById("password").value,
            }),
          });
          let data = await res.json()
          if(data.msg == 'regno or password is wrong'){
            document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <span class="font-medium">${data.msg}</span>
                `;
          }else{
          function setCookie(cookieName, cookieValue, daysToExpire) {
    const date = new Date();
    date.setTime(date.getTime() + (daysToExpire * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + "; " + expires + "; path=/";
}
                setCookie('library', data.msg._id, 7);
                window.location.replace("/")
          }
        } catch (error) {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
                <span class="font-medium">Somewent Worng</span>
                `;
        }
      };
    </script>
  </body>
</html>

'''

@app.route('/user/profile', methods=['GET'])
def Profile():
    return '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
  </head>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Lexend", sans-serif;
    }
    .search {
      width: 100%;
      flex-wrap: wrap;
      display: flex;
    }
    .search-in-1 {
      width: 100%;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      flex-direction: row;
      margin: 10px 10%;
      border-radius: 5px;
    }
    .search-nav {
      margin-top: -10px;
      /* position: fixed; */
      background-color: white;
    }
    #btn {
      border: none;
      background-color: white;
      outline: none;
      margin-top: 5px;
      margin-right: 10px;
    }
    .ntf {
      width: 300px;
      height: 300px;
    }
    .ntf-div {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }
    .opt {
      border: none;
      outline: none;
      border-radius: 2px;
    }
    .inpts {
      padding: 10px 10px;
      border-radius: 3px;
      border: none;
      font-size: 15px;
      margin: 2px;
      display: inline-block;
      margin: 5px;
      outline: none;
    }
    .head {
      font-size: x-large;
      padding-top: 20px;
      padding-bottom: 10px;
      text-align: center;
    }
    .card {
      padding: 15px;
      box-shadow: 0px 0px 2px -1px black;
    }
  </style>
  <link
    href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
    rel="stylesheet"
  />
  <body>
    <div class="p-5 flex justify-between items-center">
      <h1
        onclick="home()"
        style="text-align: center; cursor: pointer;"
        class="text-3xl font-bold tracking-tight text-gray-900"
      >
        Library Manager
      </h1>
      <div id="profile">
        <h5
          style="
            align-self: end;
            background-color: black;
            padding-right: 7px;
            padding-left: 7px;
            cursor: pointer;
          "
          class="p-1 text-white"
        >
          Login
        </h5>
      </div>
    </div>

    <div class="p-5">
      <h5
        class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
      >
        Your Books
      </h5>
    </div>

    <div class="flex justify-center">
      <div
        id="body"
        class="p-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        
      </div>
      <div id="nobooks"></div>
      <div id="open"></div>
    </div>

    <script>
      function getCookie(cookieName) {
        const name = cookieName + "=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(";");
        for (let i = 0; i < cookieArray.length; i++) {
          let cookie = cookieArray[i];
          while (cookie.charAt(0) === " ") {
            cookie = cookie.substring(1);
          }
          if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
          }
        }
        return null;
      }
      const user = getCookie("library");
      if (user == null) {
        window.location.replace("/user/login");
      } else {
        fetch("/user/check", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: user }),
        })
          .then((e) => {
            return e.json();
          })
          .then((e) => {
          e = JSON.parse(e)
            document.getElementById("profile").innerHTML = `
        <h5 onclick="logout()" style="align-self: end; background-color: black; padding-right: 7px; padding-left: 7px; cursor: pointer;" class="p-1 text-white">Logout</h5>
          `;
            document.getElementById("body").style.display = null;
            document.getElementById("open").style.display = "none";

            document.getElementById("body").innerHTML = "";
            if (e.msg.mybooks != undefined) {
            if(e.msg.mybooks.length !== 0 ){
              e.msg.mybooks.map((e, i) => {
            let today = new Date().getDate()
            let last = new Date(e.date.$date).getDate()+2
                document.getElementById("nobooks").innerHTML = ""
                document.getElementById("body").innerHTML += `
                <a  onclick='openbook("${e.title}")' style="width:300px" href="#title=${
                  e.title
                }" class="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
                <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${
                  e.title
                }</h5>
                <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${
                  e.author
                }</h5>
                
                <h5 class="mb-2 text-sm font-bold tracking-tight text-white" style='background-color:${(last - today) > 0 ?"green":"red"};padding:5px;text-align:end; width:fit-content'>${
                  last - today
                } Days left</h5>
                
                </a>
                
                `;
              });
            } 
            else {
              document.getElementById("nobooks").innerHTML = `
            <p class="font-normal text-gray-700 dark:text-gray-400 tecxt-center">
            No Books Added.
          </p>
              `;
            }
            }else {
              document.getElementById("nobooks").innerHTML = `
            <p class="font-normal text-gray-700 dark:text-gray-400 text-center">
            No Books Added.
          </p>
              `;
            }
          });
      }
      function logout(){
    const cookies = document.cookie.split('; ');

     for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
          window.location.replace('/user/login')
      }
      
      const openbook = async (title) => {
        const data = await fetch("/book/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ q: title }),
        });
        const e = JSON.parse(await data.json());
        document.getElementById("body").style.display = "none";
        document.getElementById("open").style.display = null;
        e.msg.map((e, i) => {
          document.getElementById("open").innerHTML = `
                      <div class='p-8'>
                          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">${e.title}</h5>
                          <h5 class="mt-2 text-sm font-bold tracking-tight text-gray-500">AUTHOR</h5>
                          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">${e.author}</h5>
                          <p class="font-normal text-gray-700 dark:text-gray-400">${e.content}</p>
                          <button onclick='returnbook("${e.title}")' type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700 mt-5">Return Book</button>
                          </div>
                          `;
         
        });
      };
      
      async function returnbook(title) {
          const res = await fetch("/user/removebook",{
            method:"POST",
            headers:{
              'Content-Type':"application/json"
            },
            body:JSON.stringify({id:user,title})
          })  
          const data = await res.json()
          if(data.msg == "Book removed"){
            window.location.reload()
          }

      }
      
      function home() {
        window.location.replace("/");
      }
    </script>
  </body>
</html>

    
    '''

@app.route('/admin/addbook', methods=['POST'])
def admin_add_book_POST():
    try:
        data = request.get_json()
        title = data.get('title')
        genre = data.get('genre')
        content = data.get('content')
        author = data.get('author')

        added = book_collection.insert_one({'title':title,'genre':genre,'content':content,'taken':False,'author':author})

        if added.inserted_id:
            return jsonify({'msg':"Added"})
        else:
            return jsonify({'msg':"SMO"})


    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500
@app.route('/admin/addbook', methods=['GET'])
def admin_add_book():
    return '''
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Add books</title>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@100;300;400;500;600;700;800;900&display=swap");
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "Lexend", sans-serif;
      }
    </style>
    <link
      href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/flowbite.min.css"
      rel="stylesheet"
    />
  </head>
  <body>
        
    <div style="margin: 20px">
      <h1
        onclick="home()"
        style="text-align: center; cursor: pointer;"
        class="text-3xl font-bold tracking-tight text-gray-900"
      >
        Library Manager Admin
      </h1>
      <div
        id="alert"
        class="p-4 mb-4 mt-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400"
        role="alert"
      ></div>
      <div id="success" class="p-4 mt-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
        <span class="font-medium">Success alert!</span> Change a few things up and try submitting again.
      </div>
      <label
        for="default-input"
        class="block mb-2 mt-6 text-sm font-medium text-gray-900 dark:text-white"
        >Enter Title</label
      >
      <input
        type="text"
        id="title"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      />
      <label
        for="default-input"
        class="block mb-2 mt-6 text-sm font-medium text-gray-900 dark:text-white"
        >Enter Author Name</label
      >
      <input
        type="text"
        id="author"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      />
      <label
        for="title"
        class="block mb-2 mt-6 text-sm font-medium text-gray-900 dark:text-white"
        >Select an Gerne</label
      >
      <select
        id="sel"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      >
        <option value="categ">Choose a gerne</option>
      </select>
      <label
        for="message"
        class="block mb-2 mt-6 text-sm font-medium text-gray-900 dark:text-white"
        >Your Content</label
      >
      <textarea
        id="content"
        rows="4"
        class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        placeholder="Write your thoughts here..."
      ></textarea>
      <button
        type="button"
        onclick="add()"
        class="mt-6 text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700"
      >
        Add
      </button>
    </div>
    <script>
          function home() {
        window.location.replace("/admin");
      }
      async function genre() {
        const data = await fetch("/book/genre", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const e = await data.json();
        e.msg.map((e, i) => {
          document.getElementById("sel").innerHTML += `
                <option class="opt" value=${e}>${e}</option>
                  `;
        });
      }
      genre();

      document.getElementById("alert").style.display = "none";
      document.getElementById("success").style.display = "none";
      async function add() {
        const title = document.getElementById("title").value;
        const content = document.getElementById("content").value;
        const genre = document.getElementById("sel").value;
        const author = document.getElementById("author").value;
        if (title == "" || content == "" || genre == "categ" || author == "") {
          document.getElementById("alert").style.display = null;
          document.getElementById("alert").innerHTML = `
            <span class="font-medium">Please fill all the details!</span> 
                `;
        } else {
          const send = await fetch("/admin/addbook", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, content, genre,author }),
          });
          const res = await send.json();
          if (res.msg == "SMO") {
            document.getElementById("alert").style.display = null;
            document.getElementById("alert").innerHTML = `
    
            <span class="font-medium">Something went wrong!</span> 
                `;
          } else {
            document.getElementById("success").style.display = null;
            document.getElementById("success").innerHTML = `
    
            <span class="font-medium">Added Successfully</span> 
                `;
          }
        }
      }
    </script>
  </body>
</html>

    
    '''

book_collection = database["books"]
@app.route('/book', methods=['GET'])
def get_books():
    try:
        books = list(book_collection.find({}))
        # Convert the BSON document to JSON
        books_json = dumps(books)
        return jsonify(dumps({"msg":books})), 200
    except Exception as e:
        return jsonify({'msg': 'SMO'}), 500

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

@app.route('/book/genre', methods=['GET'])
def get_genres():
    try:
        data = book_collection.distinct("genre")  # Assuming BookModal is a MongoDB model
        response_data = {'msg': data}
        return jsonify(response_data), 200
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