import os
import codecs
import tika
import numpy as np
from tika import parser
from collections import Counter
import jieba
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import ntpath
ntpath.basename("a/b/c")
tika.initVM()


class TdfIdfAnalyzer:
    def __init__(self):
        self._weight = []
        self._vocabulary = []
        self._word_idf = []
        self._file_lookup = []
        self._corpus = [] # don't remember what _corpus is for

    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def setupcorpus(self, filelist):
        for fname in filelist:
            print("***" + fname)
            self.segment_file(fname)
            ff = self.path_leaf(fname)
            self._file_lookup.append(ff)

    # utilizes sklearn vectorizer to find tf-idf for all
    def Tfidf(self):
        # always take from segfile
        vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b', stop_words=None)
        transformer = TfidfTransformer(use_idf=True)
        vectorizer_transform = vectorizer.fit_transform(self._corpus)
        tfidf = transformer.fit_transform(vectorizer_transform)

        word = vectorizer.get_feature_names()
        self._vocabulary = word
        self._weight = tfidf.toarray()
        self._word_idf = transformer.idf_

        filepath = './tfidffile'
        if not os.path.exists(filepath):
            os.mkdir(filepath)

        for i in range(len(self._weight)): # TODO: rename weight to more descriptive word
            print(u"-----Writing all the tf-idf in the "+str(i)+u" file into "+filepath+'/'+str(i)+'.txt'+"-----")
            f = open(filepath + '/' + str(i) + '.txt', 'w+', encoding="utf-8")
            for j in range(len(word)):
                f.write(word[j] + "\t" + str(self._weight[i][j]) + '\n')
            f.close()

        # testing out a query
        # Q = self.find_relevant_documents(10, "紅棗30克蜜蓮子7顆")
        # print(Q)

    def gen_vector(self, tokens, word):
        Q = np.zeros((len(self._vocabulary)))
        word_count = len(tokens)
        counter = Counter(tokens)

        for token in np.unique(tokens):
            tf = counter[token]/word_count

            try:
                ind = word.index(token)
                Q[ind] = tf * self._word_idf[ind]
            except:
                pass

        return Q

    @staticmethod
    def cosine_sim(a, b):
        cos_sim = np.dot(a, b)/(np.linalg.norm(a) * np.linalg.norm(b))
        return cos_sim

    def find_relevant_documents(self, k, query):
        tokens = []
        seg_list = jieba.cut(query, cut_all=True)
        for seg in seg_list:
            word = ''.join(seg.split())
            if seg != '' and seg != "\n" and seg != "\n\n":
                tokens.append(word)
        query_vector = self.gen_vector(tokens, self._vocabulary)
        d_cosines = []
        for d in self._weight:
            d_cosines.append(self.cosine_sim(query_vector, d))
        out = np.array(d_cosines).argsort()[-k:][::-1]
        docs = [self._file_lookup[i] for i in out]
        print(out)
        return docs

    def preprocess(self, data):
        data = self.remove_stop_words(data)
        return data

    def remove_stop_words(self, data):
        words = self.tokenize(str(data))
        new_text = ""
        for w in words:
            if w not in self._stop_words:
                new_text += w
        return new_text

    def segment_file(self, filename_in):
        result_folder = './segfile'
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        content = self.read_recipe_file(filename_in)
        seg_list = jieba.cut(content, cut_all=True)
        result = []
        for seg in seg_list:
            seg = ''.join(seg.split())
            if seg != '' and seg != "\n" and seg != "\n\n":
                result.append(seg)

        ff = self.path_leaf(filename_in)

        f = open(result_folder + '/' + ff + '-seg.txt', "w+", encoding='utf-8')
        segmented_content = ' '.join(result)
        self._corpus.append(segmented_content)
        f.write(segmented_content)
        f.close()

    @staticmethod
    def read_recipe_file(abs_path):
        # TODO: abstract out folder locations
        # replace this to be consistent
        parsed = parser.from_file(abs_path)
        recipe_from_file = parsed["content"]
        recipe_from_file = recipe_from_file.replace(u'\xa0', '').replace(u'\u3000', '')
        no_special_character = str.maketrans("", "", "【】()")
        recipe_from_file = recipe_from_file.translate(no_special_character)
        recipe_from_file = "".join(recipe_from_file.split('\n'))
        return recipe_from_file

    def get_stop_words(self):
        return codecs.open("stopwords-zh-traditional.txt", 'r', 'utf=8').read().split('\r\n')


# analyzer = TdfIdfAnalyzer()
#
# article_to_term_relevance_lookup = {}
# for filename in os.listdir(os.getcwd() + r'\recipes'):
#     print("using jieba on " + filename)
#     analyzer.segment_file(filename)
# analyzer.Tfidf()

