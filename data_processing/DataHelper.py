import DBManager
import Parser
import datetime
import sys
import os

class DataHelper:
    def __init__(self, queue, path_target):
        self.parser = Parser.Parser()
        self.db = DBManager.DBManager()
        self.queue = queue
        self.path_target = path_target

    def terminate(self):
        self.db.finish()

    def run(self, start_index, end_index):
        xmls = list(map(lambda s : s.strip(), open(self.path_target + '.txt', 'r').readlines()))
        total_number = len(xmls)
        checkpoint = start_index

        print('* Start Checkpoint: %d' % checkpoint)
        
        for xml in xmls[start_index:end_index+1]:
            try:
                self.parser.set_article(self.path_target + '/' + xml)
                sql = self.db.sql_insert_into_pmid(self.parser.get_pmid(),
                                                           self.parser.get_abstract()) 
                sql += self.db.sql_insert_into_abstract(self.parser.get_pmid(),
                                                                self.parser.get_su(),
                                                                self.parser.get_ppub()) 
                sql += self.db.sql_get_all_sentence(self.parser.get_pmid(),
                                                            self.parser.get_map_label(),
                                                            self.parser.get_origin_label(),
                                                            self.parser.get_sentence())
                self.db.commit(sql.encode())

            except KeyboardInterrupt:
                print('* Save Checkpoint: %d' % checkpoint)
                self.queue.put((checkpoint, end_index))
                break
                
            except Exception as error:
                sql = self.db.sql_insert_into_fail(str(xml), str(error))
                self.db.commit(sql.encode())
                print(str(xml) + " [" + str(checkpoint) + "/" + str(end_index) + "] -> " + str(error))
                checkpoint += 1
                continue

            checkpoint += 1

        self.terminate()
