#
# django-weblogparser
#
# Parser
#

import re
import os
from datetime import datetime, tzinfo, timedelta
from django.utils.translation import ugettext as _
from django.db import transaction
from weblogparser.models import LogFilePath, LogFile, LogEntry
from weblogparser import settings




def parse_line(line, pattern=settings.LOGFILE_DEFAULT_FORMAT, params=[]):
    """
    Attempts to parse the specified string as a log file entry,
    returning a dictionary containing the parsed data.
    """

    m = re.compile(pattern).match(line)
    if not m:
        return None
    else:
        return dict([(p, m.group(p)) for p in params])




def parse_log(filename, fmt):
    """
    Parses the specified log file, yielding dictionaries containing
    log file elements as it goes.
    """

    pattern = settings.LOGFILE_FORMAT_PATTERNS[fmt]
    # extract all of the parameters to look for in the given pattern
    params = re.findall(r'\(\?P\<([^\>]+)\>', pattern)

    with open(filename, 'rt') as f:
        for line in f:
            yield parse_line(line, pattern, params)




class Timezone(tzinfo):
    """
    From http://seehuhn.de/blog/52
    """

    def __init__(self, name='+0000'):
        self.name = name
        seconds = int(name[:-2])*3600+int(name[-2:])*60
        self.offset = timedelta(seconds=seconds)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return self.name



def parse_datetime(s):
    """
    Parses the date/time from the given string.
    """

    # first split the string into its two components
    dt, tz = tuple(s.split())

    dt = datetime.strptime(dt, settings.LOGFILE_TIMESTAMP_FORMAT) 
    return dt.replace(tzinfo=Timezone(tz)).astimezone(Timezone('+0000'))




@transaction.commit_manually
def import_log(filename, fmt, verbose=True, reparse=False, progress_lines=10000):
    """
    Attempts to import the specified log, depending on whether it
    has been imported before or not. If it has, and it was completely
    imported, the file will be ignored and the function will return.

    If it has been imported, but it was not imported completely, all
    existing log entries for the file will be deleted and the function
    will attempt to import it again.

    If it has not been imported, it will import the file completely.
    """

    basename = os.path.basename(filename)
    path = os.path.dirname(filename)

    # make sure the file path exists
    log_path, created = LogFilePath.objects.get_or_create(path=path)
    if verbose:
        print _("Log file path: %(path)s (%(status)s)") % {'status': _('created') if created else _('fetched'),
            'path': log_path.path}

    # save the log path
    transaction.commit()

    # make sure the log file exists
    log_file, created = LogFile.objects.get_or_create(path=log_path, filename=basename, fmt=fmt)
    # if the file already existed, but hasn't been parsed completely
    if not created and not log_file.parsed:
        if verbose:
            print _("Deleting incomplete log file entries for %(filename)s") % {'filename': basename}
        log_file.entries.all().delete()

    # commit the deletion
    transaction.commit()

    # if we deliberately want to re-parse the file
    if reparse and not created:
        if verbose:
            print _("Deleting log file entries for %(filename)s to re-parse") % {'filename': basename}
        log_file.entries.all().delete()
        log_file.parsed = None
        log_file.save()

    # commit the log file
    transaction.commit()

    # if the file's already been completely parsed
    if not created and log_file.parsed:
        if verbose:
            print _("Log file %(filename)s already parsed, skipping.") % {'filename': u'%s' % log_file}
        return

    if verbose:
        print _("Parsing log file %(filename)s...") % {'filename': u'%s' % log_file}

    try:
        line_count = 0
        timestamp = None
        # parse the file
        for data in parse_log(filename, fmt):
            if data is None:
                log_file.errors += 1
            else:
                path = data['request'].split()[1]
                path_without_params = path.split('?')[0]
                path_ext_arr = path_without_params.split('.')
                is_page = (len(path_ext_arr) <= 1 or (len(path_ext_arr) > 1 and path_ext_arr[-1].lower() in settings.LOGFILE_PAGE_EXTENSIONS))
                is_robot = False

                timestamp = parse_datetime(data['timestamp'])
                # create the log entry
                log_entry = LogEntry(log_file=log_file,
                    remote_host=data['remoteaddr'],
                    client_id=data['clientid'],
                    user_id=data['userid'],
                    timestamp=timestamp,
                    request=data['request'],
                    path=path,
                    status=data['status'],
                    bytes_returned=int(data['bytes']), 
                )
                if fmt in [settings.LOGFILE_FORMAT_EXTENDED, settings.LOGFILE_FORMAT_WITHSESSION]:
                    log_entry.referer = data['referer']
                    log_entry.user_agent = data['useragent']

                    user_agent = data['useragent'].lower()

                    # run through the bot list
                    for bot in settings.LOGFILE_BOTLIST:
                        if bot in user_agent:
                            is_robot = True
                            break

                if fmt == settings.LOGFILE_FORMAT_WITHSESSION:
                    log_entry.session_id = data['sessionid']

                log_entry.is_page = is_page
                log_entry.is_robot = is_robot

                log_entry.save()

            line_count += 1
            if verbose:
                if line_count % progress_lines == 0:
                    print _("On line %(line)d") % {'line': line_count}
    except:
        transaction.rollback()
        raise

    if verbose:
        print _("%(errors)d errors encountered during processing.") % {'errors': log_file.errors}
    log_file.save()

    if verbose:
        print _("Committing log entries to database...")
    transaction.commit()



def list_dir(folder, regexp=None, return_matches=False):
    """
    Finds all of the entries in the given folder which match the specified
    regular expression.

    If no regular expression is specified, returns all folder contents.
    """

    results = []
    matches = []
    all_contents = os.listdir(folder)

    for f in all_contents:
        name = f.split('/')[-1]
        m = re.match(regexp, name) if regexp else True
        if m:
            results.append(os.path.join(folder, name))
            matches.append(m)

    return (results, matches) if return_matches else results




def import_logs(basepath, pattern, fmt, verbose=True, reparse=False):
    """
    Searches the given base path for files matching the specified pattern
    and attempts to import them.

    The given pattern is to be a regular expression.
    """

    if verbose:
        print _("Parsing for regex pattern:")
        print pattern

    for filename in list_dir(basepath, regexp=pattern):
        import_log(filename, fmt, verbose=verbose, reparse=reparse)


