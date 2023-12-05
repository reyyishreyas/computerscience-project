from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'bookshop_db',
    'charset': 'utf8mb4',  # Support for emojis
}


db = mysql.connector.connect(**db_config)
cursor = db.cursor()


def create_db():
    cursor.execute('CREATE DATABASE IF NOT EXISTS bookshop_db')
    cursor.execute('USE bookshop_db')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            description TEXT,
            published_date DATE,
            genre VARCHAR(255) NOT NULL DEFAULT ''
        )
    ''')
    db.commit()


def add_book(title, author, genre, description, price, date):
    try:
        cursor.execute("""
            INSERT INTO books (title, author, genre, description, price, published_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, author, genre, description, price, date))
        
        db.commit()
        return "Book added successfully!"
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        pass


def get_books(page, per_page):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    cursor.execute('SELECT * FROM books LIMIT %s, %s', (offset, per_page))
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return books


def get_total_books_count():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return total_books


def get_book_by_id(book_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    cursor.close()
    connection.close()
    return book


def delete_book(book_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    connection.commit()
    cursor.close()
    connection.close()


def update_book(book_id, title, author, price, description, published_date):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            UPDATE books
            SET title=%s, author=%s, price=%s, description=%s, published_date=%s
            WHERE id=%s
        ''', (title, author, price, description, published_date, book_id))
        
        connection.commit()
        return "Book updated successfully!"
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        cursor.close()
        connection.close()


@app.route('/add', methods=['GET'])
def add_form():
    return render_template('add.html')

# Route to handle the form submission for adding a new book
@app.route('/add', methods=['POST'])
def add_book_route():
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    description = request.form['description']
    published_date = request.form['published_date']
    genre = request.form['genre']

    print(f"Received Data: Title={title}, Author={author}, Price={price}, Description={description}, Published Date={published_date}, Genre={genre}")

    result = add_book(title, author, genre, description, price, published_date)
    return redirect(url_for('index'))


create_db()

# Route to display all books with pagination
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_books = get_total_books_count()
    books = get_books(page, per_page)
    return render_template('index.html', books=books, page=page, per_page=per_page, total_books=total_books)

# Route to delete a book
@app.route('/delete/<int:book_id>')
def delete(book_id):
    delete_book(book_id)
    return redirect(url_for('index'))

# Route to edit a book
@app.route('/edit/<int:book_id>')
def edit(book_id):
    book = get_book_by_id(book_id)
    return render_template('edit.html', book=book)

# Route to handle the update form submission
@app.route('/update/<int:book_id>', methods=['POST'])
def update(book_id):
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    description = request.form['description']
    published_date = request.form['published_date']
    update_book(book_id, title, author, price, description, published_date)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
