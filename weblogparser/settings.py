#
# django-weblogparser
#
# Settings
# 

import os
from django.conf import settings
from django.utils.translation import ugettext as _


# log file formats
LOGFILE_FORMAT_COMMON      = 0
LOGFILE_FORMAT_EXTENDED    = 1 
LOGFILE_FORMAT_WITHSESSION = 2

LOGFILE_DEFAULT_FORMAT     = LOGFILE_FORMAT_EXTENDED

LOGFILE_FORMAT_CHOICES = (
    (LOGFILE_FORMAT_COMMON,      _('Common (CLF)')),
    (LOGFILE_FORMAT_EXTENDED,    _('Extended')),
    (LOGFILE_FORMAT_WITHSESSION, _('Extended with session ID')), # custom format for identifying sessions - requires Nginx/Apache log file format tweaking
)

LOGFILE_FORMAT_PATTERNS = {
    LOGFILE_FORMAT_COMMON      : r'(?P<remoteaddr>[\d\.]+) (?P<clientid>\S+) (?P<userid>\S+) \[(?P<timestamp>[^\]]+)\] \"(?P<request>[^\"]+)\" (?P<status>\d+) (?P<bytes>\d+).*',
    LOGFILE_FORMAT_EXTENDED    : r'(?P<remoteaddr>[\d\.]+) (?P<clientid>\S+) (?P<userid>\S+) \[(?P<timestamp>[^\]]+)\] \"(?P<request>[^\"]+)\" (?P<status>\d+) (?P<bytes>\d+) \"(?P<referer>[^\"]+)\" \"(?P<useragent>[^\"]+).*',
    LOGFILE_FORMAT_WITHSESSION : r'(?P<remoteaddr>[\d\.]+) (?P<clientid>\S+) (?P<userid>\S+) \[(?P<timestamp>[^\]]+)\] \"(?P<request>[^\"]+)\" (?P<status>\d+) (?P<bytes>\d+) \"(?P<referer>[^\"]+)\" \"(?P<useragent>[^\"]+) (?P<sessionid>\S+).*',
}

LOGFILE_TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S"

LOGFILE_DEFAULT_FILENAME_REGEX = r"access(.*)\.log"

# extensions for files that we consider to be html responses
# NOTE: the parser will automatically consider directory views,
#       such as /myblog/, as page impressions.
LOGFILE_PAGE_EXTENSIONS = ['htm', 'html']

# list of strings to use to identify bots
LOGFILE_BOTLIST = ['crawl', 'msnbot']

