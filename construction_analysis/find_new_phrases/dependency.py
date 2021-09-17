from pyhanlp import *
import operator
import jieba
import hanlp
import csv


class DependencyExtraction(object):

    def __init__(self, load = False):

        if load:
            # jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
            self.tagger = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN_FASTTEXT_ZH)
            # semantic_parser = hanlp.load(hanlp.pretrained.sdp.SEMEVAL16_NEWS_BIAFFINE_ZH)
            self.syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)

        self.hanlp = JClass('com.hankcs.hanlp.HanLP')
        self.cusdic = JClass('com.hankcs.hanlp.dictionary.CustomDictionary')
        self.jump_relation = set(['定中关系', '状中结构', '主谓关系', 'advmod', 'nsubj', 'nz','nn'])
        self.reverse_relation = set(['动补结构', '动宾关系', '介宾关系', 'dobj','pobj','acomp'])
        self.main_relation = set(['核心关系', 'root'])
        self.remove_relate = set(['标点符号'])
        self.quasi_root_tag = set([ 'VC', 'VE', 'VV'])
        # self.quasi_root_tag = set([ 'VC', 'VE', 'VV', 'AD'])
        self.include = set()
        self.group = {}
        for x in self.get_kywlst_from_file(filename='建筑行业一阶词组'):
            jieba.add_word(x)

    def get_kywlst_from_csv(self, filename, key = ''):
        with open('../data/' + filename, "r", encoding='UTF-8')as f:
            f_csv = csv.DictReader(f)
            for row in f_csv:
                if key == '':
                    yield row
                else:
                    if int(row['\ufeffID']) > 4091:
                        yield row[key], row['\ufeffID']

    def get_kywlst_from_file(self, filename):
        lst = []
        with open('../data/' + filename, "r", encoding='UTF-8') as f:
            for x in f.readlines():
                if x not in lst:
                    # lst.append(x.strip('\n'))
                    yield (x.strip('\n'))
        # return lst

    def withtage(self, seglst):
        tag_lst = self.tagger(seglst)
        sem_lst = []
        i = 0
        while i < len(tag_lst):
            tup = (seglst[i], tag_lst[i])
            i = i + 1
            sem_lst.append(tup)

        return sem_lst

    # 句子的观点提取，单root，从root出发，1.找前面最近的修饰词。2.找后面距离为1的reverse_relation
    def parseSentence(self, parse_result, s_id):
        lst_result = []
        reverse_target = {}

        for p in parse_result:
            print(p)
        for i in range(len(parse_result)):
            parse_result[i] = parse_result[i].split('\t')
            self_index = int(parse_result[i][0])
            target_index = int(parse_result[i][6])
            relation = parse_result[i][7]
            if relation in self.remove_relate:
                continue
            if target_index > self_index:
                reverse_target[target_index] = self_index
        result = {}
        result_index = []
        checked = set()
        related_words = set()
        for item in parse_result:
            relation = item[7]
            target = int(item[6])
            index = int(item[0])
            if index in checked:
                continue
            while relation in self.jump_relation:
                checked.add(index)
                next_item = parse_result[target - 1]
                relation = next_item[7]
                target = int(next_item[6])
                index = int(next_item[0])

            if relation in self.reverse_relation and target in result and target not in related_words:
                result[index] = parse_result[index - 1][1]
                result_index.append(parse_result[index - 1][0])


                if index in reverse_target:
                    reverse_target_index = reverse_target[index]
                    if abs(index - reverse_target[index]) <= 1:
                        result[reverse_target_index] = parse_result[reverse_target_index - 1][1]
                        result_index.append(parse_result[reverse_target_index - 1][0])
                        related_words.add(reverse_target_index)

            if relation in self.main_relation:
                result[index] = parse_result[index - 1][1]
                result_index.append(parse_result[index - 1][0])
                if index in reverse_target:
                    reverse_target_index = reverse_target[index]
                    if abs(index - reverse_target_index) <= 1:
                        result[reverse_target_index] = parse_result[reverse_target_index - 1][1]
                        result_index.append(parse_result[reverse_target_index - 1][0])
                        related_words.add(reverse_target_index)
            checked.add(index)

        for item in parse_result:
            word = item[1]
            if word in self.include:
                result[int(item[0])] = word

        sorted_keys = sorted(result.items(), key=operator.itemgetter(0))
        selected_words = [w[1] for w in sorted_keys]

        # self.save_vec(parse_result,result_index, s_id)
        self.save_vec2(selected_words, s_id)

        for item in parse_result:
            relation = item[7]
            target = item[6]
            index = item[0]
            ele = item[1]
            target_ele = parse_result[int(target)-1][1]
            if relation in self.main_relation:
                lst_result.append(ele + '_' + relation + '_' + 'TOP')
            if index in result_index and target in result_index:
                lst_result.append(ele+'_'+relation+'_'+target_ele)


        # print(sorted(set(result_index),key=result_index.index))
        print(selected_words)
        return selected_words

    ''' 
    关键词观点提取，根据关键词key，找到关键处的rootpath，寻找这个root中的观点，观点提取方式和parseSentence的基本一样。
    支持提取多个root的观点。
    '''
    def parseSentWithKey(self, parse_result, s_id, key=None):
        rootList = []
        result_index = []
        for p in parse_result:
            print(p)

        lst_result = []

        # 索引-1，改正确
        for i in range(len(parse_result)):
            parse_result[i] = parse_result[i].split('\t')
            parse_result[i][0] = int(parse_result[i][0]) - 1
            parse_result[i][6] = int(parse_result[i][6]) - 1
            if key and parse_result[i][1] == key:
                keyIndex = i

        for i in range(len(parse_result)):
            self_index = int(parse_result[i][0])
            target_index = int(parse_result[i][6])
            relation = parse_result[i][7]
            if relation in self.main_relation:
                if self_index not in rootList:
                    rootList.append(self_index)
            # elif relation == "conj" and target_index in rootList:
            #     if self_index not in rootList:
            #         rootList.append(self_index)

            if len(parse_result[target_index]) == 10:
                parse_result[target_index].append([])

            if target_index != -1 and not (relation == "conj" and target_index in rootList):
                parse_result[target_index][10].append(self_index)

        if key:
            rootIndex = 0
            if len(rootList) > 1:
                target = keyIndex
                while True:
                    if target in rootList:
                        rootIndex = rootList.index(target)
                        break
                    next_item = parse_result[target]
                    target = int(next_item[6])
            loopRoot = [rootList[rootIndex]]
        else:
            loopRoot = rootList

        result = {}
        related_words = set()
        for root in loopRoot:
            if key:
                self.addToResult(parse_result, keyIndex, result, related_words)
            self.addToResult(parse_result, root, result, related_words)

        for item in parse_result:
            relation = item[7]
            target = int(item[6])
            index = int(item[0])
            if relation in self.reverse_relation and target in result and target not in related_words:
                self.addToResult(parse_result, index, result, related_words)

        for item in parse_result:
            word = item[1]
            if word == key:
                result[int(item[0])] = word
        for x in result.keys():
            result_index.append(int(x+1))

        sorted_keys = sorted(result.items(), key=operator.itemgetter(0))
        selected_words = [w[1] for w in sorted_keys]
        # self.save_vec(parse_result,result_index, s_id)
        self.save_vec2(selected_words, s_id)
        return selected_words


    def save_vec(self, parse_result, result_index:[], s_id):
        lst_result = []
        lst = []
        for item in parse_result:
            relation = item[7]
            target = item[6]
            index = item[0]
            ele = item[1]
            target_ele = parse_result[int(target)-1][1]
            if relation in self.main_relation:
                lst_result.append(ele + '_' + relation + '_' + 'TOP')
            if index in result_index and target in result_index:
                lst_result.append(ele+'_'+relation+'_'+target_ele)
        lst.append(s_id)
        lst.append(lst_result)
        with open('../data/建筑句子2词向量.csv', 'a', newline='', encoding='UTF-8')as f:
            f_csv = csv.writer(f)
            f_csv.writerow(lst)

        print(lst_result)

    def save_vec2(self, select_word, s_id):
        lst = []
        lst.append(s_id)
        lst.append(select_word)
        with open('../data/建筑句子2词向量.csv', 'a', newline='', encoding='UTF-8')as f:
            f_csv = csv.writer(f)
            f_csv.writerow(lst)


    def addToResult(self, parse_result, index, result, related_words):
        result[index] = parse_result[index][1]
        if len(parse_result[index]) == 10:
            return
        reverse_target_index = 0
        for i in parse_result[index][10]:
            if i < index and i > reverse_target_index:
                reverse_target_index = i
        if abs(index - reverse_target_index) <= 1:
            result[reverse_target_index] = parse_result[reverse_target_index][1]
            related_words.add(reverse_target_index)

    def getreason(self, sentence, s_id):
        seg_list = jieba.cut(sentence)
        sem_lst = self.withtage(list(seg_list))
        syn_result = self.syntactic_parser(sem_lst)
        parse_result = str(syn_result).strip().split('\n')
        has_quasi = False
        quasi_root = ''
        has_root = False

        for item in syn_result:
            l = len(item.nonempty_fields)
            relation = item.nonempty_fields[l-1]
            if relation in self.main_relation:
                has_root = True
                break


        if not has_root:
            print('没有root：'+sentence)
            lst = parse_result[0].split('\t')
            lst[7] = 'root'
            i = 0
            while i < len(lst) - 1:
                lst[i] = lst[i] + '\t'
                i = i + 1
            parse_result[0] = ''.join(lst)
            return self.parseSentence(parse_result, s_id)

        for item in syn_result:
            l = len(item.nonempty_fields)
            relation = item.nonempty_fields[l-1]
            tag = item.nonempty_fields[1]
            if relation not in self.main_relation and tag in self.quasi_root_tag:
                has_quasi = True
                quasi_root = item.nonempty_fields[0]
                break

        if has_quasi:
            # print('===='+quasi_root)
            return self.parseSentWithKey(parse_result, s_id, key=quasi_root)
            # return self.parseSentWithKey(parse_result, key=quasi_root)
        else:
            return self.parseSentence(parse_result, s_id)
            # return self.parseSentWithKey(parse_result, key='将')





if __name__ == "__main__":
    de = DependencyExtraction(load = True)
    dic = {}
    for x, s_id in de.get_kywlst_from_csv('建筑间接原因.csv', key = 'sentence'):
        print(s_id)
        print(de.getreason(x, s_id))
        print(x)
        print('='*20)



    #print(de.getreason('施工单位安全生产主体责任不落实','111'))


