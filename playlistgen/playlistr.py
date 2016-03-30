import pandas as pd
import numpy as np
import pickle
from flask import Flask, render_template, redirect, url_for, request, abort
import pymongo
from flask.ext.pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'music'
mongo = PyMongo(app)

with open('./static/songbysong_717x717.pkl', 'rb') as f:
    song_by_songdf = pickle.load(f)

playlist = []
playlistids = []

def choose(seed_song):
    songlist = list(song_by_songdf[seed_song].sort_values(ascending=False, inplace=False).index)
    choose = abs(int(np.random.normal(0, 16)))
    while(choose >= len(songlist)):
        choose = abs(int(np.random.normal(0, 16)))
    choose = songlist[choose]
    return choose

def generate_playlist(seed_song, playlist=playlist):
    info = mongo.db.songs.find_one_or_404({"id":seed_song}, {"title":1, "artist":1})
    playlist.append((info['title'], info['artist']))
    playlistids.append(seed_song)
    ch = choose(seed_song)
    while ch in playlistids:
        ch = choose(seed_song)
    return ch

def format_playlist(playlist):
    formatted = []
    for num, track in enumerate(playlist):
        formatted.append(str(num+1)+ ". " + str(track[0]) + " by " + str(track[1]))
    return formatted

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        if request.form['songtitle'] and request.form['artist']:
            artist = request.form['artist']
            title = request.form['songtitle']
            song = mongo.db.songs.find_one_or_404({'artist':artist, 'title':title})
        if request.form['songtitle']:
            title = request.form['songtitle']
            song = mongo.db.songs.find_one_or_404({'title':title})
        if request.form['artist']:
            artist = request.form['artist']
            song = mongo.db.songs.find_one_or_404({'artist':artist})
        songid = song['id']
        print "HOME PAGE POST"
        return make_playlist(songid)
    else:
        print "HOME PAGE GET"
        return render_template('layout.html')

@app.route('/song/<songid>')
def make_playlist(songid):
    seed = songid
    playlist = []
    playlistids = []
    for x in range(20):
        seed = generate_playlist(seed, playlist=playlist)
    formatted = format_playlist(playlist)
    print str(formatted)

    return render_template('layout.html', playlist=formatted)

@app.route('/song/<songid>')
def song_profile(songid):
    assert mongo.db.name == 'music', 'wrong dbname: %s' % mongo.db.name
    song = mongo.db.songs.find_one_or_404({'id':songid})
    song = str(song)
    return song

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)