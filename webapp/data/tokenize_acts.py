from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from string import punctuation
import spacy


class ActTokenizer(object):
    def __init__(self):
        self.PUNCT_DICT = {ord(punc): None for punc in punctuation}
        self.POS_LIST = ['ADJ', 'NOUN', 'VERB']
        self.NLP = spacy.load('en')

    def keep_token(self, token):
        return (
            token.pos_ in self.POS_LIST and
            token.lemma_ != '-PRON-' #spacy's special case for pronouns
        )

    def tokenize_act(self, act):
        doc = self.NLP(act)
        tokens = [t.lemma_.lower() for t in doc if self.keep_token(t)]

        return (' '.join(t for t in tokens if t not in ENGLISH_STOP_WORDS). \
            replace("'s", ''). \
            translate(self.PUNCT_DICT)
        )

    def tokenize_acts(self, acts):
        acts = map(self.tokenize_act, acts)
        # filtering removed to avoid index mismatch with the original
        # data, allowing comparison with unprocessed text content:
        # acts = filter(lambda act: len(act) > 0, acts)
        return list(acts)
