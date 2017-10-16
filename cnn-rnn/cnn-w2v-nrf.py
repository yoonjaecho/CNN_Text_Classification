from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from sklearn import metrics
import pandas

import tensorflow as tf
from tensorflow.contrib import learn
from nrf_loader import load_data


FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_bool('test_with_fake_data', False,
                         'Test the example code with fake data.')

MAX_DOCUMENT_LENGTH = 100
EMBEDDING_SIZE = 20
N_FILTERS = 10
WINDOW_SIZE = 20
FILTER_SHAPE1 = [WINDOW_SIZE, EMBEDDING_SIZE]
FILTER_SHAPE2 = [WINDOW_SIZE, N_FILTERS]
POOLING_WINDOW = 4
POOLING_STRIDE = 2
n_words = 0


def cnn_model(x, y):
  """2 layer Convolutional network to predict from sequence of words
  to a class."""
  # Convert indexes of words into embeddings.
  # This creates embeddings matrix of [n_words, EMBEDDING_SIZE] and then
  # maps word indexes of the sequence into [batch_size, sequence_length,
  # EMBEDDING_SIZE].
  y = tf.one_hot(y, 15, 1, 0)
  word_vectors = learn.ops.categorical_variable(x, n_classes=n_words,
      embedding_size=EMBEDDING_SIZE, name='words')
  word_vectors = tf.expand_dims(word_vectors, 3)
  with tf.variable_scope('CNN_Layer1'):
    # Apply Convolution filtering on input sequence.
    conv1 = tf.contrib.layers.convolution2d(word_vectors, N_FILTERS,
                                            FILTER_SHAPE1, padding='VALID')
    # Add a RELU for non linearity.
    conv1 = tf.nn.relu(conv1)
    # Max pooling across output of Convolution+Relu.
    pool1 = tf.nn.max_pool(conv1, ksize=[1, POOLING_WINDOW, 1, 1],
        strides=[1, POOLING_STRIDE, 1, 1], padding='SAME')
    # Transpose matrix so that n_filters from convolution becomes width.
    pool1 = tf.transpose(pool1, [0, 1, 3, 2])
  with tf.variable_scope('CNN_Layer2'):
    # Second level of convolution filtering.
    conv2 = tf.contrib.layers.convolution2d(pool1, N_FILTERS,
                                            FILTER_SHAPE2, padding='VALID')
    # Max across each filter to get useful features for classification.
    pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims=[1])

  # Apply regular WX + B and classification.
  prediction, loss = learn.models.logistic_regression(pool2, y)

  train_op = tf.contrib.layers.optimize_loss(
      loss, tf.contrib.framework.get_global_step(),
      optimizer='Adagrad', learning_rate=0.01)

  return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


def main(unused_argv):
  global n_words
  # Prepare training and testing data
  nrfdata = load_data()

  x_train = pandas.DataFrame(nrfdata.train.data)[0]
  y_train = pandas.Series(nrfdata.train.target)
  x_test = pandas.DataFrame(nrfdata.test.data)[0]
  y_test = pandas.Series(nrfdata.test.target)

  '''
  # Process vocabulary
  print('Raw x_train[0] : ')
  print(x_train[0])
  vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
  x_train = np.array(list(vocab_processor.fit_transform(x_train)))
  print("x_train : ", type(x_train[0]))
  print(x_train[0])
  print(x_train[0].shape)
  x_test = np.array(list(vocab_processor.transform(x_test)))
  n_words = len(vocab_processor.vocabulary_)
  print('Total words: %d' % n_words)
  '''



  # Pretrained Word2Vec

  import gensim
  model = gensim.models.Word2Vec.load('../word2vec/model_np')
  word_set = set([])

  # x_train

  x_train_sentences = ["".join(t) for t in x_train]
  x_train = []
  for sen in x_train_sentences:
    words = sen.split()
    sentence_vector = np.zeros(100)
    for w in words:
       if w in model.wv.vocab:
         sentence_vector += model[w]
         word_set.add(w)
    x_train.append(sentence_vector)

  # Have to cast to integer or change tf var type to tf.float
  x_train = np.int_(np.array(x_train))
  #x_train = np.array(x_train)

  print('x_train[0] : ', x_train[0].shape, type(x_train[0]))
  print(x_train[0])

  print('x_train : ', x_train.shape, type(x_train))
  print(x_train)

  # x_test

  x_test_sentences = ["".join(t) for t in x_test]
  x_test = []
  for sen in x_test_sentences:
    words = sen.split()
    sentence_vector = np.zeros(100)
    for w in words:
       if w in model.wv.vocab:
         sentence_vector += model[w]
  #       word_set.add(w)
    x_test.append(sentence_vector)

  # Have to cast to integer or change tf var type to tf.float
  x_test = np.int_(np.array(x_test))
  #x_test = np.array(x_test)

  n_words = len(word_set)
  print('Total words: %d' % n_words)









  # Build model
  classifier = learn.Estimator(model_fn=cnn_model)

  # Train and predict
  classifier.fit(x_train, y_train, steps=100)
  y_predicted = [
      p['class'] for p in classifier.predict(x_test, as_iterable=True)]
  score = metrics.accuracy_score(y_test, y_predicted)
  print('Accuracy: {0:f}'.format(score))


if __name__ == '__main__':
  tf.app.run()
