#from Reasons.util import *
import re
# import synonyms
import difflib
# dense to sparse
from numpy import array
from scipy import sparse, io
from sklearn.cluster import DBSCAN
import numpy as np
from sklearn import metrics
import csv
import Levenshtein

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


def get_dist():
    dic ={}
    lst_id = []
    for id, x in get_kywlst_from_csv('句子词向量2.csv', keys=['ID', 'Vec']):
        dic[id] = re.sub("\'| |\,|\[|\]",'',x)
        lst_id.append(id)

    i = 0
    den_lst =[]

    while i < len(lst_id):
        j = 0
        lst = []
        while j < len(lst_id):
            v = difflib.SequenceMatcher(a = dic[lst_id[i]], b = dic[lst_id[j]]).quick_ratio()
            #v = Levenshtein.distance(dic[lst_id[i]], dic[lst_id[j]])
            if v > 0:
                lst.append(1/v)
            else:
                lst.append(v)
            j = j + 1
        den_lst.append(lst)
        i = i + 1
        #print(i)
    A = array(den_lst)
    S = sparse.csr_matrix(A)
    io.mmwrite("../data/dis-all.mtx", S)



def DBSCAN_1(s_eps, csvpara, min_s = None, bol_unlable = False):
    dic = {}
    newm = io.mmread("../data/dis-"+csvpara+".mtx")
    B = newm.todense()
    B[B == 0] = 200
    if min_s == None:
        db1 = DBSCAN(eps=s_eps, metric='precomputed').fit(B)
    else:
        db1 = DBSCAN(eps=s_eps, min_samples=min_s ,metric='precomputed').fit(B)
    labels1 = db1.labels_ # 每个点的标签
    i = 0
    # print("Calinski-Harabasz Score %f", (metrics.calinski_harabasz_score(B, db1)))
    for x in list(labels1):
        if dic.get(x) != None:
            dic[x].append(i)
        else:
            lst = []
            lst.append(i)
            dic[x] = lst
        i = i + 1

    if bol_unlable:
        for x in chang2realID(lst=dic[-1],para=csvpara):
            print(x)
    else:
        print(len(dic[-1]))
        n_clusters1 = len(set(labels1)) - (1 if -1 in labels1 else 0) # 类的数目
        print(n_clusters1)

    return  dic




def dic_cluster_results(dic_lable_id:{}, bol_unlable = False):
    dic = {}
    lst_sen = []
    for x in  get_kywlst_from_csv('句子词向量2.csv', keys=['Vec']):
        lst_sen.append(x[0])


    for ky in dic_lable_id.keys():
        if bol_unlable == False:
            if ky != -1:
                print(dic_lable_id[ky])

                i = 0
                # lst_sen = get_kywlst_from_csv('句子词向量.csv', keys=['Vec'])
                for x in dic_lable_id[ky]:
                    print(lst_sen[int(x)])
                    #将数据写入txt
                    with open("../data/句子词向量聚类.txt","a") as f:
                        f.write(lst_sen[int(x)]+'\n')



        else:
            if ky == -1:
                print(dic_lable_id[ky])
                i = 0
                # lst_sen = get_kywlst_from_csv('句子词向量.csv', keys=['Vec'])
                for x in dic_lable_id[ky]:
                    print(lst_sen[int(x)])
    return dic


def save_submatrix(thisround):

    newm = io.mmread("../data/dis-all.mtx")
    B = newm.todense()

    lst_sub =[]

    for x in get_kywlst_from_csv('未归簇.csv',[thisround]):
        y = x[0].replace(' ','')
        if y != '':
            lst_sub.append(int(y))


    bol_first = True
    for i in range(len(lst_sub)):
        lst = []
        for j in range(len(lst_sub)):
            # print(lst_sub[j])
            lst.append(B[lst_sub[i],lst_sub[j]])
        if bol_first:
            submat = array((lst))
            bol_first = False
        else:
            #print(i)
            submat = np.vstack([submat,array((lst))])
    #print(submat)

    S = sparse.csr_matrix(submat)
    io.mmwrite("../data/dis-"+thisround+'.mtx', S)

    return submat

def get_uncluster(para):
    lst = []

    with open('../data/' + '未归簇.csv', "r", encoding='UTF-8')as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            if row[para] != '':
                lst.append(int(row[para]))
            else:
                break

    return lst

def chang2realID_dic(dic:{}, para=None):
    rdic = {}
    lst_corr = []
    for x in get_kywlst_from_csv('未归簇.csv',[para]):
        lst_corr.append(x[0])

    if para == None:
        return dic
    else:
        for ky in dic.keys():
            rlst = []
            for x in dic[ky]:
                rlst.append(lst_corr[x])
            rdic[ky] = rlst
    # for x in rdic.items():
    #     print(x)

    return rdic

def chang2realID(lst:[], para=None):
    rlst = []
    lst_corr = []
    for x in get_kywlst_from_csv('未归簇.csv',[para]):
        lst_corr.append(x[0])

    if para == None:
        return lst
    else:
        for x in lst:
            rlst.append(lst_corr[x])

    return rlst




if __name__ == "__main__":
    #get_dist()
    save_submatrix(thisround='round5')
    ndic = {}
    ndic = DBSCAN_1(s_eps=2,csvpara='round5',bol_unlable=False, min_s=4)
    rdic = chang2realID_dic(dic=ndic, para='round5')
    dic_cluster_results(rdic,bol_unlable=False)







