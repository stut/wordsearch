import json
import random


class WordSearch:
    @staticmethod
    def generate(width, height, word_list, fmt='json', seed_random=True):
        """
        Generates a puzzle and returns it in the requested format (json or text).
        """
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
    def solve(puzzle_text, word_list=[]):
        """
        Solves a puzzle. If the supplied word_list is empty it is assumed
        that puzzle_text is in the format outputted by the as_text method
        followed by a blank line and then the word list, one word per
        line.
        """
        if len(word_list) == 0:
            tmp = puzzle_text
            puzzle_text = ''
            parsing_words = False
            for line in tmp.split('\n'):
                if parsing_words:
                    if len(line.strip()) > 0:
                        word_list.append(line.strip())
                else:
                    if len(line.strip()) > 0:
                        puzzle_text = "%s\n%s" % (puzzle_text, line.strip())
                    else:
                        parsing_words = True
        res = {}
        ws = WordSearch(puzzle_text=puzzle_text)
        for this_word in word_list:
            res[this_word] = ws.find(this_word)
        return res

    @staticmethod
    def move(x, y, direction):
        """
        Moves the provided coordinates one step in the given direction.
        """
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

    def __init__(self, width=0, height=0, puzzle_text=None):
        """
        Initialise a WordSearch puzzle. If puzzle_text is not None the other
        parameters will be ignored and the puzzle will be created from the
        contents.
        """
        if puzzle_text:
            lines = puzzle_text.strip().split('\n')
            self.width = len(lines[0].strip().replace(' ', ''))
            self.height = len(lines)
            for idx in range(self.height):
                lines[idx] = lines[idx].strip().replace(' ', '')
                if len(lines[idx]) == width:
                    raise Exception('All lines in the puzzle must be the same length')
        elif width < 1 or height < 1:
            raise Exception('Dimensions invalid and no puxxle text provided')
        else:
            self.width = width
            self.height = height

        self.grid = []
        for y in range(self.height):
            for x in range(self.width):
                self.grid.append(self.UNOCCUPIED)

        if puzzle_text:
            for y in range(self.height):
                for x in range(self.width):
                    self.grid[self.idx(x, y)] = lines[y][x].upper()

    def as_text(self, with_spaces=True):
        """
        Render the puzzle as text.
        """
        retval = ''
        idx = 0
        for c in self.grid:
            retval += c
            if with_spaces:
                retval += ' '
            idx += 1
            if not idx % self.width:
                retval = "%s\n" % retval.strip()
        return retval

    def as_json(self):
        """
        Return the puzzle in JSON format (2-dimensional array).
        """
        retval = []
        idx = 0
        for x in range(self.height):
            retval.append([])
            for y in range(self.width):
                retval[x].append(self.grid[idx])
                idx += 1
        return json.dumps(retval)

    def find(self, w):
        """
        Attempt to find the location of a word in the puzzle.
        If found returns an array of [x, y, direction].
        If not found returns None.
        """
        w = w.upper()
        first_letter = w[0]
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[self.idx(x, y)] == first_letter:
                    for direction in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']:
                        current_letter = 1
                        current_x = x
                        current_y = y
                        found = True
                        while found and current_letter < len(w):
                            (current_x, current_y) = self.move(current_x, current_y, direction)
                            if current_x < 0 or current_x >= self.width or current_y < 0 or current_y >= self.height:
                                found = False
                                break
                            if not self.grid[self.idx(current_x, current_y)] == w[current_letter]:
                                found = False
                            else:
                                current_letter += 1
                        if found:
                            return [x + 1, y + 1, direction]
        return None

    def idx(self, x, y):
        """
        Translates x and y coordinates to an index in the grid array.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return -1
        return y * self.width + x

    def get_possible_starting_points(self, this_word):
        """
        Given a word find all possible start coordinates. This method
        essentially gives every coordinate+direction combination in the grid
        where the word would fit, ignoring the contents of the grid.
        """
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
        """
        Attempt to place a word at the given start coordinates. The start
        coordinates must include the direction in the format
        [x, y, direction].
        """
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
        """
        Fills all unoccupied spaces in the grid with random letters.
        """
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
