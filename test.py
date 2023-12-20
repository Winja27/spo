# 导入所需的库
import jieba
import re
from pyhanlp import *

# 定义一个函数，用于识别实体和属性
def entity_recognition(text):
  # 使用jieba进行分词
  words = jieba.lcut(text)
  # 使用pyhanlp进行命名实体识别
  NLPTokenizer = JClass('com.hankcs.hanlp.tokenizer.NLPTokenizer')
  NER = NLPTokenizer.segment(''.join(words))
  # 定义一个字典，用于存储实体和属性
  entity_dict = {}
  # 遍历识别结果，提取实体和属性
  for term in NER:
    word = term.word # 单词
    nature = term.nature.toString() # 词性
    # 如果词性是实体或属性，将其加入字典
    if nature in ['n','m','nx','nt','nz','ng','nr','ns']:
      entity_dict[word] = nature
  # 返回实体和属性字典
  return entity_dict

# 定义一个函数，用于提取实体之间的关系
def relation_extraction(text):
  # 定义一个列表，用于存储关系
  relation_list = []
  # 使用正则表达式匹配描述中的句子结构
  pattern = re.compile(r'(\S+)有(\S+)等属性，|一(\S+)可(\S+)多(\S+)，|每(\S+)只能在一个(\S+)工作，|(\S+)聘用(\S+)有(\S+)和(\S+)。')
  matches = pattern.finditer(text)
  # 遍历匹配结果，提取关系
  for match in matches:
    # 如果匹配到“有...等属性”结构，提取“有”作为关系
    if match.group(1) and match.group(2):
      relation_list.append((match.group(1),'有',match.group(2)))
    # 如果匹配到“可...多...”结构，提取“可”作为关系
    elif match.group(3) and match.group(4) and match.group(5):
      relation_list.append((match.group(3),'可'+match.group(4),match.group(5)))
    # 如果匹配到“只能在一个...工作”结构，提取“只能在一个...工作”作为关系
    elif match.group(6) and match.group(7):
      relation_list.append((match.group(6),'只能在一个'+match.group(7)+'工作',match.group(7)))
    # 如果匹配到“聘用...有...和...”结构，提取“聘用”和“有”作为关系
    elif match.group(8) and match.group(9) and match.group(10) and match.group(11):
      relation_list.append((match.group(8),'聘用',match.group(9)))
      relation_list.append((match.group(8),'有',match.group(10)))
      relation_list.append((match.group(8),'有',match.group(11)))
  # 返回关系列表
  return relation_list

# 定义一个函数，用于生成三元组
def triple_generation(text):
  # 调用实体识别函数，获取实体和属性字典
  entity_dict = entity_recognition(text)
  # 调用关系抽取函数，获取关系列表
  relation_list = relation_extraction(text)
  # 定义一个列表，用于存储三元组
  triple_list = []
  # 遍历关系列表，生成三元组
  for relation in relation_list:
    # 获取主语、谓语和宾语
    subject = relation[0]
    predicate = relation[1]
    object = relation[2]
    # 如果宾语是属性，将其替换为实体的具体属性值
    if object in entity_dict and entity_dict[object] == 'm':
      object = subject + object
    # 将三元组加入列表
    triple_list.append((subject,predicate,object))
  # 返回三元组列表
  return triple_list

# 定义一个描述文本
text = '某图书销售连锁集团有多家书店，一家书店可销售多种图书，每种图书也可以放在多个书店销售。每家书店销售的每种图书都有月销售量。一家书店可聘任多名职工，每个职工只能在一个书店工作，书店聘用职工有聘期和工资。书店有书店编号、书店名、地址等属性，图书有图书编号、图书名、规格、单价等属性，职工有职工编号、姓名、性别、业绩等属性。'

# 调用三元组生成函数，打印结果
triple_list = triple_generation(text)
for triple in triple_list:
  print(triple)
