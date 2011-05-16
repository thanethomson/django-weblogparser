#
# django-weblogparser
#
# Command to import one or more web logs.
#

import os
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from weblogparser import parser, settings, models


class Command(BaseCommand):
    """
    The management command to handle web log parser-related function calls.
    """

    option_list = BaseCommand.option_list + (
        make_option('-f', '--filename',
            action='store',
            type='string',
            dest='filename',
            default=None,
            help=_("The name of a single file to parse and import."),
        ),
        make_option('-d', '--directory',
            action='store',
            type='string',
            dest='directory',
            default=None,
            help=_("The directory in which to search for log files."),
        ),
        make_option('-p', '--pattern',
            action='store',
            type='string',
            dest='pattern',
            default=settings.LOGFILE_DEFAULT_FILENAME_REGEX,
            help=_("The regular expression to use when looking for files in the base directory."),
        ),
        make_option('--format',
            action='store',
            type='int',
            dest='format',
            default=settings.LOGFILE_DEFAULT_FORMAT,
            help=_("The log file format to use. Currently available formats: %(formats)s. Default: %(default)s.") % {
                'formats': ', '.join(['%d - %s' % (f[0], f[1]) for f in settings.LOGFILE_FORMAT_CHOICES]),
                'default': settings.LOGFILE_DEFAULT_FORMAT,
            },
        ),
        make_option('--reparse',
            action='store_true',
            dest='reparse',
            default=False,
            help=_("Whether or not to re-parse files that already exist in the database."),
        ),
        make_option('--reset',
            action='store',
            type='string',
            default=None,
            dest='reset',
            help=_("Delete ALL of the log-related data in the database. NOTE: You must specify --reset=ALL for this to work."),
        ),
    )
    
    help = "Web log file parsing/importing functionality"

    def handle(self, *args, **kwargs):
        """
        Command handler for the "metrics" command.
        """

        # if we've got to reset the logs
        if kwargs['reset']:
            if kwargs['reset'] != 'ALL':
                raise CommandError(_("Please specify --reset=ALL in order to perform a full reset of all log data."))

            print _("Resetting all logs...")
            models.LogFilePath.objects.all().delete()
            print _("Done.")
            return

        filename = kwargs['filename']
        if len(args) and os.path.exists(args[0]):
            filename = args[0]

        if filename:
            filename = os.path.abspath(filename)

        if filename is None and kwargs['directory'] is None:
            raise CommandError(_("You must specify either a file to import or a base directory in which to search for files."))

        if filename and not os.path.isfile(filename):
            raise CommandError(_("File %(filename)s does not exist.") % {'filename': filename})

        if filename:
            parser.import_log(filename, kwargs['format'], verbose=int(kwargs['verbosity']) == 2, reparse=kwargs['reparse'])
        else:
            parser.import_logs(kwargs['directory'], kwargs['pattern'], kwargs['format'],
                verbose=int(kwargs['verbosity']) == 2, reparse=kwargs['reparse'])
        
