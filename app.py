from flask import Flask, render_template, request, jsonify
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

original_guess_list = []  # Maintain the original guess list
guess_list = []
feedback = []
max_guesses = 6  # Set the maximum number of guesses

try:
    with open('wordlist.txt') as f:
        for line in f:
            guess_list.append(line.strip())
except FileNotFoundError:
    print("File not found")

label_encoder = LabelEncoder()

@app.route('/')
def index():
    return render_template('index.html', guess_list=guess_list, feedback=feedback)

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    global guess_list, feedback, label_encoder

    guess = request.form.getlist('guess[]')
    feedback = request.form.getlist('feedback[]')

    if all(color == 'g' for color in feedback):
        return jsonify({'result': "Well Done! Guess"})

    suggestions = []
    for word in guess_list:
        valid_word = True

        if len(word) != 5 or len(guess) != 5 or len(feedback) != 5:
            valid_word = False
        else:
            for i in range(5):
                if feedback[i] == "w" and guess[i] in word and guess.count(guess[i]) == 1:
                    valid_word = False
                    break
                elif feedback[i] == "g" and guess[i] != word[i]:
                    valid_word = False
                    break
                elif feedback[i] == "y" and guess[i] not in word:
                    valid_word = False
                    break
                elif feedback[i] == "y" and guess[i] == word[i]:
                    valid_word = False
                    break

        if valid_word:
            suggestions.append(word)
        guess_list = suggestions

    frequencies = letter_frequencies(guess_list)
    scores = calculate_word_score(guess_list, frequencies)
    suggestion = find_best_word(guess_list, scores)

    suggestions.append(suggestion)

    return jsonify({'suggestions': suggestions})

def letter_frequencies(possible_words):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    arr = {}
    for c in alphabet:
        freq = [0, 0, 0, 0, 0]
        for i in range(0, 5):
            for w in possible_words:
                if w[i] == c:
                    freq[i] += 1
        arr.update({c: freq})
    return arr

def calculate_word_score(possible_words, frequencies):
    words = {}
    max_freq = [0, 0, 0, 0, 0]
    for c in frequencies:
        for i in range(0, 5):
            if max_freq[i] < frequencies[c][i]:
                max_freq[i] = frequencies[c][i]
    for w in possible_words:
        score = 1
        for i in range(0, 5):
            c = w[i]
            score *= 1 + (frequencies[c][i] - max_freq[i]) ** 2
        words.update({w: score})
    return words

def find_best_word(possible_words, scores):
    max_score = float('inf')  # start with a high score
    best_word = "words"  # start with a random word
    for w in possible_words:
        if scores[w] < max_score:
            max_score = scores[w]
            best_word = w
    return best_word

if __name__ == '__main__':
    app.run(debug=True)
