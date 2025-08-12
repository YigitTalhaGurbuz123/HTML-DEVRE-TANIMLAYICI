# Temel imaj: Python 3.10 (Render'ın default sürümü değilse Dockerfile ile zorlayabiliriz)
FROM python:3.10-slim

# Çalışma dizini oluştur
WORKDIR /app

# Gereksinimleri kopyala
COPY requirements.txt .

# Pip'i güncelle ve bağımlılıkları kur
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Uygulamayı başlat (gunicorn ile)
CMD ["gunicorn", "-k", "eventlet", "app:app", "--bind", "0.0.0.0:8000"]
