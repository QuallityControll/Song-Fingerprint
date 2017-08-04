from flask import Flask
from flask_ask import Ask, statement, question
import requests
import time
import unidecode
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import librosa
from microphone import record_audio, play_audio
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
from scipy.ndimage.morphology import iterate_structure
from collections import Counter
import pickle

app = Flask(__name__)
ask = Ask(app, '/')

fs = 44100
fss = 44032
song_database = pickle.load( open( "song_database.p", "rb" ) )
totalMatches_database = pickle.load( open( "totalMatches_database.p", "rb" ) )
songLength_database = pickle.load( open( "song_database.p", "rb" ) )


#songLength_database, totalMatches_database, song_database

# Convert Input to Array

def file_to_array(file_path):
    """  It transforms a song into a np array
    :param
        file_path[String]:
            A file path to the song
    :return:
        samples[np.array]:
            This is an array of the values of the song at the file path at a sampling rate of 44100 Hz.
    """
    samples, fs = librosa.load(file_path, sr=44100, mono=True)
    return samples


def mic_to_numpy_array(time):
    mic_input, fs = record_audio(time)
    a = []
    for i in mic_input:
        a.append(np.fromstring(i, dtype=np.int16))
    a = np.hstack(a)
    return a


###Get DATA

def spectogram(samples):
    """
    :param
        samples:
    :return:
        (S, f, t):
            This is a tuple of the spectrogram, the frequencies and the times.
        S:
            The 2D array of the coefficients of the DFT of the song. So S[i, j] is the coefficient at frequency = i
            and time = j.
        f:
    """

    digital = np.copy(samples)
    S, f, t = mlab.specgram(digital, NFFT=4096, Fs=fs, window=mlab.window_hanning, noverlap=(4096 // 2))
    to_return = (S, f, t)
    return to_return


def peaks(spectrogram_arr):
    """
    This finds the peaks of a spectrogram.
    :param:
    spectrogram_arr[np.array]:
    An array of the spectrogram.
    The 2D array of the coefficients of the DFT of the song. So S[i, j] is the coefficient at frequency = freq[i]
    and time = time[j].
    :return:
    peaks[np.array]:
    This is an array with the values of the peaks in the respective
    areas that are there.
    """
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, 10)

    is_peaks = spectrogram_arr == maximum_filter(spectrogram_arr, footprint=neighborhood)
    ys, xs = np.histogram(spectrogram_arr.flatten(), bins=spectrogram_arr.size // 2, normed=True)
    dx = xs[-1] - xs[-2]
    cdf = np.cumsum(ys) * dx  # this gives you the cumulative distribution of amplitudes
    cutoff = xs[np.searchsorted(cdf, 0.77)]
    foreground = (spectrogram_arr >= cutoff)
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax2.imshow(foreground)
    # ax1.imshow(np.logical_and(foreground, is_peaks))
    return np.logical_and(foreground, is_peaks)


def convertData(b):
    temp = []
    lenn = len(b) - 1

    b = np.array(b).T
    for time, row in enumerate(b):
        for freq, item in enumerate(row):
            if (item):
                temp.append((lenn - freq, time))
                # print((lenn - freq,time))
    # return unzip(np.where(asd))#temp
    return temp


def add_song_to_dict(peaks, songTitle, fan=20):
    """
    adds a song to a databse by anazlyzing the difference in time between the change in frequencies
    song ex:
        keys: (f1,f2,t2-t1), (f1,f3,t3-t1), ... (f1,f(1+freqfan), t(1+freqfan)-t1)
              (f2,f3,t3-t2), (f2,f4,t4-t2), ... (f2,f(2+freqfan), t(2+freqfan)-t2)
              ...

        stored for each key: ("title",diff from t1 to beg of mic audio)
    ------------------------------------------------------------------------------------------------

    paramaters:
        peaks: 2D array of Nx2: List of each song's peaks incuding the (freq and time-stamp)
        songTitle: str of songTitle

    returns:
        adds to dictionary all of the keys and a tuple of (their respective song title, t1)
    """
    # pickling - fast way for python to save dictionaries
    for peakStartIndex in range(len(peaks)):
        referencePeak = peaks[peakStartIndex]
        f1 = referencePeak[0]
        # print(peakStartIndex)
        t1 = referencePeak[1]

        # get the slice of fan:
        if fan > len(peaks[peakStartIndex + 1:]):
            peak_slice = peaks[peakStartIndex + 1:]
        else:
            peak_slice = peaks[peakStartIndex + 1:peakStartIndex + fan]

        for peak in peak_slice:
            # what happens if you reach the end!!!! include if statement
            f2 = peak[0]
            t2 = peak[1]
            # check key
            key = (f1, f2, t2 - t1)
            if not (key in song_database):
                song_database[key] = []

            song_database[key].append((songTitle, t1))
            # include another dict for the a new dict for new song nd compare


def check_database(MicPeaks, lengthOfRecording, fan=20, howManyToCompare=5):
    # !!!!TRY DOING PERCENTAES AND NORMAILIZATION FOR SPED UP SONGS AND HIGHER KEY
    """
        First calculates time differences between peaks of input

        Compares the peak distributions of the Mic input to that of the dictionary
        Calls the keys created by the Mic peaks, and searches the database for matching keys
        Creates a new dictionary and for every match, it will enter the same key and enter the tuple: (Song title, T(song) - T(MicInput))
        Checks the dictionarry with Counter() to fnd the greatest number of standardized matches
    ------------------------------------------------------------------------------------------------

    paramaters:
        MicPeaks: 2D array of Nx2: List of Mic song's peaks incuding the (freq and time-stamp)

    returns:
        New dictionary of common keys, including the tuple mentioned above^
        The greatest number of matching bins using Counter() - possibly include a confidence percentage by ranking greatest retyrns, and checking appropriate confidences
    """
    # 1)
    MicKeyList = []
    for peakStartIndex in range(len(MicPeaks)):
        referencePeak = MicPeaks[peakStartIndex]
        f1 = referencePeak[0]
        t1 = referencePeak[1]

        # get the slice of fan:
        if fan > len(MicPeaks[peakStartIndex + 1:]):
            peak_slice = MicPeaks[peakStartIndex + 1:]
        else:
            peak_slice = MicPeaks[peakStartIndex + 1:peakStartIndex + 1 + fan]

        for peak in peak_slice:
            # what happens if you reach the end!!!! include if statement
            f2 = peak[0]
            t2 = peak[1]
            # check key
            key = (f1, f2, t2 - t1)
            MicKeyList.append(key)


            #    MicKeyList = []
            #    for peakStartIndex in range(howManyRefPeaks):
            #        referencePeak = MicPeaks[peakStartIndex]
            #        f1 = referencePeak[0]
            #        t1 = referencePeak[1]

            # get the slice of fan:

            #        peak_slice = MicPeaks[peakStartIndex + 1:]

            #        for peak in peak_slice:
            # what happens if you reach the end!!!! include if statement
            #            f2 = peak[0]
            #            t2 = peak[1]
            # check key
            #            key = (f1, f2, t2 - t1)
            #            MicKeyList.append(key)

    # 2)

    CommonKeys = []
    # checks for MicKeys in song_database_dict
    #   if there is, record tuple: ("Song Title" of match, T(song) - t1 (aka ref[1]))


    # print(MicKeyList)
    for key in MicKeyList:
        # print(key)
        if key in song_database:
            # print(key,song_database[key])
            # Its a match!
            # print(len(song_database[key][0]))


            # if length of song_database[key] > 1, do a loop

            for match in song_database[key]:
                songMatchTitle = match[0]
                songT1Ref = match[1]

                CommonKeys.append(songMatchTitle)
                # CommonKeys.append(match)

    MatchCount = Counter(CommonKeys)

    # print(MatchCount.most_common())
    # print(MatchCount)







    # average:
    #############################
    totalMatches = 0
    PercentDict = {}
    for row in MatchCount.most_common(20):
        if not row[0][0] in PercentDict:
            PercentDict[row[0]] = 0

        PercentDict[row[0]] += row[1]

        totalMatches += row[1]

    # print(PercentDict)

    name = Counter(PercentDict).most_common(1)[0][0]
    # how good the #1 match is
    # how many matches / how many peaks in song that should be there are in that __ second interval
    # how many matches / (how many peaks in song / total time of song)* length of recording
    # Confidence1 = Counter(PercentDict).most_common(1)[0][1]/(lengthOfRecording*fss*totalMatches_database[name]/songLength_database[name])
    # print(Confidence1)

    # how it compares to the match next to it
    # matches of song / matches of next best song

    Confidence2 = Counter(PercentDict).most_common(1)[0][1] / Counter(PercentDict).most_common(2)[1][1]
    # print(Confidence2)
    # print("peaks found:", Counter(PercentDict).most_common(1)[0][1],"/n",'samples:',lengthOfRecording*fss,"/n","total matches:",totalMatches_database[name],'/n',"songLength",songLength_database[name])
    # print(Confidence1*(Confidence2-1))




    #############################
    PredictedSong = Counter(PercentDict).most_common(1)[0][0]
    # PercentConfidence = Confidence1 #PercentDict[PredictedSong]/totalMatches
    # PercentConfidence=1+(-0.0341778-0.9054751)/(1+((Confidence1/1.390494)**3)*.267277)
    print(Confidence2)
    PercentConfidence = 1 + (-0.0341778 - 0.9054751) / (1 + ((Confidence2 / 1.40494) ** 3) * .267277)
    tttt = [PredictedSong, int(PercentConfidence * 100)]
    print(tttt)
    return tttt


def addSong(name, fileAddress):
    temp = file_to_array(fileAddress)
    songLength_database[name] = len(temp)

    print(name + " array converted")
    S, f, t = spectogram(temp)
    b = peaks(S)
    print(name + ' peaks gotten')

    peaksd = convertData(b)
    print(name + ' data converted')
    print(len(peaksd))
    totalMatches_database[name] = len(peaksd)

    add_song_to_dict(peaksd, name)
    print(name + ' song added')


# song_database

####





#####
@ask.intent("RecordSong")
def MicCheck(length):

    print(length)
    length = (int(length))

    #return statement(length)
    MicPeaks = mic_to_numpy_array(length)
    print("Mic reocrded")
    #return statement("checl")
    Stemp, f, t = spectogram(MicPeaks)
    MicPeaksTemp = peaks(Stemp)
    print("Mic peaks gotten")
    peaksMicFinal = convertData(MicPeaksTemp)
    print("Mic data converted")

    #return statement('dipppp')
    temp =  check_database(peaksMicFinal, length)

    #if temp[1] < .32:#32
    #    return statement("I am not sure")
    #else:
    return statement("I am " + str(temp[1]) + " percent confident that the song is " + str(temp[0]) + '.')
    #print(returnn)
    #if returnn == "I am not sure":
    #    msg = returnn
    #else:
    #    msg = "I am " + returnn[1] + " percent confident that the song is " + returnn[0] + '.'
    #print(msg)
    #print(type(returnn))
    #print(type(msg))
    #return statement("asdasdasdasdsdasd")
    return statement(str(length))

@app.route('/')
def homepage():
    return "Song FP"

@ask.launch
def start_skill():
    msg = "how long would you like me to record for?"
    return question(msg)

if __name__ == '__main__':
    app.run(debug=True)