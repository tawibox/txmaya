
def byte_convert(size):
    # 2**10 = 1024
    power = 2.0**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return round(size, 1), power_labels[n]+'B'  # 'B'='bytes'

