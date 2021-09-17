from pymongo import MongoClient
import re

#建立MongoDB数据库连接
myclient = MongoClient('mongodb://localhost:27017/')
mydb = myclient["hazardousTransportation"]



def reason_to_list(oneCase):
    """
    将一个案例的间接原因分段
    """
    for reason in oneCase["间接原因"]:
        reason_list = reason.split('\n')
        while  '\t' in reason_list:
            reason_list.remove('\t')
        while  '\r' in reason_list:
            reason_list.remove('\r')
        while '' in reason_list:
            reason_list.remove('')
    test_collection.update_one({"_id": oneCase['_id']},{'$set': {'间接原因': reason_list}})


def sentence_split(oneCase):
    """
    将一个案例的每条间接原因都分句
    """
    lst = []
    lst_1 = []
    for reason in oneCase["间接原因"]:
        lst = lst + re.split(r';|：|，|；|,|。|^（[1-9]）|^[1-9]）|^<[1-9]>|^[1-9]>|^\.|^[1-9]、|^[①-⑨]|;|\u3000|◎|^[1-9]\t、|^[1-9]\.', reason)
        count = 0
        if '' in lst:
            lst.remove('')
        for z in lst:
            if z == '':
                continue
            if len(z) < 3:
                # lst.remove(z)
                continue
            else:
                 lst_1.append(re.sub(r'"|《|》|(|)|<|>|〉| |　|\d|\.|\n|\t|．|◎|^①-⑨|;|“|”|\(|\)|（|）|\u3000|（', '', z))#清除噪音

            count = count + 1
    return lst_1


def sentence_to_txt(list):
    """
    将间接原因的分句结果写入senSplit0.txt文件
    """
    file = open('../data/senSplit0.txt','a',encoding='utf-8')
    for x in list:
        file.write(str(x)+'\n')
    file.close()
'''
def get_quote_names(self):
        dic= {}
        for x in self.get_kywlst_from_file('demo.txt'):
            y = re.search(r'《\w*》',x)
            if y != None:
                dic[str(y.group())] = 1

        for x in dic.keys():
            print(x)
'''

if __name__ =="__main__":
    """
    遍历所有案例，将案例间接原因分句，并存入文本文档
    """
    #指定要操作的数据表
    test_collection = mydb["HazmatCases"]
    cases = test_collection.find({})
    #遍历每一个案例
    for case in cases:
        reason_to_list(case) #将案例的间接原因分段
        sen = sentence_split(case) #将案例原因分句
        sentence_to_txt(sen) #将分句结果存入文本文档


    #去除senSplit0.txt中的空行，结果存入senSplit1.txt
    file = open('../data/senSplit0.txt','r',encoding='utf-8')
    fileNew = open('../data/senSplit1.txt','w',encoding='utf-8')
    for text in file.readlines():
                if text.split():
                        fileNew.write(text)
    file.close()
    fileNew.close()
