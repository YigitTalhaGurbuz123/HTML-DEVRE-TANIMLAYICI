from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'efsane-bir-gizli-anahtar'  # session için zorunlu

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELLER ---
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    cards = db.relationship('Card', backref='user', lazy=True)

# Ana sayfa - 1. projenin index.html (herkes erişebilir)
@app.route('/')
def home():
    return render_template('index.html')

# Login sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        user = User.query.filter_by(login=form_login, password=form_password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/not_defteri')
        else:
            error = 'Hatalı giriş veya şifre'

    return render_template('login.html', error=error)

# Kayıt sayfası
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        login = request.form['email']
        password = request.form['password']

        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    else:
        return render_template('registration.html')

# Not defteri sayfası (giriş zorunlu)
@app.route('/not_defteri')
def not_defteri():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    cards = Card.query.filter_by(user_id=user_id).order_by(Card.id).all()
    return render_template('not_defteri.html', cards=cards)

# Belirli notu göster (giriş zorunlu)
@app.route('/card/<int:id>')
def card(id):
    if 'user_id' not in session:
        return redirect('/login')

    card = Card.query.get(id)
    if card and card.user_id == session['user_id']:
        return render_template('card.html', card=card)
    else:
        return "Bu karta erişim izniniz yok!", 403

# Yeni not sayfası (giriş zorunlu)
@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('create_card.html')

# Yeni not ekleme formu (giriş zorunlu)
@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']
        user_id = session['user_id']

        card = Card(title=title, subtitle=subtitle, text=text, user_id=user_id)
        db.session.add(card)
        db.session.commit()

        return redirect('/not_defteri')
    else:
        return render_template('create_card.html')

# Hakkında sayfası (1. proje)
@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')

# Henüz hazır olmayan diğer sayfalar için placeholder
@app.route('/deneme')
def deneme():
    return "<h1>Henüz yapılmadı. Beklemede...</h1>"

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)