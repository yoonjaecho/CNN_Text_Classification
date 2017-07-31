import os
import datetime
import sys
import DataHelper
from multiprocessing import Process, Queue

path_target = './data/articles.A-B.xml'
core_number = 4

class Main:
    def __init__(self, checkpoint=None):
        self.queue = Queue()
        self.index_pairs = []
        self.procs = []
        self.progress = 0

        if checkpoint is None:
            d = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')
            self.file_checkpoint = open('./checkpoint/checkpoint_' + d, 'w+')

            self.total_number = sum(1 for line in open(path_target + '.txt'))
            print("Total number of data:", self.total_number)

            q = int(self.total_number / core_number)
            for i in range(core_number):
                start_index = i*q
                end_index = self.total_number if i == core_number - 1 else (i+1)*q-1
                self.index_pairs.append((start_index, end_index))

            print("Checkpoint: " + str(self.index_pairs) + '\n')

        else:
            self.file_checkpoint = open(checkpoint, 'r+')

            latest_pairs = list(map(lambda s : s.strip(), self.file_checkpoint.readlines()))[-1].split(' , ')
            for index, pair in enumerate(latest_pairs):
                if index != core_number:
                    print(pair)
                    start_index, end_index = pair.split(' / ')
                    self.index_pairs.append((int(start_index), int(end_index)))
                else:
                    self.progress = int(pair.split(' / ')[0])
                    self.total_number = int(pair.split(' / ')[1])
                    
            print("index_pairs:", self.index_pairs)

    def parallelize(self):
        try:
            for index, pair in enumerate(self.index_pairs):
                proc = Process(target=DataHelper.DataHelper(self.queue, path_target).run, args=(pair[0], pair[1]))
                self.procs.append(proc)
                proc.start()

            for proc in self.procs:
                proc.join()

        except KeyboardInterrupt:
            alive_core = core_number
            while alive_core > 0:
                for proc in self.procs:
                    if proc.is_alive() == False:
                        alive_core -= 1

            print("\nKEYBOARD INTERRUPT !!\n")

            check_message = ''
            pairs = []
            for i in range(core_number):
                pairs.append(self.queue.get())

            pairs.sort()
            for pair in pairs:
                check_message += str(pair[0]) + ' / ' + str(pair[1]) + ' , '
                self.progress += int(pair[2])
            check_message += str(self.progress) + ' / ' + str(self.total_number) + '\n'
            print('{}/{} : {:.2f} % complete..\n'.format(self.progress, self.total_number, self.progress / self.total_number * 100))
            #print(str(self.progress) + ' / ' + str(self.total_number) + ', ' + str(self.progress / self.total_number * 100) + '% complete..')

            self.file_checkpoint.write(check_message)
            self.file_checkpoint.close()

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    if len(sys.argv) < 2: # First data processing
        Main().parallelize()
    else: # Data processing at specific checkpoint
        Main(sys.argv[1]).parallelize()
    print('* Elapsed Time : ' + str(datetime.datetime.now() - startTime) + '\n')
