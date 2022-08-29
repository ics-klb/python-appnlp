# -*- coding: utf-8 -*-

import re
import string
import logging

logger = logging.getLogger('botnlp')

#Global Variables
grammar_map_STEM = {
    'NOUN': '_S',
    'VERB': '_V', 'INFN': '_V', 'GRND': '_V', 'PRTF': '_V', 'PRTS': '_V',
    'ADJF': '_A', 'ADJS': '_A',
    'ADVB': '_ADV',
    'COMP': '_COMP',
    'NUMR': '_N',
    'NPRO': '_NPR',
    'CONJ': '_CONJ',
    'INTJ': '_INTJ',
    'PRED': '_PRAEDIC',
    'PREP': '_PREP'
}

grammar_map_POS_TAGS = {
    'NOUN': '_S',
    'VERB': '_VERB', 'INFN': '_VERB', 'GRND': '_VERB', 'PRTF': '_VERB', 'PRTS': '_VERB',
    'ADJF': '_ADJ', 'ADJS': '_ADJ',
    'NUMR': '_NUMR',
    'COMP': '_COMP',
    'NPRO': '_NPR',
    'CONJ': '_CONJ',
    'INTJ': '_INTJ',
    'ADVB': '_ADV',
    'PRED': '_PRAEDIC',
    'PREP': '_PREP'
}

stop_words = ('я', 'а', 'и', 'её', 'их')


word_pattern = u'[А-яA-z0-9\-]+'

# use a regular expression to remove punctuation and line breaks
punct = re.compile('[%s]' % re.escape(string.punctuation))


def remove_punctuation(inputstr):
    """
    use a regular expression to remove punctuation and line breaks
    """
    inputstr = punct.sub(' ', inputstr)
    # and remove line breaks
    inputstr = inputstr.replace('\n', ' ')


    return inputstr


def iscyrillic(word)->bool:

    return re.match(u'^[~_\u0430-\u0491]*$', word)


def get_semantic(word)->str:
    word = word.replace('&quot;', '')
    word = word.replace('[0-9]', '')
    word = remove_punctuation(word)
    word = re.sub(' +', '', word)
    word = word.replace('x', '')
    word = word.lower()

    if re.match(u'^[~_\u0430-\u0451]*$', word) \
            and not re.match(u'^[~_\u0452-\u0491]*$', word):
        lang = 'russian'
    elif re.match(u'^[~_\u0430-\u0491]*$', word):
        lang = 'ukrainian'
    else:
        lang = 'english'

    return lang


'''
Определяет условия выбора предложения для последующего анализа для формирования корректной выборки
'''
def canonize_inp(morph_analyzer, words: list,
                 tagpos: list='',
                 grammar_map: dict = grammar_map_STEM,
                 minlen=2,
                 rules='all') -> bool:

    rules = ["_" + item for item in rules.upper().split()]
    for token in words:
        forms = morph_analyzer.parse(token)
        try:
            form = max(forms, key=lambda x: (x.score, x.methods_stack[0][2]))
        except Exception as ex:
            form = forms[0]

        tmp_map = grammar_map.get(form.tag.POS, '')
        if form.tag.POS in tagpos and ('_ALL' in rules or tmp_map in rules):
            return True

    return False

'''
провести морфологический анализ и выявить его начальную форму
СТЕММИНГ: УДАЛЯЕМ ОКОНЧАНИЯ
'''
def canonize_words(morph_analyzer, words: list,
                   tagpos: list = [],
                   grammar_map: dict = grammar_map_STEM,
                   rules='all',
                   minlen=2,
                   isgram=True) -> list:

    rules = ["_" + item for item in rules.upper().split()]
    normalized = []
    for i in words:
        forms = morph_analyzer.parse(i)
        try:
            form = max(forms, key=lambda x: (x.score, x.methods_stack[0][2]))
        except Exception:
            form = forms[0]

        # logger.info("canonize_words: %s", form)
        if not ( #form.tag.POS in tagpos get_semantic
                # len(form.normal_form) < minlen or
                form.normal_form in stop_words):

            tmp_map = grammar_map.get(form.tag.POS, '')
            tmp_norm = form.normal_form # + tmp_map if isgram else form.normal_form
            if '_ALL' in rules or tmp_map in rules:
                normalized.append(tmp_norm)

    return normalized


'''
провести морфологический анализ и выявить его начальную форму
СТЕММИНГ: УДАЛЯЕМ ОКОНЧАНИЯ
Результате выдаем расширенный ответ по токенам с граматическмии элементами
'''
def canonize_words_expanded(morph_analyzer, words: list,
                   tagpos: list = [],
                   grammar_map: dict = grammar_map_STEM,
                   rules='all',
                   minlen=2,
                   isgram=True) -> dict:

    rules = ["_" + item for item in rules.upper().split()]
      #grammeme - Part of Speech, часть речи
      # gender   - род (мужской, женский, средний)
      # number  -  число (единственное, множественное)
    normalized = []
    expanded = { 'grammeme': [], 'score': []}

    for i in words:
        forms = morph_analyzer.parse(i)
        try:
            form = max(forms, key=lambda x: (x.score, x.methods_stack[0][2]))
        except Exception:
            form = forms[0]

        # logger.info("canonize_words form: %s", form)
        # logger.info("canonize_words tagpos: %s", tagpos)
        # logger.info("canonize_words stop_words: %s", stop_words)
        if not ( #form.tag.POS in tagpos
                # len(form.normal_form) < minlen or
                form.normal_form in stop_words):

            tmp_map = grammar_map.get(form.tag.POS, '')
            tmp_norm = form.normal_form # + tmp_map if isgram else form.normal_form
            if '_ALL' in rules or tmp_map in rules:
                normalized.append(tmp_norm)
                expanded['grammeme'].append('%s' % form.tag)
                expanded['score'].append(form.score)

    return normalized, expanded


class SlangRegexp(object):

    PATTERN_1 = u''.join((
        u'\w{0,5}[хx]([хx\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[уy]([уy\s\!@#\$%\^&*+-\|\/]{0,6})[ёiлeеюийя]\w{0,7}|\w{0,6}[пp]',
        u'([пp\s\!@#\$%\^&*+-\|\/]{0,6})[iие]([iие\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[3зс]([3зс\s\!@#\$%\^&*+-\|\/]{0,6})[дd]\w{0,10}|[сcs][уy]',
        u'([уy\!@#\$%\^&*+-\|\/]{0,6})[4чkк]\w{1,3}|\w{0,4}[bб]',
        u'([bб\s\!@#\$%\^&*+-\|\/]{0,6})[lл]([lл\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[yя]\w{0,10}|\w{0,8}[её][bб][лске@eыиаa][наи@йвл]\w{0,8}|\w{0,4}[еe]',
        u'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[uу]([uу\s\!@#\$%\^&*+-\|\/]{0,6})[н4ч]\w{0,4}|\w{0,4}[еeё]',
        u'([еeё\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[нn]([нn\s\!@#\$%\^&*+-\|\/]{0,6})[уy]\w{0,4}|\w{0,4}[еe]',
        u'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[оoаa@]([оoаa@\s\!@#\$%\^&*+-\|\/]{0,6})[тnнt]\w{0,4}|\w{0,10}[ё]',
        u'([ё\!@#\$%\^&*+-\|\/]{0,6})[б]\w{0,6}|\w{0,4}[pп]',
        u'([pп\s\!@#\$%\^&*+-\|\/]{0,6})[иeеi]([иeеi\s\!@#\$%\^&*+-\|\/]{0,6})',
        u'[дd]([дd\s\!@#\$%\^&*+-\|\/]{0,6})[oоаa@еeиi]',
        u'([oоаa@еeиi\s\!@#\$%\^&*+-\|\/]{0,6})[рr]\w{0,12}',
    ))

    PATTERN_2 = u'|'.join((
        u"(\b[сs]{1}[сsц]{0,1}[uуy](?:[ч4]{0,1}[иаakк][^ц])\w*\b)",
        u"(\b(?!пло|стра|[тл]и)(\w(?!(у|пло)))*[хx][уy](й|йа|[еeё]|и|я|ли|ю)(?!га)\w*\b)",
        u"(\b(п[oо]|[нз][аa])*[хx][eе][рp]\w*\b)",
        u"(\b[мm][уy][дd]([аa][кk]|[oо]|и)\w*\b)",
        u"(\b\w*д[рp](?:[oо][ч4]|[аa][ч4])(?!л)\w*\b)",
        u"(\b(?!(?:кило)?[тм]ет)(?!смо)[а-яa-z]*(?<!с)т[рp][аa][хx]\w*\b)",
        u"(\b[к|k][аaoо][з3z]+[eе]?ё?л\w*\b)",
        u"(\b(?!со)\w*п[еeё]р[нд](и|иc|ы|у|н|е|ы)\w*\b)",
        u"(\b\w*[бп][ссз]д\w+\b)",
        u"(\b([нnп][аa]?[оo]?[xх])\b)",
        u"(\b([аa]?[оo]?[нnпбз][аa]?[оo]?)?([cс][pр][аa][^зжбсвм])\w*\b)",
        u"(\b\w*([оo]т|вы|[рp]и|[оo]|и|[уy]){0,1}([пnрp][iиеeё]{0,1}[3zзсcs][дd])\w*\b)",
        u"(\b(вы)?у?[еeё]?би?ля[дт]?[юоo]?\w*\b)",
        u"(\b(?!вело|ски|эн)\w*[пpp][eеиi][дd][oaоаеeирp](?![цянгюсмйчв])[рp]?(?![лт])\w*\b)",
        u"(\b(?!в?[ст]{1,2}еб)(?:(?:в?[сcз3о][тяaа]?[ьъ]?|вы|п[рp][иоo]|[уy]|р[aа][з3z][ьъ]?|к[оo]н[оo])?[её]б[а-яa-z]*)|(?:[а-яa-z]*[^хлрдв][еeё]б)\b)",
        u"(\b[з3z][аaоo]л[уy]п[аaeеин]\w*\b)",
    ))

    regexp = re.compile(PATTERN_1, re.U | re.I)

    @staticmethod
    def test(text):
        return bool(SlangRegexp.regexp.findall(text))

    @staticmethod
    def replace(text, repl='[censored]'):
        return SlangRegexp.regexp.sub(repl, text)

    @staticmethod
    def wrap(text, wrap=('<span style="color:red;">', '</span>',)):
        words = {}
        for word in re.findall(word_pattern, text):
            if len(word) < 3:
                continue
            if SlangRegexp.regexp.findall(word):
                words[word] = u'%s%s%s' % (wrap[0], word, wrap[1],)
        for word, wrapped in words.items():
            text = text.replace(word, wrapped)
        return text
