NetworkTester
=============

A python console utility to monitor the availability of a website and hosts

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
  
  
Usage
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
