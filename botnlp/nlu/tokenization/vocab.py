import re
import string
import nltk
from nltk.corpus import stopwords


class NlpVocab(object):

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'\|\|\|', r' ', text)
        text = re.sub(r'http\S+', r'<URL>', text)
        text = text.replace('x', '')

        return text

        def preprocess_text(self, text):
            text = self.clean_text(text)
            # text = spacy_tokenizer(text)
            # text = remove_stopwords(text)
            # text = lemmatize(text)

            text = re.sub('[^a-zA-Zа-яА-Я]+', ' ', text)
            text = text.replace('&quot;', '')
            text = text.replace('ё', 'е')

            text = re.sub(' +', ' ', text)
            text_norm = self.canonize_words(text.split())

            return ' '.join(text_norm).strip()