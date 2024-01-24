import random
import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'secret-key'  # Replace with your own secret key

# Database initialization
def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            department TEXT NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

# Route for the home page
@app.route('/')
def home():
    if 'username' in session:
        if 'admin' in session and session['admin']:
            return redirect('/admin/dashboard')
        else:
            return redirect('/dashboard')
    else:
        return redirect('/login')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if 'admin' in session and session['admin']:
            return redirect('/admin/dashboard')
        else:
            return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            session['admin'] = True
            return redirect('/admin/dashboard')

        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM students WHERE name=? AND password=?
            ''',
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            session['admin'] = False
            return redirect('/dashboard')
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        department = request.form['department']

        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO students (name, password, department) VALUES (?, ?, ?)
            ''',
            (username, password, department)
        )
        conn.commit()
        conn.close()

        return redirect('/login')
    else:
        return render_template('register.html')

# Route for the student dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']

        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM students WHERE name=?
            ''',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        return render_template('dashboard.html', user=user)
    else:
        return redirect('/login')

# Route for the admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' in session and 'admin' in session and session['admin']:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM students
            '''
        )
        students = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html', students=students)
    else:
        return redirect('/login')

# Route for editing a student's details
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' in session and 'admin' in session and session['admin']:
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            department = request.form['department']

            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            cursor.execute(
                '''
                UPDATE students SET name=?, password=?, department=? WHERE id=?
                ''',
                (name, password, department, id)
            )
            conn.commit()
            conn.close()

            return redirect('/admin/dashboard')
        else:
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM students WHERE id=?
                ''',
                (id,)
            )
            student = cursor.fetchone()
            conn.close()

            return render_template('edit.html', student=student)
    else:
        return redirect('/')

# Route for deleting a student
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'username' in session and 'admin' in session and session['admin']:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            DELETE FROM students WHERE id=?
            ''',
            (id,)
        )
        conn.commit()
        conn.close()

        return redirect('/admin/dashboard')
    else:
        return redirect('/')

# Route for generating the seating plan
@app.route('/seating_plan')
def seating_plan():
    if 'username' in session:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM students
            '''
        )
        students = cursor.fetchall()
        conn.close()

        # Shuffle the students randomly
        random.shuffle(students)

        return render_template('seating_plan.html', students=students)
    else:
        return redirect('/login')

# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
