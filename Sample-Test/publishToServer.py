import collections
import logging
import time

import requests
from Database import Database

PUB_ENDPOINT = 'http://localhost:8081/pub'
STATS_CHANNEL = 'system_stats'

SystemInfo = collections.namedtuple(
    'SystemInfo',
    ['measurement_date', 'x', 'y'])



def top(sort_by='cpu_percent', top_n_procs=15):
    """
    A function that simulates the unix top command
    :return:
    """
    logger = logging.getLogger('PYTOP')
    db = Database()

    return SystemInfo(
        measurement_date=db.get_top()[0][0],
        x=db.get_top()[0][1],
        y=db.get_top()[0][2]
    )



def main():
    # create a session to enable persistent http connection
    s = requests.Session()

    logger = logging.getLogger('PYTOP')
    while True:
        stats = top()
        # publish to Nginx-Nchan broker
        s.post(PUB_ENDPOINT, params={'id': STATS_CHANNEL}, json=stats._asdict())
        logger.debug('Posted stats:{}'.format(stats))
        time.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()