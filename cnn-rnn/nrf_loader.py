
import os
import numpy as np
from tensorflow.contrib.learn.python.learn.datasets import base
import collections

Dataset = collections.namedtuple('Dataset', ['data', 'target'])


def load_data():
  module_path = os.path.dirname(__file__)
  #train_path = os.path.join(module_path, 'nrf_data', 'nrf-traindata.csv')
  #test_path = os.path.join(module_path, 'nrf_data', 'nrf-testdata.csv')

  #train_path = os.path.join(module_path, 'nrf_data', 'train_10000.csv')
  #test_path = os.path.join(module_path, 'nrf_data', 'eval_10000.csv')

  #train_path = os.path.join(module_path, 'nrf_data', 'train_10000_only_one_objective.csv')
  #test_path = os.path.join(module_path, 'nrf_data', 'eval_10000_only_one_objective.csv')

  train_path = os.path.join(module_path, 'nrf_data', 'train_10000_processed.csv')
  test_path = os.path.join(module_path, 'nrf_data', 'eval_10000_processed.csv')

  train = base.load_csv_without_header(train_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)
  test = base.load_csv_without_header(test_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)

  return base.Datasets(train=train, validation=None, test=test)


def load_origin_data():
  module_path = os.path.dirname(__file__)
  train_path = os.path.join(module_path, 'nrf_data', 'nrf-traindata.csv')
  test_path = os.path.join(module_path, 'nrf_data', 'nrf-testdata.csv')

  train = base.load_csv_without_header(train_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)
  test = base.load_csv_without_header(test_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)

  return base.Datasets(train=train, validation=None, test=test)


def load_full_data():
  module_path = os.path.dirname(__file__)
  #train_path = os.path.join(module_path, 'nrf_data', 'nrf-traindata.csv')
  #test_path = os.path.join(module_path, 'nrf_data', 'nrf-testdata.csv')
  train_path = os.path.join(module_path, 'nrf_data', 'train_10000.csv')
  test_path = os.path.join(module_path, 'nrf_data', 'eval_10000.csv')

  train = base.load_csv_without_header(train_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)
  test = base.load_csv_without_header(test_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)

  data = np.concatenate((train.data,test.data), axis=0)
  target = np.concatenate((train.target, test.target), axis=0)

  return Dataset(data=np.array(data),
                 target=np.array(target).astype(np.int32))
