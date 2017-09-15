import pymysql
import configparser
import nltk

class Extract_abstarct:
    def __init__(self, filepath):
        config = configparser.RawConfigParser()
        config.read('../data_processing/config.ini')
        self.connection = pymysql.connect(
                    host=config.get('DB', 'host'),
                    user=config.get('DB', 'user'),
                    password=config.get('DB', 'password'),
                    db=config.get('DB','db')
        )
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        self.file = open(filepath, 'w')

    def run(self):
        sql = "select abstract from pmid;"
        self.cursor.execute(sql.encode())
        results = self.cursor.fetchall()
 
        for lines in results:
            self.file.write('%s\n' % (' '.join(lines['abstract'].split())))

        self.file.close()

if __name__ == '__main__':
    Extract_abstarct('input_abstract_for_np.txt').run()
