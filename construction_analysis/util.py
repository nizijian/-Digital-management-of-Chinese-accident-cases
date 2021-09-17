import csv
import re


def get_kywlst_from_csv(filename, keys=[]):
    with open('../data/' + filename, "r", encoding='UTF-8')as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            if len(keys) == 0:
                yield row
            else:
                i = 0
                lst = []
                while i < len(keys):
                    lst.append(row[keys[i]])
                    i = i + 1
                yield lst

def save2csv(filename, value):
    with open('../data/' + filename, "a", encoding='UTF-8')as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(value)

def get_kywlst_from_file(filename):
    lst = []
    with open('../data/' + filename, "r", encoding='UTF-8') as f:
        for x in f.readlines():
            if x not in lst:
                # lst.append(x.strip('\n'))
                yield (x.strip('\n'))


def chang2list(str_lst):
    lst = []
    if str_lst != '':
        str_lst = re.sub('\[|\]|\'','',str_lst)
        lst = str_lst.split(',')
    return lst

def get_vec_lst(str_lst):
    lst = []
    if len(str_lst) > 0:
        str_lst = re.sub('\[|\]|\'', '', str_lst)
        lst = str_lst.split(',')

    return lst



def getsy_2dic():
    dic = {}
    for x,y in get_kywlst_from_csv('建筑同义词.csv', ['set','target']):
        sy_target = re.sub("'| ",'',y)
        lst = []
        lst = re.sub("\{|\}|'| ",'',x).split('-')
        for x in lst:
            dic[x] = sy_target

    return dic
def toSemantic_vec():
    dic_sy = {}
    dic_sy = getsy_2dic()
    dic = {}
    for id,y in get_kywlst_from_csv('建筑句子2词向量.csv', ['ID','Vec']):
        lst = []
        lst = re.sub("\[|\]|'| ",'',y).split(',')
        for x in lst:
           if dic_sy.get(x) != None:
               lst.append(dic_sy[x])
               lst.remove(x)
        dic[id] = lst

    return dic







def getsy_2set():
    lst_set = []
    raw_lst = []

    for x in get_kywlst_from_file('建筑同义词'):
        sy_lst = []
        sy_lst = x.split('_')
        s = set()
        s.add(sy_lst[0])
        s.add(sy_lst[1])
        raw_lst.append(s)

    i = 0
    while i < len(raw_lst):
        j = 0
        s = set()
        while j < len(raw_lst):
            if len(raw_lst[i] & raw_lst[j]) > 0:
                s = raw_lst[i] | raw_lst[j]
            j = j + 1
        lst_set.append(s)
        # 删除纳入集合的数列项
        k = 0
        while k < len(raw_lst):
            if len(s & raw_lst[k]) > 1:
                raw_lst.pop(k)
            k = k + 1
        i = i + 1



    return lst_set


if __name__ == "__main__":
    a = set('abracadabra')
    b = set('alacazam')
    c = a | b
    print(c)

    # toSemantic_vec()

    for x in toSemantic_vec().items():
        print(x)


