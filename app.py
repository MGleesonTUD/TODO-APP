from flask import Flask, g, request, render_template, redirect, abort, make_response
import sqlite3
import pickle
import base64

app = Flask(__name__)


DATABASE = 'todos.sqlite'


@app.before_first_request
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, name TEXT)')


def encode_username(name):
    obj = pickle.dumps(name)
    return base64.b64encode(obj)


def is_int(obj):
    try:
        return str(int(obj)) == str(obj)
    except ValueError or TypeError:
        return False


def get_todos():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM todos')
        return cur.fetchall()


def add_todo(name):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(f"INSERT INTO todos(name) VALUES ('{name}')")


def update_todo(pk, name):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(f"UPDATE todos SET name = '{name}' WHERE id = {pk}")


def todo_exists(pk):
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute(f"SELECT * FROM todos WHERE id = {pk}").rowcount


def delete_todo(pk):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(f"DELETE FROM todos WHERE id = {pk}")


@app.route('/', methods=['GET'])
def index():
    try:
        token = request.cookies.get('name')
        obj = base64.b64decode(token)
        user_name = str(pickle.loads(obj))
    except:
        user_name = 'User'

    todos = get_todos()

    return render_template('index.html', username=user_name, todos=todos)


@app.route('/new', methods=['POST'])
def new():
    name = request.form['name']

    if len(name.strip()) == 0:
        return redirect('/')

    add_todo(name)
    return redirect('/')


@app.route('/update', methods=['POST'])
def update():
    pk = request.form['pk']
    name = request.form['name']

    if not is_int(pk):
        abort(400)

    print(pk)

    pk = int(pk)

    if not todo_exists(pk):
        abort(404)

    if len(name.strip()) == 0:
        delete_todo(pk)
        return redirect('/')

    update_todo(pk, name)
    return redirect('/')


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


@app.route('/name', methods=['POST'])
def username():
    name = request.form['name']

    if len(name.strip()) == 0:
        name = 'User'

    response = make_response(redirect('/'))
    response.set_cookie('name', encode_username(name))

    return response
