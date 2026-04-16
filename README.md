# School Library Database

A web-based management system for school libraries designed to track book collections, reader data, and book loan processes.

## Features
- **Book Catalog:** Add, view, and manage book copies.
- **Reader Management:** Register students and track library members.
- **Loan System:** Automated issue and return processing with real-time inventory updates.
- **Data Integrity:** Prevents removal of books that currently have active loans.
- **Searchable Interface:** Interactive web UI for library operations.

## Tech Stack
- **Language:** Python 3.x
- **Framework:** Flask
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Jinja2

## Getting Started

### Prerequisites
- Python 3.x installed on your system.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pasharodygin/school-library-database.git
   cd school-library-database
   ```

2. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install flask
   ```

### Running the Application
1. Start the server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to: `http://127.0.0.1:5000`

## Project Structure
- `app.py`: Flask routes and web application logic.
- `db_module.py`: Database connection and SQL operations.
- `templates/`: HTML templates for the frontend.
- `static/`: Static assets (images, CSS).
- `school_library.db`: SQLite database file (auto-generated).
