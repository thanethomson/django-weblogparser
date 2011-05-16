#
# Analytics for django-weblog-parser
#
# Requires panya-analytics
#

from datetime import timedelta
from django.db.models import Count
from analytics.basemetric import BaseMetric
from weblogparser.models import LogEntry


class PageImpressions(BaseMetric):
    """
    A simple page impressions metric, counting the number
    of HTTP status 200 responses from the web server.

    NOTE: This assumes that all the entries in the LogEntry
    table are relevant to this instance.
    """

    uid   = 'pageimpressions'
    title = 'Page Impressions'


    def calculate(self, start_dt, end_dt):
        return LogEntry.objects.filter(status=200, timestamp__gte=start_dt,
            timestamp__lt=end_dt, is_robot=False, is_page=True).count()


    def get_earliest_data_datetime(self):
        try:
            return LogEntry.objects.filter(status=200, is_robot=False, is_page=True).order_by('timestamp')[0].timestamp
        except IndexError:
            return None




class Sessions(BaseMetric):
    """
    Calculates the number of sessions. 
    """

    uid   = 'sessions'
    title = 'Sessions'


    def calculate(self, start_dt, end_dt):
        return LogEntry.objects.filter(status=200, is_robot=False, is_page=True,
            timestamp__gte=start_dt, timestamp__lt=end_dt).aggregate(Count('session_id', distinct=True))['session_id__count']


    def get_earliest_data_datetime(self):
        try:
            return LogEntry.objects.filter(status=200, is_robot=False, is_page=True).order_by('timestamp')[0].timestamp
        except IndexError:
            return None


