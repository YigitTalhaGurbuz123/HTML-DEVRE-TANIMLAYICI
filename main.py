from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from get_class import get_class


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'fa7b0c9416d3eab2c4f80b2197daeeaf'  # session için zorunlu

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

siniflar = {
    "Arduino UNO": [
        "Arduino UNO, mikrodenetleyici tabanlı popüler bir geliştirme kartıdır.",
        "Genellikle elektronik projelerde giriş-çıkış kontrolü için kullanılır.",
        "ATmega328P mikrodenetleyiciye sahiptir ve programlaması kolaydır.",
        "USB portu üzerinden bilgisayara bağlanarak kod yüklenir.",
        "Hobi ve eğitim amaçlı projelerde en çok tercih edilen karttır."
    ],
    "Raspberry Pi": [
        "Raspberry Pi, küçük ve uygun fiyatlı bir tek kart bilgisayardır.",
        "Linux tabanlı işletim sistemi ile çalışır ve çok amaçlıdır.",
        "GPIO pinleri sayesinde elektronik projelerde donanım kontrolü yapılabilir.",
        "Masaüstü bilgisayar, medya oynatıcı veya sunucu olarak kullanılabilir.",
        "Eğitimde programlama ve donanım öğrenmek için çok popülerdir."
    ],
    "Esp32": [
        "ESP32, Wi-Fi ve Bluetooth özellikli güçlü bir mikrodenetleyici kartıdır.",
        "Daha fazla giriş-çıkış pini ve işlemci gücü sunar.",
        "IoT projelerinde kablosuz bağlantı için sıklıkla tercih edilir.",
        "Düşük güç tüketimi ve çift çekirdekli işlemcisi vardır.",
        "Arduino IDE ile kolayca programlanabilir."
    ],
    "Direnç": [
        "Direnç, elektrik devrelerinde akımı sınırlayan pasif bir devre elemanıdır.",
        "Birimi ohm (Ω) olarak ifade edilir.",
        "LED gibi bileşenlerin korunmasında kullanılır.",
        "Elektrik akışını kontrol ederek devrenin güvenli çalışmasını sağlar.",
        "Farklı renk kodları ile değerleri belirlenir."
    ],
    "Led": [
        "LED (Light Emitting Diode), ışık yayan yarı iletken bir diyottur.",
        "Elektrik akımı geçtiğinde ışık üretir.",
        "Farklı renk ve boyutlarda olabilir.",
        "Devrelerde durum göstergesi olarak yaygın kullanılır.",
        "Düşük güç tüketimi ve uzun ömrü ile tercih edilir."
    ],
    "Breadboard": [
        "Breadboard, lehim yapmadan devre kurulmasını sağlayan prototip kartıdır.",
        "Elektronik bileşenler kolayca takılıp çıkarılabilir.",
        "Pinler arasındaki bağlantılar plastik içindeki metal şeritlerle sağlanır.",
        "Genellikle eğitim ve test amaçlı kullanılır.",
        "Elektronik projelerde hızlı prototipleme için idealdir."
    ],
    "Transistör": [
        "Transistör, elektrik sinyallerini yükselten veya anahtarlayan yarı iletkendir.",
        "NPN ve PNP olmak üzere iki temel tipi vardır.",
        "Amplifikatör ve anahtar devrelerde kullanılır.",
        "Düşük güçlü sinyalleri kontrol etmek için idealdir.",
        "Elektronik devrelerin temel yapı taşlarından biridir."
    ],
    "Entegre devre": [
        "Entegre devre (IC), çok sayıda elektronik bileşenin tek bir çip üzerinde toplandığı devredir.",
        "Analog veya dijital fonksiyonları gerçekleştirebilir.",
        "Boyut ve maliyeti azaltarak karmaşık devrelerin yapılmasını sağlar.",
        "Çeşitli türleri (op-amp, mikrodenetleyici, hafıza vb.) vardır.",
        "Modern elektronik cihazların temel bileşenidir."
    ],
    "Motor sürücü": [
        "Motor sürücü, motorları kontrol etmek için kullanılan elektronik modüldür.",
        "DC ve step motorların hız ve yön kontrolünü sağlar.",
        "Genellikle mikrodenetleyicilerle birlikte kullanılır.",
        "L298N gibi yaygın sürücü entegreleri bulunur.",
        "Yüksek akımlı motorların doğrudan kontrolünü mümkün kılar."
    ],
    "Dc Motor": [
        "DC motor, doğru akımla çalışan elektrik motorudur.",
        "Dönme hareketi sağlar ve hız kontrolü yapılabilir.",
        "Robotik projelerde ve mekanik hareket gerektiren yerlerde kullanılır.",
        "Basit yapısı ve kolay kontrolü ile yaygındır.",
        "Enerji kaynağına bağlı olarak dönüş yönü değiştirilebilir."
    ],
    "Elektrolitik Kondansatör": [
        "Elektrolitik kondansatör, yüksek kapasiteli bir kondansatör türüdür.",
        "Polariteli olup doğru yönde bağlanmalıdır.",
        "Filtreleme ve enerji depolama amaçlı kullanılır.",
        "Genellikle güç kaynaklarında tercih edilir.",
        "Kapasite değeri mikrofarad (μF) mertebesindedir."
    ],
    "Seramik Kondansatör": [
        "Seramik kondansatör, küçük boyutlu ve yüksek frekanslı devrelerde kullanılır.",
        "Polaritesizdir, her iki yönde de bağlanabilir.",
        "Genellikle sinyal filtrelemede tercih edilir.",
        "Düşük kapasiteli ve yüksek dayanıklılığa sahiptir.",
        "Farklı değerlerde ve gerilimlerde üretilir."
    ],
    "Servo Motor": [
        "Servo motor, açısal pozisyonu hassas kontrol eden motordur.",
        "Genellikle robotik kol ve RC araçlarda kullanılır.",
        "Geri besleme sistemi ile belirli açılara dönebilir.",
        "Düşük güç tüketimi ve yüksek tork sağlar.",
        "PWM sinyalleriyle kontrol edilir."
    ],
    "Ultrasonik Sensör": [
        "Ultrasonik sensör, ses dalgalarıyla mesafe ölçümü yapar.",
        "Genellikle 2 cm ile 400 cm arası mesafeyi algılar.",
        "Robotik ve otomasyon projelerinde engel tespiti için kullanılır.",
        "Gönderdiği ses dalgasının yansımasını ölçer.",
        "Kolay programlanabilir ve hassas bir sensördür."
    ],
    "OLED / TFT Ekran": [
        "OLED ve TFT, küçük boyutlu renkli ekranlardır.",
        "OLED, organik LED teknolojisi kullanır ve daha canlı renkler sunar.",
        "TFT, sıvı kristal ekrana sahiptir ve yaygın kullanılır.",
        "Genellikle Arduino ve Raspberry Pi projelerinde görüntüleme için kullanılır.",
        "Düşük güç tüketimi ve yüksek çözünürlük özellikleri vardır."
    ],
    "RTC Modülü (DS3231)": [
        "RTC modülü, gerçek zamanlı saat bilgisi sağlar.",
        "DS3231, yüksek hassasiyetli bir RTC entegresidir.",
        "Güç kesintilerinde bile zamanı tutar.",
        "Arduino ve diğer mikrodenetleyicilerle kolayca entegre edilir.",
        "Saat, tarih ve alarm fonksiyonlarını destekler."
    ],
    "Röle Modülü": [
        "Röle modülü, düşük güçlü sinyallerle yüksek güçlü devreleri kontrol eder.",
        "Elektriksel izolasyon sağlar ve anahtarlama yapar.",
        "Genellikle 220V AC cihazların kontrolünde kullanılır.",
        "Arduino gibi kartlarla kumanda edilebilir.",
        "Anahtarlama işlemi elektromekanik ya da solid-state olabilir."
    ],
    "LDR": [
        "LDR (Light Dependent Resistor), ışığa duyarlı dirençtir.",
        "Işık yoğunluğu arttıkça direnci azalır.",
        "Gece-gündüz algılama ve ışık kontrollü devrelerde kullanılır.",
        "Basit ve ucuz bir sensördür.",
        "Analog sinyal verir ve mikrodenetleyici ile okunabilir."
    ],
    "IR ALICI": [
        "IR alıcı, kızılötesi sinyalleri algılayan sensördür.",
        "Uzaktan kumanda sinyallerini okumak için kullanılır.",
        "Genellikle TV, robot ve otomasyon projelerinde yer alır.",
        "Modüle edilmiş IR ışığını filtreleyerek alır.",
        "Arduino ile kolayca entegre edilebilir."
    ],
    "Potansiyometre": [
        "Potansiyometre, ayarlanabilir direnç elemanıdır.",
        "Çevirme hareketi ile direnç değeri değişir.",
        "Ses açma-kapama ve ışık ayarı gibi uygulamalarda kullanılır.",
        "Analog girişler için ideal bir kontrol cihazıdır.",
        "Genellikle üç uçlu ve döner tiptedir."
    ],
    "Diyot": [
        "Diyot, elektriğin tek yönde akmasını sağlayan yarı iletkendir.",
        "Devrelerde ters polarite koruması için kullanılır.",
        "LED, Zener diyot gibi farklı türleri vardır.",
        "Doğru akımı yönlendirme ve sinyal düzeltme görevleri vardır.",
        "Yüksek frekanslı devrelerde de yaygın kullanılır."
    ],
    "Push Button": [
        "Push button, basıldığında devreyi tamamlayan anahtardır.",
        "Genellikle kısa süreli tetikleme için kullanılır.",
        "Arduino projelerinde giriş sinyali olarak yaygındır.",
        "Fiziksel buton formundadır ve kolay bulunur.",
        "Basılı tutulduğunda sinyal devam eder."
    ],
    "Buzzer": [
        "Buzzer, ses çıkışı sağlayan elektronik bileşendir.",
        "Doğru akım uygulandığında ses üretir.",
        "Alarm, uyarı ve geri bildirim amaçlı kullanılır.",
        "Pasif ve aktif tipleri vardır.",
        "Arduino projelerinde kolayca kontrol edilir."
    ],
    "Breadboard Güç Kartı": [
        "Breadboard güç kartı, breadboard için 5V ve 3.3V güç sağlar.",
        "Genellikle USB veya pil ile beslenir.",
        "Projelerde sabit ve güvenli voltaj kaynağıdır.",
        "Modüler ve kolay takılıp çıkarılır.",
        "Prototip devrelerin enerji ihtiyacını karşılar."
    ],
    "Step motor": [
        "Step motor, adım adım dönen bir motordur.",
        "Hassas konum kontrolü için uygundur.",
        "3D yazıcılar ve CNC makinelerde kullanılır.",
        "Elektronik olarak belirli açılarda döner.",
        "Genellikle sürücü kartlarıyla kontrol edilir."
    ],
    "LCD ekran": [
        "LCD ekran, sıvı kristal kullanarak görüntü gösterir.",
        "Monokrom veya renkli çeşitleri vardır.",
        "Alfanümerik ve grafik modülleri yaygındır.",
        "Arduino projelerinde bilgi göstermek için tercih edilir.",
        "Düşük güç tüketir ve okunabilirliği iyidir."
    ],
    "7 Segment Display": [
        "7 segment display, sayısal karakterleri göstermek için kullanılır.",
        "Yedi LED segmentten oluşur.",
        "Basit sayıcı ve saat projelerinde yaygındır.",
        "Anot ve katot ortak tipleri vardır.",
        "Kolay sürülür ve okunması basittir."
    ],
    "PIR Sensör": [
        "PIR sensör, insan veya hayvan hareketini algılar.",
        "Pasif kızılötesi sensör olarak çalışır.",
        "Güvenlik ve otomatik aydınlatma sistemlerinde kullanılır.",
        "Ortam sıcaklığındaki değişiklikleri tespit eder.",
        "Düşük güç tüketir ve hassas algılama yapar."
    ],
    "Raspberry Pi Pico": [
        "Raspberry Pi Pico, düşük maliyetli bir mikrodenetleyici kartıdır.",
        "RP2040 işlemciyi kullanır ve programlanması kolaydır.",
        "GPIO pinleri ile çok sayıda donanım kontrolü yapılabilir.",
        "Arduino ve MicroPython ile uyumludur.",
        "Küçük projeler ve öğrenme amaçlı idealdir."
    ],
    "Arduino Mega": [
        "Arduino Mega, çok sayıda giriş-çıkış pini olan gelişmiş Arduino kartıdır.",
        "ATmega2560 mikrodenetleyiciye sahiptir.",
        "Daha büyük ve karmaşık projeler için uygundur.",
        "Hafıza ve pin sayısı Arduino UNO'dan fazladır.",
        "Robotik ve endüstriyel uygulamalarda tercih edilir."
    ]
}


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
    
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

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

@app.route('/canli_sohbet')
def canli_sohbet():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))
    
    user = User.query.get(session['user_id'])
    if not user:  # Kullanıcı bulunamadıysa
        session.clear()
        return redirect(url_for('login', next=request.path))
    
    messages = ChatMessage.query.order_by(ChatMessage.id).all()
    return render_template('canli_sohbet.html', username=user.login, messages=messages)

@socketio.on('message')
def handle_message(msg):
    # msg -> "username: mesaj"
    print(f"Gelen mesaj: {msg}")

    # Mesajı ayırıp veritabanına kaydet
    try:
        username, text = msg.split(": ", 1)
    except ValueError:
        username, text = "Bilinmeyen", msg

    new_msg = ChatMessage(
        username=username,
        message=text,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_msg)
    db.session.commit()

    send(msg, broadcast=True)

@app.route('/devre_elemanlari')
def devre_elemanlari():
    return render_template('devre_elemanlari.html')

# Henüz hazır olmayan diğer sayfalar için placeholder
@app.route('/deneme')
def deneme():
    return render_template('beklemede.html')

MODEL_PATH = r"C:\Kodlar\Kodland\PythonPro\Final_Projesi\HTML-DEVRE-TANIMLAYICI\keras_model.h5"
LABELS_PATH = r"C:\Kodlar\Kodland\PythonPro\Final_Projesi\HTML-DEVRE-TANIMLAYICI\labels.txt"
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/devre_tanima', methods=['GET', 'POST'])
def devre_tanima():
    prediction = None
    description = None
    error = None

    if request.method == 'POST':
        if 'image' not in request.files:
            error = "Dosya yüklenmedi!"
            return render_template('devre_tanima.html', error=error)

        file = request.files['image']
        if file.filename == '':
            error = "Dosya seçilmedi!"
            return render_template('devre_tanima.html', error=error)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                prediction = get_class(MODEL_PATH, LABELS_PATH, filepath)
                if prediction is None:
                    error = "Güven düşük, devre elemanı tanımlanamadı."
                else:
                    # Sınıf adı tahmin edilince açıklamaları alıyoruz:
                    description = siniflar.get(prediction)
                    if description is None:
                        description = ["Açıklama bulunamadı."]  # fallback
            except Exception as e:
                error = f"Model çalıştırılırken hata: {e}"

    return render_template('devre_tanima.html', prediction=prediction, description=description, error=error)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)