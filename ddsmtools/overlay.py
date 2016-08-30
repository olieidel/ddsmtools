import numpy as np
from mahotas import polygon

from ddsmtools.utils import file_lines_list, zip_list_to_dict, flatten_list, is_int_try


def overlay_file_name(p):
    return '.'.join(p.split('.')[:-1]) + '.OVERLAY'


def parse_overlay(file):
    with open(file) as f:
        l = file_lines_list(f)
    total_abnorm = int(l[0][1])
    abn = []
    pos = 1
    for i in range(total_abnorm):
        # find position of last key: TOTAL_OUTLINES
        for li, v in enumerate(l[pos:]):
            if v[0] == 'TOTAL_OUTLINES':
                last_key = li + pos
                break

        until = last_key + 1

        d = {}
        for v in l[pos:until]:
            if v[0] == 'LESION_TYPE':
                lesion_attribs = ['NAME'] + v[1:]
                insert_v = [zip_list_to_dict(lesion_attribs)]
            else:
                insert_v = flatten_list(v[1:])
                insert_v = int(insert_v) if is_int_try(insert_v) else insert_v

            if v[0] in d:
                # key already in dict
                d[v[0]].append(insert_v)
            else:
                d[v[0]] = insert_v

        total_outl = d['TOTAL_OUTLINES']
        pos = until
        outl_list = []
        for j in range(total_outl):
            # in case of faulty total_outlines count, skip
            if len(l) >= pos:
                break
            outl = {'NAME': l[pos][0],
                    'START_COORDS': (int(l[pos + 1][0]), int(l[pos + 1][1])),
                    'PATH': [int(x) for x in l[pos + 1][2:-1] if is_int_try(x)]}  # remove hash at end
            outl_list.append(outl)
            pos += 2
        d['OUTLINES'] = outl_list
        abn.append(d)
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