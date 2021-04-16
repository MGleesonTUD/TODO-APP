from flask import Flask, request, render_template, redirect, abort, make_response
import sqlite3
import pickle
import base64

app = Flask(__name__)


DATABASE = 'todos.sqlite'


# ENSURE DATABASE/TABLE EXISTS ON STARTUP
@app.before_first_request
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, name TEXT)')


# SERIALIZE AND BASE64 ENCODE A STRING
def encode_username(name):
    obj = pickle.dumps(name)
    return base64.b64encode(obj)


# VALIDATE THAT AN OBJECT IS A CORRECTLY FORMATTED INTEGER
def is_int(obj):
    try:
        return str(int(obj)) == str(obj)
    except ValueError or TypeError:
        return False


# RETRIEVE ALL ITEMS FROM THE DATABASE
def get_todos():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM todos')
        return cur.fetchall()


# ADD A NEW ITEM TO THE DATABASE
def add_todo(name):
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(f"INSERT INTO todos(name) VALUES ('{name}');")
        conn.commit()


# UPDATE AN EXISTING ITEM IN THE DATABASE
def update_todo(pk, name):
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(f"UPDATE todos SET name = '{name}' WHERE id = {pk};")
        conn.commit()


# CHECK IF AN ITEM WITH A PROVIDED PRIMARY KEY EXISTS
def todo_exists(pk):
    with sqlite3.connect(DATABASE) as conn:
        return conn.executescript(f"SELECT * FROM todos WHERE id = {pk};").rowcount


# DELETE AN ITEM FROM THE DATABASE
def delete_todo(pk):
    with sqlite3.connect(DATABASE) as conn:
        conn.executescript(f"DELETE FROM todos WHERE id = {pk};")
        conn.commit()


# SERVE THE MAIN PAGE
@app.route('/', methods=['GET'])
def index():
    # ATTEMPT TO BASE64 DECODE AND DESERIALIZE USERNAME FROM COOKIE, DEFAULT TO 'User' UPON FAILURE
    try:
        token = request.cookies.get('name')
        obj = base64.b64decode(token)
        user_name = str(pickle.loads(obj))
    except:
        user_name = 'User'

    todos = get_todos()

    return render_template('index.html', username=user_name, todos=todos)


# POST HANDLER TO CREATE NEW ITEM
@app.route('/new', methods=['POST'])
def new():
    name = request.form['name']

    if len(name.strip()) == 0:
        return redirect('/')

    add_todo(name)
    return redirect('/')


# POST HANDLER TO UPDATE EXISTING ITEM
@app.route('/update', methods=['POST'])
def update():
    pk = request.form['pk']
    name = request.form['name']

    if not is_int(pk):
        abort(400)

    pk = int(pk)

    if not todo_exists(pk):
        abort(404)

    # DELETE INSTEAD IF NEW INPUT IS BLANK
    if len(name.strip()) == 0:
        delete_todo(pk)
        return redirect('/')

    update_todo(pk, name)
    return redirect('/')


# POST HANDLER TO DELETE AN EXISTING ITEM
@app.route('/delete', methods=['POST'])
def delete():
    pk = request.form['pk']

    if not is_int(pk):
        abort(400)

    pk = int(pk)

    if not todo_exists(pk):
        abort(404)

    delete_todo(pk)
    return redirect('/')


# POST HANDLER TO UPDATE USERNAME IN THE COOKIE
@app.route('/name', methods=['POST'])
def username():
    name = request.form['name']

    # DEFAULT TO 'User' IF INPUT IS BLANK
    if len(name.strip()) == 0:
        name = 'User'

    response = make_response(redirect('/'))
    response.set_cookie('name', encode_username(name))

    return response
