import sys
import json
import DBManager

class Extraction:
    def __init__(self):
        self.data_count = 0
        self.db = DBManager.DBManager()
        self.sections = { 'BACKGROUND': 0, 'OBJECTIVE': 1, 'METHODS': 2, 'RESULTS': 3, 'CONCLUSIONS': 4 }

    def print_data(self, argv):
        section = argv[1]
        count = argv[2]
        
        sql_target = self.db.sql_select_section_sentence(section, count)
        print(json.dumps(self.db.fetch(sql_target.encode()), indent = 4))
                         
    def save_data(self, argv):
        section = argv[1]
        count = argv[2]
        
        sql_target = self.db.sql_select_section_sentence(section, count)
        sql_no_target = self.db.sql_select_not_section_sentence(section, count)
        result_target = self.db.fetch(sql_target.encode())
        result_no_target = self.db.fetch(sql_no_target.encode())
        
        file_training = open('data/training_data/' + section.lower() + str(self.data_count) + '.csv', 'w')
        file_test = open('data/test_data/not_' + section.lower() + str(self.data_count) + '.csv', 'w')
        for i in range(int(count)):
            file_training.write('%d:::%s\n' % (self.sections[section], result_target[i]['sentence']))
            file_test.write('%d:::%s\n' % (self.sections[result_no_target[i]['section']], result_no_target[i]['sentence']))
        
        self.data_count += 1
        file_training.close()
        file_test.close()
        
    def run(self):
        while True:
            command = input('\n> ').upper().split(' ')
            
            if (command[0] == 'EXIT'):
                break
            elif (command[0] == 'PRINT'):
                self.print_data(command)
            elif (command[0] == 'SAVE'):
                self.save_data(command)
            else:
                print('No Query')
         
        self.db.finish()
        
if __name__ == '__main__':
    Extraction().run()