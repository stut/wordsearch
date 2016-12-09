from hashlib import sha1
import json
import os
import random
import time
from flask import Flask, render_template, request, jsonify

from wordsearch import WordSearch

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
generated_dir = os.path.join(root_dir, 'generated')
app = Flask(__name__.split('.')[0])

with open('words.json', encoding='utf-8', mode='r') as f:
    all_words = json.load(f)
word_lengths = []
for word in all_words:
    if len(word) not in word_lengths:
        word_lengths.append(len(word))
word_lengths.sort()
with open('cats.json', encoding='utf-8', mode='r') as f:
    all_cats = json.load(f)
cat_list = list(all_cats.keys())
cat_list.sort()


@app.route('/')
def index():
    return render_template('index.html', wordlengths=word_lengths, catlist=cat_list, words=do_get_words())


@app.route('/cats')
def get_cats():
    return jsonify(cat_list)


def do_get_words(cat=None, count=10, minlen=1, maxlen=10):
    retval = []
    maxtries = count * 1000
    while len(retval) < count:
        if cat:
            selected = random.choice(all_cats[cat])
        else:
            selected = random.choice(all_words)
        if len(selected) in range(minlen, maxlen+1) and selected not in retval:
            retval.append(selected)
        else:
            maxtries -= 1
            if maxtries <= 0:
                for word in all_words:
                    if len(word) in range(minlen, maxlen+1) and word not in retval:
                        retval.append(word)
                        if len(retval) == count:
                            break
                if len(retval) < count:
                    return retval
    return retval


@app.route('/words')
def get_words():
    cat = request.args.get('cat', None)
    count = int(request.args.get('count', 10))
    minlen = int(request.args.get('minlen', 1))
    maxlen = int(request.args.get('maxlen', 100))
    if count < 1 or count > 100:
        return jsonify({
            "error": "Count must be between 1 and 100"
        })
    if minlen < 0:
        return jsonify({
            "error": "Max length must be at least 5"
        })
    if maxlen < 5:
        return jsonify({
            "error": "Max length must be at least 5"
        })
    if minlen > maxlen:
        return jsonify({
            "error": "Max length must be greater than min length"
        })
    if cat and cat not in cat_list:
        return jsonify({
            "error": "Unknown category"
        })
    retval = do_get_words(cat=cat, count=count, minlen=minlen, maxlen=maxlen)
    if len(retval) < count:
        return jsonify({
            "error": "Unable to satisfy requirements"
        })
    return jsonify(retval)


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
        filename = '%s-%04d' % (time.time(), random.randint(1, 9999))
        filename = sha1(filename.encode('utf-8')).hexdigest()
        puzzle = {
            "grid": WordSearch.generate(width, height, words, fmt='text'),
            "words": '\n'.join(words),
            "url": 'http://wordsearch.stut.net/r/%s' % filename
        }
        with open(os.path.join(generated_dir, '%s.txt' % filename), 'w') as f:
            f.write(puzzle['grid'])
            f.write('\n')
            f.write(puzzle['words'])
        return jsonify(puzzle)
    except Exception as e:
        error = {
          "error": str(e)
        }
        return jsonify(error)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6152)
