import requests
import pymysql
import re
from bs4 import BeautifulSoup


def getResponse(area, url):
    data = {
        'keyword': 'Python',
        'jobarea': area
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
    # 获取职位
    position = soup.select('#resultList > div:nth-child({}) > p > span > a'.format(bar))[0].string.strip()
    # 获取公司
    company = soup.select('#resultList > div:nth-child({}) > span.t2 > a'.format(bar))[0].string.strip()
    # 获取工作地点
    location = soup.select('#resultList > div:nth-child({}) > span.t3'.format(bar))[0].string.strip()
    # 获取薪资
    salary = soup.select('#resultList > div:nth-child({}) > span.t4'.format(bar))[0].string
    if type(salary) == type(None):
        salary = ''
    else:
        salary = salary.strip()
    url = soup.select('#resultList > div:nth-child({}) > p > span > a'.format(bar))[0].attrs['href']
    information = getMes(url)
    return position, company, location, salary, information


def getMes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }
    rsp = requests.get(url, headers=headers)
    rsp.encoding = 'gbk'
    soup = BeautifulSoup(rsp.text, 'lxml')
    info = str(soup.select('body > div.tCompanyPage > div.tCompany_center.clearfix > div.tCompany_main > div:nth-child(1) > div'))
    pattern = re.compile(r'[\w/+、，\u4e00-\u9fa5]{8,}')
    info = pattern.findall(info)
    information = ''.join(info)
    return information


def nextUrl(content):
    soup = BeautifulSoup(content, 'lxml')
    next_url = soup.select('#rtNext')[0].attrs['href']
    return next_url


def getPages(content):
    soup = BeautifulSoup(content, 'lxml')
    # 获取总页数
    pages = int(re.compile(r'\d+').search(soup.select('#resultList > div.dw_page > div > div > div > span:nth-child(3)')[0].string).group())
    return pages


def getBars(content):
    soup = BeautifulSoup(content, 'lxml')
    # 获取当前页面总条数
    bars = int((len(soup.find_all(name='span', attrs={'class':'t5'}, recursive=True))) - 1)
    return bars


def save(message):
    try:
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='spiderdb', port=3306)
        # 创建游标
        cursor = db.cursor()
        message = list(message)
        if message[0] != '职位名':
            if '北京' in message[2]:
                message[2] = '北京'
            elif '上海' in message[2]:
                message[2] = '上海'
            elif '广州' in message[2]:
                message[2] = '广州'
            elif '珠海' in message[2]:
                message[2] = '珠海'
            elif '深圳' in message[2]:
                message[2] = '深圳'
            elif '杭州' in message[2]:
                message[2] = '杭州'
            elif '成都' in message[2]:
                message[2] = '成都'
            elif '武汉' in message[2]:
                message[2] = '武汉'
            elif '长沙' in message[2]:
                message[2] = '长沙'
            # 使用execute()执行sql语句
            sql = 'insert into message values("{0}","{1}","{2}","{3}","{4}")'.format(message[0], message[1], message[2], message[3], message[4])
            cursor.execute(sql)
            cursor.connection.commit()
        db.close()
    except Exception as e:
        print(e)
    return None


if __name__ == "__main__":
    url = 'https://search.51job.com/jobsearch/search_result.php?'
    area = input('输入地区代码：')
    content = getResponse(area, url)
    pages = getPages(content)
    for page in range(pages):
        bars = getBars(content)
        for bar in range(4,bars+4):
            message = getInfo(content, bar)
            save(message)
        if page != pages - 1:
            url = nextUrl(content)
            content = getResponse(area, url)

'''
area = {
    '北京': '010000',
    '上海': '020000',
    '广州': '030200',
    '珠海': '030500',
    '深圳': '040000',
    '杭州': '080200',
    '成都': '090200',
    '武汉': '180200',
    '长沙': '190200'
}
'''
