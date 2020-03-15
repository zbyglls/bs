import requests
import pymysql
import re
from bs4 import BeautifulSoup
#url = 'https://search.51job.com/jobsearch/search_result.php?'

def getResponse(url):
    data = {
        'keyword': 'python',
        'jobarea': '030200'
    }
    try:
        rsp = requests.get(url, params=data)
        rsp.encoding = 'gbk'
    except Exception as e:
        print(e)
    else:
        return rsp.text

def getInfo(content, bar):
    soup = BeautifulSoup(content, 'lxml')
    #获取职位
    position = soup.select('#resultList > div:nth-child({}) > p > span > a'.format(bar))[0].string.strip()
    #获取公司
    company = soup.select('#resultList > div:nth-child({}) > span.t2 > a'.format(bar))[0].string.strip()
    #获取工作地点
    location = soup.select('#resultList > div:nth-child({}) > span.t3'.format(bar))[0].string.strip()
    #获取薪资
    salary = soup.select('#resultList > div:nth-child({}) > span.t4'.format(bar))[0].string
    if type(salary) == type(None):
        salary = ''
    else:
        salary = salary.strip()
    #获取发布时间
    time = soup.select('#resultList > div:nth-child({}) > span.t5'.format(bar))[0].string.strip()
    return position, company, location, salary, time
def nextUrl(content):
    soup = BeautifulSoup(content, 'lxml')
    next_url = soup.select('#rtNext')[0].attrs['href']
    return next_url
def getPages(content):
    soup = BeautifulSoup(content, 'lxml')
    #获取总页数
    pages = int(re.compile(r'\d+').search(soup.select('#resultList > div.dw_page > div > div > div > span:nth-child(3)')[0].string).group())
    return pages
def getBars(content):
    soup = BeautifulSoup(content, 'lxml')
    #获取当前页面总条数
    bars = int((len(soup.find_all(name='span', attrs={'class':'t5'}, recursive=True))) - 1)
    return bars
def mysqlHandler(message):
    try:
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='spiderdb', port=3306)
        #创建游标
        cursor = db.cursor()
        if message[0] != '职位名':
            if 'Python' in message[0] or 'python' in message[0] or '爬虫' in message[0] or '数据分析' in message[0]:
                #使用execute()执行sql语句
                sql = 'insert into guangzhou values("{0}","{1}","{2}","{3}","{4}")'.format(message[0], message[1], message[2], message[3], message[4])
                cursor.execute(sql)
                cursor.connection.commit()
        db.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    url = 'https://search.51job.com/jobsearch/search_result.php?'
    content = getResponse(url)
    pages = getPages(content)
    for page in range(pages):
        bars = getBars(content)
        for bar in range(4,bars+4):
            message = getInfo(content, bar)
            mysqlHandler(message)
        if page != pages - 1:
            url = nextUrl(content)
            content = getResponse(url)


