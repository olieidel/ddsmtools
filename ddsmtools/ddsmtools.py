import os
from glob import glob
from datetime import date
import numpy as np
from mahotas import polygon


def is_int_try(v):
    try:
        i = int(v)
    except:
        return False
    return True


def date_from_list(l):
    l = [int(x) for x in l if is_int_try(x)]
    return date(day=l[0], month=l[1], year=l[2])


def ics_file_name(path):
    dir_name = os.path.dirname(path)
    ics_files = glob(dir_name + '/*.ics')
    if len(ics_files) == 0:
        print('found no corresponding ics file')
        return None
    elif len(ics_files) == 1:
        print('found ics file')
        return ics_files[0]
    else:
        print('found multiple ics files! Using first one.')
        return ics_files[0]


def overlay_file_name(p):
    return '.'.join(p.split('.')[:-1]) + '.OVERLAY'


def file_lines_list(file, skip_list=[]):
    return [l.strip().split(' ') for l in file if len(l.strip()) > 0 and l.strip() not in skip_list]


def lines_to_dict(l):
    return {l[i][0]: l[i][1:] for i in range(len(l))}


def flatten_single_dict_vals(d):
    for k, v in d.items():
        if isinstance(v, (list, tuple)) and len(v) == 1:
            d[k] = v[0]
    return d


def dict_vals_to_int(d):
    for k, v in d.items():
        if is_int_try(v):
            d[k] = int(v)
    return d


def zip_list_to_dict(l):
    zip_dict = {k: v for (k, v) in list(zip(l, l[1:]))[::2]}
    if len(l) % 2 == 1:
        zip_dict[l[-1:][0]] = ''
    return zip_dict


def parse_ics(file):
    headings = ['FILM', 'SEQUENCE']
    sequences = ['LEFT_CC', 'LEFT_MLO', 'RIGHT_CC', 'RIGHT_MLO']

    with open(file, 'r') as f:
        ics_lines = file_lines_list(f, headings)
    ics_attribs = lines_to_dict(ics_lines)
    ics_attribs = flatten_single_dict_vals(ics_attribs)
    ics_attribs = dict_vals_to_int(ics_attribs)

    ics_attribs['DATE_DIGITIZED'] = date_from_list(ics_attribs['DATE_DIGITIZED'])
    ics_attribs['DATE_OF_STUDY'] = date_from_list(ics_attribs['DATE_OF_STUDY'])

    for k, v in ics_attribs.items():
        if k in sequences:
            # Clean up Overlay Information.
            # Remove information (one key, no value) from list, create dictionary entry and merge dicts
            d = {}
            if 'OVERLAY' in v:
                d['HAS_OVERLAY'] = True
                v.remove('OVERLAY')
            elif 'NON_OVERLAY' in v:
                d['HAS_OVERLAY'] = False
                v.remove('NON_OVERLAY')
            ics_attribs[k] = {**d, **zip_list_to_dict(v)}
            ics_attribs[k] = dict_vals_to_int(ics_attribs[k])

    return ics_attribs


def parse_overlay(file):
    with open(file) as f:
        l = file_lines_list(f)
    total_abnorm = int(l[0][1])
    abn = []
    pos = 1
    for i in range(total_abnorm):
        m = lines_to_dict(l[pos:pos + 6])
        m = flatten_single_dict_vals(m)
        m = dict_vals_to_int(m)
        m['LESION_TYPE'].insert(0, 'TYPE')
        m['LESION_TYPE'] = zip_list_to_dict(m['LESION_TYPE'])
        total_outl = m['TOTAL_OUTLINES']
        pos += 6
        outl_list = []
        for j in range(total_outl):
            outl = {'NAME': l[pos][0],
                    'START_COORDS': (int(l[pos + 1][0]), int(l[pos + 1][1])),
                    'PATH': [int(x) for x in l[pos + 1][2:-1] if is_int_try(x)]}  # remove hash at end
            outl_list.append(outl)
            pos += 2
        m['OUTLINES'] = outl_list
        abn.append(m)
    return abn


def path_to_directions(l):
    """
    as seen here: https://github.com/multinormal/ddsm/blob/master/ddsm-software/get_ddsm_groundtruth.m
    original documentation: http://marathon.csee.usf.edu/Mammography/DDSM/case_description.html#OVERLAYFILE
    rows and columns are swapped
    """
    chain_code = {0: [-1, 0],
                  1: [-1, 1],
                  2: [0, 1],
                  3: [1, 1],
                  4: [1, 0],
                  5: [1, -1],
                  6: [0, -1],
                  7: [-1, -1]}
    # chain_code = {0: [0, -1],
    #               1: [1, -1],
    #               2: [1, 0],
    #               3: [1, 1],
    #               4: [0, 1],
    #               5: [-1, 1],
    #               6: [-1, 0],
    #               7: [-1, -1]}
    return [chain_code[x] for x in l]


def directions_to_coords(xy_list, start_coords):
    """
    start coords are reversed in ics file (column, row) as documented here:
    http://marathon.csee.usf.edu/Mammography/DDSM/case_description.html

    :param xy_list:
    :param start_coords:
    :return:
    """

    start_coords = tuple(reversed(start_coords))
    a = [list(start_coords)] + xy_list
    a = np.asarray(a)
    a = a.cumsum(axis=0)
    return a


def path_to_coords(path, start_coords):
    '''
    short-hand function for calling path_to_directions() and directions_to_coords() successively.
    :param path:
    :param start_coords:
    :return:
    '''
    return directions_to_coords(path_to_directions(path), start_coords)


def coords_to_polygon_mask(xy, shape):
    m = np.zeros(shape, dtype=np.bool)
    m[xy[:, 0], xy[:, 1]] = True
    return m


def coords_to_fill_mask(xy, shape):
    canvas = np.zeros(shape)
    polygon.fill_polygon(xy, canvas)  # modifies canvas in-place!
    return canvas


def mask_to_display(mask):
    '''
    Returns a better plotable mask by setting 0s to nan. This requires converting the array to float.
    :param mask: boolean mask
    :return: float mask with 0s set to nan
    '''
    mask = mask.astype('float')
    mask[mask == 0] = np.nan
    return mask
