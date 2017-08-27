

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
HIDDEN_SIZE = 20


def char_rnn_model(x, y, mode, params):
  print ('params', params)
  optimizer = params['optimizer']
  y = tf.one_hot(y, 2, 1, 0)
  byte_list = learn.ops.one_hot_matrix(x, 256)
  byte_list = tf.unpack(byte_list, axis=1)

  cell = tf.nn.rnn_cell.GRUCell(HIDDEN_SIZE)
  #cell = tf.nn.rnn_cell.LSTMCell(HIDDEN_SIZE)
  #cell = tf.nn.rnn_cell.RNNCell(HIDDEN_SIZE)
  _, encoding = tf.nn.rnn(cell, byte_list, dtype=tf.float32)

  prediction, loss = learn.models.logistic_regression(encoding, y)

  train_op = tf.contrib.layers.optimize_loss(
      loss, tf.contrib.framework.get_global_step(),
      optimizer=optimizer, learning_rate=0.01) # SGD, adagrad

  return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


def run(opt):
  # Prepare training and testing data
  kiomdata = load_kiom()

  x_train = pandas.DataFrame(kiomdata.train.data)[0]
  y_train = pandas.Series(kiomdata.train.target)
  x_test = pandas.DataFrame(kiomdata.test.data)[0]
  y_test = pandas.Series(kiomdata.test.target)

  # Process vocabulary
  char_processor = learn.preprocessing.ByteProcessor(MAX_DOCUMENT_LENGTH)
  x_train = np.array(list(char_processor.fit_transform(x_train)))
  x_test = np.array(list(char_processor.transform(x_test)))

  # Build model
  classifier = learn.Estimator(model_fn=char_rnn_model, params={'optimizer': opt})

  # Train and predict
  classifier.fit(x_train, y_train, steps=100)
  y_predicted = [
      p['class'] for p in classifier.predict(x_test, as_iterable=True)]
  return metrics.accuracy_score(y_test, y_predicted)

def main(unused_argv):
    optimizers = ['Adam','SGD', 'Adagrad']
    for optimizer in optimizers:
        score =run(optimizer)
        print('optimizer', optimizer)
        print('RNN-CHAR-KIOM Accuracy: {0:f}'.format(score))

if __name__ == '__main__':
    tf.app.run()