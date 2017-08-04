import pymysql
import configparser

class DBManager:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('config.ini')
        self.connection = pymysql.connect(host=config.get('DB', 'host'),
                                          user=config.get('DB', 'user'),
                                          password=config.get('DB', 'password'),
                                          db=config.get('DB', 'db'))
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    def sql_insert_into_pmid(self, pmid, abstract):
        return "insert into pmid (`pmid`, `abstract`) values('" + pmid + "', '" + abstract + "');"

    def sql_insert_into_abstract(self, pmid, su, ppub):
        return "insert into abstract (`pmid`, `s/u`, `pub-date`) values('" + pmid + "', '" + su + "', '" + ppub + "');"
    
    def sql_insert_into_sentence(self, pmid, section, original_section, sentence):
        return "insert into sentence(`pmid`, `section`, `original_section`, `sentence`) values('" + pmid + "', '" + section  + "', '" + original_section + "', '" + sentence + "'); "

    def sql_get_all_sentence(self, pmid, sections, original_sections, sentences):
        sql = ''
        
        if sections == '-':
            for sentence in sentences[0]:
                sql += self.sql_insert_into_sentence(pmid, '-', '-', sentence)
        else:
            for index, section in enumerate(sections):
                for sentence in sentences[index]:
                    sql += self.sql_insert_into_sentence(pmid, sections[index], original_sections[index], sentence)
        
        return sql
    
    def sql_insert_into_fail(self, file_name, error):
        return "insert into fail (`file_name`, `error`) values('" + file_name + "', '" + error + "');"
    
    def sql_select_section_sentence(self, section, count):
        return "select sentence from sentence where `section` = '" + section + "' order by rand() limit " + str(count) + ";"
    
    def sql_select_not_section_sentence(self, section, count):
        return "select section, sentence from sentence where `section` = '-' order by rand() limit " + str(count) + ";"
    
    def fetch(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def commit(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()

    def finish(self):
        self.connection.close()

if __name__ == "__main__":
    db = DBManager()
    print(db.sql_insert_into_pmid('my_pmid', 'my_abstract'))
