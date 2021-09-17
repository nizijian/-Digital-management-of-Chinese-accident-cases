from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import json
from dependency import DependencyExtraction

class DBO(object):

    def __init__(self):
        self.myclient = MongoClient('mongodb://localhost:27017/')
        self.mydb = self.myclient["事故案例"]
        self.col_construct = self.mydb["建筑项目_狭义"]
        self.col_all = self.mydb['建筑行业_全集']


    def get_indirect(self):
        lst = []
        lst_1 = []
        for x in self.col_construct.find({}, {"间接原因": 1, '_id': 1}):
            for y in x['间接原因']:
                lst = lst + re.split(r';|：|，|；|,|。|^（[1-9]）|^[1-9]）|^\.|^[1-9]、|^[①-④]|;|\u3000|◎|^[1-9]\t、|^[1-9]\.', y)
        count = 0
        lst.remove('')
        for z in lst:
            if z == '':
                continue
            if len(z) < 3:
                # lst.remove(z)
                continue
            else:
                lst_1.append(self.del_noise_char(z))

            count = count + 1

        return lst_1






    def del_noise_char(self, sen):
        return sen
        sen = re.sub(r'"|《|》|(|)| |　|\d|\.|．|◎|;|“|”|\(|\u3000|（', '', sen)


    def get_kywlst_from_file(self, filename):
        lst = []
        with open('../data/' + filename, "r", encoding='UTF-8') as f:
            for x in f.readlines():
                if x not in lst:
                    # lst.append(x.strip('\n'))
                    yield (x.strip('\n'))


    def get_quote_names(self):
        dic= {}
        for x in self.get_kywlst_from_file('demo.txt'):
            y = re.search(r'《\w*》',x)
            if y != None:
                dic[str(y.group())] = 1

        for x in dic.keys():
            print(x)







if __name__ == "__main__":
    dbo = DBO()
    # de = DependencyExtraction(load=True)
    # lst = []
    # lst = dbo.get_indirect()
    # for x in lst:
    #     print(x)
        # if x != '':
        #     de.getreason(x)
    dbo.get_quote_names()
