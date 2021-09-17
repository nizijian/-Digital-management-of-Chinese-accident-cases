# -*- coding: utf-8 -*-
"""
# @Time    : 2018/05/26 下午5:13
# @Update  : 2018/09/28 上午10:30
# @Author  : zhanzecheng/片刻
# @File    : demo.py.py
# @Software: PyCharm
"""
import os
import jieba
from model import TrieNode
from utils import *
from config import basedir


def load_data(filename, stopwords):
    """

    :param filename:
    :param stopwords:
    :return: 二维数组,[[句子1分词list], [句子2分词list],...,[句子n分词list]]
    """
    data = []
    lst = []
    # lst = get_kywlst_from_file(filename ='corewords')
    # for x in get_kywlst_from_file(filename ='低IDF关键词'):
    #     lst.append(x)
    for x in get_kywlst_from_file(filename ='../data/hmtdict.txt'):
        lst.append(x)
    for yy in lst:
        jieba.add_word(str(yy))
    with open(filename, 'r',encoding='utf-8') as f:
        for line in f:
            word_list = [x for x in jieba.cut(line.strip(), cut_all=False) if x not in stopwords]
            data.append(word_list)
    return data


def load_data_2_root(data):
    print('------> 插入节点')
    cot = 0
    for word_list in data:
        cot = cot + 1
        print(cot)
        print(word_list)
        # tmp 表示每一行自由组合后的结果（n gram）
        # tmp: [['它'], ['是'], ['小'], ['狗'], ['它', '是'], ['是', '小'], ['小', '狗'], ['它', '是', '小'], ['是', '小', '狗']]
        ngrams = generate_ngram(word_list, 3)
        for d in ngrams:
            root.add(d)
    save_model(root, root_name)
    print('------> 插入成功')


if __name__ == "__main__":
    root_name = "../data/root.pkl"
    stopwords = get_stopwords()
    if os.path.exists(root_name):
        root = load_model(root_name)
    else:
        dict_name = '../data/dict.txt'
        word_freq = load_dictionary(dict_name)
        root = TrieNode('*', word_freq)
        save_model(root, root_name)

    # 加载新的文章
    filename = '../data/senSplit2.txt'
    data = load_data(filename, stopwords)
    # 将新的文章插入到Root中
    load_data_2_root(data)


