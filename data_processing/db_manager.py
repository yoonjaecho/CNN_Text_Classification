import pymysql
import configparser

class DB_manager:

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('config.ini')
        self.connection = pymysql.connect(host=config.get('DB', 'host'),
                                          user=config.get('DB', 'user'),
                                          password=config.get('DB', 'password'),
                                          db=config.get('DB', 'db'))
        self.cursor = self.connection.cursor()

    def sql_insert_into_pmid(self, pmid, abstract):
        return "insert into pmid (`pmid`, `abstract`) values('" + pmid + "', '" + abstract + "');"

    def sql_insert_into_abstract(self, pmid, su, ppub):
        return "insert into abstract (`pmid`, `s/u`, `pub-date`) values('" + pmid + "', '" + su + "', '" + ppub + "');"
    
    def sql_insert_into_sentence(self, pmid, section, original_section, sentence):
        return "insert into sentence(`pmid`, `section`, `original_section`, `sentence`) values('" + pmid + "', '" + section  + "', '" + original_section + "', '" + sentence + "'); "

    def commit(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()

    def finish(self):
        self.connection.cursor.close()

if __name__ == "__main__":
    db = DB_manager()
    print(db.sql_insert_into_pmid('my_pmid', 'my_abstract'))
