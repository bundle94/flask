import os
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import psycopg2
import requests
from bs4 import BeautifulSoup
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
conn = None


labels = {0: 'apple', 1: 'banana', 2: 'beetroot', 3: 'bell pepper', 4: 'cabbage', 5: 'capsicum', 6: 'carrot',
          7: 'cauliflower', 8: 'chilli pepper', 9: 'corn', 10: 'cucumber', 11: 'eggplant', 12: 'garlic', 13: 'ginger',
          14: 'grapes', 15: 'jalepeno', 16: 'kiwi', 17: 'lemon', 18: 'lettuce',
          19: 'mango', 20: 'onion', 21: 'orange', 22: 'paprika', 23: 'pear', 24: 'peas', 25: 'pineapple',
          26: 'pomegranate', 27: 'potato', 28: 'raddish', 29: 'soy beans', 30: 'spinach', 31: 'sweetcorn',
          32: 'sweetpotato', 33: 'tomato', 34: 'turnip', 35: 'watermelon'}

model = load_model('FV.h5')

def get_db_connection():
    conn = psycopg2.connect(database="calories_calculator", user="postgres", password="root", host="localhost",
                        port="5432")
    return conn

def fetch_calories(prediction):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select calories from public.foods where name = '"+prediction+"'")
    data = cur.fetchall()
    print(data[0][0])
    cur.close()
    conn.close()
    return data[0][0]

def fetch_category(result):
    print(result)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM public.categories where id in (select category from public.foods where name = '"+result+"')")
    data = cur.fetchall()
    print(data[0][0])
    cur.close()
    conn.close()
    return data[0][0]

def fetch_photo(result):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select photo from public.foods where name = '"+result+"'")
    data = cur.fetchall()
    print(data[0][0])
    cur.close()
    conn.close()
    return data[0][0]

def prepare_image(img_path):
    img = load_img(img_path, target_size=(224, 224, 3))
    img = img_to_array(img)
    img = img / 255
    img = np.expand_dims(img, [0])
    answer = model.predict(img)
    y_class = answer.argmax(axis=-1)
    print(y_class)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = labels[y]
    print(res)
    return res.capitalize()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/recognize', methods = ['POST', 'GET'])
def classify_food():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        image = request.files['image']
        if image.filename != '':
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #img = Image.open(image).resize((250, 250))
                save_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                result = prepare_image(save_image_path)
                res = {'name': result, 'category': fetch_category(result), 'calories': fetch_calories(result), 'photo': fetch_photo(result)}
                #print(res)
                return jsonify(res)
        else:
            flash("An image needs to be selected")
            return render_template('index.html')



if __name__ == '__main__':
    app.run(host="0.0.0.0")