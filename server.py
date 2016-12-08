import os
from flask import Flask, send_from_directory, request, jsonify

from wordsearch import WordSearch

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__.split('.')[0])

@app.route('/')
def index():
    return send_from_directory(root_dir, 'index.html')

@app.route('/create', methods=['POST'])
def create():
    width = int(request.form['width'])
    height = int(request.form['height'])
    words = request.form['words'].splitlines()
    for idx in range(len(words), 0):
        if len(words[idx].trim()) == 0:
            words.pop(idx)
        else:
            words[idx] = words[idx].trim()

    try:
        if len(words) == 0:
            raise Exception('At least one word is required!')
        if not width or not height:
            raise Exception('Please specify a valid grid size!')
        if width > 100 or height > 100:
            raise Exception('Maximum of 100 rows and columns!')
        puzzle = {
            "grid": WordSearch.generate(width, height, words, format='text'),
            "words": '\n'.join(words)
        }
        print(puzzle)
        return jsonify(puzzle)
    except Exception as e:
        error = {
          "error": str(e)
        }
        print(error)
        return jsonify(error)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
