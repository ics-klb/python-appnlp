# -*- coding: utf-8 -*-
from botnlp.nlu.models.core import CoreModel
#wget http://vectors.nlpl.eu/repository/11/180.zip / russian

class Word2VecModel(CoreModel):

    def get_model(self, *args, **kwargs):
        pass

    @staticmethod
    def train_model(sentences, size=200, window=5, min_count=3):
        '''

        :param sentences: предложения или путь к данным
        :param size:
        :param window:
        :param min_count:
        :return:
        '''
        import multiprocessing
        from gensim.models import Word2Vec
        from gensim.models.word2vec import LineSentence

        data = LineSentence(sentences)
        return Word2Vec(sentences=data, vector_size=size, window=window, min_count=min_count, workers=multiprocessing.cpu_count())

