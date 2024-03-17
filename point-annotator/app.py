from flask import Flask, render_template, request, jsonify, url_for
import numpy as np
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64
import os

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

app = Flask(__name__)

# change the parameters here
image_filenames = [f for f in os.listdir('static/images') if f.lower().endswith(('.jpg', '.png', 'jpeg'))]
image_paths = ['images/' + f for f in image_filenames]
max_height = 600
base_url = '/my-app'

current_image_index = 0
marks = []

@app.route('/')
def index():
    image_path = url_for('static', filename=image_paths[current_image_index])
    return render_template('index.html', image_path=image_path, max_height=max_height)

@app.route('/next', methods=['POST'])
def next_image():
    global current_image_index
    global marks

    if len(marks) >= 2:
        with open('annotations.txt', 'ab') as f:
            s = f"{image_filenames[current_image_index]}, {marks[0:2]}\n"
            f.write(s.encode('utf-8'))

    marks = []

    if current_image_index < len(image_paths) - 1:
        current_image_index += 1

    return jsonify({'image_path': url_for('static', filename=image_paths[current_image_index])})

@app.route('/previous', methods=['POST'])
def previous_image():
    global current_image_index
    global marks
    marks = []

    if current_image_index > 0:
        current_image_index -= 1

    return jsonify({'image_path': url_for('static', filename=image_paths[current_image_index])})

@app.route('/reset', methods=['POST'])
def reset():
    global marks
    marks = []
    return 'reset done!'

@app.route('/record_coordinates', methods=['POST'])
def record_coordinates():
    global current_image_index
    global marks
    global max_height

    x = request.json['x']
    y = request.json['y']

    w, h = Image.open('static/'+ image_paths[current_image_index]).size

    scale_factor = 1 if h <= max_height else max_height/h

    x = int(x/scale_factor)
    y = int(y/scale_factor)

    marks.append([x, y])

    #img = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    # Convert the image to a NumPy array
    #img_array = np.array(img)

    #for mark in marks:
    #    img_array[max(0,mark[1]-1):min(w+1,mark[1]+2), max(0,mark[0]-1):min(h+1,mark[0]+2)] = [0, 0, 0, 255]

    # Convert the NumPy array back to an image
    #pil_mask_ = Image.fromarray(img_array)

    # Create a BytesIO buffer to store the raw bytes of the image
    #buffer = BytesIO()

    # Save the image to the buffer as PNG
    #pil_mask_.save(buffer, format='PNG')

    # Retrieve the raw bytes of the image from the buffer
    #buffer.seek(0)
    #image_bytes = buffer.getvalue()

    # Encode the image bytes as base64
    #base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Print the base64 representation of the image
    #print(base64_image)

    #print(x, y)
    
    #return jsonify({'success': True, 'mask': "data:image/png;base64," + base64_image})

    return 'recorded coordinates!'


if __name__ == '__main__':

    app.wsgi_app = DispatcherMiddleware(
        Response('Not Found', status=404),
        {base_url: app.wsgi_app}
    )

    app.run(debug=True, port=8083)