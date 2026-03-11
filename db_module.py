import sqlite3
from datetime import datetime
DB_NAME = "school_library.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def show_all_readers():
    """Возвращает список всех читателей в базе данных."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, student_id, class_group FROM readers")
    rows = cursor.fetchall()
    conn.close()
    return rows


def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            total_copies INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_group TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            reader_id INTEGER,
            loan_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (reader_id) REFERENCES readers(id)
        )
    """)
    conn.commit()
    conn.close()


def add_book(title, author, genre, copies=1):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Проверить, существует ли книга
    cursor.execute("SELECT id, total_copies, available_copies FROM books WHERE title = ? AND author = ?",
                   (title, author))
    existing_book = cursor.fetchone()

    if existing_book:
        new_total = existing_book['total_copies'] + copies
        new_available = existing_book['available_copies'] + copies
        cursor.execute("""
            UPDATE books SET total_copies = ?, available_copies = ? WHERE id = ?
        """, (new_total, new_available, existing_book['id']))
    else:
        # 2. Если нет, вставить новую
        cursor.execute("""
            INSERT INTO books (title, author, genre, total_copies, available_copies)        
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, genre, copies, copies))

    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, есть ли активные займы для этой книги
    cursor.execute("SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_date IS NULL", (book_id,))
    active_loans_count = cursor.fetchone()[0]

    if active_loans_count > 0:
        print(f"Ошибка: Невозможно удалить книгу ID {book_id}. Есть {active_loans_count} активных займов.")
        conn.close()
        return False

    # Если займов нет, удаляем
    try:
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Книга с ID {book_id} успешно удалена.")
            return True
        else:
            print(f"Книга с ID {book_id} не найдена.")
            return False
    except Exception as e:
        print(f"Произошла ошибка при удалении книги: {e}")
        return False
    finally:
        conn.close()


def add_reader(name, class_group, student_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO readers (name, class_group, student_id)
            VALUES (?, ?, ?)
        """, (name, class_group, student_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def issue_book(book_id, reader_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT available_copies FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book or book['available_copies'] <= 0:
        conn.close()
        return False
    loan_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO loans (book_id, reader_id, loan_date)
        VALUES (?, ?, ?)
    """, (book_id, reader_id, loan_date))
    cursor.execute("""
        UPDATE books SET available_copies = available_copies - 1 WHERE id = ?
    """, (book_id,))
    conn.commit()
    conn.close()
    return True


def return_book(loan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, return_date FROM loans WHERE id = ?", (loan_id,))
    loan = cursor.fetchone()
    if not loan or loan['return_date']:
        conn.close()
        return False
    return_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        UPDATE loans SET return_date = ? WHERE id = ?    """, (return_date, loan_id))
    cursor.execute("""
        UPDATE books SET available_copies = available_copies + 1 WHERE id = ?
    """, (loan['book_id'],))
    conn.commit()
    conn.close()
    return True


def delete_reader(reader_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, есть ли активные займы для этого читателя
    cursor.execute("SELECT COUNT(*) FROM loans WHERE reader_id = ? AND return_date IS NULL", (reader_id,))
    active_loans_count = cursor.fetchone()[0]

    if active_loans_count > 0:
        print(f"Ошибка: Невозможно удалить читателя ID {reader_id}. У него {active_loans_count} невозвращенных книг.")
        conn.close()
        return False

    # Если займов нет, удаляем
    try:
        cursor.execute("DELETE FROM readers WHERE id = ?", (reader_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Читатель с ID {reader_id} успешно удален.")
            return True
        else:
            print(f"Читатель с ID {reader_id} не найден.")
            return False
    except Exception as e:
        print(f"Произошла ошибка при удалении читателя: {e}")
        return False
    finally:
        conn.close()


def show_all_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    return rows


def show_active_loans():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.id, b.title, r.name, r.class_group, l.loan_date
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN readers r ON l.reader_id = r.id
        WHERE l.return_date IS NULL
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows
