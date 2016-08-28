import numpy as np


def mask_to_display(m):
    """
    Returns a better plotable mask by setting 0s to nan. This requires converting the array to float.
    :param m: boolean mask
    :return: mask (as numpy array of type float) with zeroes set to nan
    """
    m = m.astype('float')
    m[m == 0] = np.nan
    return m

