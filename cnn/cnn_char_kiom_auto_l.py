
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from sklearn import metrics
import pandas

import tensorflow as tf
from tensorflow.contrib import learn
from tensorflow.python.framework import ops
from kiom_loader import load_kiom

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_bool('test_with_fake_data', False, 'Test the example code with fake data.')

MAX_DOCUMENT_LENGTH = 100
N_FILTERS = 80
FILTER_SHAPE1 = [20, 256]
FILTER_SHAPE2 = [20, N_FILTERS]
POOLING_WINDOW = 4
POOLING_STRIDE = 2
BATCH_SIZE = 64

def char_cnn_model(x, y):
  """Character level convolutional neural network model to predict classes."""
  y = tf.one_hot(y, 2, 1, 0)
  byte_list = tf.reshape(learn.ops.one_hot_matrix(x, 256), [-1, MAX_DOCUMENT_LENGTH, 256, 1])
  with tf.variable_scope('CNN_Layer1'):
      # Apply Convolution filtering on input sequence.
      conv1 = learn.ops.conv2d(byte_list, N_FILTERS, FILTER_SHAPE1, padding='VALID')
      # Add a RELU for non linearity.
      input_tensor1 = ops.convert_to_tensor(conv1)
      print("shape of pool1: ", input_tensor1.get_shape())
      conv1 = tf.nn.relu(conv1)
      # Max pooling across output of Convolution+Relu.
      pool1 = tf.nn.max_pool(conv1, ksize=[1, POOLING_WINDOW, 1, 1], strides=[1, POOLING_STRIDE, 1, 1], padding='SAME')
      # Transpose matrix so that n_filters from convolution becomes width.
      input_tensor = ops.convert_to_tensor(pool1)
      print("after max_pool, shape of pool1: ", input_tensor.get_shape())
      pool1 = tf.transpose(pool1, [0, 1, 3, 2])

  with tf.variable_scope('CNN_Layer2'):
      # Second level of convolution filtering.
      conv2 = learn.ops.conv2d(pool1, N_FILTERS, FILTER_SHAPE2, padding='VALID')
      # Max across each filter to get useful features for classification.
      pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims=[1])

  # Apply regular WX + B and classification.
  # optimizer : SGD, Adagrad
  prediction, loss = learn.models.logistic_regression(pool2, y)
  train_op = tf.contrib.layers.optimize_loss(loss, tf.contrib.framework.get_global_step(), optimizer='Adagrad', learning_rate=0.01)
  return {'class': tf.argmax(prediction, 1), 'prob': prediction}, loss, train_op


def main(unused_argv):
  # Prepare training and testing data
  #dbpedia = learn.datasets.load_dataset('dbpedia', test_with_fake_data=FLAGS.test_with_fake_data, size='large')
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
  classifier = learn.Estimator(model_fn=char_cnn_model)

  # Train and predict
  classifier.fit(x_train, y_train, steps=1000, batch_size=BATCH_SIZE)
  y_predicted = [p['class'] for p in classifier.predict(x_test, as_iterable=True)]
  score = metrics.accuracy_score(y_test, y_predicted)
  print('cnn char kiom Accuracy: {0:f}'.format(score))

if __name__ == '__main__':
  tf.app.run()