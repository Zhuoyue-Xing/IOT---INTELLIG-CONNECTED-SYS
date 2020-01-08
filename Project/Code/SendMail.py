import smtplib
from email.mime.text import MIMEText

gmail_user = 'iot2019temp@gmail.com'
gmail_password = 'aleoxwrprndhangm' # your gmail password

msg = MIMEText('Alert: A sensor node collect abnormal data\nTime:\nNode number:\nNode location:\nAbnormal data:\n')
msg['Subject'] = 'Alert: A sensor node collect abnormal data'
msg['From'] = gmail_user
msg['To'] = 'iot2019temp@gmail.com'

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_user, gmail_password)
server.send_message(msg)
server.quit()

print('Email sent!')