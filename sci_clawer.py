#coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import urllib
import urllib2
from os.path import isfile
from pybloomfilter import BloomFilter
from sci_common import (querywords, PaperInfo, chooseEnglishLanguage, parseReference, parseReferenceCount)
import cPickle as pkl
import logging  

#----------------logger init------------W
logging.basicConfig(level=logging.INFO,
                filename='selenium-sci.log')
formatter = logging.Formatter('%(asctime)s, %(filename)s:%(lineno)d, %(levelname)s: %(message)s')
logging.getLogger('').setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
###--------------main-----------------###

driver = webdriver.Chrome()

filterPath = '/Users/shibo/filter.bloom'
bf = BloomFilter.open(filterPath) if isfile(filterPath) else BloomFilter(1000000, 0.001, filterPath)
logging.info('bloom filter loaded')
#将paper信息保存在paperInfo对象中
paperInfo = PaperInfo()

for index , query in enumerate(querywords):
	logging.info('current query:'+query)
	driver.get('http://apps.webofknowledge.com/')
	chooseEnglishLanguage(driver)
	form = driver.find_element_by_name("value(input1)")
	#form = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.NAME, "value(input1)")))
	form.clear()
	form.send_keys(query)
	form.submit()
	logging.info('form submmited')
	resultCount = int(driver.find_element_by_id('hitCount.top').text)
	logging.info('records in total: '+ resultCount)
	pageCount = int(driver.find_element_by_id('pageCount.top').text)
	logging.info('total page number: ' + pageCount)
	count = 0;

	#一页一页下载
	for pageNum in range(1,pageCount+1):
	    #爬取本页内部链接
	    for i in range(1 , 11):
	        count = count +1
	        if count > resultCount:
	            break
	        xpath = '//*[@id="RECORD_'+ str(count) +'"]/div[3]/div[1]/div/a'
	        paperLink = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,xpath)))
	        #field
	        title = paperLink.text
	        #检查是否已经下载过
	        if title in bf: continue 
	        paperInfo.title = title
	        citedTimes = driver.find_element_by_xpath('//*[@id="RECORD_'+ str(count) +'"]/div[4]/div').text
	        #field
	        paperInfo.citedTimes = parseReferenceCount(citedTimes)
	        paperLink.click()
	        #field
	        paperInfo.fromUrl = driver.current_url#此url可以获取，但无法直接访问，只能从结果列表中点击，因为sci的产生的网页都是动态网页
	        
	        blocks  = driver.find_elements_by_class_name('block-record-info')
	        for block in blocks:
	            try:
	                title3 = block.find_element_by_class_name('title3').text
	                if title3 == 'Abstract':
	                    #field
	                    paperInfo.abstract = block.find_element_by_class_name('FR_field').text
	                elif title3 == 'Conference':
	                    fr_fields = block.find_elements_by_class_name('FR_field')
	                    for fr_field in fr_fields:
	                        fr_label = fr_field.find_element_by_class_name('FR_label').text
	                        if fr_label == 'Conference:':
	                            #field
	                            #此处不能使用fr_field.find_element_by_tag_name('value').text
	                            #因为sci有时产生value标签，有时不产生
	                            paperInfo.conference = fr_field.text[len('Conference:'):]
	                            break
	                elif title3 == 'Keywords' :
	                	paperInfo.keywords = block.find_element_by_class_name('FR_field').text
	               	elif title3 == 'Publisher':
	               		paperInfo.publisher = block.find_element_by_class_name('FR_field').text
	            except NoSuchElementException , e:
	                fr_fields = block.find_elements_by_class_name('FR_field')
	                for fr_field in fr_fields:
	                    fr_label = fr_field.find_element_by_class_name('FR_label').text
	                    if fr_label == 'By:':
	                        #field
	                        paperInfo.author = fr_field.text[4:]
	                    elif fr_label == 'Published:':
	                        #field
	                        paperInfo.publish_time = fr_field.text[len('Published:')+1 : ]
	        #field
	        referenceList = []
	        try:
	            referenceXpath = '//*[@id="records_form"]/div/div/div/div[2]/div[2]/div/div/p[2]/a'
	            reference = driver.find_element_by_xpath(referenceXpath)
	            reference.click()
	            referenceList = parseReference(driver)
	            driver.back()
	        except NoSuchElementException, e:
	            print 'WARNING: no reference'
	        paperInfo.referenceList = referenceList  
	        #field
	        paperInfo.current_time = time.strftime('%Y-%m-%d %H:%M:%S')
	        paperInfo.saveToMysql()
	        bf.add(paperInfo.title)
	        print paperInfo
	        paperInfo.reset()
	        driver.back()
	        print '================'
	    #下一页
	    nextPage = driver.find_element_by_class_name('paginationNext')
	    if nextPage.get_attribute('href') == 'javascript: void(0)':
	        break
	    nextPage.click()
bf.close()
driver.quit()