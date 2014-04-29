NetworkTester
=============

A python console utility to monitor the availability of a website and hosts

============================================================================
# Can ping any number of hosts and one website. 
  May be useful in an enterprise to test the availability of the most important servers 
  and of the corporate website. Mail configuration data is hardcoded for now.

# Setup is in: [appfolder]setup.ini
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
