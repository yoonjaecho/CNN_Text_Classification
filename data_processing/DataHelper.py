import db_manager
import parser
import datetime
import sys
import os

class DataHelper:
    def __init__(self, queue, path_target):
        self.parser = parser.Parser()
        self.db_manager = db_manager.DB_manager()
        self.queue = queue
        self.path_target = path_target
        self.pid = os.getpid()

    def terminate(self):
        self.db_manager.finish()

    def run(self, start_index, end_index):
        xmls = list(map(lambda s : s.strip(), open(self.path_target + '.txt', 'r').readlines()))
        total_number = len(xmls)
        checkpoint = start_index
        print('* Start Checkpoint: %d\n' % checkpoint)
        
        for xml in xmls[start_index:end_index+1]:
            print(self.pid, "is running at",checkpoint)

            try:
                self.parser.set_article(self.path_target + '/' + xml)
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
                print("Success")

            except KeyboardInterrupt:
                print('\n* Save Checkpoint: %d' % checkpoint)
                self.queue.put(checkpoint, end_index)
                break
                
            except Exception as error:
                sql = self.db_manager.sql_insert_into_fail(str(xml),
                                                           str(error))
                self.db_manager.commit(sql.encode())
                print("Error")
                continue

            checkpoint += 1
                
        self.terminate()
