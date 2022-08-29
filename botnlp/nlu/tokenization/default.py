"""
Предобработка текстов для тренировки моделей осуществлялась следующим образом:
 - лемматизация и удаление стоп-слов;
 - приведение лемм к нижнему регистру;
 - добавление частеречного тэга для каждого слова.
методы предобработки текста: токенизации, удалении стоп-слов, стемминге и лемматизации с Python-библиотеками pymorphy2 и NLTK.
Токенизация — процесс разбиения текстового документа на отдельные слова, которые называются токенами
Стеммизация — процесс приведения слова к его корню/основе.
"""
import re
import string
import nltk

from botnlp.functions import getsetup_config
from botnlp.nlu.tokenization import remove_punctuation



class NlpTokenDefault(object):

    language = 'default'
    content = ''

    minlen = 2
    taglist = ''  # PRCL CONJ NPRO PREP ADJF PREP ADJF NUMR  nomn
    tagpos  = []

    _morphpology = None

    def __init__(self, **kwargs):
        self.set_tagpos()


    def _has_tag(self, parsed_sent, tag):
        return any(tag == ptag for token, parses in parsed_sent for norm, ptag in parses)

    def _has_unkn(self, parsed_sent):
        return self._has_tag(parsed_sent, 'UNKN')

    def get_parse(self, text):
        forms = []
        try:
            forms = self._morphpology.parse(text)
            form = max(forms, key=lambda x: (x.score, x.methods_stack[0][2]))
        except Exception as ex:
            form = forms[0]

        return form

    def get_score(self, text):
        score = 0
        if self.word_is_known(text):
            form = self.get_parse(text)
            score = form.score

        print('get_score ', self.language, text, score)
        return score

    def word_is_known(self, text):

        return self._morphpology.word_is_known(text)

    def get_tagpos(self):

        return self.tagpos

    def set_tagpos(self, taglist=False):

        if False == taglist:
            cfg = getsetup_config()
            taglist = cfg['tags']['tag_pos'] if 'tag_pos' in cfg['tags'] else self.taglist

        if type(taglist) == str:
            self.tagpos = taglist.split()

        return self

    def set_stopwords(self, stopwords = False):
        if not stopwords:
            from nltk.corpus import stopwords
            self._stopwords = stopwords.words(self.language)
        else:
            self._stopwords = stopwords
        return self


    def set_text(self, text):
        self.content = text
        return self

    @staticmethod
    def clean_lemma(lemma, pos):
        out_lemma = lemma.strip().replace(' ', '').replace('_', '').lower()
        if '|' in out_lemma or out_lemma.endswith('.jpg') or out_lemma.endswith('.png'):
            return None

        if pos != 'PUNCT':
            if out_lemma.startswith('«') or out_lemma.startswith('»'):
                out_lemma = ''.join(out_lemma[1:])
            if out_lemma.endswith('«') or out_lemma.endswith('»'):
                out_lemma = ''.join(out_lemma[:-1])
            if out_lemma.endswith('!') or out_lemma.endswith('?') or out_lemma.endswith(',') \
                    or out_lemma.endswith('.'):
                out_lemma = ''.join(out_lemma[:-1])
        return out_lemma

    def clean_punctuation(self, text):
        # text = text.split()
        # return ' '.join(c for c in text if c not in string.punctuation)
        return remove_punctuation(text)


    def clean_text(self):
        text = self.content
        text = text.lower()
        text = re.sub(r'\|\|\|', r' ', text)
        text = re.sub(r'http\S+', r'<URL>', text)
        text = text.replace('&quot;', '"')
        text = text.replace('x', '')

        return text

    def num_replace(self, word):
        newtoken = 'x' * len(word)

        return newtoken

    def normalize(self):
        text = self.content
        # text = re.sub('[^a-zA-Zа-яА-Я\,\.]+', ' ', text) # не работает для укр
        text = text.replace('&quot;', '')
        text = text.replace('ё', 'е')
        text = re.sub(' +', ' ', text)

        return text


    def remove_stopwords(self):
        text = self.content
        try:
            return " ".join([token for token in text.split() if not token in self._stopwords])
        except:
            return ""

    '''
    lemmatise performs lemmatization on words
    '''
    def lemmatize(self):
        text = self.content
        if not self._lem:
            from nltk.stem import WordNetLemmatizer
            self._lem = nltk.stem.WordNetLemmatizer()

        try:
            return "".join(self._lem.lemmatize(text)).strip()
        except:
            return " "


    # Tokenization function
    def tokenize(self, text):
        if not self._stem:
            from nltk.stem import SnowballStemmer
            self._stem = nltk.stem.SnowballStemmer(self.language)

        for token in nltk.word_tokenize(text):
            if token in string.punctuation: continue
            yield self._stem.stem(token)


    def tokenize_train(self):
        pass


    def tokenize_query(self):
        pass

    '''
    Определяет условия выбора предложения для последующего анализа для формирования корректной выборки
    '''
    def canonize_inp(self, words: list, rules='all') -> bool:
        pass

    '''
    провести морфологический анализ и выявить его начальную форму
    СТЕММИНГ: УДАЛЯЕМ ОКОНЧАНИЯ
    '''
    def canonize_words(self, words: list, rules='all',
                       isgram=True) -> list:
        return []

    def canonize_words_expanded(self, words: list, rules='all',
                       isgram=True) -> list:
        return []


    def preprocess(self, rules='all', isgram=True, isdubl=False, isexpand = False) -> string:
        self.content = self.clean_text()
        # self.content = self.spacy_tokenizer()
        # self.content = self.remove_stopwords()
        # self.content = self.lemmatize()
        self.content = self.normalize()

        content = self.content.split()
        if isexpand == False:
            text_norm = self.canonize_words(content, isgram=isgram, rules=rules)
            if isdubl:
                text_norm = list(dict.fromkeys(text_norm))

            result = ' '.join(text_norm).strip()
        else:
            text_norm, expanded = self.canonize_words_expanded(content, isgram=isgram, rules=rules)
            text_norm = ' '.join(text_norm).strip()

            result = [text_norm, expanded]

        return result

    def preprocess_train(self, text, rules='all', isgram=True, isdubl=False):
        text = self.clean_punctuation(text)
        return self.set_text(text)\
               .preprocess(rules=rules, isgram=isgram, isdubl=isdubl)

    def preprocess_query(self, text, rules='all', isgram=True, isdubl=False):

        return self.set_text(text)\
            .preprocess(rules=rules, isgram=isgram, isdubl=isdubl)

    def preprocess_expanded(self, text, rules='all', isgram=True, isdubl=False):
        return self.set_text(text)\
            .preprocess(rules=rules, isgram=isgram, isdubl=isdubl, isexpand=True)

    def preprocess_answer(self, text):
        text = re.sub('&quot;', '"', text)
        #text = re.sub('\d+', '', text)

        return text

