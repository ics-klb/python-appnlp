# -*- coding: utf-8 -*-
import re
import string
import logging
import datetime

import nltk
import pymorphy2
from botnlp.nlu.tokenization import NlpTokenDefault, canonize_words, canonize_words_expanded, canonize_inp

logger = logging.getLogger('botnlp')
# for word in text_ru.split(u’ ’):
#     if re.match(u’([^a-zа-яë]+)’, word):
#     word = pymorph.parse(word)[0].normal_form
#     print word,


class NlpTokenRussian(NlpTokenDefault):

    language = 'russian'
    regex = "[А-Яа-я]+"
    minlen = 1

    def __init__(self, **kwargs):
        super(NlpTokenRussian, self).__init__(**kwargs)
        self._morphpology = pymorphy2.MorphAnalyzer(lang='ru')
        self.regex = re.compile(self.regex)
        #self.remove_punctuation = dict((ord(punct), None) for punct in string.punctuation)


    def lemmatize(self, text):
        try:
            return self._morphpology.parse(text)
        except:
            return " "

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

    def canonize_words_expanded(self, words: list, rules='all', isgram=True) -> list:

        return canonize_words_expanded(self._morphpology, words, minlen=self.minlen,
                              tagpos=self.tagpos, rules=rules, isgram=isgram)


    def normalize(self):
        text = self.content
        text = re.sub('[^a-zA-Zа-яА-Я\,\.]+', ' ', text)
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

    def hello(self):
        now_corpus = {"hey": ('здравствуйте', 'доброе утро', 'добрый день', 'добрый вечер', 'доброй ночи')}

        nowdt = datetime.datetime.now()
        # nowdt += datetime.timedelta(hours=1)  # можешь проверить тут

        if nowdt.hour > 4 and nowdt.hour <= 12:
            greet = now_corpus["hey"][1]
        if nowdt.hour > 12 and nowdt.hour <= 16:
            greet = now_corpus["hey"][2]
        if nowdt.hour > 16 and nowdt.hour <= 24:
            greet = now_corpus["hey"][3]
        if nowdt.hour >= 0 and nowdt.hour <= 4:
            greet = now_corpus["hey"][4]

        return greet
