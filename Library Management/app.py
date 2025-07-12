from flask import Flask, render_template, request, redirect, jsonify
from db_config import get_connection
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/books")
def books():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM BOOKS")
        books_data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("books.html", books=books_data)
    except Exception as e:
        return f"Database Error: {e}"

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        try:
            student_id = int(request.form["student_id"])
            name = request.form["name"]
            email = request.form["email"]

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO STUDENTS (student_id, name, email)
                VALUES (:1, :2, :3)
            """, (student_id, name, email))
            conn.commit()

            cur.execute("SELECT name FROM STUDENTS WHERE student_id = :1", (student_id,))
            updated_name = cur.fetchone()[0]

            cur.close()
            conn.close()

            return render_template("student_success.html", name=name, updated_name=updated_name)
        except Exception as e:
            return f"Error: {e}"
    return render_template("add_student.html")

@app.route("/students")
def students():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM STUDENTS")
        student_data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("students.html", students=student_data)
    except Exception as e:
        return f"Database Error: {e}"

@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM STUDENTS WHERE student_id = :1", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/students")
    except Exception as e:
        return jsonify({"message": f"Error deleting student: {e}"}), 500

@app.route("/issue_book", methods=["GET", "POST"])
def issue_book():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Fetch books and students for dropdowns
        cur.execute("SELECT book_id, title FROM BOOKS")
        books = cur.fetchall()

        cur.execute("SELECT student_id, name FROM STUDENTS")
        students = cur.fetchall()

        if request.method == "POST":
            issue_id = int(request.form["issue_id"])
            book_id = int(request.form["book_id"])
            student_id = int(request.form["student_id"])
            issue_date = datetime.strptime(request.form["issue_date"], '%Y-%m-%d')
            return_date = datetime.strptime(request.form["return_date"], '%Y-%m-%d')

            cur.execute("""
                INSERT INTO ISSUE_BOOKS (issue_id, book_id, student_id, issue_date, return_date)
                VALUES (:1, :2, :3, :4, :5)
            """, (issue_id, book_id, student_id, issue_date, return_date))
            conn.commit()

            cur.close()
            conn.close()
            return redirect("/issues")

        cur.close()
        conn.close()
        return render_template("issue_book.html", books=books, students=students)
    except Exception as e:
        return f"Issue Error: {e}"

@app.route("/issues")
def issues():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT i.issue_id, b.title, s.name, i.issue_date, i.return_date
            FROM ISSUE_BOOKS i
            JOIN BOOKS b ON i.book_id = b.book_id
            JOIN STUDENTS s ON i.student_id = s.student_id
        """)
        issue_data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("issues.html", issues=issue_data)
    except Exception as e:
        return f"Error retrieving issues: {e}"

@app.route("/delete_issue", methods=["POST"])
def delete_issue():
    try:
        issue_id = int(request.form["delete_issue_id"])
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ISSUE_BOOKS WHERE issue_id = :1", (issue_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/issues")
    except Exception as e:
        return f"Error deleting issue: {e}"

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO BOOKS (book_id, title, author, publisher, total_copies)
                VALUES (:1, :2, :3, :4, :5)
            """, (
                int(request.form["book_id"]),
                request.form["title"],
                request.form["author"],
                request.form["publisher"],
                int(request.form["total_copies"])
            ))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/books")
        except Exception as e:
            return f"Error adding book: {e}"
    return render_template("add_book.html")

# Modified delete_book route
@app.route("/delete_book", methods=["POST"])
def delete_book():
    try:
        # Get book_id from form data
        book_id = int(request.form["book_id"])

        # Establish database connection
        conn = get_connection()
        cur = conn.cursor()

        # Execute DELETE statement to remove the book by its ID
        cur.execute("DELETE FROM BOOKS WHERE book_id = :1", (book_id,))
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Redirect back to the books list page after successful deletion
        return redirect("/books")
    except Exception as e:
        # In case of error, show the error message
        return f"Error deleting book: {e}"

if __name__ == "__main__":
    app.run(debug=True)
