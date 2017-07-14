import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import librosa
from microphone import record_audio  # , play_audio
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
from scipy.ndimage.morphology import iterate_structure

fs = 44100


def file_to_array(file_path):
    """
    It transforms a song into a np array.

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
    """
    It transforms a mic input into an np array.

    :param
        time[float]:
            The time it needs to record

    :return:
        mic[np.array]:
            This is an array of the values of the song that was recorded at a sampling rate of 44100 Hz.

    """
    mic_input, fs = record_audio(time)
    mic = []
    for i in mic_input:
        mic.append(np.fromstring(i, dtype=np.int16))
    mic = np.hstack(mic)
    return mic


def plot_spectrogram(samples):
    """
    It takes a sample of a song and plots the spectrogram of it.

    :param
        samples[np.array]:
            The array of sampled values of the song that was recorded or filed in.

    :return:
        Nothing. It plots the spectrogram

    """
    digital = np.copy(samples)
    fig, ax = plt.subplots()
    s, f, t, im = ax.specgram(digital, NFFT=4096, Fs=fs, window=mlab.window_hanning, noverlap=(4096 // 2))
    fig.colorbar(im)


def spectrogram(samples):
    """
    This creates a spectrogram of the song that the samples array represents.

    :param
        samples[np.array]:
            The array of sampled values of the song that was recorded or filed in.
    :return:
        (S, f, t)[Tuple of np.arrays]:
            This is a tuple of the spectrogram, the frequencies and the times.
        S[np.array]:
            The 2D array of the coefficients of the DFT of the song. So S[i, j] is the coefficient at frequency = f[i]
            and time = t[j].
        f[np.array]:
            f is a 1D array of frequency values.
        t[np.array]:
            t is a 1D array of time values.

    """
    digital = np.copy(samples)
    s, f, t = mlab.specgram(digital, NFFT=4096, Fs=fs, window=mlab.window_hanning, noverlap=(4096 // 2))
    to_return = (s, f, t)
    return to_return


def plot_song(samples):
    """
    This takes the samples array and graphs it with time.

    :param
        samples:
            The array of sampled values of the song that was recorded or filed in.

    :return:
        Nothing. Prints out a graph of the song.
    """

    cut_samples = samples[::1000]
    # plt.plot(cutSamples)
    times = np.arange(len(samples))
    times = times / 44100
    cut_times = times[::1000]
    fig, ax = plt.subplots()
    ax.plot(cut_times, cut_samples)


def plot_dft(samples):
    """
    This plots the Discrete Fourier Analysis of the song that the samples array represents.

    :param
        samples[np.array]:
            The array of sampled values of the song that was recorded or filed in.

    :return:
        Nothing. It prints out a graph of the Discrete Fourier Analysis of the song.
    """
    dft = np.fft.rfft(samples)
    times = np.arange(len(samples))
    times = times / 44100
    cut_dft = dft[::1000]
    freq = np.arange(len(dft)) / times[-1]
    cut_freq = freq[::1000]
    fig, ax = plt.subplots()
    ax.plot(cut_freq, np.abs(cut_dft))
    ax.set_xlabel("Frequencies(Hz)")


def peaks(spectrogram_arr, freq):
    """
    This finds the peaks of a spectrogram.

    :param:
        spectrogram_arr[np.array]:
            An array of the spectrogram.
            The 2D array of the coefficients of the DFT of the song. So S[i, j] is the coefficient at frequency = i
            and time = j.
    :return:
        peaks[np.array]:
            This is an array with the values of the peaks in the respective
            areas that are there.
    """
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, 10)

    is_peaks = spectrogram_arr == maximum_filter(spectrogram_arr, footprint=neighborhood)
    # ys, xs = np.histogram(spectrogram_arr.flatten(), bins=len(freq) // 2, normed=True)
    # dx = xs[-1] - xs[-2]
    # cdf = np.cumsum(ys) * dx  # this gives you the cumulative distribution of amplitudes
    # cutoff = xs[np.searchsorted(cdf, 0.77)]
    # foreground = (spectrogram_arr >= cutoff)
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax2.imshow(foreground)
    # ax1.imshow(np.logical_and(foreground, is_peaks))
    return is_peaks


S, f, t = spectrogram(mic_to_numpy_array(10))
peaks(S, f)
