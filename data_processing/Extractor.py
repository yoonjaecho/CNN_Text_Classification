import sys
import os
import json
import DBManager

path_train = 'data/train_data/'
path_eval = 'data/eval_data/'
path_test = 'data/test_data/'

separator = ':::'

command_print = 'PRINT'
command_map = 'MAP'
command_origin = 'ORIGIN'
command_test = 'TEST'
command_help = 'HELP'
command_exit = 'EXIT'

syntax_map = '[mapped_section name]+ [train count] [eval count]'
syntax_origin = '[original_section name]+ [count]'
syntax_test = '[count]'

class Extractor:
    def __init__(self):
        self.db = DBManager.DBManager()
        self.mapped_sections = { 'BACKGROUND': 0, 'OBJECTIVE': 1, 'METHODS': 2, 'RESULTS': 3, 'CONCLUSIONS': 4 }
        self.mapped_sections_num = { '0': 'BACKGROUND', '1': 'OBJECTIVE', '2': 'METHODS', '3': 'RESULTS', '4': 'CONCLUSIONS' }
        
        self.sentences_count_original = { }
        self.sentences_count_mapped = { 'BACKGROUND': 0, 'OBJECTIVE': 0, 'METHODS': 0, 'RESULTS': 0, 'CONCLUSIONS': 0, '-': 0}
        for key in self.sentences_count_mapped:
            sql = self.db.sql_select_section_count(key)
            result = self.db.fetch(sql)
            self.sentences_count_mapped[key] = int(result[0]['count'])
        
    def exist_dir(self):
        if not os.path.isdir(path_train):
            os.mkdir(path_train)
        if not os.path.isdir(path_eval):
            os.mkdir(path_eval)
        if not os.path.isdir(path_test):
            os.mkdir(path_test)
            
    def exist_mapped_section(self, list_section):
        for section in list_section:
            if (not section in self.mapped_sections) and (not section in self.mapped_sections_num):
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
            print("... The '%s' section does not exist." % (', '.join(list_section)))
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

    def check_sentence_count_mapped(self, list_section, count):
        for section in self.replace_mapped_section(list_section):
            sentences = self.sentences_count_mapped[section]
            if count > sentences:
                print('... The number of sentences exceeds the range. (%d / %d)' % (count, sentences))
                return False
            
        return True
    
    def check_sentence_count_original(self, list_section, count):
        sentences = 0
        for section in list_section:
            sentences += self.sentences_count_original[section]
            
        if count > sentences:
            print('... The number of sentences exceeds the range. (%d / %d)' % (count, sentences))
            return False
        
        return True
    
    def replace_mapped_section(self, list_section):
        for index, number in enumerate(list_section):
            if number in self.mapped_sections_num:
                list_section[index] = self.mapped_sections_num[number]
        
        return set(list_section)

    def print_processing(self, argv):
        if len(argv) < 2:
            print('... %s %s %s' % (command_print, command_map, syntax_map))
            print('... %s %s %s' % (command_print, command_origin, syntax_origin))
            print('... %s %s %s' % (command_print, command_test, syntax_test))
            return
        if (not argv[1] == command_map) and (not argv[1] == command_origin) and (not argv[1] == command_test):
            print('... %s %s %s' % (command_print, command_map, syntax_map))
            print('... %s %s %s' % (command_print, command_origin, syntax_origin))
            print('... %s %s %s' % (command_print, command_test, syntax_test))
            return
        
        if argv[1] == command_map:
            self.mapped_section_processing(argv[1:], True)
        elif argv[1] == command_origin:
            self.original_section_processing(argv[1:], True)
        elif argv[1] == command_test:
            self.test_processing(argv[1:], True)
            
    def mapped_section_processing(self, argv, check_print=False):
        if len(argv) < 4:
            print('...%s %s %s' % (' ' + command_print if check_print else '', command_map, syntax_map))
            return
        if not self.exist_mapped_section(argv[1:-2]):
            return
        if (not self.check_pos_int(argv[-2])) or (not self.check_pos_int(argv[-1])):
            return
        if not self.check_sentence_count_mapped(argv[1:-2], int(argv[-1]) + int(argv[-2])):
            return
        
        list_section = self.replace_mapped_section(argv[1:-2])
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
                    file_train.write('%d%s%s\n' % (self.mapped_sections[target['section']], ,separator, ' '.join(target['sentence'].split())))
                for target in result[count_train : count_total]:
                    file_eval.write('%d%s%s\n' % (self.mapped_sections[target['section']], separator, ' '.join(target['sentence'].split())))

            file_train.close()
            file_eval.close()
            print('... OK')
            
    def original_section_processing(self, argv, check_print=False):
        if len(argv) < 3:
            print('...%s %s %s' % (' ' + command_print if check_print else '', command_origin, syntax_origin))
            return
        if not self.exist_original_section(argv[1:-1]):
            return
        if not self.check_pos_int(argv[-1]):
            return
        if not self.check_sentence_count_original(argv[1:-1], int(argv[-1])):
            return
        
        list_section = argv[1:-1]
        count_total = int(argv[-1])
        
        if check_print:
            sql = self.db.sql_select_original_list_section_sentence(list_section, count_total)
            result = self.db.fetch(sql.encode())

            print(json.dumps(result, indent=4))
            print('------------------------------------------------------------------------------------------ End of section data.')
                
        else:
            self.exist_dir()
            file_test = open(path_test + '_'.join(list(map(lambda s : s.lower(), list_section))) + '_' + str(count_total) + '.csv', 'w')
            
            sql = self.db.sql_select_original_list_section_sentence(list_section, count_total)
            result = self.db.fetch(sql.encode())
            
            for target in result:
                file_test.write('%s%s%s\n' % (target['original_section'], separator, ' '.join(target['sentence'].split())))

            file_test.close()
            print('... OK')
   
    def test_processing(self, argv, check_print=False):
        if len(argv) < 2:
            print('...%s %s %s' % (' ' + command_print if check_print else '', command_test, syntax_test))
            return
        if not self.check_pos_int(argv[1]):
            return
        if not self.check_sentence_count_mapped(['-'], int(argv[1])):
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
                file_test.write('%s\n' % (' '.join(target['sentence'].split())))
                
            file_test.close()
            print('... OK')
        
    def print_manual(self):
        print('\n* [command] [original_section | mapped_section name]+ [count]+\n')
        
        print('* Command:')
        print(' > %s: Used to check the result value.' % (command_print))
        print(' > %s: Stores the result values as two types based on the mapped sections. (train, eval)' % (command_map))
        print(' > %s: Stores the result values based on the original section. (test)' % (command_origin))
        print(' > %s: Stores unstructured test sentences. (test)' % (command_test))
        print(' > %s: Print the manual.' % (command_help))
        print(' > %s: Exit the program.\n' % (command_exit))
        
        print('* Original section name:')
        print(' > Included in the original section name')
        print('* Mapped section name:')
        print(' > Available section names are:')
        print('  { BACKGROUND: 0, OBJECTIVE: 1, METHODS: 2, RESULTS: 3, CONCLUSIONS: 4 }\n')
        
        print('* Count:')
        print(' > The number of sentences.')
        print(' > In the %s command, must input the each data count. (train, eval)\n' % (command_map))
        
    def run(self):
        self.print_manual()

        while True:
            command = input('\n> ').upper().split(' ')
            
            if (command[0] == command_exit):
                print('... Bye')
                break
            elif (command[0] == command_print):
                self.print_processing(command)
            elif (command[0] == command_map):
                self.mapped_section_processing(command)
            elif (command[0] == command_origin):
                self.original_section_processing(command)
            elif (command[0] == command_test):
                self.test_processing(command)
            elif (command[0] == command_help):
                self.print_manual()
            else:
                print('... Unknown Command')
         
        self.db.finish()
        
if __name__ == '__main__':
    Extractor().run()
