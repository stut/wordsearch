import json
import random


class WordSearch:
    @staticmethod
    def generate(width, height, word_list, fmt='json', seed_random=True):
        if seed_random:
            random.seed()
        the_words = list(word_list)
        the_words.sort(key=lambda item: (-len(item), item))
        for i in range(len(the_words)):
            the_words[i] = the_words[i].upper()
        if len(the_words[0]) > width and len(the_words[0]) > height:
            raise Exception('Longest word is too big for the requested grid')

        ws = WordSearch(width, height)
        action_stack = []
        while len(the_words) > 0:
            current_word = the_words.pop(0)
            starts = ws.get_possible_starting_points(current_word)
            placed = False
            while len(starts) > 0 and not placed:
                idx = random.randrange(len(starts))
                start = starts[idx]
                starts.pop(idx)
                if ws.place(current_word, start):
                    """ Placed """
                    action_stack.append({
                        "grid": list(ws.grid),
                        "word": current_word,
                        "starts": list(starts)
                    })
                    placed = True
            if not placed:
                """ Failed to place, backtrack """
                if len(action_stack) == 0:
                    raise Exception('Impossible puzzle')
                prev = action_stack.pop()
                current_word = prev['word']
                ws.grid = prev['grid']
                starts = prev['starts']
                placed = False
        ws.fill_gaps()
        if fmt == 'text':
            return ws.as_text()
        return ws.as_json()

    @staticmethod
    def move(x, y, direction):
        if direction == 'n':
            return [x, y-1]
        elif direction == 'ne':
            return [x + 1, y - 1]
        elif direction == 'e':
            return [x + 1, y]
        elif direction == 'se':
            return [x + 1, y + 1]
        elif direction == 's':
            return [x, y + 1]
        elif direction == 'sw':
            return [x - 1, y - 1]
        elif direction == 'w':
            return [x - 1, y]
        elif direction == 'nw':
            return [x - 1, y - 1]
        raise Exception('Invalid direction: [%s]' % direction)

    UNOCCUPIED = '#'

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        for x in range(height):
            for y in range(width):
                self.grid.append(self.UNOCCUPIED)

    def as_text(self):
        retval = ''
        idx = 0
        for c in self.grid:
            retval += c + ' '
            idx += 1
            if not idx % self.width:
                retval += "\n"
        return retval

    def as_json(self):
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

    def get_possible_starting_points(self, this_word):
        l = len(this_word)
        possible_xs = range(0, self.width)
        possible_ys = range(0, self.height)
        starts = []
        for x in possible_xs:
            for y in possible_ys:
                if y - l + 1 >= 0:
                    starts.append([x, y, 'n'])
                    if x + l < self.width:
                        starts.append([x, y, 'ne'])
                    if x - l >= 0:
                        starts.append([x, y, 'nw'])
                if x + l <= self.width:
                    starts.append([x, y, 'e'])
                if x - l + 1 >= 0:
                    starts.append([x, y, 'w'])
                if y + l <= self.height:
                    starts.append([x, y, 's'])
                    if x + l - 1 < self.width:
                        starts.append([x, y, 'se'])
                    if x - l + 1 >= 0:
                        starts.append([x, y, 'sw'])
        return starts

    def place(self, word, start):
        x, y, direction = start
        fits = True
        for c in word:
            char = self.grid[self.idx(x, y)]
            if not char == self.UNOCCUPIED and not char == c.upper():
                fits = False
                break
            x, y = self.move(x, y, direction)
        if fits:
            x, y, direction = start
            for c in word:
                self.grid[self.idx(x, y)] = c.upper()
                x, y = self.move(x, y, direction)
        return fits

    def fill_gaps(self):
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
