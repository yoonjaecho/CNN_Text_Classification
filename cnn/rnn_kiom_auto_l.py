
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from sklearn import metrics
import pandas

import tensorflow as tf
from tensorflow.contrib import learn
from kiom_loader import load_kiom

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_bool('test_with_fake_data', False,
                         'Test the example code with fake data.')

MAX_DOCUMENT_LENGTH = 100
EMBEDDING_SIZE = 50
n_words = 0


def input_op_fn(x):
  word_vectors = learn.ops.categorical_variable(x, n_classes=n_words,
      embedding_size=EMBEDDING_SIZE, name='words')
  # Split into list of embedding per word, while removing doc length dim.
  # word_list results to be a list of tensors [batch_size, EMBEDDING_SIZE].
  word_list = tf.unpack(word_vectors, axis=1)
  return word_list


def run(cell_type, optimizer):
  global n_words
  # Prepare training and testing data
  kiomdata = load_kiom()

  x_train = pandas.DataFrame(kiomdata.train.data)[0]
  y_train = pandas.Series(kiomdata.train.target)
  x_test = pandas.DataFrame(kiomdata.test.data)[0]
  y_test = pandas.Series(kiomdata.test.target)

  # Process vocabulary
  vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
  x_train = np.array(list(vocab_processor.fit_transform(x_train)))
  x_test = np.array(list(vocab_processor.transform(x_test)))
  n_words = len(vocab_processor.vocabulary_)
  print('Total words: %d' % n_words)


  # Build model: a single direction GRU with a single layer
  classifier = learn.TensorFlowRNNClassifier(
      rnn_size=EMBEDDING_SIZE, n_classes=2, cell_type=cell_type,
      input_op_fn=input_op_fn, num_layers=1, bidirectional=False,
      sequence_length=None, steps=10000, optimizer=optimizer,
      learning_rate=0.01, continue_training=True)

  # Train and predict
  classifier.fit(x_train, y_train, steps=10000)
  y_predicted = classifier.predict(x_test)

  score = metrics.accuracy_score(y_test, y_predicted)
  return score

def main(unused_argv):
    cell_types = ['rnn', 'lstm', 'gru']
    optimizers = ['Adagrad', 'SGD', 'Adam']
    for cell_type in cell_types:
        for optimizer in optimizers:
            #print('cell_type', cell_type)
            #print('optimizer', optimizer)
            score = run(cell_type, optimizer)
            #print('Accuracy: {0:f}'.format(score))
            print('|  cell_type   |    optimizer  |   accuracy  |')
            print('%s\t%s\t%s' % (cell_type, optimizer, score))


if __name__ == '__main__':
    tf.app.run()