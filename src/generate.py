#ツイートを学習し、それらしいツイートを生成するコード
import numpy as np

from keras.layers.core import Activation, Dense, Dropout
from keras.layers.cudnn_recurrent import CuDNNLSTM
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from keras import regularizers
from keras.optimizers import RMSprop

from janome.tokenizer import Tokenizer
import collections



def CuDNNLSTMmodel():
    model = Sequential()
    model.add(CuDNNLSTM(512, return_sequences=True, input_shape=(2,2)))
    model.add(Dropout(0.2))
    model.add(CuDNNLSTM(128, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(CuDNNLSTM(64, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(CuDNNLSTM(32))
    model.add(Dropout(0.2))
    model.add(Dense(2, activation='softmax'))
    return model

def LSTMmodel(maxlen, nb):
    model = Sequential()
    model.add(LSTM(128, input_shape=(maxlen, nb)))
    model.add(Dense(nb))
    model.add(Activation("softmax"))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01))
    return model

def generateToken(tweetlist):
    #maxlen個の連続した単語から次の単語を予測し、stepずつずらしながらデータセットを作成
    maxlen = 5
    step = 1

    #str_ = "\n".join(tweetlist)
    #tokens = Tokenizer().tokenize(str_, wakati=True)
    #nb_tokens = len(set(tokens)) #語彙数
    #tokens_to_num = dict((t, i) for i, t in enumerate(set(tokens)))
    #num_to_tokens = dict((i, t) for i, t in enumerate(set(tokens)))

    tokens_to_num = {}
    count = 0
    input_tokens = []
    label_tokens = []
    for tweet in tweetlist:
        tokens_in_tweet = Tokenizer().tokenize(tweet, wakati=True)
        for token_in_tweet in tokens_in_tweet:
            if not token_in_tweet in tokens_to_num:
                tokens_to_num[token_in_tweet] = count
                count += 1
        if len(tokens_in_tweet) > maxlen:
            for i in range(0, len(tokens_in_tweet) - maxlen, step):
                input_tokens.append(tokens_in_tweet[i:i + maxlen])
                label_tokens.append(tokens_in_tweet[i + maxlen])
    nb_tokens = len(tokens_to_num)
    num_to_tokens = dict([(value, key) for (key, value) in tokens_to_num.items()])
    X = np.zeros((len(input_tokens), maxlen, nb_tokens), dtype=np.bool)
    y = np.zeros((len(input_tokens), nb_tokens), dtype=np.bool)
    for i, input_token in enumerate(input_tokens):
        for j, tk in enumerate(input_token):
            X[i, j, tokens_to_num[tk]] = 1
        y[i, tokens_to_num[label_tokens[i]]] = 1
    np.save("test_X.npy", X)
    np.save("test_y.npy", y)

def test():
    X = np.load("data/test_X.npy")
    y = np.load("data/test_y.npy")
    model = LSTMmodel(X.shape[1], X.shape[2])
    model.fit(X, y, batch_size=128, epochs=1)

if __name__ == "__main__":
    #f = open("data/nisizaki.txt", "r", encoding="UTF8")
    #tweet_list = f.read().split("&split")
    #generateToken(tweet_list)
    test()