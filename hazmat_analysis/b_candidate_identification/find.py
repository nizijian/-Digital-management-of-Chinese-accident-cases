from utils import *
import jieba
from pymongo import MongoClient
from bson.objectid import ObjectId
import hanlp

def getphrase_inReason(result:[]):
        tagger = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN_FASTTEXT_ZH)
        myclient = MongoClient('mongodb://localhost:27017/')
        mydb = myclient["hazardousTransportation"]
        col_construct = mydb["HazmatCases"]

        lst_reason = []

        for x in col_construct.find({}, { "间接原因": 1, "_id": 1}):
            lst_reason.append(str(x['间接原因']))


        count = len(result)

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
    getphrase_inReason(result)






