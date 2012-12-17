from collections import defaultdict, Counter
from itertools import combinations
from string import ascii_lowercase as alphabet

import multiprocessing
import readline

board_string = raw_input("Enter the letters on the board: ")[:25].lower()
board = Counter(board_string)

words = defaultdict(set)
with open('letterpress_dict') as d:
    for word in d:
        word = word.strip()
        for letter in board:
            if letter in word:
                words[letter].add(word)

# look at partitioning the letters differently to increase cache hits
cache = {}
def all_words_with(letters):
    letters = frozenset(letters)
    if letters not in cache:
        if len(letters) >= 3: # so subproblems have at least a pair of letters
            even = (letter for i, letter in enumerate(letters) if i % 2 == 0)
            odd = (letter for i, letter in enumerate(letters) if i % 2 == 1)
            cache[letters] = all_words_with(even).intersection(all_words_with(odd))
        else:
            cache[letters] = reduce(lambda x, y: x.intersection(y),
                    (words[letter] for letter in letters))

    return cache[letters]

def all_words(letters):
    return (word for word in all_words_with(letters)
                if not Counter(word) - Counter(letters))
    # the count of the letters is greater than the count of the letters in the word

def score(word):
    s = 0
    for letter, count in Counter(word).iteritems():
        s += (2 * them[letter] * count)
        count -= them[letter]
        s += (1 * neutral[letter] * count)
    return s

neutral = board
while neutral:
    us = Counter(raw_input("Enter your letters: ").lower())
    them = Counter(raw_input("Enter their letters: ").lower())
    neutral = board - us - them

    max_word = 0
    max_score = 0
    for count in range(15, 0, -1):
        # parallelize ?
        for letters in combinations(board, count): # branch
            for word in all_words(letters):
                s = score(word)
                if s > max_score:
                    max_score = s
                    max_word = word

        if max_score > count * 1.5: # bound (set higher for better scores and lower perf)
            break

    print max_word
    for wordset in words.itervalues():
        if max_word in wordset:
            wordset.remove(max_word)

    for wordset in cache.itervalues():
        if max_word in wordset:
            wordset.remove(max_word)

print 'done'
