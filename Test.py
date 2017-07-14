import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import librosa
from microphone import record_audio, play_audio

fs = 44100


def file_to_array(file_path):
    """  It transforms a song into a np array
    :param
        file_path[String]:
            A file path to the song

    :return:
        samples[np.array]:
            This is an array of the values of the song at the file path at a sampling rate of 44100 Hz.
    """
    samples, fs = librosa.load(file_path, sr = 44100, mono = True)
    return samples


def mic_to_numpy_array(time):
    mic_input, fs= record_audio(time)
    a = []
    for i in mic_input:
        a.append(np.fromstring(i, dtype=np.int16))
    a = np.hstack(a)
    return a



def plot_spectogram(samples):
    """ It takes a sample of a song and plots the spectrogram of it.

    :param
        samples[np.array]:
            The array of samples of the song that was recorded or filed in.
    :return:
        Nothing

    """
    digital = np.copy(samples)
    fig, ax = plt.subplots()
    S, f, t, im = ax.specgram(digital, NFFT=4096, Fs=fs, window=mlab.window_hanning, noverlap=(4096 // 2))
    fig.colorbar(im)


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


def plot_song(samples):
    cutSamples = samples[::1000]
    # plt.plot(cutSamples)
    times = np.arange(len(samples))
    times = times / 44100
    cutTimes = times[::1000]
    fig, ax = plt.subplots()
    ax.plot(cutTimes, cutSamples)


def plot_dft(samples):
    dft = np.fft.rfft(samples)
    times = np.arange(len(samples))
    times = times / 44100
    cutDFT = dft[::1000]
    freq = np.arange(len(dft)) / times[-1]
    cutFreq = freq[::1000]
    fig, ax = plt.subplots()
    ax.plot(cutFreq, np.abs(cutDFT))
    ax.set_xlabel("Frequencies(Hz)")

song = mic_to_numpy_array(2)
plot_spectogram(song)

