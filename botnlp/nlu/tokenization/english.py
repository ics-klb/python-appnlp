# -*- coding: utf-8 -*-
import re
import string

import nltk
import pymorphy2
from botnlp.nlu.tokenization import NlpTokenDefault, canonize_words, canonize_inp


class NlpTokenEnglish(NlpTokenDefault):

    language = 'english'
    regex = "[A-Za-z]+"
    minlen = 2

    def __init__(self, **kwargs):
        super(NlpTokenEnglish, self).__init__(**kwargs)
        self._morphpology = pymorphy2.MorphAnalyzer()


    def lemmatize(self, text):
        try:
            return self._morphpology.parse(text)
        except:
            return " "


    def word_is_known(self, text):
        return self._morphpology.word_is_known(text)


    '''
    Определяет условия выбора предложения для последующего анализа для формирования корректной выборки
    '''
    def canonize_inp(self, words: list, rules='all') -> bool:

        return canonize_inp(self._morphpology, words, tagpos=self.tagpos, rules=rules)

    '''
    провести морфологический анализ и выявить его начальную форму
    СТЕММИНГ: УДАЛЯЕМ ОКОНЧАНИЯ
    '''

    def canonize_words(self, words: list, rules='all', isgram=True) -> list:

        return canonize_words(self._morphpology, words, minlen=self.minlen,
                              tagpos=self.tagpos, rules=rules, isgram=isgram)

    def normalize(self):
        text = self.content
        text = re.sub('[^a-zA-Z\,\.]+', ' ', text)
        text = text.replace('&quot;', '')
        text = text.replace('ё', 'е')
        text = re.sub(' +', ' ', text)

        return text

# ----------------------- Tokenization function
    """
        Разбиения на предложения в NLTK  на токены  использовать слова
    """
    def tokenize(self, text):

        for token in nltk.word_tokenize(text):
            if token in string.punctuation: continue
            yield token

    def tokenize_train(self):
        try:
            return " ".join(self.content)
        except:
            return ""

    def tokenize_query(self):
        try:
            return " ".join(self.regex.findall(self.content))
        except:
            return ""
