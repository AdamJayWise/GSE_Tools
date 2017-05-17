# take a dataframe df, an x axis column label x_label, a y axis column label y_label, and generate a plot
# showing the response of df[y_label] as a function of df[x_label], grouped by sample_uid and condition_uid

# This is specifically meant to work on aggregated IV curve measurements where many measurements are recorded for a
# particular sample with uid sample_uid, typically the column labelled 'Serial'

# Import libraries
from datetime import datetime
from datetime import timedelta
#import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

# define errorbar fill function
def errorfill(x, y, yerr, color=None, alpha_fill=0.05, ax=None):
    ax = ax if ax is not None else plt.gca()
    if color is None:
        color = 'black'
    if np.isscalar(yerr) or len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = yerr
    ax.plot(x, y, color=color)
    ax.fill_between(x, ymax, ymin, color=color, alpha=alpha_fill)



# Define trajectory - plotting function

def plot_trajectories(ax='ax1', data='dataframe', x_label='Date', y_label='Pmax', sample_uid='Module#',
                      cond_uid='Condition', normalized=False, norm_index=1, show_legend=True, stat=True):
    # Create a tag string to hold any modifications for labelling the x axis at the end
    x_label_suffix = ''

    x_group_label = 'Condition'

    def jointimes(row):
        return datetime.combine(row['Date'], datetime.time(row['Time']))
    # Take a look at the x_label columns... if it's called 'date', attempt to turn it into a datetime object
    if (x_label.lower() == 'date') & (type(data[x_label].iloc[0]) == str):
        try:
            data.loc[:,'Date'] = data['Date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
        except:
            print('Problem Converting Date ', sys.exc_info())
            try:
                data[:,'Date'] = data['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
            except:
                print('Problem Converting Date ',sys.exc_info())
                return

        # Clean up the date & time, sorting by date+time, and converting the date to days post initial measure
        data.loc[:, 'Time'] = data['Time'].apply(lambda x: datetime.strptime(x, '%H:%M:%S'))
        data.loc[:,'DateTime'] = data.apply(jointimes, axis=1)
        data.sort_values('DateTime', inplace=True)
        data.loc[:, 'Date'] = data['Date']-min(data['Date'])
        data.loc[:,'Date'] = data['Date'].apply(lambda x:x.days)


        # Has a sample been processed and re-measured on the same day?  If so, apply a time offset for
        # each re-processing and re-measurement, grouped by the x_group_label
        for d in data['Date'].unique():
            for i,c in enumerate(data[data['Date']==d][x_group_label].unique()):
                data.loc[(data['Date']==d)&(data[x_group_label]==c),'Date'] = d + (i/2)


    # Establish a repeatable colormap dict from the list of unique condition_uids
    line_colors = ['black', 'blue', 'red', 'green', 'purple', 'grey']
    grps = [c for c in data[cond_uid].unique()]
    cmap = zip(line_colors[:len(grps)], grps)
    line_color_dict = {k: v for v, k in cmap}

    # Plot trajectory by sample UID
    alphadict = {True:0.1,False:0.9}
    for label,grp in data.groupby(sample_uid):
        labeldict = {True: None, False: grp[cond_uid].iloc[-1]}
        group_color = line_color_dict[grp[cond_uid].iloc[-1]]
        if normalized:
            norm_factor = grp[y_label].iloc[norm_index]
        if not normalized:
            norm_factor = 1
        ax.plot(grp[x_label], grp[y_label] / norm_factor,'-', color=group_color, label=labeldict[stat], alpha=alphadict[stat])

    # Draw stastical Data if flag is set - this is a a line for median with filled areas for +-1STD
    if stat == True:
        for c in data[cond_uid].unique():
            #grab subsample of data corresponding to a particular condition
            data_subset = data[data[cond_uid] == c]
            p_x = [unique_date for unique_date in data_subset[x_label].unique()]
            p_y = [data_subset[data_subset[x_label] == d][y_label].median() for d in p_x]

            if normalized:
                norm_factor = p_y[norm_index]
                p_y = [e / norm_factor for e in p_y]

            ax.plot(p_x, p_y, '.-', color=line_color_dict[c], label=c, lw=1.5)


    # Get rid of extraneous legend entries by dumping non-unique plot labels
    [handles, labels] = ax.get_legend_handles_labels()
    handles_unique = []
    labels_unique = []

    for h, l in zip(handles, labels):
        if (l not in labels_unique) & (l not in y_label):
            labels_unique.append(l)
            handles_unique.append(h)

    # Dictionary for what to append to the axis, if anything
    normdict = {True: 'Normalized', False: ''}
    stat_title_dict = {True: ' Dashed Lines - Group Median', False: ''}
    # If show_legend is enabled, display a legend and title
    if show_legend:
        leg = ax.legend(handles_unique, labels_unique, loc="upper left", fontsize=8)
        ax.set_title('Parameters ' + normdict[normalized] + stat_title_dict[stat], fontsize=10)
        leg.get_frame().set_facecolor('white')
        leg.get_frame().set_alpha(0.85)

    # Set the Labels to look nice
    ax.set_ylabel(y_label)
    ax.set_xlabel('Time, Days', fontsize=10)

    return


# End plot trajectory function

# Helper function for plotting multiple values on one axis
def layout_multiplot(cond_list='', data='', x_label='Date', sample_uid='Module#', cond_uid='Condition', normalized=True,
                     statistical=False):
    f, axarr = plt.subplots(len(cond_list), sharex=True, figsize=[8, 8])
    for i in range(len(cond_list)):
        if i == 0:
            legend = True
        else:
            legend = False
        plot_trajectories(ax=axarr[i], data=data, x_label=x_label, y_label=cond_list[i], sample_uid=sample_uid,
                          cond_uid=cond_uid, normalized=normalized, norm_index=1, show_legend=legend,
                          stat=statistical)
        if i != len(cond_list) - 1:
            axarr[i].set_xlabel('')
    plt.show()

