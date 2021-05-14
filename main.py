"""
CS 6120 Spring 2021 Final Project Chatbot
Odin Thorsen
Rohan Subramaniam
A simple chat bot that uses a corpus of conversations from movies to generate a response to the user. In the case
a good enough response cannot be generated from the corpus, a Recurrent Neural Network trained on the same conversations
generates a response.
The RNN weights and model are trained and saved because of the 15-45 minute training time depending on the depth and
amount of the corpus used.
Code referenced from https://towardsdatascience.com/personality-for-your-chatbot-with-recurrent-neural-networks-2038f7f34636
for the RNN implementation
"""

import itertools
import logging
import string

import nltk
from keras.layers import Dense, BatchNormalization
from keras.layers import LSTM, TimeDistributed
from keras.layers.embeddings import Embedding
from keras.models import Sequential
from keras.models import model_from_json
from keras.preprocessing import sequence
from keras.preprocessing.text import text_to_word_sequence

from model.TextGenerator import TextGenerator
from word_vector_math import *

# Padding tokens for the sentence text. Helps with disambiguating sentence boundaries
START_TOKEN = "SENTENCE_START"
END_TOKEN = "SENTENCE_END"
UNKNOWN_TOKEN = "UNKNOWN_TOKEN"
PADDING_TOKEN = "PADDING"


def parse_text():
    """
    parses text into padded sentences and raw list of sentences
    :return: padded sentences and raw string sentences
    """
    f = open("resources/movie_lines.txt", "r", encoding="iso-8859-1")
    sent_tokens = []
    line_sents = []
    sents = []

    # Read and parse each line from the file ignoring metadata except line number
    while True:
        line = f.readline()
        if not line:
            break
        parts = line.split(" +++$+++ ")
        line_num = int(parts[0][1:])  # line number minus the "L"
        line_text = parts[4][:-1]  # trims off \n character
        line_sents.append((line_num, line_text))

    # Sort based on line number to have related lines appear sequentially
    for sent in sorted(line_sents):  # pad and return sorted sentences
        temp = [START_TOKEN] + text_to_word_sequence(sent[1]) + [END_TOKEN]
        sent_tokens.append(temp)
        sents.append(sent[1])

    f.close()

    return sent_tokens, sents


def get_words_mappings(tokenized_sentences, vocabulary_size):
    """
    Maps words to indices and vice versa for translation to and from the RNN model
    :param tokenized_sentences: Padded word tokenized sentences
    :param vocabulary_size: max size of vocab
    :return: index to word and word to index mappings
    """
    # we can rely on nltk to quickly get the most common words, and then limit our vocabulary to the specified size
    frequence = nltk.FreqDist(itertools.chain(*tokenized_sentences))
    vocab = frequence.most_common(vocabulary_size)
    index_to_word = [x[0] for x in vocab]
    # Add padding for index 0
    index_to_word.insert(0, PADDING_TOKEN)
    # Append unknown token (with index = vocabulary size + 1)
    index_to_word.append(UNKNOWN_TOKEN)
    word_to_index = dict([(w,i) for i,w in enumerate(index_to_word)])
    return index_to_word, word_to_index


def train_model(sents, word_to_index, sent_max_len, vocabulary_size):
    """
    Creates, trains, and saves a Recurrent Neural Network (RNN) model for text generation
    This is only called if changing the model parameters and not in normal chat bot operation
    :param sents: padded tokenized sentences
    :param word_to_index: word to index mappings
    :param sent_max_len: max sent length
    :param vocabulary_size: size of vocab
    :return:
    """
    # Train on 1/10 of the corpus for time sake
    train_size = min(int(len(sents) / 10), 100000)
    print("Train size: {}".format(train_size))
    print("sents size: {}".format(len(sents)))
    train_data = [[word_to_index.get(w, word_to_index[UNKNOWN_TOKEN]) for w in sent] for sent in
                  sents[:train_size]]

    # pad sentences to fixed length (pad with 0s if shorter, truncate if longer)
    train_data = sequence.pad_sequences(train_data, maxlen=sent_max_len, dtype='int32', padding='post',
                                        truncating='post')

    # create training data for rnn:
    # input is sentence truncated from last word, output is sentence truncated from first word
    X_train = train_data[:, :-1]
    y_train = train_data[:, 1:]
    X_train = X_train.reshape([X_train.shape[0], X_train.shape[1], 1])
    y_train = y_train.reshape([y_train.shape[0], y_train.shape[1], 1])

    # Define model and parameters
    hidden_size = 512
    embedding_size = 128

    # model with embedding
    model = Sequential()
    model.add(Embedding(vocabulary_size, embedding_size, mask_zero=True))
    model.add(BatchNormalization())
    model.add(LSTM(hidden_size, return_sequences=True, activation='relu'))
    model.add(TimeDistributed(Dense(vocabulary_size, activation='softmax')))

    # model.summary()  # Use if you want to check before compiling

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])

    # Train model
    num_epoch = 4
    batch_size = 32
    model.fit(X_train, y_train, epochs=num_epoch, batch_size=batch_size, verbose=1)

    # export model (architecture)
    model_path = "model_vocab_{}_max_{}.json".format(vocabulary_size, sent_max_len)
    model_json = model.to_json()
    with open(model_path, "w") as f:
        f.write(model_json)

    # export model weights
    weights_path = "model_weights_{}_max_{}.hdf5".format(vocabulary_size, sent_max_len)
    model.save_weights(weights_path)


def generate(index_to_word, word_to_index, sent_max_len, user_input=None):
    """
    Generates a sentence using the RNN model in case the TFIDF score was too low

    :param index_to_word: index to word mapping
    :param word_to_index: word to index mapping
    :param sent_max_len: max sentence length
    :param user_input: user input sentence for seed
    :return: 5 sentences generated from the RNN
    """

    model_path = "resources/model_vocab_6002_max_8.json"  # Pre-trained model to save 30+ minutes on startup
    weights_path = "resources/model_weights_6002_max_8.hdf5"
    # Load previously saved model
    with open(model_path, 'r') as f:
        model = model_from_json(f.read())
    # Load weights into model
    model.load_weights(weights_path)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # instantiate Text Generator
    text_gen = TextGenerator(model, index_to_word, word_to_index, sent_max_len=sent_max_len)
    # generate 2 new sentences
    n_sents = 2
    results = []
    for _ in range(n_sents):
        res = text_gen.indices_to_words(text_gen.get_sentence(5, seed=user_input))
        results.append(res)
    return results


def bot(train=False, gen=False):
    """
    Core chat bot loop program. Parses text for the TFIDF and RNN models and stores for the loop

    :param train: bool True for training new set
    :param gen: bool True for generating only text without input
    :return:
    """
    padded_sents, docs = parse_text()
    vocabulary_size = 6000
    sent_max_len = 8

    index_to_word, word_to_index = get_words_mappings(padded_sents, vocabulary_size)
    vocabulary_size = len(index_to_word)

    # DEBUGGING FLAGS
    ################################
    if train:  # Used if we want to train the model and NOT activate the bot.
        train_model(padded_sents, word_to_index, sent_max_len, vocabulary_size)
    elif gen:  # Used to just print out RNN output without trying TF-IDF
        print(generate(index_to_word, word_to_index, sent_max_len))
    #################################

    # If we're not using a debug flag, run the chat bot
    else:
        # tf_idf on 1/10 of corpus for time efficiency purposes
        d_l = len(docs) / 100
        print(d_l)
        docs = docs[0:int(d_l)]
        [tf_idfs, lexicon, idfs] = tf_idf(docs)
        s = ""
        print("Hello there, what’s on your mind?")
        while s != "I don't want to talk to you anymore":
            s = input()
            user_input_tf_idf_vec = td_idf_erizer(s, lexicon, idfs)
            max_similarity = -99999
            response = "I'm sorry, I don't understand you"

            for i, tf_idf_vec in enumerate(tf_idfs):
                similarity = cosine_similarity(user_input_tf_idf_vec, tf_idf_vec)
                if similarity > max_similarity:
                    max_similarity = similarity
                    response = docs[i + 1]
            print("Cosine similarity: " + str(max_similarity))
            if max_similarity < 0.5:
                print("Generating RNN response, one moment please...")
                response = generate(index_to_word, word_to_index, sent_max_len)[1]
            print(response)


if __name__ == '__main__':
    bot()
