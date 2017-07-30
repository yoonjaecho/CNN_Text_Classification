import os
import datetime
import sys
import DataHelper
from multiprocessing import Process, Queue

path_target = './data/articles.A-B.xml'
#path_target = './data/temp'

core_number = 4

class Main:
    def __init__(self, checkpoint=None):
        self.queue = Queue()
        self.index_pairs = []
        self.procs = []
        self.data_helper = DataHelper.DataHelper(self.queue, path_target)

        if checkpoint is None:
            d = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')
            self.file_checkpoint = open('./checkpoint/checkpoint_' + d, 'w+')
            total_number = sum(1 for line in open(path_target + '.txt'))
            print("total_number:", total_number)
            q = int(total_number / core_number)
            for i in range(core_number):
                start_index = i*q
                end_index = (i+1)*q if i == core_number-1 else (i+1)*q-1
                self.index_pairs.append((start_index, end_index))
            print("index_pairs:", self.index_pairs)

        else:
            self.file_checkpoint = open(checkpoint, 'r+')
            latest_pairs = list(map(lambda s : s.strip(), self.file_checkpoint.readlines()))[-1].split(' , ')
            for pair in latest_pairs:
                start_index, end_index = pair.split(' | ')
                self.index_pairs.append((int(start_index), int(end_index)))
            print("index_pairs:", self.index_pairs)

    def parallelize(self):
        for index, pair in enumerate(self.index_pairs):
            proc = Process(target=DataHelper.DataHelper(self.queue, path_target).run, args=(pair[0], pair[1]))
            self.procs.append(proc)
            proc.start()

        for proc in self.procs:
            proc.join()

        print('* Elapsed Time : ' + str(datetime.datetime.now() - startTime) + '\n')

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    if len(sys.argv) < 2: # First data processing
        Main().parallelize()
    else: # Data processing at specific checkpoint
        Main(sys.argv[1]).parallelize()
    
