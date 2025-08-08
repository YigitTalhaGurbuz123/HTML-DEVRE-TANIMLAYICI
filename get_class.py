from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

def get_class(model_path, labels_path, image_path, confidence_threshold=0.7):
    # Modeli yükle
    model = load_model(model_path)

    # Etiketleri oku (utf-8 ile açtığından emin ol)
    with open(labels_path, 'r', encoding='utf-8') as f:
        labels = f.read().splitlines()

    # Görseli hazırla
    img = image.load_img(image_path, target_size=(224, 224))  # modelin inputuna göre
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Tahmin yap
    prediction = model.predict(img_array)[0]  # tek örnek olduğu için [0]
    predicted_index = np.argmax(prediction)
    confidence = prediction[predicted_index]
    
    if confidence < confidence_threshold:
        return None  # Güven düşükse bilinmiyor kabul et

    predicted_label = labels[predicted_index]
    return predicted_label
