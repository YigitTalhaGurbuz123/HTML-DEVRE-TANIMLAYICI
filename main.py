from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')

@app.route('/card')
def card():
    return render_template('card.html')  # varsa o sayfayı göster

if __name__ == '__main__':
    app.run(debug=True)