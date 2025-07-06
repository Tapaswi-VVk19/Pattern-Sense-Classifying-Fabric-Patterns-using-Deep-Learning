from flask import Flask, render_template, request
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

model = load_model("psm_best_model.h5")

classes = [
    'Animal', 'Cartoon', 'Floral', 'Geometry', 'Ikat',
    'Plain', 'Polka Dot', 'Squares', 'Stripes', 'Tribal'
]

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_pattern(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array, verbose=0)[0]
        top_class = np.argmax(prediction)
        confidence = prediction[top_class]

        return f"{classes[top_class]} ({confidence*100:.1f}% confidence)"

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/industries')
def industries():
    return render_template('industries.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == "" or not allowed_file(file.filename):
            return render_template('predict.html', prediction="⚠️ Invalid file type.")

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        prediction = predict_pattern(path)
        img_path = '/' + path.replace('\\', '/').replace('\\', '/')


        return render_template('predict.html', prediction=prediction, img_path=img_path)

    return render_template('predict.html')

if __name__ == '__main__':
    app.run(debug=True)
