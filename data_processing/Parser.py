import nltk
from bs4 import BeautifulSoup

path_opennlp = "apache-opennlp-1.8.1/bin/opennlp"
file_opennlp_sent = "apache-opennlp-1.8.1/en-sent.bin"
file_labels = 'data/Structured-Abstracts-Labels-102615.txt'

class Parser:
    def __init__(self):
        self.file_article = ''
        self.article = ''
        self.su = ''
        self.labels = {}
        for line in open(file_labels, 'r').readlines():
            label = line.split('|')
            self.labels[label[0]] = label[1]
    
    def set_article(self, file_article):
        self.file_article = file_article
        self.article = BeautifulSoup(open(file_article, 'r').read(), 'html.parser')
        self.su = 's' if len(self.article.select('abstract sec')) != 0 else 'u'
        
    def get_pmid(self):
        for node in self.article.select('article-id'):
            if node['pub-id-type'] == 'pmid':
                return node.text
            
    def get_ppub(self):
        for node in self.article.select('pub-date'):
            if node['pub-type'] == 'ppub':
                p_date = ''
                if node.year != None:
                    p_date += '%s' % (node.year.text)
                    
                if node.month != None:
                    p_date += '%02d' % (int(node.month.text))
                else:
                    p_date += '00'
                return p_date
            
        for node in self.article.select('pub-date'):
            if node['pub-type'] == 'epub':
                e_date = ''
                if node.year != None:
                    e_date += '%s' % (node.year.text)
                    
                if node.month != None:
                    e_date += '%02d' % (int(node.month.text))
                else:
                    e_date += '00'
                return e_date
            
    def get_su(self):
        return self.su

    def get_abstract(self):
        abstract = ''
        
        if self.su == 's':
            for node in self.article.select('abstract sec'):
                if node.p != None:
                    abstract += node.p.text
                
        if self.su == 'u':
            abstract = self.article.select('abstract')[0].p.text 
            
        return self.utf8_to_ascii(abstract.replace("'", ""))
    
    def get_origin_label(self):
        if self.su == 'u':
            return '-'
        
        origin_label = []
        for node in self.article.select('abstract sec'):
            if node.p != None:
                origin_label.append(node.title.text.upper().strip().replace(":", ""))
        return origin_label
            
    def get_map_label(self):
        if self.su == 'u':
            return '-'
        
        map_label = []
        for label in self.get_origin_label():
            if label in self.labels:
                map_label.append(self.labels[label])
            else:
                map_label.append('-')
        return map_label
    
    def get_sentence(self):
        sentences = []

        if self.su == 's':
            for node in self.article.select('abstract sec'):
                if node.p != None:
                    sentences.append(self.classify_sentence(node.p.text.replace("'", "")))
        
        if self.su == 'u':
            sentences.append(self.classify_sentence(self.get_abstract()))

        return sentences
    
    def classify_sentence(self, content):
        sentences = nltk.sent_tokenize(self.utf8_to_ascii(content.strip()))
        return sentences
    
    def utf8_to_ascii(self, text):
        return text.encode('ascii', 'ignore')

    def print_article(self):
        print(self.file_article)
        print('PMID:  ' + self.get_pmid())
        print('PPUB:  ' + self.get_ppub())
        print('ABSTRACT:  ' + self.get_abstract())
        print('S/U:  ' + self.get_su())
        print('Original Labels:  ' + ', '.join(self.get_origin_label()))
        print('Mapping Labels:  ' + ', '.join(self.get_map_label()))
        for section in self.get_sentence():
            for sentence in section:
                print(sentence)
        print('\n\n')