

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np
import pandas
from sklearn import metrics
import tensorflow as tf
from tensorflow.contrib import learn
from kiom_loader import load_kiom


FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_bool('test_with_fake_data', False,
                         'Test the example code with fake data.')

MAX_DOCUMENT_LENGTH = 10
EMBEDDING_SIZE = 50
n_words = 0


def bag_of_words_model(x, y):
  """A bag-of-words model. Note it disregards the word order in the text."""
  target = tf.one_hot(y, 15, 1, 0)
  word_vectors = learn.ops.categorical_variable(x, n_classes=n_words,
      embedding_size=EMBEDDING_SIZE, name='words')
  features = tf.reduce_max(word_vectors, reduction_indices=1)
  prediction, loss = learn.models.logistic_regression(features, target)
  train_op = tf.contrib.layers.optimize_loss(
      loss, tf.contrib.framework.get_global_step(),
      optimizer='Adagrad', learning_rate=0.01) # SGD, Adagrad
  return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


def rnn_model(x, y):
  """Recurrent neural network model to predict from sequence of words
  to a class."""
  # Convert indexes of words into embeddings.
  # This creates embeddings matrix of [n_words, EMBEDDING_SIZE] and then
  # maps word indexes of the sequence into [batch_size, sequence_length,
  # EMBEDDING_SIZE].
  word_vectors = learn.ops.categorical_variable(x, n_classes=n_words,
      embedding_size=EMBEDDING_SIZE, name='words')

  # Split into list of embedding per word, while removing doc length dim.
  # word_list results to be a list of tensors [batch_size, EMBEDDING_SIZE].
  word_list = tf.unpack(word_vectors, axis=1)

  # Create a Gated Recurrent Unit cell with hidden size of EMBEDDING_SIZE.
  cell = tf.nn.rnn_cell.GRUCell(EMBEDDING_SIZE)

  # Create an unrolled Recurrent Neural Networks to length of
  # MAX_DOCUMENT_LENGTH and passes word_list as inputs for each unit.
  _, encoding = tf.nn.rnn(cell, word_list, dtype=tf.float32)

  # Given encoding of RNN, take encoding of last step (e.g hidden size of the
  # neural network of last step) and pass it as features for logistic
  # regression over output classes.
  target = tf.one_hot(y, 15, 1, 0)
  prediction, loss = learn.models.logistic_regression(encoding, target)

  # Create a training op.
  train_op = tf.contrib.layers.optimize_loss(
      loss, tf.contrib.framework.get_global_step(),
      optimizer='Adam', learning_rate=0.01)

  return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


def main(unused_argv):
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

  # Build model
  classifier = learn.Estimator(model_fn=bag_of_words_model)

  # Train and predict
  classifier.fit(x_train, y_train, steps=100)
  y_predicted = [
      p['class'] for p in classifier.predict(x_test, as_iterable=True)]
  score = metrics.accuracy_score(y_test, y_predicted)
  print('DNN kiom Accuracy: {0:f}'.format(score))


if __name__ == '__main__':
  tf.app.run()