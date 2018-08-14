def process_data(row):
    dict = {}
    row_array = row.split(",")
    for entry in row_array:
        if entry != "\n":
            pair = entry.split(":")
            dict[pair[0]] = pair[1]
    return dict


if __name__ == '__main__':
    row = b'rpm:2000,tps:50, fuel open time:25,ignition angle:-20,\n'
    x = process_data(row.decode("utf-8"))
    print(x)
