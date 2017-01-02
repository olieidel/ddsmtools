import numpy as np
from matplotlib import patches as mpatches
from ddsmtools import overlay


def mask_to_display(m):
    """
    Returns a better plottable mask by setting 0s to nan. This requires
    converting the array to float.
    :param m: boolean mask
    :return: mask (as numpy array of type float) with zeroes set to nan
    """
    m = m.astype('float')
    m[m == 0] = np.nan
    return m

def overlays_prepare(plt, m, shape):
    """
    prepare data for plotting overlays onto image with their respective
    description

    :param plt: matplotlib pyplot object
    :param m: parsed overlays dict
    :param shape: shape of image
    :return: masks: boolean masks of overlays
    :return: legends: legends dict for further processing in overlays_plot
    :return colors: colors as rgb which to use for overlays
    :return color_vals: single values of colors for plotting
    """

    n = len([i2
             for i in m
             for i2 in i['OUTLINES']])
    cmap = plt.cm.rainbow
    locs = ['upper right', 'upper left', 'lower left', 'lower right']

    color_vals = np.linspace(0.3, 1.0, num=n)
    colors = [cmap(x) for x in color_vals]
    masks = [mask_to_display(overlay.coords_to_fill_mask(overlay.path_to_coords(x2['PATH'], x2['START_COORDS']), shape))
             for x in m
             for x2 in x['OUTLINES']]
    c_i = 0
    legends = []
    for i, abn in enumerate(m):
        h = []
        for outl in abn['OUTLINES']:
            h.append(mpatches.Patch(color=colors[c_i], label=outl['NAME']))
            c_i += 1
        legends.append({'title': 'L' + str(i + 1) + ': ' + abn['PATHOLOGY'],
                        'handles': h,
                        'loc': locs[i]})

    return masks, legends, colors, color_vals

def overlays_plot(plt, ax, image, masks, legends, colors, color_vals):
    ax.imshow(image, vmin=0, vmax=4096, cmap='gray')
    ax.hold(True)
    for m in zip(masks, color_vals):
        ax.imshow(m[0], alpha=.3, vmin=0, vmax=1/m[1], cmap='rainbow')
    for l in legends:
        leg = plt.legend(handles=l['handles'], title=l['title'], loc=l['loc'])
        plt.gca().add_artist(leg)

    return None
