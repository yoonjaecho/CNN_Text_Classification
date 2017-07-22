import db_manager
import parser
import datetime

path_target = './data/articles.A-B.xml'

class Main:
    def __init__(self):
        self.parser = parser.Parser()
        self.db_manager = db_manager.DB_manager()
        
        self.file_fail_list = open('fail_list.txt', 'w')
        self.file_checkpoint =  open('checkpoint', 'r+')
        self.checkpoint = int(list(map(lambda s : s.strip(), self.file_checkpoint.readlines()))[-1].split(' | ')[0])

    def run(self):
        xmls = list(map(lambda s : s.strip(), open(path_target + '.txt', 'r').readlines()))
        total_number = len(xmls)
        fail_number = 0
        
        print('\n* Start Checkpoint: %d\n' % self.checkpoint)
        
        for xml in xmls[self.checkpoint:]:
            if self.checkpoint % 10 == 0:
                print('%d / %d, Success : %d, Fail: %d' 
                      % (self.checkpoint + 1, total_number, self.checkpoint - fail_number + 1, fail_number))
            self.checkpoint += 1

            try:
                self.parser.set_article(path_target + '/' + xml)
                sql = self.db_manager.sql_insert_into_pmid(self.parser.get_pmid(), self.parser.get_abstract()) + self.db_manager.sql_insert_into_abstract(self.parser.get_pmid(), self.parser.get_su(), self.parser.get_ppub()) + self.db_manager.sql_get_all_sentence(self.parser.get_pmid(), self.parser.get_map_label(), self.parser.get_origin_label(), self.parser.get_sentence())
                self.db_manager.commit(sql.encode())

            except KeyboardInterrupt:
                print('\n* Save Checkpoint: %d' % self.checkpoint)
                break
                
            except Exception as error:
                fail_number += 1
                print('%d / %d, Success : %d, Fail: %d' 
                      % (self.checkpoint + 1, total_number, self.checkpoint - fail_number + 1, fail_number))
                print('********************  ' + str(xml) + '  ->  ' + str(error))
                self.file_fail_list.write(str(xml) + '  ->  ' + str(error) + '\n')
                continue
        
        self.file_checkpoint.write('\n' + str(self.checkpoint) + ' | ' + str(datetime.datetime.now()))
        self.file_checkpoint.close()
        self.file_fail_list.close()
        self.db_manager.finish()

if __name__ == "__main__" :
    startTime = datetime.datetime.now()
    Main().run()
    print('* Elapsed Time : ' + str(datetime.datetime.now() - startTime) + '\n')
