# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 12:09:24 2016

@author: matthew
"""

import matplotlib.pyplot as plt
from matplotlib.mlab import GaussianKDE
from matplotlib import cbook
import numpy as np

def sinaplot(dataset, positions=None, vert=True, widths=0.5,
             showmeans=False, showextrema=True, showmedians=False, scaled=True,
             points=100, bw_method=None, ax=None,
             scatter_kwargs=None, line_kwargs=None):
    """
    a cross between a violinplot and a scatterplot, from the R package sinaplot.
    Reimplemented by ripping off the violinplot function from matplotlib and 
    tweaking a few bits.
    """
    
    def _kde_method(X, coords):
        # fallback gracefully if the vector contains only one value
        if np.all(X[0] == X):
            return (X[0] == coords).astype(float)
        kde = GaussianKDE(X, bw_method)
        return kde.evaluate(coords)
    vpstats = cbook.violin_stats(dataset, _kde_method, points=points)
    
    if ax is None:
        ax = plt.subplot()
    
    if scatter_kwargs is None:
        scatter_kwargs = dict(s=20, color='b', marker='o', alpha=0.9)
    scatter_color = scatter_kwargs.pop('color')
    
    if line_kwargs is None:
        line_kwargs = dict(color='red', linewidth='1')

    # Collections to be returned
    artists = {}

    N = len(vpstats)
    datashape_message = ("List of violinplot statistics and `{0}` "
                         "values must have the same length")

    # Validate positions
    if positions is None:
        positions = np.arange(1, N + 1)
    elif len(positions) != N:
        raise ValueError(datashape_message.format("positions"))
    positions = positions.reshape((N, 1))
        
    # Validate widths
    if np.isscalar(widths):
        widths = np.ones((N, 1)) * widths
    elif len(widths) != N:
        raise ValueError(datashape_message.format("widths"))
    widths = widths.reshape((N, 1))

    # Validate colors
    if isinstance(scatter_color, str):
        scatter_color = [scatter_color] * N
    elif len(scatter_color) != N:
        raise ValueError(datashape_message.format("scatter_color"))
    
    # Calculate ranges for statistics lines
    pmins = -0.25 * np.array(widths) + positions
    pmaxes = 0.25 * np.array(widths) + positions        

    # Check whether we are rendering vertically or horizontally
    if vert:
        perp_lines = ax.hlines
        par_lines = ax.vlines
    else:
        perp_lines = ax.vlines
        par_lines = ax.hlines

    # Calculate jittered scatter positions and render sinaplots
    jittered = []
    means = []
    mins = []
    maxes = []
    medians = []
    
    scatter_color_flattened = []
    for i in range(N):
        x = dataset[:,i]
        xp = vpstats[i]['coords']
        fp = vpstats[i]['vals']
        #Uses numpy interpolate to estimate the limits for each points
        interp = np.interp(x, xp, fp)
        jittered.append(np.asarray([np.random.uniform(-r, r) for r in interp]))
        
        # append some stuff for the means/medians/extremities
        means.append(vpstats[i]['mean'])
        mins.append(vpstats[i]['min'])
        maxes.append(vpstats[i]['max'])
        medians.append(vpstats[i]['median'])
        scatter_color_flattened += [scatter_color[i],]*len(x)
        
    jittered = np.asarray(jittered)
    
    # get scale_factor (either scaled by largest value in all sinaplots or not scaled)
    if scaled:
        scale_factor = jittered.max()
    else:
        scale_factor = jittered.max(1)
        scale_factor = scale_factor.reshape((N, 1))
    
    jittered = 0.5 * widths * jittered / scale_factor + positions
    
    #plot scatterplot
    if vert:
        artists['scatter'] = plt.scatter(jittered.flatten(),
                                         dataset.T.flatten(),
                                         color=scatter_color_flattened,
                                         **scatter_kwargs)
    else:
        artists['scatter'] = plt.scatter(dataset.T.flatten(),
                                         jittered.flatten(),
                                         color=scatter_color_flattened,
                                         **scatter_kwargs)    
    
    # Render means
    if showmeans:
        artists['cmeans'] = perp_lines(means, pmins, pmaxes, **line_kwargs)
    # Render extrema
    if showextrema:
        artists['cmaxes'] = perp_lines(maxes, pmins, pmaxes, **line_kwargs)
        artists['cmins'] = perp_lines(mins, pmins, pmaxes, **line_kwargs)
        artists['cbars'] = par_lines(positions, mins, maxes, **line_kwargs)

    # Render medians
    if showmedians:
        artists['cmedians'] = perp_lines(medians, pmins, pmaxes, **line_kwargs)

    return artists