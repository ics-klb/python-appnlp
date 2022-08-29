# -*- coding: utf-8 -*-
import logging

import gensim
import numpy as np
import pymorphy2

GRAMMAR_MAP_STEM = {
    'NOUN': '_S',
    'VERB': '_V', 'INFN': '_V', 'GRND': '_V', 'PRTF': '_V', 'PRTS': '_V',
    'ADJF': '_A', 'ADJS': '_A',
    'ADVB': '_ADV',
    'PRED': '_PRAEDIC'
}
GRAMMAR_MAP_POS_TAGS =  {
    'NOUN': '_NOUN',
    'VERB': '_VERB', 'INFN': '_VERB', 'GRND': '_VERB', 'PRTF': '_VERB', 'PRTS': '_VERB',
    'ADJF': '_ADJ', 'ADJS': '_ADJ',
    'ADVB': '_ADV',
    'PRED': '_ADP'
}

morph_analyzer = pymorphy2.MorphAnalyzer()

class NlpModelSemantic(object):

    @staticmethod
    def canonize_words(words: list, grammar_map: dict = GRAMMAR_MAP_STEM) -> list:

        stop_words = ('быть', 'мой', 'наш', 'ваш', 'их', 'его', 'её', 'их',
                      'этот', 'тот', 'где', 'который', 'либо', 'нибудь', 'нет', 'да')

        normalized = []
        for w in words:
            forms = morph_analyzer.parse(w.lower())
            try:
                form = max(forms, key=lambda x: (x.score, x.methods_stack[0][2]))
            except Exception:
                form = forms[0]
                print(form)
            if not (form.tag.POS in ['PREP', 'CONJ', 'PRCL', 'NPRO', 'NUMR']
                    or 'Name' in form.tag
                    or 'UNKN' in form.tag
                    or form.normal_form in stop_words):  # 'ADJF'
                norm_word = form.normal_form.replace("ё", "е")
                normalized.append(norm_word + grammar_map.get(form.tag.POS, ''))

        return normalized

    @staticmethod
    def semantic_density(bag: list, w2v_model, unknown_coef=0.0) -> float:
        sim_sum = 0.0
        divisor = 0
        # weight_sum = 0.0
        for i in range(len(bag)):
            for j in range(i + 1, len(bag)):
                if bag[i] != bag[j]:
                    divisor += 1
                    # weight = 1 / (j - i)
                    # weight_sum += weight
                    try:
                        # sim_sum += w2v_model.similarity(bag[i], bag[j]) # * weight
                        sim_sum += np.dot(w2v_model[bag[i]], w2v_model[bag[j]])  # vectors already normalized
                    except:
                        sim_sum += unknown_coef  # * weight
            return sim_sum / divisor if divisor > 0 else 0.0  # / weight_sum

    @staticmethod
    def bag_to_matrix(bag: list, w2v_model):
        mx = []
        for i in range(len(bag)):
            try:
                mx.append(w2v_model[bag[i]])
            except:
                pass
        return np.vstack(mx) if len(mx) > 0 else np.array([])

    @staticmethod
    def most_similar(w2v_model, positive="", negative="", topn=10):
        pos_bag = NlpModelSemantic.canonize_words(positive.split())
        neg_bag = NlpModelSemantic.canonize_words(negative.split())
        return w2v_model.most_similar(pos_bag, neg_bag, topn) if len(positive) > 0 else ()


    @staticmethod
    def semantic_similarity_fast(mx1, mx2) -> float:
        return np.sum(np.dot(mx1, mx2.T)) if len(mx1) > 0 and len(mx2) > 0 else 0.0

    @staticmethod
    def semantic_similarity_fast_log(mx1, mx2) -> float:
        return np.sum(np.dot(mx1, mx2.T)) * np.log10(len(mx2)) / (len(mx2) * len(mx1)) \
               if len(mx1) > 0 and len(mx2) > 0 else 0.0

    @staticmethod
    def semantic_similarity(bag1, bag2: list, w2v_model, unknown_coef=0.0) -> float:
        sim_sum = 0.0
        for i in range(len(bag1)):
            for j in range(len(bag2)):
                try:
                    # sim_sum += w2v_model.similarity(bag1[i], bag2[j])
                    sim_sum += np.dot(w2v_model[bag1[i]], w2v_model[bag2[j]]) # vectors already normalized
                except:
                    sim_sum += unknown_coef

        return sim_sum / (len(bag1) * len(bag2)) if len(bag1) > 0 and len(bag2) > 0 else 0.0

    @staticmethod
    def semantic_association(self, bag: list, w2v_model, topn=10) -> list:
        positive_lst = [w for w in bag if w in w2v_model.vocab]
        if len(positive_lst) > 0:
            assoc_lst = w2v_model.most_similar(positive=positive_lst, topn=topn)
            return [a[0] for a in assoc_lst]
        else:
            print('empty association for bag:', bag)
            return ['пустота_S']
