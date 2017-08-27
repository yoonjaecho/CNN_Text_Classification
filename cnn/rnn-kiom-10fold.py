
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from sklearn import metrics
import pandas

import tensorflow as tf
from tensorflow.contrib import learn
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from kiom_loader import load_full_kiom

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_bool('test_with_fake_data', False,
                         'Test the example code with fake data.')

MAX_DOCUMENT_LENGTH = 100
EMBEDDING_SIZE = 50
n_words = 0


def input_op_fn(x):
  """Customized function to transform batched x into embeddings."""
  # Convert indexes of words into embeddings.
  # This creates embeddings matrix of [n_words, EMBEDDING_SIZE] and then
  # maps word indexes of the sequence into [batch_size, sequence_length,
  # EMBEDDING_SIZE].
  word_vectors = learn.ops.categorical_variable(x, n_classes=n_words,
      embedding_size=EMBEDDING_SIZE, name='words')
  # Split into list of embedding per word, while removing doc length dim.
  # word_list results to be a list of tensors [batch_size, EMBEDDING_SIZE].
  word_list = tf.unpack(word_vectors, axis=1)
  return word_list


def main(unused_argv):
  global n_words
  # Prepare training and testing data
  kiomdata = load_full_kiom()

  prev_validation_data = pandas.DataFrame(kiomdata.data)[0]
  validation_target = pandas.Series(kiomdata.target)

  # Process vocabulary
  vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
  validation_data = np.array(list(vocab_processor.fit_transform(prev_validation_data)))
  n_words = len(vocab_processor.vocabulary_)
  print('Total words: %d' % n_words)

  kf = StratifiedKFold(n_splits=10)
  iteration = 1
  for train, test in kf.split(validation_data, validation_target) :
      print ("iteration : ", iteration)
      train_data, train_target = validation_data[train], validation_target[train]
      test_data, test_target = validation_data[test], validation_target[test]

      # Build model: a single direction GRU with a single layer
      classifier = learn.TensorFlowRNNClassifier(
        rnn_size=EMBEDDING_SIZE, n_classes=2, cell_type='lstm',
        input_op_fn=input_op_fn, num_layers=1, bidirectional=False,
        sequence_length=None, steps=5000, optimizer='Adam',
        learning_rate=0.01, continue_training=True)

      # Train and predict
      classifier.fit(train_data, train_target, steps=10000)
      test_predicted = classifier.predict(test_data)

      score = metrics.f1_score(test_target, test_predicted, average="macro")
      matrix = confusion_matrix(test_target, test_predicted)

      # score = metrics.accuracy_score(test_target, y_predicted)
      print('F1 score: {0:f}'.format(score))
      print(matrix)

      iteration += 1

if __name__ == '__main__':
  tf.app.run()
