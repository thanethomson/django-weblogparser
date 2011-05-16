#
# django-weblog-parser v0.1
#
# Admin
#

from django.contrib import admin
from weblogparser.models import LogFilePath, LogFile, LogEntry


class LogFilePathAdmin(admin.ModelAdmin):
    list_display = ['path']
admin.site.register(LogFilePath, LogFilePathAdmin)


class LogFileAdmin(admin.ModelAdmin):
    list_display = ['path', 'filename', 'created', 'modified', 'errors']
admin.site.register(LogFile, LogFileAdmin)


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'log_file', 'status', 'bytes_returned']
    list_filter = ['status']
admin.site.register(LogEntry, LogEntryAdmin)

