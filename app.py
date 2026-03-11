from flask import Flask, render_template, request, redirect, url_for

from db_module import (
    add_book, show_all_books, issue_book, return_book,
    init_database, add_reader, delete_book,
    delete_reader, show_active_loans, show_all_readers
)

app = Flask(__name__)
init_database()


# --- Маршрут для отображения всех книг ---
@app.route('/')
def index():
    books = show_all_books()
    return render_template('index.html', books=books)


# --- Маршрут для добавления книги (GET - показать форму, POST - обработать форму) ---
@app.route('/add_book', methods=['GET', 'POST'])
def add_book_page():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        try:
            copies = int(request.form.get('copies') or 1)
        except ValueError:
            copies = 1

        add_book(title, author, genre, copies)
        return redirect(url_for('index'))

    return render_template('add_book_form.html')


# --- Маршрут для выдачи книги ---
@app.route('/issue', methods=['GET', 'POST'])
def issue():
    if request.method == 'POST':
        try:
            book_id = int(request.form['book_id'])
            reader_id = int(request.form['reader_id'])
            if issue_book(book_id, reader_id):
                # Успех
                pass
            else:
                # Ошибка
                pass
            return redirect(url_for('active_loans'))
        except ValueError:
            # Ошибка ввода
            pass

    readers = show_all_readers()
    books = show_all_books()
    return render_template('issue_form.html', readers=readers, books=books)


# --- Роут для отображения ВСЕХ активных займов (только просмотр) ---
@app.route('/active_loans')
def active_loans():
    active = show_active_loans()
    # Этот шаблон будет просто отображать список, без кнопок возврата (по желанию)
    return render_template('active_loans.html', active_loans=active)


# --- Роут для выбора возврата (отображение + форма) ---
@app.route('/return_selection', methods=['GET'])
def return_selection_page():
    active_loans = show_active_loans()
    # Используем return_form.html (где есть кнопка отправки формы возврата)
    return render_template('return_form.html', active_loans=active_loans)


# --- Роут для обработки возврата (Принимает Loan ID) ---
@app.route('/process_return/<int:loan_id>', methods=['POST'])
def process_return(loan_id):
    return_book(loan_id)
    # Перенаправляем на страницу выбора возврата, чтобы обновить список
    return redirect(url_for('return_selection_page'))


# Создаем маршрут для отображения списка читателей
@app.route('/readers', methods=['GET'])
def manage_readers_page():
    readers = show_all_readers()
    return render_template('readers.html', readers=readers)


# Маршрут для добавления читателя (POST)
@app.route('/add_reader', methods=['POST'])
def add_reader_route():
    name = request.form['name']
    class_group = request.form['class_group']
    student_id = request.form['student_id']
    add_reader(name, class_group, student_id)
    return redirect(url_for('manage_readers_page'))


# Маршрут для удаления читателя
@app.route('/delete_reader/<int:reader_id>', methods=['POST'])
def delete_reader_route(reader_id):
    delete_reader(reader_id)
    return redirect(url_for('manage_readers_page'))


# Функция для удаления книги
@app.route('/delete_book/<int:book_id>', methods=['POST'])
def book_delete_action(book_id):
    delete_book(book_id)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
