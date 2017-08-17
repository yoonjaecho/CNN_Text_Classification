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
        self.sections_num = { '0': 'BACKGROUND', '1': 'OBJECTIVE', '2': 'METHODS', '3': 'RESULTS', '4': 'CONCLUSIONS' }

        self.sentences_count = { 'BACKGROUND': 0, 'OBJECTIVE': 0, 'METHODS': 0, 'RESULTS': 0, 'CONCLUSIONS': 0, '-': 0}
        for key in self.sentences_count:
            sql = self.db.sql_select_section_count(key)
            result = self.db.fetch(sql)
            self.sentences_count[key] = result[0]['count']
        
    def exist_dir(self):
        if not os.path.isdir(path_train):
            os.mkdir(path_train)
        if not os.path.isdir(path_eval):
            os.mkdir(path_eval)
        if not os.path.isdir(path_test):
            os.mkdir(path_test)
            
    def exist_section(self, list_section):
        for section in list_section:
            if (not section in self.sections) and (not section in self.sections_num):
                print("... The '%s' section does not exist." % (section))
                return False
        return True
    
    def check_pos_int(self, value):
        try:
            if int(value) < 0:
                print('... Input must be a positive integer.')
                return False
        except ValueError:
            print("... '%s' is not an integer." % (value))
            return False
        
        return True
    
    def replace_section(self, list_section):
        for index, number in enumerate(list_section):
            if number in self.sections_num:
                list_section[index] = self.sections_num[number]
        
        return set(list_section)

    def print_data(self, argv):
        if len(argv) < 2:
            print('... PRINT SAVE [section name]+ [train count] [eval count]')
            print('... PRINT TEST [count]')
            return
        if (not argv[1] == 'SAVE') and (not argv[1] == 'TEST'):
            print('... PRINT SAVE [section name]+ [train count] [eval count]')
            print('... PRINT TEST [count]')
            return
        
        if argv[1] == 'SAVE':
            if len(argv) < 5:
                print('... PRINT SAVE [section name]+ [train count] [eval count]')
                return
            if not self.exist_section(argv[2:-2]): # Check if a section does not exist
                return
            if not self.check_pos_int(argv[-2]) or not self.check_pos_int(argv[-1]):
                return
            
            count_train = int(argv[-2])
            count_eval = int(argv[-1])
            count_total = count_train + count_eval
            list_section = self.replace_section(argv[2:-2])
            
            for section in list_section:
                sql = self.db.sql_select_section_sentence(section, count_total)
                result = self.db.fetch(sql.encode())
                
                print(json.dumps(result[:count_train], indent=4))
                print('------------------------------------------------------------------------------------------ End of train data.')
                print(json.dumps(result[count_train : count_total], indent=4))
                print('------------------------------------------------------------------------------------------ End of eval data.')
                
        if argv[1] == 'TEST':
            if len(argv) < 3:
                print('... PRINT TEST [count]')
                return
            if not self.check_pos_int(argv[2]):
                return
            
            count_total = int(argv[2])
            sql = self.db.sql_select_not_section_sentence(count_total)
            result = self.db.fetch(sql.encode())
            
            print(json.dumps(result, indent=4))
            print('------------------------------------------------------------------------------------------ End of test data.')
            
    def save_data(self, argv):
        if len(argv) < 4:
            print('... SAVE [section name]+ [train count] [eval count]')
            return
        if not self.exist_section(argv[1:-2]): # Check if a section does not exist
            return
        if not self.check_pos_int(argv[-2]) or not self.check_pos_int(argv[-1]):
            return
        
        list_section = self.replace_section(argv[1:-2])
        count_train = int(argv[-2])
        count_eval = int(argv[-1])
        count_total = count_train + count_eval
        
        self.exist_dir() # Check if a directory does not exist
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
        if len(argv) < 2:
            print('... TEST [count]')
            return
        if not self.check_pos_int(argv[1]):
            return
        
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
        print('\n* [command] [section name]+ [count]+\n')
        
        print('* Command:')
        print(' > PRINT: Used to check the result value.')
        print(' > SAVE: The result values are stored in 2 types. (train, eval)')
        print(' > TEST: Store the test data.')
        print(' > HELP: Print the manual.')
        print(' > EXIT: Exit the program.\n')
        
        print('* Section name:')
        print(' > Available section names are:')
        print('  { BACKGROUND: 0, OBJECTIVE: 1, METHODS: 2, RESULTS: 3, CONCLUSIONS: 4 }\n')
        
        print('* Count:')
        print(' > The number of sentences.')
        print(' > In the SAVE command, must input the each data count. (train, eval)\n')
        
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
