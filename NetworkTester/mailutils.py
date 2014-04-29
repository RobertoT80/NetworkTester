import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mail(object):
    def __init__(self, smtpserver, mail_from, mail_to, subject, html_body):
        print(smtpserver, mail_from, mail_to, subject, html_body)
        self.smtpserver = smtpserver
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.subject = subject
        self.html_body = html_body

    def sendmail(self):
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.mail_from
        msg['To'] = self.mail_to
        html_mime = MIMEText(self.html_body, 'html' )
        msg.attach(html_mime)
        try:
            s = smtplib.SMTP(self.smtpserver)
            result = s.sendmail(self.mail_from, self.mail_to, msg.as_string())
            s.quit()
            print(result)
            return (True, 'True')
        except Exception as err:
            msg = "Could not send email: {}".format(err)
            return (False, err)
