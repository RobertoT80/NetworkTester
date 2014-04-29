#!C:\Python33\python.exe
intro="""
============================================================================
# Can ping any number of hosts and sends a get request to a website.

  Setup is in: [appfolder]setup.ini
  You can edit it launching "networktester.exe default" then select "e".

  Logs are as many as 5 files, 2 MB maximum, saved in %appfolder%\Log\ 
  They are named: networktester[hostname][username].log

# The website is considered unavailable if the webserver can't be contacted.
  Error if the webserver replies any number other than 200.
  In both cases it sends an alert.

# The hosts are considered unavailable if there's no DNS match
  or if the client has networking issues (i.e. cabling or hardware).
  Instead they are considered OFFLINE if the ping request doesn't anwer back.

# If the website is OFFLINE for 3 times in a row (default: 1:30 mins) sends
  an email including the error in the body and beeps the case for 5 seconds.
  Then it waits for an hour to resets the trigger again.
==============================================================================
"""

# """""""""""""""""""" Imports """"""""""""""""""""

import os, sys 
import time
import threading, queue
import subprocess
import winsound
import requests

import config
import log
import mailutils

# """""""""""""""""""" Log """"""""""""""""""""
mainlog=log.Log('networkTester')

def log(msg, level):
    if level == 'error':
        mainlog.logger.error(msg)
    elif level == 'debug':
        mainlog.logger.debug(msg)
    elif level == 'warn':
        mainlog.logger.warn(msg)
    else:
        mainlog.logger.info(msg)

# """""""""""""""""""" Tester Class """"""""""""""""""""

class Tester(object):
    def __init__(self, polling, reset, threshold):
        """
        
        """

        log('{0} Program started. {0}'.format('=' * 15), 'info')
        log('tester(polling={0}, reset={1}, threshold={2}'.format(polling, reset, threshold), 'debug')

        self.config = config.Config(mainlog.get_attr('ini_path'))
        self.servers, self.host = self.config.read()
        if (len(self.servers)) == 0:
            self.servers = ['localhost']

        self.margin = int([max(len(server) for server in self.servers)][0]) # between server[0] and status[0]
        # configurable args
        self.polling = polling # seconds  to wait for next scan
        self.reset = reset # reset * polling, to reset every hour would be 120*30
        self.threshold = threshold # then sends email and beeps

        self._website_error_count = 0 # reset zeroes it
        self._website_error_count_total = 0
        self._website_unavailable_count = 0
        self._website_unavailable_count_total = 0
        
        self._website_error = None
        self._cycle = 0 # total scan count
		
        """ mail data is currently hardcoded : uncomment and configure
        self.smtpserver = 
        self.mail_from = 
        self.mail_to = 
        self.mailsent, self.mailsent_time, self.mail_error = None, None, None
		"""

        os.system("cls")
        msg = 'Settings read from:\n{0}\n\nServers: {1}\nWebsite: {2}'.format(self.config.inifile, self.servers, self.host)
        print(msg)
        log(msg, 'info')
        print(self.__str__())

    def __repr__(self):
        if (self.polling * self.reset) > 60:
            minutes = (self.polling * self.reset) // 60
            frequency_check = "{0} min".format(minutes)
        else:
            frequency_check = "{0} sec".format(self.polling * self.reset)
        if self.threshold == 1:
            _threshold = "just once"
        else:
            _threshold = "{0} times in a row".format(self.threshold)
        return "Checks every {0} sec, alerts every {1}.\n Website has to be offline {2}.".format(
            self.polling, frequency_check, _threshold)

    def __str__(self):
        return "Polling: {0}, reset: {1}, threshold: {2}\n".format(self.polling, self.reset, self.threshold)
            
    def alert(self, unavailable = False):
        log(" *** alert(unavailable={0})".format(unavailable), 'debug')
        if unavailable == True:
            self.error_content = "Website can't be reached."
            self._website_error ='unavailable'
            
        winsound.Beep(8000, 500)
        mail_log = "Trying to send email to {0} through {1}...".format(self.mail_to, self.smtpserver)
        subject = '{0} {1} '.format(self.host, str(self._website_error))
        mail = mailutils.Mail(self.smtpserver, self.mail_from, self.mail_to, subject, self.error_content)
        result = mail.sendmail()
        self.mailsent_time = time.strftime("%H:%M.%S, %Y-%m-%d")
        result_str = 'Send mail result: {0} '.format(result)
        log(result_str, 'info')
        if isinstance(result, tuple):
            if result[0] == True:
                self.mailsent = True
                log('Mail sent.', 'info')
            else:
                self.mail_error = result[1].errno
                self.mailsent = False
                log(result, 'error')

    def isonlineWebsite(self):
        log(" *** isonlineWebsite()", 'debug')
        self._cycle += 1
        try:
            r = requests.get(self.host)
        except:
            msg = 'unavailable'
            loglevel = 'warn'
            self._website_unavailable_count += 1
            self._website_unavailable_count_total += 1
            if self._website_unavailable_count == self.threshold:
                self.alert(unavailable=True)
        else:
            if r.status_code == 200:
                msg = "online"
                loglevel = 'info'
            else: # full list at requests.status_codes
                self._website_error = r.status_code
                self.error_content = r.content.decode()
                log(self.error_content, 'debug')
                msg = "error, status code = {0}".format(r.status_code)
                loglevel = 'error'
                self._website_error_count += 1
                self._website_error_count_total += 1
                if self._website_error_count == self.threshold:
                    self.alert()
                    
        finally:
            msg = '\n[WEBSITE]\n * "{0}" {1}.\n   Requests: {2} (errors: {3}, unavailable: {4})\n'.format(
                self.host, msg, self._cycle, self._website_error_count_total, self._website_unavailable_count_total)
            
            log(msg, loglevel)
            if self._cycle % self.reset == 0:
                    self._website_error_count = 0
                    self._website_unavailable_count = 0
                    #self.mailsent, self.mailsent_time, self.mail_error = None, None, None
            return msg

    def isonlineServers(self):
        log(" *** isonlineServers()", 'debug')
        cur_time = time.strftime("%Y-%m-%d - %H:%M.%S")
        output = " {0}\n NETWORK MONITOR\n {1}\n {0}\n\n[SERVERS]\n".format('-'*21, cur_time)
        q = queue.Queue()
        
        for server in self.servers:
            p  = Async_ping(q, server, self.margin)
            p.run()
            q.put(p)
            output += p.output + '\n'
            log(p.server + ': ' + p.status, p.loglevel)

        if self.host:
            website_status = self.isonlineWebsite()
            output += website_status

        if self.mailsent:
            output += '   :) Mail sent at {0} because:\n   "{1}" was offline with error {2}.'.format(
                self.mailsent_time, self.host, self._website_error)
        elif self.mailsent == False:
            output += '   :( Could not send email at {0}, error {1}\n   (Website error was: {2})'.format(
                self.mailsent_time, self.mail_error, self._website_error)
        
        for i in range(1,self.polling):
            os.system("cls")
            next_in = "\n\n\n\n ===========\n Next in: {0}  \n ===========\n {1}".format(
                str(self.polling-i), self.__repr__())
            print(output + next_in)
            time.sleep(1)


# """""""""""""""""""" Async_ping Class """"""""""""""""""""

class Async_ping(threading.Thread):
    def __init__(self, queue, server, margin):
        threading.Thread.__init__(self)
        self.queue = queue
        self.server = server
        self.output = "" # pipe output
        self.margin = 14 # hor spacing between hostname[0] and status[0]
        self.status = None
        self.loglevel = None

    def run(self):
        p = subprocess.Popen("ping {} -n 1".format(self.server), stdout=subprocess.PIPE)
        result = str(p.communicate()[0])
        if 'transmit failed' in result:
            self.status = 'unavailable'
            self.loglevel = 'warn'
        elif  ('100% loss' in result) or ('could not find' in result) or ('unavailable' in result):
            self.status = 'OFFLINE'
            self.loglevel = 'error'
        else:
            self.status = 'ONLINE '
            self.loglevel = 'info'
        self.output = " * [{0}]{1}{2}".format(self.server, ' ' * (self.margin - len(self.server)), self.status)

# """""""""""""""""""" Main """"""""""""""""""""

def networktester_help():
    print(intro)

def usage():
    usage="""
============================================================================
 To launch it with the default values type:
 > networktester.exe default

 To customize it run the command with the args (any number of them).
 > networktester.exe [arg] [n]
 Example:
 > networktester.exe polling 30 reset 120 threshold 3

 # Frequency for checks, in seconds:
   polling (default 30, minimum value is 10)
 # Every how many checks it resets:
   reset (default 120)
 # How many times it has to fail for the email and beep to be triggered:
   threshold (default 10)

 For more infos type:
 > networktester.exe more
============================================================================
 """
    print(usage)

def main():

    log(" *** main({0})".format(sys.argv), 'debug')
    object_args = [['polling', 30], ['reset', 120], ['threshold', 3]]
    object_args_names = [arg[0] for arg in object_args]
    if len(sys.argv) == 1:
        usage()
        return
    elif len(sys.argv) == 2:
        arg = sys.argv[-1]
        if arg == 'help':
            usage()
            return
        elif arg == 'more':
            networktester_help()
            return
        elif arg == 'default':
            log('Using default args...', 'info')
        else:
            print('{0} is not a valid argument.\nTo get help: networktester.exe help'.format(arg))
            return
    else:
        args = sys.argv[1:]
        str_args = [arg for arg in args if isinstance(arg, str)]
        for arg in str_args:
            if arg in object_args_names:
                object_args_names = [arg[0] for arg in object_args]
                for name in object_args_names:
                    if arg == name:
                        try:
                            myvalue = args[args.index(arg)+1]
                            myvalue = int(myvalue)
                            if myvalue <= 0:
                                print('Value cannot be zero or negative.\n\nTo get help: networktester.exe help')
                                raise SystemExit
                        except ValueError:
                            print('{0} is not a number.\n\nTo get help: networktester.exe help'.format(myvalue))
                            return
                        except IndexError:
                            print('You did not provide a value for: {0}.\n\nTo get help: networktester.exe help'.format(arg))
                            return
                        except Exception as err:
                            print('Error: {0}'.format(err))
                            return
                        else:
                            if (arg == 'polling') and myvalue < 10:
                                # Polling at least should be 2-3 seconds
                                print('The value for polling is too low, I am forcing it to 10 seconds.\n')
                                myvalue = 10
                                time.sleep(2)
                            object_args[object_args_names.index(arg)][1] = myvalue
                            
    values = [value[1] for value in object_args]
    # Reset cycle can't obviously be smaller than the threshold
    if values[1] < values[2]:
        print('The reset value is smaller than the threshold.\nSetting default values instead.')
        values[1] = 120
        values[2] = 3

    t= Tester(values[0], values[1], values[2])

    start = input('\nType:\n\n"s" to start,\n\n"c" to cancel,\n\n"e" to edit hosts,\n\n"o" to open log.\n\n').lower()

    if start.startswith('e'):
        os.startfile(t.config.inifile)
        print("\n{0} opened.".format(t.config.inifile))
        return
    elif start.startswith('o'):
        os.startfile(mainlog.logfile)
        print("\n{0} opened.".format(mainlog.logfile))
    elif not start.lower().startswith('s'):
        print('\nTo get help: networktester.exe help')
        return
    else:
        while True:
            try:
                t.isonlineServers()
            except KeyboardInterrupt:
                msg = '\nProgram terminated by user at {0}.'.format(time.strftime("%H:%M.%S"))
                print(msg)
                log(msg, 'info')
                raise SystemExit

if __name__ == '__main__':
    main()



    
