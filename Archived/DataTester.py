import json
from time import sleep

from Process import Process

if __name__ == '__main__':
    processor = Process()
    while True:
        data = processor.get_data()
        print(data)
