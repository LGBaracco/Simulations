import os
from multiprocessing import Pool

processes = ('aggregation_part2.py', 'aggregation_part3.py', 'aggregation_part4.py')


def run_process(process):
    os.system('python {}'.format(process))


if __name__ == '__main__':

    pool = Pool(processes=3)
    pool.map(run_process, processes)
