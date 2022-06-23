import numpy as np
from flask import Flask, render_template, request
import spotipy
import wget
from pydub import AudioSegment
from scipy.fft import *
from scipy.io import wavfile
from spotipy.oauth2 import SpotifyClientCredentials
import os
import os.path

app = Flask(__name__)

cid = '91165de706b54f21976471b85b978e0f'
secret = 'f4c12a3983d246699326d3ccd1ae0f44'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        search_text = request.form['nm']
        if not search_text:
            string = "doamne feri"
            print(string)
            return render_template('base.html', no_error=string)
        results = sp.search(q=search_text, limit=1)
        songlist = results['tracks']['items']
        if not songlist:
            string = "doamne feri"
            print(string)
            return render_template('base.html', search_error=string)
        tracks = results['tracks']
        for item in tracks['items']:
            song_url = item['preview_url']
            # not all songs return a 30 seconds preview, try Abba
            if not song_url:
                string = "doamne feri"
                print(string)
                return render_template('base.html', error=string)
            else:
                url_name = wget.filename_from_url(song_url)
                filename = url_name + '.mp3'
                print(filename)
                if not os.path.isfile(filename):
                    wget.download(song_url, filename)
            sound = AudioSegment.from_mp3(filename)
            wf = url_name + '.wav'
            sound.export(wf, format="wav")
            # Open the file and convert to mono
            sr, data = wavfile.read(wf)
            # if there is any data, take only one audio channel
            if data.ndim > 1:
                data = data[:, 0]
            else:
                pass
            print()
            start_time = 0
            end_time = 10000
            dataToRead = data[int(start_time * sr / 1000): int(end_time * sr / 1000) + 1]
            # Fourier Transform
            N = len(dataToRead)
            yf = rfft(dataToRead)
            xf = rfftfreq(N, 1 / sr)
            # Get the most dominant frequency and return it
            idx = np.argmax(np.abs(yf))
            fr = xf[idx]
            print(fr)
        return render_template('base.html', tracks=songlist, value=fr)
    else:
        user = request.args.get('nm')
        return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
