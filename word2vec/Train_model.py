import gensim
import codecs

class SentenceReader:
    def __init__(self, filepath):
        self.filepath = filepath

    def __iter__(self):
        for line in codecs.open(self.filepath):
            yield line.split(' ')

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
