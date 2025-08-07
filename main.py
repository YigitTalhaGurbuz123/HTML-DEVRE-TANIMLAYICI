from flask import Flask, render_template, request, redirect, session, url_for

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'fa7b0c9416d3eab2c4f80b2197daeeaf'  # session için zorunlu

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
    next_page = request.args.get('next')  # GET ile gelen next parametresi

    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        next_page = request.form.get('next')  # POST ile gelen next parametresi

        user = User.query.filter_by(login=form_login, password=form_password).first()
        if user:
            session['user_id'] = user.id
            return redirect(next_page or url_for('home'))
        else:
            error = 'Hatalı giriş veya şifre'

    return render_template('login.html', error=error, next=next_page)

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
        return redirect(url_for('login', next=request.path))
    
    user_id = session['user_id']
    cards = Card.query.filter_by(user_id=user_id).order_by(Card.id).all()
    return render_template('not_defteri.html', cards=cards)

# Belirli notu göster (giriş zorunlu)
@app.route('/card/<int:id>')
def card(id):
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))

    card = Card.query.get(id)
    if card and card.user_id == session['user_id']:
        return render_template('card.html', card=card)
    else:
        return "Bu karta erişim izniniz yok!", 403

# Yeni not sayfası (giriş zorunlu)
@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))
    return render_template('create_card.html')

# Yeni not ekleme formu (giriş zorunlu)
@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))

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

@app.route('/not_defteri2')
def not_defteri2():
    if 'user_id' in session:
        return redirect('/not_defteri')
    else:
        return redirect('/login')
    
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error = ''
    success = ''

    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        user = User.query.filter_by(login=email).first()

        if user:
            user.password = new_password
            db.session.commit()
            success = 'Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.'
        else:
            error = 'Bu e-posta adresiyle kayıtlı bir kullanıcı bulunamadı.'

    return render_template('forgot_password.html', error=error, success=success)

# Hakkında sayfası (1. proje)
@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')

@app.route('/devre_elemanlari')
def devre_elemanlari():
    return render_template('devre_elemanlari.html')

# Henüz hazır olmayan diğer sayfalar için placeholder
@app.route('/deneme')
def deneme():
    return render_template('beklemede.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
