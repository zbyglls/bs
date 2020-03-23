import pymysql
import re


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


def func(data):
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
        if '万' in item[3] and '年' in item[3]:
            if len(re.findall(re.compile('\d*\.?\d+'), item[3])) == 2:
                low_salary = re.findall(re.compile('\d*\.?\d+'), item[3])[0]
                high_salary = re.findall(re.compile('\d?\.?\d+'), item[3])[1]
                low_salary = float(low_salary) / 12
                high_salary = float(high_salary) / 12
                item[3] ='{0}-{1}万/月'.format(low_salary,high_salary)
            else:
                salary = re.findall(re.compile('\d*\.?\d+'), item[3])[0]
                salary = float(salary) / 12
                item[3] = '{}万/月'.format(salary)
        elif '千' in item[3]:
            if len(re.findall(re.compile('\d*\.?\d+'), item[3])) == 2:
                low_salary = re.findall(re.compile('\d*\.?\d+'), item[3])[0]
                high_salary = re.findall(re.compile('\d?\.?\d+'), item[3])[1]
                low_salary = float(low_salary) / 10
                high_salary = float(high_salary) / 10
                item[3] = '{0}-{1}万/月'.format(low_salary, high_salary)
            else:
                salary = re.findall(re.compile('\d*\.?\d+'), item[3])[0]
                salary = float(salary) / 10
                item[3] = '{}万/月'.format(salary)
        elif '天' in item[3]:
            salary = re.findall(re.compile('\d*\.?\d+'), item[3])[0]
            salary = float(salary) * 21 / 10  #每月工作21天
            item[3] = '{}万/月'.format(salary)

    return data


rst = func(getData())
for i in rst:
    print(i)
