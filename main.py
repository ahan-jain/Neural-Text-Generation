import random
import pickle

import numpy as np
import pandas as pd
from nltk.tokenize import RegexpTokenizer

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Activation
from tensorflow.keras.optimizers import RMSprop

text_data = pd.read_csv("fake_or_real.csv")

text = list(text_data.text.values)
combined_text = " ".join(text)

partial_text = combined_text[:100000]

tokenizer = RegexpTokenizer(r"\w+")
tokens = tokenizer.tokenize(partial_text.lower())

unique_tokens = np.unique(tokens)
unique_token_index = {token : idx for idx, token in enumerate(unique_tokens)}

initial_words = 10
input = []
next_words = []

for i in range(len(tokens) - initial_words):
    input.append(tokens[i:i + initial_words])
    next_words.append(tokens[i + initial_words])

X = np.zeros((len(input), initial_words, len(unique_tokens)), dtype=bool)
y = np.zeros((len(next_words), len(unique_tokens)), dtype=bool)

for i, words in enumerate(input):
    for j, word in enumerate(words):
        X[i, j, unique_token_index[word]] = 1
    y[i, unique_token_index[next_words[i]]] = 1

model = Sequential()
model.add(LSTM(128, input_shape=(initial_words, len(unique_tokens)), return_sequences=True))
model.add(LSTM(128))
model.add(Dense(len(unique_tokens)))
model.add(Activation("softmax"))

model.compile(loss="categorical_crossentropy", optimizer=RMSprop(learning_rate=0.01), metrics = ["accuracy"])
model.fit(X, y, batch_size=128, epochs = 300, shuffle=True)

model.save("text_gen_model_v2.h5")

model = load_model("text_gen_model_v2.h5")

def predict_next_word(input, best):
    input = input.lower()
    X = np.zeros((1, initial_words, len(unique_tokens)))
    for i, word in enumerate(input.split()):
        X[0, i, unique_token_index[word]] = 1

    predictions = model.predict(X)[0]
    return np.argpartition(predictions, -best)[-best:]

possible = predict_next_word("I want to see what is possible in this world", 5)

print([unique_tokens[idx] for idx in possible])

def generate_text(input, length, choices=3):
    sequence = input.split()
    current_pos = 0
    for i in range(length):
        sub_sequence = " ".join(tokenizer.tokenize(" ".join(sequence).lower())[current_pos:current_pos+initial_words])
        try:
            choice = unique_tokens[random.choice(predict_next_word(sub_sequence, creativity))]
        except:
            choice = random.choice(unique_tokens)
        sequence.append(choice)
        current_pos+=1
    return " ".join(sequence)

generate_text("I want to see what is possible in this world", 20, 5)

