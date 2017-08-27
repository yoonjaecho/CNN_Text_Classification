import pymysql
import configparser
import nltk

class Extract_abstarct:
    def __init__(self, filepath):
        config = configparser.RawConfigParser()
        config.read('config.ini')
        self.connection = pymysql.connect(
                    host=config.get('DB', 'host'),
                    user=config.get('DB', 'user'),
                    password=config.get('DB', 'password'),
                    db=config.get('DB','db')
        )
        self.cursor = connection.cursor(pymysql.cursors.DictCursor)
        self.file = open(filepath, 'w')

    def run(self):
        sql = "select abstract from pmid;"
        self.cursor.execute(sql.encode())
        results = self.cursor.fetchall()

        is_noun = lambda pos:pos[:2] == 'NN'
        for lines in results:
            tokenized = nltk.word_tokenize(lines['abstract'])
            nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
            lower_nouns = [x.lower() for x in filter(lambda y: len(y)>=2, nouns)] self.file.write(" ".join(lower_nouns) + '\n')

        self.file.close()

if __name__ == '__main__':
    Extract_abstarct('input_abstract.txt').run()
