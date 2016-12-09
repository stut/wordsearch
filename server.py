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
wordlengths = []
for word in all_words:
    if len(word) not in wordlengths:
        wordlengths.append(len(word))
wordlengths.sort()
with open('cats.json', encoding='utf-8', mode='r') as f:
    all_cats = json.load(f)
catlist = list(all_cats.keys())
catlist.sort()

@app.route('/')
def index():
    return render_template('index.html', wordlengths=wordlengths, catlist=catlist, words=do_get_words())

@app.route('/cats')
def get_cats():
    return jsonify(catlist)

def do_get_words(cat=None, count=10, minlen=1, maxlen=10):
    retval = []
    maxtries = count * 1000
    while (len(retval) < count):
        if cat:
            selected = random.choice(all_cats[cat])
        else:
            selected = random.choice(all_words)
        if len(selected) >= minlen and len(selected) <= maxlen and selected not in retval:
            retval.append(selected)
        else:
            maxtries -= 1
            if maxtries <= 0:
                print('Searching...')
                for word in all_words:
                    if len(word) >= minlen and len(word) <= maxlen and word not in retval:
                        print('Found %s' % word)
                        retval.append(word)
                        if len(retval) == count:
                            break
                if len(retval) < count:
                    return retval
    return retval

@app.route('/words')
def get_words(cat=None):
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
    if cat and cat not in catlist:
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
        puzzle = {
            "grid": WordSearch.generate(width, height, words, format='text'),
            "words": '\n'.join(words)
        }
        #print(puzzle)
        filename = '%s-%04d.txt' % (time.time(), random.randint(1, 9999))
        with open(os.path.join(generated_dir, filename), 'w') as f:
            f.write(puzzle['grid'])
            f.write('\n')
            f.write(puzzle['words'])
        return jsonify(puzzle)
    except Exception as e:
        error = {
          "error": str(e)
        }
        #print(error)
        return jsonify(error)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6152)
