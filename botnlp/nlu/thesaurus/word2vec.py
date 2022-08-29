# -*- coding: utf-8 -*-
import re
import string
import nltk
from botnlp.nlu.tokenization.russian import NlpTokenRussian

class Thesaurus(NlpTokenRussian):

    language = 'ukrainian'

    minlen = 2