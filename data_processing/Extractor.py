import sys
import os
import json
import DBManager

path_train = 'data/train_data/'
path_eval = 'data/eval_data/'
path_test = 'data/test_data/'

class Extractor:
    def __init__(self):
        self.db = DBManager.DBManager()
        self.sections = { 'BACKGROUND': 0, 'OBJECTIVE': 1, 'METHODS': 2, 'RESULTS': 3, 'CONCLUSIONS': 4 }
        
    def exist_dir(self):
        if not os.path.isdir(path_train):
            os.mkdir(path_train)
        if not os.path.isdir(path_eval):
            os.mkdir(path_eval)
        if not os.path.isdir(path_test):
            os.mkdir(path_test)

    def print_data(self, argv):
        section = argv[1]
        count = argv[2]
        
        sql_target = self.db.sql_select_section_sentence(section, count)
        print(json.dumps(self.db.fetch(sql_target.encode()), indent = 4))
                         
    def save_data(self, argv):
        list_section = argv[1:-2]
        count_train = int(argv[-2])
        count_eval = int(argv[-1])
        count_total = count_train + count_eval
        
        self.exist_dir() # Check does exist directory
        file_train = open(path_train + '_'.join(list(map(lambda s : s.lower(), list_section))) + '_' + str(count_train) + '.csv', 'w')
        file_eval = open(path_eval + '_'.join(list(map(lambda s : s.lower(), list_section))) + '_' + str(count_eval) + '.csv', 'w')
        
        for section in list_section:
            sql = self.db.sql_select_section_sentence(section, count_total)
            result = self.db.fetch(sql.encode())
            
            for target in result[:count_train]:
                file_train.write('%d:::%s\n' % (self.sections[target['section']], target['sentence']))
            for target in result[count_train : count_total]:
                file_eval.write('%d:::%s\n' % (self.sections[target['section']], target['sentence']))
        
        file_train.close()
        file_eval.close()
        print('... OK')
   
    def test_data(self, argv):
        count_total = int(argv[1])
        
        self.exist_dir() # Check does exist directory
        file_test = open(path_test +  'test_' + str(count_total) + '.csv', 'w')
        
        sql = self.db.sql_select_not_section_sentence(count_total)
        result = self.db.fetch(sql.encode())
        
        for target in result:
            file_test.write('%s\n' % (target['sentence']))
        
        file_test.close()
        print('... OK')
        
    def print_manual(self):
        print('\n* [command] [section name] [count]\n')
        
        print('* Command:')
        print(' > PRINT: It is used to check the result value.')
        print(' > SAVE: The result values are stored in 3 types. (train, eval, test)')
        print(' > HELP: Print the manual.')
        print(' > EXIT: Exit the program.\n')
        
        print('* Section name:')
        print(' > Available section names are:')
        print('  { BACKGROUND, OBJECTIVE, METHODS, RESULTS, CONCLUSIONS }\n')
        
        print('* Count:')
        print(' > The number of sentences.\n')
        
    def run(self):
        self.print_manual()

        while True:
            command = input('\n> ').upper().split(' ')
            
            if (command[0] == 'EXIT'):
                print('... Bye')
                break
            elif (command[0] == 'PRINT'):
                self.print_data(command)
            elif (command[0] == 'SAVE'):
                self.save_data(command)
            elif (command[0] == 'TEST'):
                self.test_data(command)
            elif (command[0] == 'HELP'):
                self.print_manual()
            else:
                print('... Unknown Command')
         
        self.db.finish()
        
if __name__ == '__main__':
    Extractor().run()
