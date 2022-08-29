# -*- coding: utf-8 -*-
"""
BotNlp utility functions
"""

import argparse
import configparser
import os

import logging
import botnlp

if botnlp.is_debugger == True:
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def echo(*args, **kwargs):
    print(args)
    for i, k in kwargs.items():
        print(i, '=', k)


def pren(*args, **kwargs):
    if botnlp.is_debugger == True:
        echo(*args, **kwargs)


def getsetup_config():

    config = configparser.ConfigParser()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    config_file_path = os.path.join(parent_directory, 'setup.cfg')

    config.read(config_file_path)

    return config


def get_botnlp_version():

    config = configparser.ConfigParser()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    config_file_path = os.path.join(parent_directory, 'setup.cfg')

    config.read(config_file_path)

    return config['botnlp']['version']


def initialize_class(data, *args, **kwargs):
    """
    :param data: A string or dictionary containing a import_path attribute.
    """
    if isinstance(data, dict):
        import_path = data.get('import_path')
        data.update(kwargs)
        Class = import_module(import_path)

        return Class(*args, **data)
    else:
        Class = import_module(data)

        return Class(*args, **kwargs)


def import_module(dotted_path):
    """
    Imports the specified module based on the
    dot notated import path for the module.
    """
    import importlib
    pren("import_module: ", dotted_path)

    module_parts = dotted_path.split('.')
    module_path = '.'.join(module_parts[:-1])
    module = importlib.import_module(module_path)

    return getattr(module, module_parts[-1])


def validate_adapter_class(validate_class, adapter_class):
    """
    Raises an exception if validate_class is not a
    subclass of adapter_class.

    :param validate_class: The class to be validated.
    :type validate_class: class

    :param adapter_class: The class type to check against.
    :type adapter_class: class

    :raises: Adapter.InvalidAdapterTypeException
    """
    from botnlp.nlu.adapters import Adapter

    # If a dictionary was passed in, check if it has an import_path attribute
    if isinstance(validate_class, dict):

        if 'import_path' not in validate_class:
            raise Adapter.InvalidAdapterTypeException(
                'The dictionary {} must contain a value for "import_path"'.format(
                    str(validate_class)
                )
            )

        # Set the class to the import path for the next check
        validate_class = validate_class.get('import_path')

    if not issubclass(import_module(validate_class), adapter_class):
        raise Adapter.InvalidAdapterTypeException(
            '{} must be a subclass of {}'.format(
                validate_class,
                adapter_class.__name__
            )
        )


def print_progress_bar(description, iteration_counter, total_items, progress_bar_length=20):
    """
    Print progress bar
    :param description: Training description
    :type description: str

    :param iteration_counter: Incremental counter
    :type iteration_counter: int

    :param total_items: total number items
    :type total_items: int

    :param progress_bar_length: Progress bar length
    :type progress_bar_length: int

    :returns: void
    :rtype: void
    """
    import sys

    percent = float(iteration_counter) / total_items
    hashes = '#' * int(round(percent * progress_bar_length))
    spaces = ' ' * (progress_bar_length - len(hashes))
    sys.stdout.write('\r{0}: [{1}] {2}%'.format(description, hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    if total_items == iteration_counter:
        print('\r')


def get_argparse():
    parser = argparse.ArgumentParser(description='Attention Nlp bots')

    parser.add_argument('-d', '--debug', help='Set debug mode')
    parser.add_argument('-tr', '--train', help='Train the model with corpus')
    parser.add_argument('-te', '--test', help='Test the saved w2v model')
    parser.add_argument('-ter', '--test_vector_relation', help='Test the saved w2v model')
    parser.add_argument('-l', '--load', help='Load the model and train')
    parser.add_argument('-c', '--corpus', help='Test the saved model with vocabulary of the corpus')
    parser.add_argument('-r', '--reverse', action='store_true', help='Reverse the input sequence')
    parser.add_argument('-f', '--filter', action='store_true', help='Filter to small training data set')
    parser.add_argument('-i', '--input', action='store_true', help='Test the model by input the sentence')
    parser.add_argument('-it', '--iteration', type=int, default=10000, help='Train the model with it iterations')
    parser.add_argument('-p', '--print', type=int, default=5000, help='Print every p iterations')
    parser.add_argument('-b', '--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('-la', '--layer', type=int, default=1, help='Number of layers in encoder and decoder')
    parser.add_argument('-hi', '--hidden', type=int, default=50, help='size of word vectors')
    parser.add_argument('-be', '--beam', type=int, default=1, help='Hidden size in encoder and decoder')
    parser.add_argument('-lr', '--learning_rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('-s', '--save', type=float, default=10000, help='Save every s iterations')
    parser.add_argument('-co', '--context_size', type=int, default=2, help='The (n-1) of the n-gram')
    parser.add_argument('-d', '--draw', help='Draw 2D word vector with the word vector model')
    parser.add_argument('-dm', '--draw_manually', help='Draw 2D word vector manually')
    parser.add_argument('-fb', '--frequency_boundary', type=int, default=1500, help='The frequency_boundary of the 2D graph')
    parser.add_argument('-lo', '--loss', help='Draw the loss trend graph while the word vector model was being trained')
    parser.add_argument('-pr', '--predict', help='Predict the next word with previous 2 words.')

    args = parser.parse_args()

    return args