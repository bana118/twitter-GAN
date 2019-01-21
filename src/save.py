#debug用にtweetをファイルに保存するコード
import tweepy, re, os, config, codecs

# 同じディレクトリにconfig.pyを作成し、以下の値を定義しておく
consumer_key = config.CONSUMER_KEY
consumer_secret = config.CONSUMER_SECRET
access_key = config.ACCESS_TOKEN
access_secret = config.ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)
account_id = "nisizaki"
processedTweets = []  # RTを除外、リプライの@～を削除、リンクのhttp～を除外
for page in range(1, 17):
    tweets = api.user_timeline(account_id, count=200, page=page)
    for tweet in tweets:
        text = tweet.text
        if not re.match(r"^RT.*", text) and not re.match(r"^https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", text):
            text = re.sub(r"@.* ", "", text)
            text = re.sub(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", "", text)
            if not text == "":
                processedTweets.append(text)

str_ = '&split'.join(processedTweets) #&splitを区切り文字として使う。&splitがtweetに含まれないことを祈る

with open("data.txt", 'wt', encoding="UTF-8") as f:
    f.write(str_)
