import pymysql
import re
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pylab import *
import imageio
mpl.rcParams['font.sans-serif'] = ['SimHei']


def getData():
    try:
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='spiderdb', port=3306)
        # 创建游标
        cursor = db.cursor()
        # 使用execute()执行sql语句
        sql = 'select * from spiderdb.message'
        cursor.execute(sql)
        rst = cursor.fetchall()
        db.close()
    except Exception as e:
        print(e)
    else:
        return rst


def process(data):
    data = list(data)
    # 去除不完整数据
    new_data = []
    for item in data:
        if item[3] != '':
            new_data.append(item)
    # 去除无用数据
    patern = re.compile(r'.*?python.*?|.*?数据分析.*?|.*?爬虫.*?\
    |.*?测试.*?|.*?运维.*?|.*?计算机视觉.*?|.*?自然语言处理.*?|.*?\
    算法.*?|.*?机器学习.*?|.*?数挖掘.*?', re.I)
    data = []
    for item in new_data:
        if patern.match(item[0]):
            data.append(list(item))
    # 规范薪资信息
    for item in data:
        salary = re.findall(re.compile('\d*\.?\d+'), item[3])
        if len(salary) == 2:
            if '万' in item[3] and '年' in item[3]:
                low_salary = format(float(salary[0]) / 12, '.1f')
                high_salary = format(float(salary[1]) / 12, '.1f')
                item[3] ='{0}-{1}万/月'.format(low_salary,high_salary)
            elif '千' in item[3]:
                    low_salary = format(float(salary[0]) / 10, '.1f')
                    high_salary = format(float(salary[1]) / 10, '.1f')
                    item[3] = '{0}-{1}万/月'.format(low_salary, high_salary)
        else:
            if '万' in item[3] and '年' in item[3]:
                salary = format(float(salary[0]) / 12, '.1f')
                item[3] = '{}万/月'.format(salary)
            elif '千' in item[3]:
                salary = format(float(salary[0]) / 10, '.1f')
                item[3] = '{}万/月'.format(salary)
            elif '天' in item[3]:
                salary = format(float(salary[0]) * 21 / 10000, '.1f')  # 每月工作21天
                item[3] = '{}万/月'.format(salary)

    return data


def func(data):
    position = []
    location = []
    salary = []
    for item in data:
        if item[2] != '异地招聘':
            location.append(item[2])
            if item[2] == '上海':
                position.append(item[0])
                salary.append(item[3])
    return position, location, salary


def area(data):
    areadict = {}
    for item in data:
        areadict[item] = data.count(item)
    labels = []
    fracs = []

    explode = [0.01, 0.1, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
    for k, v in areadict.items():
        labels.append(k)
        fracs.append(v)
    print(labels)
    plt.axes(aspect=1)
    # labels标签参数,x是对应的数据列表,autopct显示每一个区域占的比例,explode突出显示某一块,shadow阴影
    plt.pie(x=fracs, labels=labels, autopct="%.2f%%", explode=explode, shadow=True)
    plt.savefig('饼图.png')


def sal(data):
    salarylist = []
    for item in data:
        salary = re.findall(re.compile('\d*\.?\d+'), item)
        salarylist.append(float(salary[0]))
    salarylist.sort()
    plt.hist(salarylist, 30, width=0.3)
    plt.xlabel('Salary/(万/月)')
    plt.ylabel('count')
    plt.xlim(0, 6)  # 设置x轴分布范围
    plt.savefig('直方图.png')


def occup(data):
    jieba.load_userdict("userdict.txt")
    seglist = []
    for item in data:
        seg_list = jieba.cut(item, cut_all=False) # 精确模式
        for i in seg_list:
            if len(i) > 3:
                if re.compile(r'Python?[\u4e00-\u9fa5]+|[\u4e00-\u9fa5]|Python').match(i):
                    seglist.append(i)
    wordcount = {}
    for item in seglist:
        wordcount[item] = seglist.count(item)
    for item in list(wordcount.keys()):
        if wordcount[item] <= 2:
            del wordcount[item]
    word = WordCloud(font_path='msyh.ttc', background_color='white', height=480, width=640).generate_from_frequencies(wordcount)# 产生词云
    word.to_file('cloud.png')  # 保存图片


if __name__ == '__main__':
    position, location, salary = func(process(getData()))
    area(location)
    sal(salary)
    occup(position)