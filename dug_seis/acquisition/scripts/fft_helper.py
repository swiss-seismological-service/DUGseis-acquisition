import numpy as np
import scipy.fftpack

import matplotlib.pyplot as plt
plt.style.use('classic')

def fft_helper(stream, trace_nr = 0, T = 5e-6, plot_sig=True):
    sig = stream.traces[trace_nr].data
    N = sig.size

    x = np.linspace(0.0, N*T, N)
    yf = scipy.fftpack.fft(sig)
    xf = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

    if plot_sig:
        plt.plot(sig)
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * np.abs(yf[:N//2]), marker='o')
    plt.show()