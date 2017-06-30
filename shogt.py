from __future__ import print_function
from collections import defaultdict
import random
import copy
import sys

MAX_WORD_LEN=8
WORD_LIST_FILE = 'wiki_and_unix.txt'
ALPHABET = [chr(l) for l in range(ord('A'), ord('Z')+1)]

log = print

def load_word_list(filename):
    print("loading word list")
    words = defaultdict(lambda: defaultdict(set) )
    for i, word in enumerate(open(filename)):
        word = word.strip()
        if i % 30000 == 0:
            log(i)
        if len(word) < 3 or len(word)> MAX_WORD_LEN:
            continue
        if word[0] == word[0].upper():
            continue
        word = word.upper()
        not_last = word[:-1]
        for letter in ALPHABET:
            words[letter][not_last.count(letter)].add(word)
    print("Loaded")
    return words

def would_have_remaining(words, anagram):
    last_letter = anagram[-1]
    n = anagram.count(last_letter)
    for i in range(n, MAX_WORD_LEN):
        for word in words[last_letter][i]:
            last_word_letter = word[-1]
            if word.count(last_word_letter) > anagram.count(last_word_letter):
                log("Word %s works!" % word)
                return True
            else:
                log("Word %s doesn't work  %s: (%d vs %d)" % (word, last_letter, word.count(last_letter), anagram.count(last_letter)))
        #log("No words left with %s %d times" % (last_letter, i))
    return False

def pare_down(words, anagram):
    excluded = set()
    for letter in set(anagram[:-1]):
        for i in range(anagram.count(letter)):
            if i in words[letter]:
                excluded |= words[letter][i]
    last_letter = anagram[-1]
    for i in range(anagram.count(last_letter)):
        if i in words[last_letter]:
            excluded |= words[last_letter][i]

    for letter in ALPHABET:
        for word_list in words[letter].values():
            word_list -= excluded

def random_word(word_list):
    for letter, counts in word_list.items():
        for count, words in counts.items():
            if len(words) > 0:
                return random.sample(words, 1)
    return None

def all_words(word_list):
    available_words = set()
    for letter, counts in word_list.items():
        for words in counts.values():
            available_words |= words
    return available_words

def find_exact_match(anagram, words):
    letters = anagram[:-1]
    possibilities = None

    anagram_sorted = sorted(anagram)
    for word in all_words(words):
        if sorted(word) == anagram_sorted and \
                word[-1] == anagram[-1]:
            return word

def test():
    word_list = load_word_list(WORD_LIST_FILE)
    print(find_exact_match("ATTCAK", word_list))
    print(find_exact_match("MORARY", word_list))
    print(find_exact_match("OGLXIENTN", word_list))

def computer_choice(anagram, word_list):
    possibilities = []
    for letter in ALPHABET:
        if len(anagram) >= 3:
            match = find_exact_match(anagram + letter, word_list)
        if len(anagram) < 3 or match is None:
            if would_have_remaining(word_list, anagram + letter):
                log("Possible: %s" % letter)
                possibilities.append(letter)
            else:
                log("Impossible: %s (no words)" % letter)
            #new_word_list = copy.deepcopy(word_list)
            #pare_down(new_word_list, anagram + letter)
            #possible = random_word(new_word_list)
            #if possible is not None:
            #    log("Possible: %s (%s)"% (letter, possible))
            #    possibilities.append(letter)
        else:
            log("Impossible: %s (%s)"%(letter, match))
    if len(possibilities) == 0:
        return None
    letter = random.choice(possibilities)
    pare_down(word_list, anagram + letter)
    return letter

def play_turn(anagram, word_list):

    letter = raw_input("Input next letter:").upper()
    while len(letter) != 1:
        letter = raw_input("Please input only one letter:").upper()

    if len(anagram) > 2:
        match = find_exact_match(anagram + letter, word_list)
        if match is not None:
            print("You lost! You spelled %s!" % match)
            return None
    anagram += letter
    if len(anagram) > 2:
        old_word_list = copy.deepcopy(word_list)
    pare_down(word_list, anagram)
    if len(anagram) > 2:
        if random_word(word_list) == None:
            print("You lost! No words left for anagram: %s" % anagram)
            available = all_words(old_word_list)
            sample = random.sample(available, 5 if len(available) >= 5 else len(available))
            print("I was going for one of: %s" % sample)
            return None
    letter = computer_choice(anagram, word_list)
    if letter == None:
        available = all_words(word_list)
        sample = random.sample(available, 5 if len(available) >= 5 else len(available))
        print("I lost! (I assume you were going for one of %s)" % sample)

        return None
    anagram += letter
    print(anagram)
    return anagram

if __name__ == '__main__':

    if '-l' in sys.argv:
        log = print
    else:
        log = lambda x : None

    word_list = load_word_list(WORD_LIST_FILE)
    anagram = play_turn("", word_list)
    while anagram is not None:
        anagram = play_turn(anagram, word_list)

