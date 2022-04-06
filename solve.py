from wordsearch import WordSearch

with open('10x10.txt', 'r') as f:
    text = f.read()

res = WordSearch.solve(text)
print(res)
