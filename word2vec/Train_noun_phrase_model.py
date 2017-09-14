import gensim
import codecs
import _tkinter
import nltk

class SentenceReader:
    def __init__(self, filepath):
        self.filepath = filepath
        
        self.sentence_re = r'(?:(?:[A-Z])(?:.[A-Z])+.?)|(?:\w+(?:-\w+)*)|(?:\$?\d+(?:.\d+)?%?)|(?:...|)(?:[][.,;"\'?():-_`])'
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.stemmer = nltk.stem.porter.PorterStemmer()
        self.grammar = r"""
            NBAR:
                {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

            NP:
                {<NBAR>}
                {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
        """
        self.chunker = nltk.RegexpParser(self.grammar)
        
    def __iter__(self):
        for line in codecs.open(self.filepath):
            yield self.get_list_noun_phrase(line)
            
    def get_list_noun_phrase(self, text):
        toks = nltk.regexp_tokenize(text, self.sentence_re)
        postoks = nltk.tag.pos_tag(toks)
        tree = self.chunker.parse(postoks)
        
        ret = []
        for term in self.get_terms(tree):
            ret.append('_'.join(term))
            
        return ret

    def leaves(self, tree):
        """Finds NP (nounphrase) leaf nodes of a chunk tree."""
        for subtree in tree.subtrees(filter = lambda t: t.label()=='NP'):
            yield subtree.leaves()

    def normalise(self, word):
        """Normalises words to lowercase and stems and lemmatizes it."""
        word = word.lower()
        # word = stemmer.stem_word(word) #if we consider stemmer then results comes with stemmed word, but in this case word will not match with comment
        word = self.lemmatizer.lemmatize(word)
        return word

    def acceptable_word(self, word):
        """Checks conditions for acceptable word: length, stopword. We can increase the length if we want to consider large phrase"""
        accepted = bool(2 <= len(word) <= 40)
        return accepted
    
    def get_terms(self, tree):
        for leaf in self.leaves(tree):
            term = [ self.normalise(w) for w,t in leaf if self.acceptable_word(w) ]
            yield term

class Word2Vec:
    def __init__(self, input_file):
        self.sentences_vocab = SentenceReader(input_file)
        self.sentences_train = SentenceReader(input_file)
        self.model = gensim.models.Word2Vec()
        self.model.build_vocab(self.sentences_vocab)

    def train(self):
        self.model.train(
            self.sentences_train,
            total_examples=self.model.corpus_count,
            epochs=self.model.iter
        )
        print("Train complete..!")

    def save(self, output_file):
        self.model.save(output_file)

if __name__ == '__main__':
    w2v = Word2Vec('input_abstract.txt')
    w2v.train()
    w2v.save('model')

    # Load and test the model
    model = gensim.models.Word2Vec.load('model')
    print(model['nicotine'])
    print(model.most_similar('nicotine'))
