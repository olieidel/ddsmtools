import numpy as np
from mahotas import polygon

from ddsmtools.utils import file_lines_list, zip_list_to_dict,
flatten_list, is_int_try


def overlay_file_name(p):
    """
    generate overlay file name from ljpeg file name
    """
    return '.'.join(p.split('.')[:-1]) + '.OVERLAY'


def parse_overlay(file):
    def get_indices(lines):
        abnormality_indices = [i for (i, x) in
                               enumerate(lines) if x[0]=='ABNORMALITY']
        path_indices = [i for (i, x) in enumerate(lines) if
                        is_int_try(x[0])]
        path_desc_indices = [x-1 for x in path_indices]
        total_outline_indices = [i for (i, x) in enumerate(lines) if
        x[0]=='TOTAL_OUTLINES']

        return abnormality_indices, path_indices, path_desc_indices,
        total_outline_indices

    with open(file) as f: lines = file_lines_list(f)

    abnormality_indices, path_indices, path_desc_indices,
    total_outline_indices = get_indices(lines)

    # overwrite outlines as dicts for i in path_indices:
    lines[i] = ['OUTLINE',
                {'NAME': lines[i-1][0], 'START_COORDS': (lines[i][0],
                            lines[i][1]), 'PATH': [int(x) for x in
                            lines[i][2:]if is_int_try(x)]}]

    # cast to int
    for i, x in enumerate(l):
        if len(l[i]) == 2 and is_int_try(l[i][1]):
            l[i][1] = int(l[i][1])

    # delete unneeded entries
    to_delete = []
    to_delete = total_outline_indices + path_desc_indices
    to_delete.sort()

    for i in to_delete[::-1]:
        del lines[i]

    # recalculate indices, ugh
    # we cannot use a dict yet because we have duplicate entries,
    # mostly for outlines and rarely for lesion_types
    abnormality_indices, path_indices, path_desc_indices, total_outline_indices = get_indices(lines)

    # append last entry so we cant split the abnormalities
    abnormality_indices.append(len(l))

    # split the abnormalities
    abnormality_split = [l[x:abnormality_indices[i+1]] for (i, x) in
    enumerate(abnormality_indices) if i != len(abnormality_indices)-1]

    # iterate over the now-split abnormalities
    for abn in abnormality_split:
        # merge all outline dicts to list
        outlines = [x[1] for x in abn if x[0]=='OUTLINE']
        outlines_index = [i for (i, x) in enumerate(abn) if x[0]=='OUTLINE']

        # delete the old entries
        for i in outlines_index[::-1]:
            del abn[i]

        # append to list
        abn.append(['OUTLINES', outlines])

        # get lesion_type entries
        lesion_types = [x[1:] for x in abn if x[0]=='LESION_TYPE']

        # prepend NAME in front as usually there is an uneven count of
        # tags and the first entry is actually some sort of
        # description of the lesion type
        [x.insert(0, 'NAME') for x in lesion_types]

        # zip list pairs to dict in hope that there now is an even count
        lesion_types = [zip_list_to_dict(x) for x in lesion_types]

        # delete the now old entries
        lesion_type_indices = [i for (i, x) in enumerate(abn) if x[0]=='LESION_TYPE']
        for i in lesion_type_indices[::-1]:
            del abn[i]

        # append to list
        abn.append(['LESION_TYPES', lesion_types])

    # finally, return a list of dicts, each dict consisting of a lesion
    return [lines_to_dict(x) for x in abnormality_split]

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
    """
    short-hand function for calling path_to_directions() and directions_to_coords() successively.
    :param path:
    :param start_coords:
    :return:
    """
    return directions_to_coords(path_to_directions(path), start_coords)


def coords_to_polygon_mask(xy, shape):
    m = np.zeros(shape, dtype=np.bool)
    m[xy[:, 0], xy[:, 1]] = True
    return m


def coords_to_fill_mask(xy, shape):
    canvas = np.zeros(shape)
    polygon.fill_polygon(xy, canvas)  # modifies canvas in-place!
    return canvas
