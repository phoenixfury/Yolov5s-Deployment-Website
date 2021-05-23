from flask import Flask, flash, request, redirect, url_for, render_template
import torch
import yaml
import os
import cv2
from IPython.core.magic import register_line_cell_magic
from IPython.display import Image, clear_output  # to display images
# from app import app
import urllib.request
from werkzeug.utils import secure_filename
import shutil
from timeit import default_timer as timer



UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("try1.html")

@app.route('/', methods=['POST'])
def upload_image():
    start = timer()
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        f = os.path.join('static/uploads', filename)
        os.system(f'python yolov5\detect.py --weights ACV_pro_YOLOv5s_best.pt --img 416 --conf 0.4 --source {f}')
        

        all_subdirs = [os.path.join('runs\detect',d) for d in os.listdir('runs\detect')]
        latest_subdir = max(all_subdirs, key=os.path.getmtime)
        f_t = os.listdir(latest_subdir)[0]
        print(f_t)
        file_to_move = os.path.join(latest_subdir, f_t)
        dest = os.path.join(r'static\uploads',f_t)

        shutil.move( file_to_move, dest)
                #print('upload_image filename: ' + filename)
        end = timer()
        flash('Detected in:')
        flash(abs(end - start))
        flash('Image successfully uploaded and detected below')
                
        return render_template('try1.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route("/<name>")
def user(name):
    return "Hello {name}".format(name=name)

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)