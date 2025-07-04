from flask_login import logout_user
from flask import Flask, render_template, redirect, url_for
from app import create_app

app = create_app()

# ✅ Landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# ✅ Logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)

