import subprocess
from bs4 import BeautifulSoup

path_opennlp = "apache-opennlp-1.8.1/bin/opennlp"
file_opennlp_sent = "apache-opennlp-1.8.1/en-sent.bin"
file_labels = 'data/Structured-Abstracts-Labels-102615.txt'

class Parser:
    def __init__(self):
        self.path_article = ''
        self.article = ''
        self.su = ''
        self.labels = {}
        for line in open(file_labels, 'r').readlines() :
            label = line.split('|')
            self.labels[label[0]] = label[1]
    
    def set_article(self, path_article):
        self.path_article = path_article
        self.article = BeautifulSoup(open(path_article, 'r').read(), 'html.parser')
        self.su = 's' if len(self.article.select('abstract sec')) != 0 else 'u'
        
    def get_pmid(self):
        for node in self.article.select('article-id') :
            if node['pub-id-type'] == 'pmid' :
                return node.text
            
    def get_ppub(self):
        for node in self.article.select('pub-date') :
            if node['pub-type'] == 'ppub' :
                return '%s%02d' % (node.year.text, int(node.month.text))
            
    def get_su(self):
        return self.su

    def get_abstract(self):
        abstract = ''
        
        if self.su == 's' :
            for node in self.article.select('abstract sec') :
                abstract += node.p.text
                
        if self.su == 'u' :
            abstract = self.article.select('abstract')[0].p.text 
            
        return abstract.replace("'", "")
    
    def get_origin_label(self):
        if self.su == 'u' :
            return '-'
        
        origin_label = []
        for node in self.article.select('abstract sec') :
            origin_label.append(node.title.text.upper())
        return origin_label
            
    def get_map_label(self):
        if self.su == 'u' :
            return '-'
        
        map_label = []
        for node in self.article.select('abstract sec') :
            map_label.append(self.labels[node.title.text.upper()])
        return map_label
    
    def get_sentence(self):
        sentences = []
        
        if self.su == 's' :
            for node in self.article.select('abstract sec') :
                sentences.append(self.classify_sentence(node.p.text.replace("'", "")))
        
        if self.su == 'u' :
            sentences.append(self.classify_sentence(self.get_abstract()))

        return sentences
    
    def classify_sentence(self, content):
        process_nlp = subprocess.Popen([path_opennlp, 'SentenceDetector', file_opennlp_sent], 
                                       stdin = subprocess.PIPE, 
                                       stdout = subprocess.PIPE, 
                                       stderr = subprocess.PIPE)
        stdout, stderr = process_nlp.communicate(content.encode())
        return stdout.decode().split('\n')[:-3]
        
    def print(self):
        print(self.path_article)
        print('PMID:  ' + self.get_pmid())
        print('PPUB:  ' + self.get_ppub())
        print('ABSTRACT:  ' + self.get_abstract())
        print('S/U:  ' + self.get_su())
        print('Original Labels:  ' + ', '.join(self.get_origin_label()))
        print('Mapping Labels:  ' + ', '.join(self.get_map_label()))
        for section in self.get_sentence() :
            for sentence in section :
                print(sentence)
        print('\n\n')