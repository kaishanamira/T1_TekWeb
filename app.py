from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from flask_session import Session
from db_config import init_mysql

app = Flask(__name__)
app.secret_key = "rahasia_super_secret"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

mysql = init_mysql(app)
bcrypt = Bcrypt(app)

@app.route('/')
def main():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, author, isbn, genre, language, total_copies, available_copies, shelf, status FROM books")
    books = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', books=books)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/')
        else:
            flash('Login gagal. Periksa kembali username dan password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
