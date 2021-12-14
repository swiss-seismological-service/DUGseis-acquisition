def plot_waveform(dataStream):
    
    import numpy as np
    import matplotlib.pyplot as plt
    plt.style.use('classic')
    
    ## Plotting waveforms
    # Time vector
    sampRate = dataStream.traces[0].stats['sampling_rate']
    samp_v = np.arange(0, dataStream[0].data.shape[0], 1)*1/sampRate*1000
    # samp_v_pre = -1 * np.arange(0,(eve_time - dataStream.traces[0].stats.starttime) * sampRate, 1)*1/sampRate*1000
    # samp_v_post = np.arange(0,(dataStream.traces[0].stats.endtime - eve_time) * sampRate, 1)*1/sampRate*1000
    # samp_v = np.concatenate((np.flip(samp_v_pre, 0), samp_v_post), axis=0, out=None)
    a_max = []
    # see if the two vectors have an equal amount of samples
    if len(samp_v) != dataStream.traces[0].stats.npts:
        if dataStream.traces[0].stats.npts > len(samp_v):       # append to samp_v if too short
            samp_v = np.append(samp_v, samp_v[len(samp_v) - 1] + (samp_v[len(samp_v) - 1] - samp_v[len(samp_v) - 2]))
        else:
            samp_v = samp_v[:-1].copy()     # take one entry off
    for k in range(len(dataStream)):
        a_max.append(format(np.amax(np.absolute(dataStream[k].data)), '.1f'))

    fig = plt.figure(constrained_layout=False)
    gs1 = fig.add_gridspec(nrows=len(dataStream), ncols=1, left=0.05, right=0.95,
                            wspace=0, hspace=0)
    # fig, axs = plt.subplots(len(dataStream), 1, facecolor='w', edgecolor='k')
    # plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=.5)
    # fig.subplots_adjust(hspace=0, wspace=0)
    for i in range(len(dataStream)):
        ax1 = fig.add_subplot(gs1[i, :])
        ax1.grid(b=None, which='major', axis='x', color='silver', linestyle='-', linewidth=0.25)
        ax1.set_axisbelow(True)
        ax1.plot(samp_v, dataStream[i].data, linewidth=0.25, marker='o')
        # ax1.set_yticklabels([]) # hide y axis numbers
        ax1.set_ylabel('sta:' + dataStream.traces[i].stats.station +
                       ' ch:' + dataStream.traces[i].stats.location, rotation=90, fontsize=12)

        ax1.set_xlim([np.min(samp_v), np.max(samp_v)])
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.tick_params(top=False)
        ax1.tick_params(right=False)
        plt.text(0.99, 0.99, 'peak amp: ' + str(a_max[i]) + ' counts',
                 horizontalalignment='right',
                 verticalalignment='top',
                 transform=ax1.transAxes, color='black', fontsize=6)
        if i < len(dataStream)-1:
            ax1.set_xticklabels([])
        else:
            ax1.set_xlabel('time [ms]')
            # plt.suptitle('seismic event: ' + title, fontsize=12)

    plt.savefig('test' + '.png')
    plt.show()
    #    for m in range(len(trig_time_only)):
    #        axs[trig_ch[0][m]].plot((trig_time_only[m], trig_time_only[m]) , (axs[trig_ch[0][m]].get_ylim()[0], axs[trig_ch[0][m]].get_ylim()[1]), 'r-')
    #
    return fig