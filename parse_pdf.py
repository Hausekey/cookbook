import os
import codecs
import tika
import numpy as np
import bert
from tika import parser
from bert import tokenization
from six import string_types
tika.initVM()

class TdfIdfAnalyzer:
    def __init__(self):
        self._tokenizer = self.create_tokenizer()
        self.DOCUMENTS_COUNT = len(os.listdir(os.getcwd() + r'\recipes'))
        self._stop_words = self.get_stop_words()
        self._vocabulary = self.set_up_vocabulary()
        self.VOCABULARY_SIZE = len(self._vocabulary)
        self._word_index = {w: idx for idx, w in enumerate(self._vocabulary)}
        self._word_idf = self.set_up_word_idf()

    def set_up_vocabulary(self):
        vocabulary = set()
        for filename in os.listdir(os.getcwd() + r'\recipes'):
            recipe = self.read_recipe_file(filename)
            tokenizer = self.create_tokenizer()
            words = self.tokenize(recipe)
            vocabulary.update(words)
        vocabulary = list(vocabulary)
        return vocabulary

    def word_tf(self, word, document):
        if isinstance(document, string_types):
            document = self.tokenize(document)
        return float(document.count(word))/ len(document)


    def tf_idf(self, word, document):
        if isinstance(document, string_types):
            document = self.tokenize(document)

        if word not in self._word_index:
            return .0
        tf = self.word_tf(word, document)
        idf = self._word_idf[self._word_index[word]]
        return tf * idf


    def create_tokenizer(self):
        return bert.tokenization.FullTokenizer(vocab_file="vocab.txt")


    def tokenize(self, text):  # can tokenizing be improved?
        words_from_text = self._tokenizer.tokenize(text)
        return [w for w in words_from_text if w not in self._stop_words and not w.isdigit()]


    def read_recipe_file(self, filename_in):
        parsed = parser.from_file(r"C:\Users\Jackie\PycharmProjects\parsepdf\recipes" + '\\' + filename_in)
        recipe_from_file = parsed["content"]
        recipe_from_file = recipe_from_file.replace(u'\xa0', '').replace(u'\u3000', '')
        no_special_character = str.maketrans("", "", "【】()")
        recipe_from_file = recipe_from_file.translate(no_special_character)
        recipe_from_file = "".join(recipe_from_file.split('\n'))
        return recipe_from_file


    def get_stop_words(self):
        return codecs.open("stopwords-zh-traditional.txt", 'r', 'utf=8').read().split('\r\n')

    def set_up_word_idf(self):
        word_idf = np.zeros(self.VOCABULARY_SIZE)
        for filename in os.listdir(os.getcwd() + r'\recipes'):
            recipe = self.read_recipe_file(filename)
            words = set(self.tokenize(recipe))
            indexes = [self._word_index[word] for word in words]
            word_idf[indexes] += 1.0
        word_idf = np.log(self.DOCUMENTS_COUNT / (1 + word_idf).astype(float))
        return word_idf

analyzer = TdfIdfAnalyzer()
print(analyzer._word_idf[analyzer._word_index['髮']])
print(analyzer.word_tf('髮', analyzer.read_recipe_file('冬菇燜髮菜 加桂花陳酒更香.doc')))
print(analyzer.tf_idf('髮', analyzer.read_recipe_file('冬菇燜髮菜 加桂花陳酒更香.doc')))

article_to_term_relevance_lookup = {}
for filename in os.listdir(os.getcwd() + r'\recipes'):
    term_relevance = {}
    recipe = analyzer.read_recipe_file(filename)
    for term in recipe:
        print(term)
        term_relevance[term] = analyzer.tf_idf(term, recipe)
    article_to_term_relevance_lookup[filename] = term_relevance

print(article_to_term_relevance_lookup)
