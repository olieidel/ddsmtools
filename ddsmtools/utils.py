from datetime import date


def is_int_try(v):
    try:
        i = int(v)
    except:
        return False
    return True


def date_from_list(l):
    l = [int(x) for x in l if is_int_try(x)]
    if l[1] > 12:
        # months and day have been swapped, thanks for that
        l[0], l[1] = l[1], l[0]
    return date(day=l[0], month=l[1], year=l[2])


def file_lines_list(file, skip_list=[]):
    return [l.strip().split(' ') for l in file if len(l.strip()) > 0 and l.strip() not in skip_list]


def lines_to_dict(l):
    d = {}
    for v in l:
        try:
            k, v = line_to_kv(v)
        except:
            k = v[0]
            v = None
        d[k] = v
    return d


def line_to_kv(l):
    return (l[0], (l[1:] if len(l) > 2 else l[1])) if len(l) > 1 else (l[0],)


def flatten_single_dict_vals(d):
    for k, v in d.items():
        d[k] = flatten_list(v)
    return d


def flatten_list(l):
    if isinstance(l, (list, tuple)) and len(l) == 1:
        return l[0]
    return l


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
