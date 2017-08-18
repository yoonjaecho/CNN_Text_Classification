import DBManager
import Parser
import datetime
import sys
import os

class DataHelper:
    def __init__(self, queue, xmls):
        self.parser = Parser.Parser()
        self.db = DBManager.DBManager()
        self.queue = queue
        self.xmls = xmls

    def terminate(self):
        self.db.finish()

    def run(self, start_index, end_index):
        checkpoint = start_index
        progess = 0
        print('* Start Checkpoint: %d' % checkpoint)
        
        for xml in self.xmls:
            try:
                self.parser.set_article(xml)
                print 'processing file : ', xml
                # print 'insert pmid'
                sql = self.db.sql_insert_into_pmid(self.parser.get_pmid(),
                                                   self.parser.get_abstract())
                # print 'insert abstract'
                sql += self.db.sql_insert_into_abstract(self.parser.get_pmid(),
                                                        self.parser.get_su(),
                                                        self.parser.get_ppub())
                # print 'insert sentence'
                sql += self.db.sql_get_all_sentence(self.parser.get_pmid(),
                                                    self.parser.get_map_label(),
                                                    self.parser.get_origin_label(),
                                                    self.parser.get_sentence())

                # print 'insert sql commit'
                # print sql.encode()
                self.db.commit(sql.encode())
                # print 'end'

            except KeyboardInterrupt:
                print('* Save Checkpoint: %d' % checkpoint)
                self.queue.put((checkpoint, end_index, progess))
                self.terminate()
                return
            
            except Exception as error:
                self.db.check_connection()
                print(str(xml) + " -> " + str(error) + " [" + str(checkpoint) + "/" + str(end_index) + "]")
                fail_sql = self.db.sql_insert_into_fail(str(xml), str(error).replace("'", ""))
                self.db.commit(fail_sql.encode())

            checkpoint += 1
            progess += 1

        # Finish work at this process
        print('A subprocess finished at {}'.format(end_index))
        self.queue.put((checkpoint, end_index, progess))
        self.terminate()