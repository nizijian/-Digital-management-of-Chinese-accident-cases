import pandas as pd
import csv

df = pd.read_csv('../data/句子词向量.csv')
df = df.drop_duplicates(subset=['Vec'], keep='first', inplace=False)
df1 = df.drop(["ID"],axis=1) #删除ID这列数据

df1.to_csv('../data/句子词向量2.csv',index=False)


#建立从1开始的新的ID列
df1 = pd.read_csv('../data/句子词向量2.csv')
cols = ['ID'] + list(df1.columns)
df1.index += 1
df1['ID'] = df1.index
df2 = df1[cols]

df2.to_csv('../data/句子词向量2.csv',index=False)