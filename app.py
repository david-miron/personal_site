
from flask import Flask, request, render_template, send_from_directory
import os
import glob
import sys
import binascii
import argparse

app = Flask(__name__, static_url_path='/static')
app.config['IMAGE_EXTS'] = [".png", ".jpg", ".jpeg", ".gif", ".tiff"]


def encode(x):
    return binascii.hexlify(x.encode('utf-8')).decode()

def decode(x):
    return binascii.unhexlify(x.encode('utf-8')).decode()

@app.route('/')
def home():
    root_dir = app.config['ROOT_DIR']
    image_paths = []
    image_dirs = None
    lock = 0
    for root,dirs,files in os.walk(root_dir):
        
        if lock == 0:
            image_dirs = dirs
        lock = 1

        for file in files:
            if any(file.endswith(ext) for ext in app.config['IMAGE_EXTS']):
                image_paths.append(encode(os.path.join(root,file)))

    return render_template('index.html', galleries=image_dirs)

@app.route('/gallery/')
def ques():
    # url is: /gallery/?idd=ABC
    idd = request.args.get('idd', default='', type=str)
    root_dir = app.config['ROOT_DIR'] + idd
    image_paths = []
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in app.config['IMAGE_EXTS']):
                image_paths.append(encode(os.path.join(root,file)))
    print(image_paths)
    return render_template('gallery.html', paths=image_paths)

@app.route('/gallery/cdn/<path:filepath>')
def download_file(filepath):
    dir,filename = os.path.split(decode(filepath))
    print(dir, filename)
    return send_from_directory(dir, filename, as_attachment=False)

if __name__=="__main__":
    parser = argparse.ArgumentParser('Usage: %prog [options]')
    parser.add_argument('root_dir', help='Gallery root directory path')
    parser.add_argument('-l', '--listen', dest='host', default='127.0.0.1', \
                                    help='address to listen on [127.0.0.1]')
    parser.add_argument('-p', '--port', metavar='PORT', dest='port', type=int, \
                                default=5000, help='port to listen on [5000]')
    args = parser.parse_args()
    app.config['ROOT_DIR'] = args.root_dir
    app.run(host=args.host, port=args.port, debug=True)
