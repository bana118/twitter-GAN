import os
import sys
import re
import tkinter as tk
import PIL
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import json
import config
import tweepy
import pickle

# 同じディレクトリにconfig.pyを作成し、以下の値を定義しておく
consumer_key = config.CONSUMER_KEY
consumer_secret = config.CONSUMER_SECRET
access_key = config.ACCESS_TOKEN
access_secret = config.ACCESS_TOKEN_SECRET


def pushed():
    global img
    fileType = [("png", "*.png"), ("jpg", "*jpg")]  # 画像の種類を選択
    iDir = "/Users/Desktop/"
    f = filedialog.askopenfilename(filetypes=fileType, initialdir=iDir)
    if re.match(r"(.*)\.png", f):
        print("pngです")
        img = Image.open(open(str(f), "rb"))
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(bg="white", width=200, height=200)
        canvas.place(x=100, y=100)
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
    elif re.match(r"(.*)\.jpg", f):
        print("jpgです")
        img = Image.open(open(str(f), "rb"))
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(bg="white", width=200, height=200)
        canvas.place(x=100, y=100)
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
    else:
        print("それ以外です")


def GAN(processedTweets):
    print(processedTweets)

def getTweets():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    account_id = "nisizaki"
    processedTweets = [] #RTを除外、リプライの@～を削除、リンクのhttp～を除外
    for page in range(1,17):
        tweets = api.user_timeline(account_id, count=200, page=page)
        for tweet in tweets:
            text = tweet.text
            if not re.match(r"^RT.*", text) and not re.match(r"^https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", text):
                text = re.sub(r"@(.|_)* ", "", text)
                text = re.sub(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", "", text)
                processedTweets.append(text)

    

def run():
    global root
    root = tk.Tk()
    root.title("twitter-GAN")
    root.geometry("800x600+1000+10")
    root.protocol("WM_DELETE_WINDOW", root.quit)
    button = tk.Button(root, text="ファイル送信", command=pushed)
    testbutton = tk.Button(root, text="test", command=getTweets)
    button.pack()
    testbutton.pack()
    root.mainloop()


if __name__ == "__main__":
    run()
