import os
import codecs
import tika
tika.initVM()
from tika import parser

import bert
from bert import tokenization
from collections import defaultdict
import math
from six import string_types
import numpy as np

def word_tf(word, document):
    if isinstance(document, string_types):
        document = tokenize(document)
    return float(document.count(word))/ len(document)

def tf_idf(word, document):
    if isinstance(document, string_types):
        document = tokenize(document)

    if word not in word_index:
        return .0
    tf = word_tf(word, document)
    idf = word_idf[word_index[word]]
    return word_tf(word, document) * word_idf[word_index[word]]

def create_tokenizer():
    return bert.tokenization.FullTokenizer(vocab_file="vocab.txt")

def tokenize(text):
    words = tokenizer.tokenize(text)
    return [w for w in words if w not in stop_words and not w.isdigit()]


def read_recipe_file(filename):
    parsed = parser.from_file(r"C:\Users\Jackie\PycharmProjects\parsepdf\recipes" + '\\' + filename)
    recipe = parsed["content"]
    recipe = recipe.replace(u'\xa0', '').replace(u'\u3000', '')
    no_special_character = str.maketrans("", "", "【】()")
    recipe = recipe.translate(no_special_character)
    recipe = "".join(recipe.split('\n'))
    return recipe
# def fit_model(seg_word=True, algorithm="bpe"):
#     if seg_word:
#         print("Performing word segmentation...")
#
#     #Train Model
#     print("Training model...")
#     spm.SentencePieceProcessor.Train(
#         '--input={} --model_prefix={} --vocab_size={} '
#         '--input_sentence_size=20000000 '
#         '--character_coverage=0.995 --model_type={algorithm}'.format(
#             TMPPATH_WORD if seg_word else TMPPATH,
#             MODEL_PREFIX.format(algorithm=algorithm),
#             VOC_SIZE, algorithm="unigram"
#         )
#     )

vocabulary = set()
stop_words = codecs.open("stopwords-zh-traditional.txt", 'r', 'utf=8').read().split('\r\n')
print(stop_words)
start_index = -1
stop_index = -1
print("jz1: " + os.getcwd())
algorithm = "unigram"
for filename in os.listdir(os.getcwd() + r'\recipes'):
    recipe = read_recipe_file(filename)
    tokenizer = create_tokenizer()
    words = tokenize(recipe)
    vocabulary.update(words)

vocabulary = list(vocabulary)
word_index = {w: idx for idx, w in enumerate(vocabulary)}

VOCABULARY_SIZE = len(vocabulary)
DOCUMENTS_COUNT = len(os.listdir(os.getcwd() + r'\recipes'))

print(VOCABULARY_SIZE)
print(DOCUMENTS_COUNT)

word_idf = np.zeros(VOCABULARY_SIZE)
for filename in os.listdir(os.getcwd() + r'\recipes'):
    recipe = read_recipe_file(filename)
    tokenizer = create_tokenizer()
    words = set(tokenize(recipe))
    indexes = [word_index[word] for word in words]
    word_idf[indexes] += 1.0

word_idf = np.log(DOCUMENTS_COUNT / (1 + word_idf).astype(float))

print(word_idf[word_index['髮']])
print(word_tf('髮', read_recipe_file('冬菇燜髮菜 加桂花陳酒更香.doc')))
print(tf_idf('髮', read_recipe_file('冬菇燜髮菜 加桂花陳酒更香.doc')))