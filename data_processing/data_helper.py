import db_manager
import parser
import datetime
import sys

path_target = './data/articles.A-B.xml'

class Main:
    def __init__(self, init_check=None):
        self.parser = parser.Parser()
        self.db_manager = db_manager.DB_manager()
        
        if init_check != None:
            print("Data processing starts at", init_check)
            self.file_checkpoint = open(init_check, 'r+')
            self.file_fail_list = open('fail_list.txt', 'a')
            self.fail_number = sum(1 for line in open('fail_list.txt'))
            self.checkpoint = int(list(map(lambda s : s.strip(), self.file_checkpoint.readlines()))[-1].split(' | ')[0])
        else:
            print("First data processing..")
            d = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')
            self.file_checkpoint = open('./checkpoint/checkpoint_' + d, 'w+')
            self.file_fail_list = open('fail_list.txt', 'w+')
            self.fail_number = 0
            self.checkpoint = 0
            
    def terminate(self):
        self.file_checkpoint.close()
        self.file_fail_list.close()
        self.db_manager.finish()
        
    def run(self):
        xmls = list(map(lambda s : s.strip(), open(path_target + '.txt', 'r').readlines()))
        total_number = len(xmls)
        print('* Start Checkpoint: %d\n' % self.checkpoint)
        
        for xml in xmls[self.checkpoint:]:
            self.checkpoint += 1
            try:
                self.parser.set_article(path_target + '/' + xml)
                sql = self.db_manager.sql_insert_into_pmid(self.parser.get_pmid(),
                                                           self.parser.get_abstract()) 
                sql += self.db_manager.sql_insert_into_abstract(self.parser.get_pmid(),
                                                                self.parser.get_su(),
                                                                self.parser.get_ppub()) 
                sql += self.db_manager.sql_get_all_sentence(self.parser.get_pmid(),
                                                            self.parser.get_map_label(),
                                                            self.parser.get_origin_label(),
                                                            self.parser.get_sentence())
                self.db_manager.commit(sql.encode())

            except KeyboardInterrupt:
                print('\n* Save Checkpoint: %d' % self.checkpoint)
                break
                
            except Exception as error:
                self.fail_number += 1
                print('%d / %d, Success : %d, Fail: %d' 
                      % (self.checkpoint + 1, total_number, self.checkpoint - self.fail_number + 1, self.fail_number))
                err_message = str(xml) + ' -> ' + str(error) + ', at [' + str(self.checkpoint - 1) + '/' + str(total_number) +']'
                print(err_message)
                self.file_fail_list.write(err_message + '\n')
                continue
                
            if self.checkpoint % 10 == 0:
                print('%d / %d, Success : %d, Fail: %d' 
                      % (self.checkpoint + 1, total_number, self.checkpoint - self.fail_number + 1, self.fail_number))
                
        self.file_checkpoint.write('\n' + str(self.checkpoint) + ' | ' + str(datetime.datetime.now()))
        self.terminate()

if __name__ == "__main__" :
    startTime = datetime.datetime.now()
    if len(sys.argv) < 2: # First data processing
        Main().run()
    else: # Data processing at specific checkpoint
        Main(sys.argv[1]).run()
    print('* Elapsed Time : ' + str(datetime.datetime.now() - startTime) + '\n')
