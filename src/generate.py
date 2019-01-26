#ツイートを学習し、それらしいツイートを生成するコード
import numpy as np

from keras.layers.core import Activation, Dense, Dropout
from keras.layers.cudnn_recurrent import CuDNNLSTM
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint, LambdaCallback
from keras import regularizers
from keras.optimizers import RMSprop

from janome.tokenizer import Tokenizer
import collections
import random, sys

#苦し紛れ
char_indices = {}
indices_char = {}
text = ""
chars = ""
pre_model = Sequential()

def CuDNNLSTMmodel(maxlen, nb):
    model = Sequential()
    model.add(CuDNNLSTM(128, input_shape=(maxlen, nb)))
    model.add(Dense(nb))
    model.add(Activation("softmax"))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01))
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
    #np.save("data/test_X.npy", X)
    #np.save("data/test_y.npy", y)
    global char_indices, indices_char, text, chars, pre_model
    char_indices = tokens_to_num
    indices_char = num_to_tokens
    text = list(tokens_to_num.keys())
    chars = text
    pre_model = CuDNNLSTMmodel(X.shape[1], X.shape[2])
    print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
    pre_model.fit(X, y, batch_size=128, epochs=60, callbacks=[print_callback])

def test():
    X = np.load("data/test_X.npy")
    y = np.load("data/test_y.npy")
    model = LSTMmodel(X.shape[1], X.shape[2])
    print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
    model.fit(X, y, batch_size=128, epochs=60, callbacks=[print_callback])


def on_epoch_end(epoch, logs):
    maxlen = 5
    #f = open("data/nisizaki.txt", "r", encoding="UTF8")
    #tweet_list = f.read().split("&split")
    #text = Tokenizer().tokenize(" ".join(tweet_list), wakati=True)
    #chars = text
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    # モデルは40文字の「文」からその次の「字」を予測するものであるため、
    # その元となる40文字の「文」を入力テキストからランダムに選ぶ
    start_index = random.randint(0, len(text) - maxlen - 1)
    #start_index = 0

    # diversityとは多様性を意味する言葉
    # この値が低いとモデルの予測で出現率が高いとされた「字」がそのまま選ばれ、
    # 高ければそうでない「字」が選ばれる確率が高まる
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print('----- diversity:', diversity)

        generated = ''

        # 元にする「文」を選択
        sentence = "".join(text[start_index: start_index + maxlen])
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)
    for i in range(50):

        # 現在の「文」の中のどの位置に何の「字」があるかのテーブルを
        # フィッティング時に入力したxベクトルと同じフォーマットで生成
        # 最初の次元は「文」のIDなので0固定
        x_pred = np.zeros((1, maxlen, len(chars)))
        for t, char in enumerate(text[start_index: start_index + maxlen]):
            x_pred[0, t, char_indices[char]] = 1.

        # 現在の「文」に続く「字」を予測する
        preds = pre_model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = indices_char[next_index]

        # 予測して得られた「字」を生成し、「文」に追加
        generated += next_char

        # モデル入力する「文」から最初の文字を削り、予測結果の「字」を追加
        # 例：sentence 「これはドイツ製」
        #     next_char 「の」
        #     ↓
        #     sentence 「れはドイツ製の」
        sentence = sentence[1:] + next_char

        sys.stdout.write(next_char)
        sys.stdout.flush()
    print()

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

if __name__ == "__main__":
    f = open("data/nisizaki.txt", "r", encoding="UTF8")
    tweet_list = f.read().split("&split")
    generateToken(tweet_list)