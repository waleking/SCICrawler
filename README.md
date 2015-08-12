###description: 
a python crawler to download SCI paper. It store key words in a list , search these words in turn automatically , and then download them.

###feature:
* log current status, and breakpoint recovery
* filter downloaded papers using bloom filter
* fault tolerant as much as I can (there must be many other detail to take care)
* persistence to mysql

###related tools:
selenium, PhantomJS (perfect combination)

###related python modules:
urllib[2], pybloomfilter, cPickle, logging, MySQLdb, urlparse
