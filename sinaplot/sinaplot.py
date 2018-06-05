import matplotlib.pyplot as plt
from seaborn.categorical import _ViolinPlotter
import numpy as np


class _SinaPlotter(_ViolinPlotter):

    def __init__(self, x, y, hue, data, order, hue_order,
                 bw, cut, scale, scale_hue, gridsize,
                 width, inner, split, dodge, orient, linewidth,
                 color, palette, saturation,
                 violin_facealpha, point_facealpha):
        # initialise violinplot
        super(_SinaPlotter, self).__init__(
            x, y, hue, data, order, hue_order,
            bw, cut, scale, scale_hue, gridsize,
            width, inner, split, dodge, orient, linewidth,
            color, palette, saturation
        )

        # Set object attributes
        self.dodge = dodge
        # bit of a hack to set color alphas for points and violins
        self.point_colors = [(*color, point_facealpha) for color in self.colors]
        self.colors = [(*color, violin_facealpha) for color in self.colors]

    def jitterer(self, values, support, density):
        if values.size:
            max_density = np.interp(values, support, density)
            max_density *= self.dwidth
            low = 0 if self.split else -1
            jitter = np.random.uniform(low, 1, size=len(max_density)) * max_density
        else:
            jitter = np.array([])
        return jitter

    def draw_sinaplot(self, ax, kws):
        """Draw the points onto `ax`."""
        # Set the default zorder to 2.1, so that the points
        # will be drawn on top of line elements (like in a boxplot)
        for i, group_data in enumerate(self.plot_data):
            if self.plot_hues is None or not self.dodge:

                if self.hue_names is None:
                    hue_mask = np.ones(group_data.size, np.bool)
                else:
                    hue_mask = np.array([h in self.hue_names
                                         for h in self.plot_hues[i]], np.bool)
                    # Broken on older numpys
                    # hue_mask = np.in1d(self.plot_hues[i], self.hue_names)

                strip_data = group_data[hue_mask]
                density = self.density[i]
                support = self.support[i]

                # Plot the points in centered positions
                cat_pos = np.ones(strip_data.size) * i
                cat_pos += self.jitterer(strip_data, support, density)
                kws.update(color=self.point_colors[i])
                if self.orient == "v":
                    ax.scatter(cat_pos, strip_data, **kws)
                else:
                    ax.scatter(strip_data, cat_pos, **kws)

            else:
                offsets = self.hue_offsets
                for j, hue_level in enumerate(self.hue_names):
                    hue_mask = self.plot_hues[i] == hue_level
                    strip_data = group_data[hue_mask]
                    density = self.density[i][j]
                    support = self.support[i][j]
                    if self.split:
                        # Plot the points in centered positions
                        center = i
                        cat_pos = np.ones(strip_data.size) * center
                        jitter = self.jitterer(strip_data, support, density)
                        cat_pos = cat_pos + jitter if j else cat_pos - jitter
                        kws.update(color=self.point_colors[j])
                        if self.orient == "v":
                            ax.scatter(cat_pos, strip_data, zorder=2, **kws)
                        else:
                            ax.scatter(strip_data, cat_pos, zorder=2, **kws)
                    else:
                        # Plot the points in centered positions
                        center = i + offsets[j]
                        cat_pos = np.ones(strip_data.size) * center
                        cat_pos += self.jitterer(strip_data, support, density)
                        kws.update(color=self.point_colors[j])
                        if self.orient == "v":
                            ax.scatter(cat_pos, strip_data, zorder=2, **kws)
                        else:
                            ax.scatter(strip_data, cat_pos, zorder=2, **kws)

    def add_legend_data(self, ax, color, label):
        """Add a dummy patch object so we can get legend data."""
        # get rid of alpha band
        if len(color) == 4:
            color = color[:3]
        rect = plt.Rectangle([0, 0], 0, 0,
                             linewidth=self.linewidth / 2,
                             edgecolor=self.gray,
                             facecolor=color,
                             label=label)
        ax.add_patch(rect)

    def plot(self, ax, kws):
        """Make the sinaplot."""
        if kws.pop('violin', True):
            self.draw_violins(ax)
        elif self.plot_hues is not None:
            # we need to add the dummy box back in for legends
            for j, hue_level in enumerate(self.hue_names):
                self.add_legend_data(ax, self.colors[j], hue_level)
        self.draw_sinaplot(ax, kws)
        self.annotate_axes(ax)
        if self.orient == "h":
            ax.invert_yaxis()


def sinaplot(x=None, y=None, hue=None, data=None, order=None, hue_order=None,
             bw="scott", cut=2, scale="count", scale_hue=True, gridsize=100,
             violin=True, inner=None, 
             width=.8, split=False, dodge=True, orient=None,
             linewidth=1, color=None, palette=None, saturation=.75, violin_facealpha=0.25,
             point_linewidth=None, point_size=5, point_edgecolor="none", point_facealpha=1,
             legend=True, random_state=None, ax=None, **kwargs):

    plotter = _SinaPlotter(x, y, hue, data, order, hue_order,
                           bw, cut, scale, scale_hue, gridsize,
                           width, inner, split, dodge, orient, linewidth,
                           color, palette, saturation,
                           violin_facealpha, point_facealpha)

    np.random.seed(random_state)
    point_size = kwargs.get("s", point_size)
    if point_linewidth is None:
        point_linewidth = point_size / 10
    if point_edgecolor == "gray":
        point_edgecolor = plotter.gray
    kwargs.update(dict(s=point_size ** 2,
                       edgecolor=point_edgecolor,
                       linewidth=point_linewidth,
                       violin=violin))

    if ax is None:
        ax = plt.gca()

    plotter.plot(ax, kwargs)
    if not legend:
        ax.legend_.remove()
    return ax