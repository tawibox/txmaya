# re-range, fit tool


def re_range(value_old, max_old, min_old, max_new, min_new):
    range_old = (max_old - min_old)
    range_new = (max_new - min_new)
    value_new = (((value_old - min_old) * range_new) / range_old) + min_new
    return value_new

