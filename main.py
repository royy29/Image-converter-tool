# import os
# import tempfile
# import zipfile
# from flask import Flask, request, send_file, render_template, redirect, url_for
# from PIL import Image
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.config['ALLOWED_EXTENSIONS'] = {'webp'}
# app.config['TEMP_DIR'] = tempfile.gettempdir()

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def convert_webp_to_jpg_quality100(image_file, quality=100):
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=app.config['TEMP_DIR']) as output_file:
#         image = Image.open(image_file)
#         image.convert("RGB").save(output_file, "JPEG", quality=quality)
#         output_file.seek(0)
#         return output_file.name
    
# def convert_webp_to_jpg_quality70(image_file, quality=70):
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=app.config['TEMP_DIR']) as output_file:
#         image = Image.open(image_file)
#         image.convert("RGB").save(output_file, "JPEG", quality=quality)
#         output_file.seek(0)
#         return output_file.name

# @app.route('/', methods=['GET', 'POST'])
# def upload_and_download():
#     if request.method == 'POST':
#         if 'files[]' not in request.files:
#             return redirect(request.url)
#         files = request.files.getlist('files[]')
#         converted_files = []
#         for file in files:
#             if file and allowed_file(file.filename):
#                 output_path = convert_webp_to_jpg_quality100(file)
#                 converted_files.append((secure_filename(file.filename).replace('.webp', '.jpg'), output_path))
#         return render_template('index.html', files=converted_files)
#     return render_template('index.html', files=[])

# @app.route('/download/<filename>')
# def download(filename):
#     file_path = request.args.get('file_path')
#     if file_path and os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True, download_name=filename, mimetype='image/jpeg')
#     return redirect(url_for('upload_and_download'))

# @app.route('/download_zip', methods=['POST'])
# def download_zip():
#     files = request.form.getlist('files')
#     zip_filename = os.path.join(app.config['TEMP_DIR'], 'converted_images.zip')
#     with zipfile.ZipFile(zip_filename, 'w') as zipf:
#         for file_path in files:
#             zipf.write(file_path, os.path.basename(file_path))
#     return send_file(zip_filename, as_attachment=True, download_name='converted_images.zip')

# if __name__ == "__main__":
#     app.run(debug=True)

import os
import tempfile
import zipfile
from flask import Flask, request, send_file, render_template, redirect, url_for
from PIL import Image
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS_WEBP'] = {'webp'}
app.config['ALLOWED_EXTENSIONS_SVG'] = {'svg'}
app.config['TEMP_DIR'] = tempfile.gettempdir()

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def convert_webp_to_jpg_quality100(image_file, quality=100):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=app.config['TEMP_DIR']) as output_file:
        image = Image.open(image_file)
        image.convert("RGB").save(output_file, "JPEG", quality=quality)
        output_file.seek(0)
        return output_file.name

def convert_webp_to_jpg_quality70(image_file, quality=70):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', dir=app.config['TEMP_DIR']) as output_file:
        image = Image.open(image_file)
        image.convert("RGB").save(output_file, "JPEG", quality=quality)
        output_file.seek(0)
        return output_file.name

def convert_svg_to_png(image_file):
    # Read SVG content
    svg_data = image_file.read().decode('utf-8')
    
    # Convert SVG content to PNG
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=app.config['TEMP_DIR']) as output_file:
        cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=output_file.name)
        output_file.seek(0)
        return output_file.name

@app.route('/', methods=['GET', 'POST'])
def upload_and_download():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('files[]')
        converted_files = []
        for file in files:
            if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS_WEBP']):
                output_path = convert_webp_to_jpg_quality100(file)
                converted_files.append((secure_filename(file.filename).replace('.webp', '.jpg'), output_path))
        return render_template('index.html', files=converted_files)
    return render_template('index.html', files=[])

@app.route('/download/<filename>')
def download(filename):
    file_path = request.args.get('file_path')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename, mimetype='image/jpeg')
    return redirect(url_for('upload_and_download'))

@app.route('/download_zip', methods=['POST'])
def download_zip():
    files = request.form.getlist('files')
    zip_filename = os.path.join(app.config['TEMP_DIR'], 'converted_images.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in files:
            zipf.write(file_path, os.path.basename(file_path))
    return send_file(zip_filename, as_attachment=True, download_name='converted_images.zip')

@app.route('/svg_to_png', methods=['GET', 'POST'])
def svg_to_png():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('files[]')
        converted_files = []
        for file in files:
            if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS_SVG']):
                output_path = convert_svg_to_png(file)
                converted_files.append((secure_filename(file.filename).replace('.svg', '.png'), output_path))
        return render_template('svg_to_png.html', files=converted_files)
    return render_template('svg_to_png.html', files=[])

@app.route('/download_png/<filename>')
def download_png(filename):
    file_path = request.args.get('file_path')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename, mimetype='image/png')
    return redirect(url_for('svg_to_png'))

if __name__ == "__main__":
    app.run(debug=True)
