import os
from glob import glob

from ddsmtools.utils import file_lines_list, lines_to_dict, flatten_single_dict_vals, dict_vals_to_int, date_from_list, \
    zip_list_to_dict


def ics_file_name(path):
    dir_name = os.path.dirname(path)
    ics_files = glob(dir_name + '/*.ics')
    if len(ics_files) == 0:
        print('found no corresponding ics file')
        return None
    elif len(ics_files) == 1:
        # print('found ics file')
        return ics_files[0]
    else:
        print('found multiple ics files! Using first one.')
        return ics_files[0]


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
    ics_attribs['DIGITIZER'] = ' '.join(ics_attribs['DIGITIZER'])

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
