#coding=utf-8
import time
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
                 "reliable, rapid turnaround aircraft",
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
    def reset(self):
        self.__init__()
    def __str__(self):
        shortTitle = short(self.title)
        shortAbstract = short(self.abstract)
        return '%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s\n%-15s: %s' % \
            ('title',shortTitle , 'citedTimes', self.citedTimes,'fromUrl', self.fromUrl,\
             'referenceList', self.referenceList, 'abstract', shortAbstract, 'keywords', self.keywords, \
             'conference', self.conference, 'publisher', self.publisher, 'author', self.author, \
             'publish_time', self.publish_time, 'current_time', self.current_time)
    def saveToMysql(self):
        print 'save to mysql, not implement yet'

def short(longString):
    """
    缩短过长的字符串
    """
    return longString[0:30]+' ... '+longString[-31:-1] if len(longString)>60 else longString

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
    
def parseReference(driver):
    resultCount = int(driver.find_element_by_id('hitCount.top').text)
    pageCount = int(driver.find_element_by_id('pageCount.top').text)
    count = 1;
    titleList = []
    for pageNum in range(1,pageCount+1):
        items = driver.find_elements_by_class_name('search-results-item')
        for item in items:
            reference_title = item.find_element_by_class_name('reference-title').text
            titleList.append(reference_title)
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
