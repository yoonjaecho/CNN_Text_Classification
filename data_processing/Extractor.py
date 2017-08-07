import sys
import os
import json
import DBManager

path_training = 'data/training_data/'
path_eval = 'data/eval_data/'
path_test = 'data/test_data/'

class Extractor:
    def __init__(self):
        self.db = DBManager.DBManager()
        self.sections = { 'BACKGROUND': 0, 'OBJECTIVE': 1, 'METHODS': 2, 'RESULTS': 3, 'CONCLUSIONS': 4 }
        
    def exist_dir(self):
        if not os.path.isdir(path_training):
            os.mkdir(path_training)
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
        section = argv[1]
        count = int(argv[2])
        
        sql_target = self.db.sql_select_section_sentence(section, count * 2)
        sql_no_target = self.db.sql_select_not_section_sentence(section, count)
        result_target = self.db.fetch(sql_target.encode())
        result_no_target = self.db.fetch(sql_no_target.encode())

        self.exist_dir() # Check does exist directory
        
        file_training = open(path_training + section.lower() + '_' + str(count) + '.csv', 'w')
        file_eval = open(path_eval + section.lower() + '_' + str(count) + '.csv', 'w')
        file_test = open(path_test + 'not_' + section.lower() + '_' + str(count) + '.csv', 'w')
        for i in range(int(count)):
            file_training.write('%d:::%s\n' % (self.sections[section], result_target[i]['sentence']))
            file_eval.write('%d:::%s\n' % (self.sections[section], result_target[i + count]['sentence']))
            file_test.write('%s\n' % (result_no_target[i]['sentence']))
        
        file_training.close()
        file_eval.close()
        file_test.close()
        
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
                print('... OK')
            elif (command[0] == 'HELP'):
                self.print_manual()
            else:
                print('... Unknown Command')
         
        self.db.finish()
        
if __name__ == '__main__':
    Extractor().run()
