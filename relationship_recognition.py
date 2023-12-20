# 导入库
import re
import spacy
import pandas as pd

# 加载中文模型
nlp = spacy.load('zh_core_web_sm')


# 定义实体识别函数
def entity_recognition(text):
    # 使用spacy进行分词和命名实体识别
    doc = nlp(text)
    # 创建一个空的数据框，用于存储实体和实体类型
    df = pd.DataFrame(columns=['Entity', 'Type'])
    # 遍历doc中的实体
    for ent in doc.ents:
        # 将实体和实体类型添加到数据框中
        df = df.append({'Entity': ent.text, 'Type': ent.label_}, ignore_index=True)
    # 返回数据框
    return df


# 定义关系抽取函数
def relation_extraction(text):
    # 使用spacy进行分词和依存句法分析
    doc = nlp(text)
    # 创建一个空的数据框，用于存储实体对和关系
    df = pd.DataFrame(columns=['Entity1', 'Entity2', 'Relation'])
    # 遍历doc中的每个词
    for token in doc:
        # 如果词是一个动词，那么它可能是一个关系
        if token.pos_ == 'VERB':
            # 获取该词的子树，即与该词相关的所有词
            subtree = list(token.subtree)
            # 创建一个空列表，用于存储子树中的实体
            entities = []
            # 遍历子树中的每个词
            for word in subtree:
                # 如果词是一个实体，那么将它添加到实体列表中
                if word.ent_type_ != '':
                    entities.append(word.text)
            # 如果实体列表中有两个或以上的实体，那么它们可能是一个实体对
            if len(entities) >= 2:
                # 遍历实体列表中的每两个实体
                for i in range(len(entities) - 1):
                    for j in range(i + 1, len(entities)):
                        # 将实体对和关系添加到数据框中
                        df = df.append({'Entity1': entities[i], 'Entity2': entities[j],
                                        'Relation': token.text}, ignore_index=True)
    # 返回数据框
    return df


# 定义三元组生成函数
def triple_generation(text):
    # 调用实体识别函数，获取实体和实体类型
    entity_df = entity_recognition(text)
    # 调用关系抽取函数，获取实体对和关系
    relation_df = relation_extraction(text)
    # 创建一个空的数据框，用于存储三元组
    df = pd.DataFrame(columns=['Subject', 'Predicate', 'Object'])
    # 遍历关系数据框中的每一行
    for index, row in relation_df.iterrows():
        # 获取实体1和实体2
        entity1 = row['Entity1']
        entity2 = row['Entity2']
        # 获取实体1和实体2的类型
        type1 = entity_df[entity_df['Entity'] == entity1]['Type'].values[0]
        type2 = entity_df[entity_df['Entity'] == entity2]['Type'].values[0]
        # 获取关系
        relation = row['Relation']
        # 根据实体类型的不同，确定主语和宾语
        if type1 == 'ORG' and type2 == 'ORG':
            # 如果两个实体都是组织，那么按照顺序确定主语和宾语
            subject = entity1
            object = entity2
        elif type1 == 'ORG' and type2 != 'ORG':
            # 如果实体1是组织，实体2不是组织，那么实体1是主语，实体2是宾语
            subject = entity1
            object = entity2
        elif type1 != 'ORG' and type2 == 'ORG':
            # 如果实体1不是组织，实体2是组织，那么实体2是主语，实体1是宾语
            subject = entity2
            object = entity1
        else:
            # 如果两个实体都不是组织，那么按照顺序确定主语和宾语
            subject = entity1
            object = entity2
        # 将三元组添加到数据框中
        df = df.append({'Subject': subject, 'Predicate': relation, 'Object': object}, ignore_index=True)
    # 返回数据框
    return df


# 定义描述字符串
text = '某图书销售连锁集团有多家书店，一家书店可销售多种图书，每种图书也可以放在多个书店销售。每家书店销售的每种图书都有月销售量。一家书店可聘任多名职工，每个职工只能在一个书店工作，书店聘用职工有聘期和工资。书店有书店编号、书店名、地址等属性，图书有图书编号、图书名、规格、单价等属性，职工有职工编号、姓名、性别、业绩等属性。'

# 调用三元组生成函数，获取三元组
triple_df = triple_generation(text)

# 打印三元组
print(triple_df)
