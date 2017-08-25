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

        self.sentences_count_original = { }
        self.sentences_count = { 'BACKGROUND': 0, 'OBJECTIVE': 0, 'METHODS': 0, 'RESULTS': 0, 'CONCLUSIONS': 0, '-': 0}
        for key in self.sentences_count:
            sql = self.db.sql_select_section_count(key)
            result = self.db.fetch(sql)
            self.sentences_count[key] = int(result[0]['count'])
        
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
    
    def exist_original_section(self, list_section):
        count = 0
        for section in list_section:
            if not section in self.sentences_count_original:
                sql = self.db.sql_select_original_section_count(section)
                result = self.db.fetch(sql)
                self.sentences_count_original[section] = int(result[0]['count'])
                
            count += self.sentences_count_original[section]
            
        if count == 0:
            print("... The '%s' section does not exist." % (", ".join(list_section)))
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

    def check_sentence_count(self, list_section, count):
        for section in self.replace_section(list_section):
            sentences = self.sentences_count[section]
            if count > sentences:
                print('... The number of sentences exceeds the range. (%d / %d)' % (count, sentences))
                return False
        return True
    
    def check_sentence_count_original(self, list_section, count):
        sentences = 0
        for section in self.replace_section(list_section):
            sentences += self.sentences_count_original[section]
            
        if count > sentences:
            print('... The number of sentences exceeds the range. (%d / %d)' % (count, sentences))
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
            print('... PRINT SECTION [original_section name]+ [count]')
            print('... PRINT TEST [count]')
            return
        if (not argv[1] == 'SAVE') and (not argv[1] == 'TEST') and (not argv[1] == 'SECTION'):
            print('... PRINT SAVE [section name]+ [train count] [eval count]')
            print('... PRINT SECTION [original_section name]+ [count]')
            print('... PRINT TEST [count]')
            return
        
        if argv[1] == 'SAVE':
            self.save_data(argv[1:], True)
        if argv[1] == 'SECTION':
            self.section_data(argv[1:], True)
        if argv[1] == 'TEST':
            self.test_data(argv[1:], True)
            
    def save_data(self, argv, check_print=False):
        if len(argv) < 4:
            print('...%s SAVE [section name]+ [train count] [eval count]' % (' PRINT' if check_print else ''))
            return
        if not self.exist_section(argv[1:-2]):
            return
        if not self.check_pos_int(argv[-2]) or not self.check_pos_int(argv[-1]):
            return
        if not self.check_sentence_count(argv[1:-2], int(argv[-1]) + int(argv[-2])):
            return
        
        list_section = self.replace_section(argv[1:-2])
        count_train = int(argv[-2])
        count_eval = int(argv[-1])
        count_total = count_train + count_eval
        
        if check_print:
            for section in list_section:
                sql = self.db.sql_select_section_sentence(section, count_total)
                result = self.db.fetch(sql.encode())
                
                print(json.dumps(result[:count_train], indent=4))
                print('------------------------------------------------------------------------------------------ End of train data.')
                print(json.dumps(result[count_train : count_total], indent=4))
                print('------------------------------------------------------------------------------------------ End of eval data.')
                
        else:
            self.exist_dir()
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
            
    def section_data(self, argv, check_print=False):
        if len(argv) < 3:
            print('...%s SECTION [original_section name]+ [count]' % (' PRINT' if check_print else ''))
            return
        if not self.exist_original_section(argv[1:-1]):
            return
        if not self.check_pos_int(argv[-1]):
            return
        if not self.check_sentence_count_original(argv[1:-1], int(argv[-1])):
            return
        
        list_section = self.replace_section(argv[1:-1])
        count_total = int(argv[-1])
        
        if check_print:
            sql = self.db.sql_select_original_list_section_sentence(list_section, count_total)
            result = self.db.fetch(sql.encode())

            print(json.dumps(result, indent=4))
            print('------------------------------------------------------------------------------------------ End of section data.')
                
        else:
            self.exist_dir()
            file_test = open(path_test + '_'.join(list(map(lambda s : s.lower(), list_section))) + '_' + str(count_total) + '.csv', 'w')

            for section in list_section:
                sql = self.db.sql_select_original_list_section_sentence(list_section, count_total)
                result = self.db.fetch(sql.encode())

                for target in result:
                    file_test.write('%s:::%s\n' % (target['original_section'], target['sentence']))

            file_test.close()
            print('... OK')
   
    def test_data(self, argv, check_print=False):
        if len(argv) < 2:
            print('...%s TEST [count]' % (' PRINT' if check_print else ''))
            return
        if not self.check_pos_int(argv[1]):
            return
        if not self.check_sentence_count(['-'], int(argv[1])):
            return

        count_total = int(argv[1])
        
        if check_print:
            sql = self.db.sql_select_not_section_sentence(count_total)
            result = self.db.fetch(sql.encode())
            
            print(json.dumps(result, indent=4))
            print('------------------------------------------------------------------------------------------ End of test data.')
        
        else:
            self.exist_dir()
            file_test = open(path_test +  'test_' + str(count_total) + '.csv', 'w')
            
            sql = self.db.sql_select_not_section_sentence(count_total)
            result = self.db.fetch(sql.encode())
            
            for target in result:
                file_test.write('%s\n' % (target['sentence']))
                
            file_test.close()
            print('... OK')
        
    def print_manual(self):
        print('\n* [command] [original_section | section name]+ [count]+\n')
        
        print('* Command:')
        print(' > PRINT: Used to check the result value.')
        print(' > SAVE: The result values are stored in 2 types. (train, eval)')
        print(' > SECTION: Store the result values based on the original section. (test)')
        print(' > TEST: Store the test data. (test)')
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
            elif (command[0] == 'SECTION'):
                self.section_data(command)
            elif (command[0] == 'TEST'):
                self.test_data(command)
            elif (command[0] == 'HELP'):
                self.print_manual()
            else:
                print('... Unknown Command')
         
        self.db.finish()
        
if __name__ == '__main__':
    Extractor().run()
