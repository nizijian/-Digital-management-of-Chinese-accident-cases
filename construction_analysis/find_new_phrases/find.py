from utils import *
import jieba
from pymongo import MongoClient
from bson.objectid import ObjectId
import hanlp

def getphrase_inReason(result:[]):
        tagger = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN_FASTTEXT_ZH)
        myclient = MongoClient('mongodb://localhost:27017/')
        mydb = myclient["事故案例"]
        col_construct = mydb["建筑项目_狭义"]

        lst_reason = []

        for x in col_construct.find({}, {"直接原因": 1, "间接原因": 1, "分不清原因": 1, "_id": 1}):
            lst_reason.append(str(x['直接原因']))
            lst_reason.append(str(x['间接原因']))
            lst_reason.append(str(x['分不清原因']))

        # if '易燃易爆界区内作' in lst_reason:
        #     print('ok')
        # for y in lst_reason:
        #     if '易燃易爆界区内作' in str(y):
        #         print(y)
        # y = '在运行中的易燃易爆界区内作业，却对危险源及其应对措施缺乏足够的认识'
        # if '易燃易爆界区内作' in y:
        #     print(y)

        count = len(result)

        # for y in result:
        #     for z in lst_reason:
        #         if y[0].replace('_','') in z:
        #             print(y)
        #             break

        for y in result:
            lst  = tagger(y[0].split('_'))
            print(tuple(lst)+y)


    


if __name__ == "__main__":
    root_name = "../data/root.pkl"
    root = load_model(root_name)


    topN = 5
    result, add_word = root.find_word(topN)

    root.find_negative()

    # 如果想要调试和选择其他的阈值，可以print result来调整
    # print("\n----\n", result)
    # for x in result:
    #     print(x)
    lst = []
    # getphrase_inReason(result)






