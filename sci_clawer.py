#coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import urllib
import urllib2
from os.path import isfile
from pybloomfilter import BloomFilter
from sci_common import (nextPage , querywords, Status, PaperInfo, chooseEnglishLanguage, parseReference)
from sci_common import (parseReferenceCount, parsePaperInfoDict, getReferenceList, buildUrl, submitForm, clickFirstLink)
import cPickle as pkl
import logging  
import traceback

#定义常量
CONST_LIMIT = 2 # 每个query论文爬取上限
#----------------logger init------------W
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s, %(filename)s:%(lineno)d, %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='sci.log')
formatter = logging.Formatter('%(asctime)s, %(filename)s:%(lineno)d, %(levelname)s: %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
###--------------main-----------------###

driver = webdriver.Chrome()

filterPath = 'sci.bloom_filter'
bf = BloomFilter.open(filterPath) if isfile(filterPath) else BloomFilter(1000000, 0.001, filterPath)
logging.info('bloom filter loaded')
#将paper信息保存在paperInfo对象中
paperInfo = PaperInfo()
#status用于记录当前状态
status = Status()
statusPath = 'sci.status'
if isfile(statusPath) :
    status = pkl.load(open(statusPath,'r'))
    logging.info('status loaded')
try:
    #从当前query_index位置开始
    for i in range(status.query_index , len(querywords)):
        #初始化这次query的状态
        status.reset()
        query = querywords[i]
        status.query_index = i ; status.query = query
        #count 用于记录每个query爬取的论文数量，每个query最多爬取100篇
        count = 0
        logging.info('current query:'+'index = '+ str(i) + 'keyword = '+query)
        driver.get('http://apps.webofknowledge.com/')
        chooseEnglishLanguage(driver)
        submitForm(driver , query)
        #点击第一个链接，跳转到详情界面
        resultCount = 0
        try:
            resultCount = driver.find_element_by_id('hitCount.top').text.strip().replace(',', '')
        except NoSuchElementException , e:
            logging.warning('search found no records exception. query = ' + query)
            continue
        status.resultCount = resultCount
        logging.info('resultCount: '+ resultCount)
        if int(resultCount) <= 0 : 
            logging.warning('resultCount = ' + str(resultCount) +'skip this keyword:'+query) 
            continue
        clickFirstLink(driver)
        #baseUrl 是可以直接链接到paper详情的url，形如
        #http://apps.webofknowledge.com/full_record.do?product=UA&doc=100&qid=1&SID=3EoGHDEgjGivYbtN3Pn&search_mode=GeneralSearch&page=1
        #可以修改get参数中得doc构造不同paper的url
        baseUrl = driver.current_url
        #爬取本页内部链接
        for j in range(status.index , int(resultCount) + 1):
            status.index = j
            paperInfo.reset()
            url = buildUrl(baseUrl, j)
            logging.info('url=' + url)
            try:
                driver.get(url)
                title = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[1]').text
                
                #检查是否已经下载过
                if title not in bf:
                    logging.info('processing: <'+title+'>')
                    paperInfo.title = title
                    paperInfo.citedTimes = int(driver.find_element_by_class_name('TCcountFR').text)
                    paperInfo.fromUrl = driver.current_url#此url可以获取，但无法直接访问，只能从结果列表中点击，因为sci的产生的网页都是动态网页
                    infoDict = parsePaperInfoDict(driver)
                    paperInfo.abstract = infoDict.get('Abstract','')
                    paperInfo.conference = infoDict.get('Conference','')
                    paperInfo.keywords = infoDict.get('Author Keywords','')
                    paperInfo.publisher = infoDict.get('Publisher','')
                    paperInfo.author = infoDict.get('By','')
                    paperInfo.publish_time = infoDict.get('Published','')
                    paperInfo.referenceList = getReferenceList(driver)
                    paperInfo.current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    paperInfo.query = query
                    paperInfo.saveToMysql()
                    logging.info('<paper>'+paperInfo.__str__()+'</paper>')
                    bf.add(paperInfo.title)
                else:
                    logging.warning('<'+title+'> contained in bloomFilter')
                count += 1
            except NoSuchElementException , e:
                logging.warning(traceback.format_exc())
            finally:
                if count >= CONST_LIMIT : break
except TimeoutException , e:
    logging.error('timeout exception')
    logging.error(traceback.format_exc())
finally:
    bf.close()
    logging.info('bloom filter closed')
    pkl.dump(status, open(statusPath,'w'))
    logging.info('current status saved')
    # driver.quit()