import os
import datetime
import sys
import DataHelper
from multiprocessing import Process, Queue

file_name_list = './data/articles.A-Z.xml.txt'
core_number = 4

class Main:
    def __init__(self, checkpoint=None):
        self.queue = Queue()
        self.index_pairs = []
        self.procs = []
        self.progress = 0
        self.xmls = list(map(lambda s : s.strip(), open(file_name_list, 'r').readlines()))
        
        if checkpoint is None:
            self.file_checkpoint = open('./checkpoint/checkpoint_' + datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S'), 'w+')
            self.total_number = len(self.xmls)
            q = int(self.total_number / core_number)
            
            for i in range(core_number):
                start_index = i * q
                end_index = self.total_number if i == core_number - 1 else (i + 1) * q - 1
                self.index_pairs.append((start_index, end_index))
                
        else:
            self.file_checkpoint = open(checkpoint, 'r+')
            latest_pairs = list(map(lambda s : s.strip(), self.file_checkpoint.readlines()))[-1].split(' , ')
            
            for index in range(core_number):
                start_index, end_index = map(int, latest_pairs[index].split(' / '))
                self.index_pairs.append((start_index, end_index))
                
            self.progress, self.total_number = map(int, latest_pairs[-1].split(' / ')) 
            
        print("Total number of data:", self.total_number)            
        print("Checkpoint: " + str(self.index_pairs) + '\n')

    def parallelize(self):
        try:
            for index, pair in enumerate(self.index_pairs):
                proc = Process(target=DataHelper.DataHelper(self.queue, self.xmls[pair[0]:pair[1]+1]).run, args=(pair[0], pair[1]))
                self.procs.append(proc)
                proc.start()

            for proc in self.procs:
                proc.join()

        except KeyboardInterrupt:
            # Wait for all processes to terminate
            while True:
                alive_proc = False
                for proc in self.procs:
                    if proc.is_alive() == True:
                        alive_proc = True
                if alive_proc == False:
                    break

            print("\nKEYBOARD INTERRUPT !!\n")

            # Save checkpoint ...
            check_message = ''
            pairs = [self.queue.get() for i in range(core_number)]
            pairs.sort()

            for pair in pairs:
                check_message += str(pair[0]) + ' / ' + str(pair[1]) + ' , '
                self.progress += int(pair[2])
            check_message += str(self.progress) + ' / ' + str(self.total_number) + '\n'
            print('{}/{} : {:.2f} % complete..\n'.format(self.progress, self.total_number, self.progress / self.total_number * 100))

            self.file_checkpoint.write(check_message)
            self.file_checkpoint.close()

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    
    if len(sys.argv) < 2: # First data processing
        Main().parallelize()
    else: # Data processing at specific checkpoint
        Main(sys.argv[1]).parallelize()
        
    print('* Elapsed Time : ' + str(datetime.datetime.now() - startTime) + '\n')
