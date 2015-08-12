#coding=utf-8
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import traceback
import MySQLdb
import urllib
import urlparse

querywords = [
                 "suborbital reusable launch vehicle",
                 "suborbital spacecraft vehicle",
                 "suborbital spacecraft spaceplane",
                 "suborbital spacecraft flight",
                 "suborbital spacecraft launch vehicle",
                 "re-entry and hypersonic flight",
                 "high thrust-to-weight",
                 "routine space access",
                 "hypersonic vehicles",
                 "reliable rapid turnaround aircraft",
                 "Reusable first stage",
                 "Reusable Booster System",
                 "Launch demo payload to orbit",
                 "HTHL",
                 "VTHL",
                 "VTVL",
                 "TSTO",
                 "SSTO",
                 "Ground launch",
                 "Air launch",
                 "barge launch",
                 "Sea launch",
                 "Land downrange",
                 "Return to launch site",
                 "Space access aircraft",
                 "Affordable hypersonic aircraft",
                 "Hypersonic test bed",
                 "operationally responsive spacelift",
                 "ORS",
                 "Modular launch",
                 "Integrated RLV Subsystems",
                 "high propellant mass fraction",
                 "rocketback poststaging maneuver",
                 "autonomously controlled trajectory",
                 "Sequential burning",
                 "Staging Point",
                 "aerodynamic environment",
                 "Return to Launch Site",
                 "Aerodynamic layout",
                 "Aerodynamic configuration",
                 "wing tip mounted vertical tails",
                 "aerodynamic environment",
                 "aerodynamic heating",
                 "aerodynamic force",
                 "aerodynamic characteristics",
                 "CFD",
                 "computational fluid dynamics",
                 "wind tunnel testing",
                 "Propulsion systems",
                 "affordable propulsion systems",
                 "Off-the-Shelf propulsion",
                 "Reusable long life affordable propulsion",
                 "non-toxic propellants",
                 "Management of the propellant",
                 "Pumping systems",
                 "RBCC",
                 "TBCC",
                 "Thermal protection systems",
                 "Durable, low-maintenance thermal protection systems",
                 "TPS and Structures",
                 "Metallic TPS",
                 "Composite TPS",
                 "Hybrid TPS",
                 "Active TPS",
                 "Passive TPS",
                 "hot structure",
                 "Durable thermal structures",
                 "Durable thermal protection",
                 "Composite Hot Structures",
                 "Honeycomb Composites",
                 "Aircraft Hot Wash Structures",
                 "stressing heating",
                 "lightweight structures and components",
                 "Composite structures and tanks",
                 "Robust airframe composition",
                 "composite structures",
                 "Affordable Composite Airframe",
                 "Light weight airframe",
                 "high energy airframe",
                 "Monocoque Tank",
                 "Integral load bearing structure",
                 "Tank Structure Integration",
                 "Autonomous Operations",
                 "Adaptive Guidance and Control",
                 "Integrate with Adaptive G&C",
                 "Autonomous Flight Termination System",
                 "Rangeless range space based command control data acquisition",
                 "safe reliable recovery abort",
                 "Inner-loop Control Allocation",
                 "Adaptive Reconfigurable Control",
                 "Outer-loop Adaptive Guidance",
                 "On-line Trajectory Reshaping",
                 "Integrated Systems Health Management",
                 "More failure tolerance",
                 "Integrated Systems Health Management",
                 "Determine real-time system health",
                 "Integrated System Health Monitoring",
                 "Failure Mode Effects Criticality Analysis",
                 "low-manpower ground operations",
                 "Clean pad minimal infrastructure operations",
                 "aircraft-like operations",
                 "Streamlined “clean pad” operations",
                 "reducing infrastructure and manpower requirements",
                 "enabling flight from a wide range of locations",
                 "lean operations",
                 "Aircraft-Like Ops",
                 "Affordable Infrastructure",
                 "Cycle of Prep Launch Recovery and Turnaround within Single Day",
                 "Rapid Turn Reduces Manpower",
                 "Few Facilities Small Crew Size",
                 "Clean pad - rapid throughput",
                 "Ops Control Center – like aircraft",
                 "Containerized payloads",
                 "Standard interfaces processes",
                 "Low man-power aircraft-like operations"
                 ]
createTableSql = 'create table if not exists paperInfo(`article_id` int PRIMARY KEY NOT NULL AUTO_INCREMENT, `title` text,'\
                ' `citedTimes` int , `fromUrl` text , `referenceList` text , `abstract`  text , `keywords` text,'\
                ' `conference` text, `publisher` text, `author` text, `query` varchar(255),'\
                ' `publish_time` text , `current_time` datetime)'
insertSql = 'insert into paperInfo(`title`, `citedTimes`, `fromUrl`,`referenceList`,`abstract`,`keywords`,'\
            ' `conference`,`publisher`, `author`, `publish_time`, `current_time`, `query`)'\
            ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
class PaperInfo():
    """
    封装paper的基本信息，提供保存机制
    """
    def __init__(self):
        self.title = ''
        self.citedTimes = 0
        self.fromUrl = ''
        self.referenceList = []
        self.abstract = ''
        self.keywords = ''
        self.conference= ''
        self.publisher = ''
        self.author= ''
        self.publish_time = ''
        self.current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.query = ''
    def reset(self):
        self.__init__()
    def __str__(self):
        shortTitle = short(self.title)
        shortAbstract = short(self.abstract)
        return '%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s' % \
            ('title',shortTitle , 'citedTimes', self.citedTimes,'fromUrl', self.fromUrl,\
             'referenceList', self.referenceList, 'abstract', shortAbstract, 'keywords', self.keywords, \
             'conference', self.conference, 'publisher', self.publisher, 'author', self.author, \
             'publish_time', self.publish_time, 'current_time', self.current_time, 'query',self.query)
    def toList(self):
        return [self.title, self.citedTimes, self.fromUrl, list2str(self.referenceList), self.abstract , self.keywords , self.conference , \
                self.publisher , self.author , self.publish_time , self.current_time, self.query]
    def saveToMysql(self):
        conn = MySQLdb.connect(host='localhost',user='root',passwd='123123', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('create database if not exists test')
        conn.select_db('test')
        cur.execute(createTableSql)
        value = self.toList()
        print '============'
        print value
        cur.execute(insertSql,value)
        conn.commit()
        cur.close()
        conn.close()
class Status():
    def __init__(self):
        self.query_index = 0
        self.query = ''
        self.resultCount = 0
        self.index = 1
    def reset(self):
        self.__init__()
def short(longString):
    """
    缩短过长的字符串
    """
    return longString[0:30]+' ... '+longString[-31:-1] if len(longString)>60 else longString
def list2str(list):
    return ' !@# '.join(list)
#从形如“Times Cited: 1”中解析出被引用次数
def parseReferenceCount(reference):
    if 'Times Cited: ' not in reference:
        print 'not sci reference'
        return 0
    pos1 = reference.find(': ')
    pos2 = reference.find('(')
    if pos1 == -1:
        return 0
    else:
        return int(reference[pos1+1:pos2])
#选择english,方便解析
def chooseEnglishLanguage(driver):
    languageElement = driver.find_element_by_xpath('//div[1]/div[12]/ul[2]/li[3]/a')
    if languageElement.get_attribute('title') == 'English': return
    languageElement.click()
    englishItem = driver.find_element_by_xpath('//div[1]/div[12]/ul[2]/li[3]/ul/li[3]/a')
    assert englishItem.get_attribute('title') == 'English' , 'ERROR: not english language'
    englishItem.click()
    logging.info('choose english language')

def getReferenceList(driver):
    referenceList = []
    referenceXpath = '//*[@id="records_form"]/div/div/div/div[2]/div[2]/div/div/p[2]'
    reference = driver.find_element_by_xpath(referenceXpath)
    referenceCount = int(reference.text.split(' ')[0])
    logging.info('referenceCount:'+str(referenceCount))
    if referenceCount != 0:
        reference.find_element_by_tag_name('a').click()
        referenceList = parseReference(driver)
        driver.back()
    return referenceList

    
def parseReference(driver):
    # resultCount = int(WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID , 'hitCount.top'))).text)
    resultCount = int(driver.find_element_by_id('hitCount.top').text)
    # pageCount = int(WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID , 'pageCount.top'))).text)
    pageCount = int(driver.find_element_by_id('pageCount.top').text)
    count = 1
    titleList = []
    for pageNum in range(1,pageCount+1):
        items = driver.find_elements_by_class_name('search-results-item')
        for item in items:
            try:
                reference_title = item.find_element_by_class_name('reference-title').text
                titleList.append(reference_title)
            except NoSuchElementException, e:
                logging.warning(item.text)
                logging.warning(e)
            count += 1
            if count>resultCount : break
        #下一页
        nextPage = driver.find_element_by_class_name('paginationNext')
        if nextPage.get_attribute('href') == 'javascript: void(0)':
            break
        nextPage.click()
    for pageNum in range(pageCount-1):
        driver.back()
    return titleList


def nextPage(driver):
    """
    点击到下一页
    """
    try:
        nextPage = driver.find_element_by_class_name('paginationNext')
        if nextPage.get_attribute('href') == 'javascript: void(0)':
            return False
        nextPage.click()
    except NoSuchElementException , e:
        logging.error(traceback.format_exc())
        return False
    except Exception ,e:
        logging.error(traceback.format_exc())
        return False
    return True

def parsePaperInfoDict(driver):
    """
    将论文详情页面中得内容保存到一个字典中
    """
    infoDict = {}
    blocks  = driver.find_elements_by_class_name('block-record-info')
    for block in blocks:
        if not block.is_displayed(): continue
        fr_fields = block.find_elements_by_class_name('FR_field')
        for fr_field in fr_fields:
            if not fr_field.is_displayed(): continue
            fieldContent = fr_field.text
            pos = fieldContent.find(':')
            if pos != -1:
                infoDict[fieldContent[:pos]] = fieldContent[pos+1:].strip()
            else:
                try:
                    title3 = block.find_element_by_class_name('title3').text
                    infoDict[title3] = fieldContent
                except NoSuchElementException , e:
                    logging.error(block.text)
                    logging.error(traceback.format_exc())
    return infoDict


def buildUrl(baseUrl,docID):
    """
    根据baseUrl和当前要下载的docID构造新的url
    """
    url_parts = list(urlparse.urlparse(baseUrl))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query['doc'] = str(docID)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)

def submitForm(driver , query):
    """
    提交表单
    """
    form = driver.find_element_by_name("value(input1)")
    #form = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.NAME, "value(input1)")))
    form.clear()
    form.send_keys(query)
    form.submit()
    logging.info('form submmited')

def clickFirstLink(driver):
    """
    点击第一个结果，进入到paper详情界面，准备循环爬取
    """
    xpath = '//*[@id="RECORD_1"]/div[3]/div[1]/div/a'
    firstResultLink = WebDriverWait(driver,60).until(EC.element_to_be_clickable((By.XPATH , xpath)))
    firstResultLink.click()
    logging.info('click first link done')

