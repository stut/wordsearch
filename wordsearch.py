import json
import random

class WordSearch:
    @staticmethod
    def generate(width, height, wordlist, format='json', seedrandom=True):
        if seedrandom:
            random.seed()
        words = list(wordlist)
        words.sort(key=lambda item: (-len(item), item))
        for i in range(len(words)):
            words[i] = words[i].upper()
        if len(words[0]) > width and len(words[0]) > height:
            raise Exception('Longest word is too big for the requested grid')

        ws = WordSearch(width, height)
        actionstack = []
        while len(words) > 0:
            currentword = words.pop(0)
            starts = ws.getPossibleStartingPoints(currentword)
            placed = False
            while len(starts) > 0 and not placed:
                idx = random.randrange(len(starts))
                start = starts[idx]
                starts.pop(idx)
                if ws.place(currentword, start):
                    """ Placed """
                    actionstack.append({
                        "grid": list(ws.grid),
                        "word": currentword,
                        "starts": list(starts)
                    })
                    placed = True
            if not placed:
                """ Failed to place, backtrack """
                if len(actionstack) == 0:
                    raise Exception('Impossible puzzle')
                prev = actionstack.pop()
                currentword = prev['word']
                ws.grid = prev['grid']
                starts = prev['starts']
                placed = False
        ws.fillgaps()
        if format == 'text':
            return ws.asText()
        return ws.asJson()

    UNOCCUPIED = '#'
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        for x in range(height):
            for y in range(width):
                self.grid.append(self.UNOCCUPIED)

    def asText(self):
        retval = ''
        idx = 0
        for c in self.grid:
            retval += c + ' '
            idx += 1
            if not idx % self.width:
                retval += "\n"
        return retval

    def asJson(self):
        retval = []
        idx = 0
        for x in range(self.height):
            retval.append([])
            for y in range(self.width):
                retval[x].append(self.grid[idx])
                idx += 1
        return json.dumps(retval)

    def idx(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return -1
        return y * self.width + x

    def getPossibleStartingPoints(self, word):
        l = len(word)
        possible_xs = []
        for x in range(self.width):
            if x + l < self.width or x - l >= 0:
                possible_xs.append(x)
        possible_ys = []
        for y in range(self.height):
            if y + l < self.height or y - l >= 0:
                possible_ys.append(y)
        starts = []
        for x in possible_xs:
            for y in possible_ys:
                if y - l >= 0:
                    starts.append([x, y, 'n'])
                    if x + l < self.width:
                        starts.append([x, y, 'ne'])
                    if x - l >= 0:
                        starts.append([x, y, 'nw'])
                if x + l < self.width:
                    starts.append([x, y, 'e'])
                if x - l >= 0:
                    starts.append([x, y, 'w'])
                if y + l < self.height:
                    starts.append([x, y, 's'])
                    if x + l < self.width:
                        starts.append([x, y, 'se'])
                    if x - l >= 0:
                        starts.append([x, y, 'sw'])
        return starts

    def move(self, x, y, dir):
        if dir == 'n':
            return [x, y-1]
        elif dir == 'ne':
            return [x + 1, y - 1]
        elif dir == 'e':
            return [x + 1, y]
        elif dir == 'se':
            return [x + 1, y + 1]
        elif dir == 's':
            return [x, y + 1]
        elif dir == 'sw':
            return [x - 1, y - 1]
        elif dir == 'w':
            return [x - 1, y]
        elif dir == 'nw':
            return [x - 1, y - 1]
        raise Exception('Invalid direction: [%s]' % dir)

    def place(self, word, start):
        x, y, dir = start
        fits = True
        for c in word:
            char = self.grid[self.idx(x, y)]
            if not char == self.UNOCCUPIED and not char == c.upper():
                fits = False
                break
            x, y = self.move(x, y, dir)
        if fits:
            x, y, dir = start
            for c in word:
                self.grid[self.idx(x, y)] = c.upper()
                x, y = self.move(x, y, dir)
        return fits

    def fillgaps(self):
        for i in range(len(self.grid)):
            if self.grid[i] == self.UNOCCUPIED:
                self.grid[i] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

if __name__ == '__main__':
    words = [
        "ruby",
        "blocks",
        "heredocs",
        "classes",
        "iterator",
        "module",
        "objects",
        "flexible",
        "each",
        "happy",
        "mutable",
        "lambda",
        "hash",
        "array"
      ]
    print(WordSearch.generate(10, 10, words))
    for word in words:
        print(word.lower())
