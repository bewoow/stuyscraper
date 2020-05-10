import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from datetime import datetime as dt

import requests
from urllib.request import urlopen

import logging # TODO: Add logging

url = 'https://www.stuytown.com/api/units?location=fd3cb2d5-ac75-4057-88c1-106ca4d4cb91,79f509f5-2cc0-480c-9886-ac52e6878415'

# Get email account information
with open('email_account_info.txt') as f:
    data = f.readlines()
    smtp_server = data[0].strip()
    smtp_port = int(data[1].strip())
    email_username = data[2].strip()
    email_password = data[3].strip()

# Get email recipients
with open('recipients.txt') as f:
    data = f.readlines()
    email_recipients = [email.strip() for email in data]

def send_email(send_from, send_to, subject, text, email_password, \
    smtp_server = 'smtp.gmail.com', smtp_port = 465):
    try:
        assert isinstance(send_to, list)

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(send_from, email_password)
        server.sendmail(send_from, send_to, msg.as_string())
        server.close()
    except Exception as e:
        print('Something went wrong...')

while True:
    if dt.now().hour in range(6, 9):  #start, stop are integers (eg: 6, 9)
        apts = requests.get(url).json()['result']
        studios = [apt for apt in apts if apt['bedrooms'] == 0]
        one_beds = [apt for apt in apts if apt['bedrooms'] == 1]
        two_beds = [apt for apt in apts if apt['bedrooms'] == 2 or (apt['bedrooms'] == 1 and apt['isflex'] == True)]

        body = 'Hey, check below: \n\n'
        try:
            cheapest_price_studio = sorted(studios, key=lambda x: x['price'])[0]
            print('Lowest price for studio: ${0}'.format(cheapest_price_studio['price']))
            if cheapest_price_studio['price'] < 2500:
                print('{0} sqft'.format(cheapest_price_studio['sqft']))
                print(cheapest_price_studio['absoluteUrl'])

                body += '\tStudio: ${0:d}, {1} sqft, {2}\n\n'.format(cheapest_price_studio['price'], \
                    cheapest_price_studio['sqft'], cheapest_price_studio['absoluteUrl'])
        except IndexError:
            print('No studios available')

        try:
            cheapest_one_bed = sorted(one_beds, key=lambda x: x['price'])[0]
            print('Lowest price for 1-bedroom: ${0}'.format(cheapest_one_bed['price']))
            if cheapest_one_bed['price'] < 3000:
                print('{0} sqft'.format(cheapest_one_bed['sqft']))
                print(cheapest_one_bed['absoluteUrl'])

                body += '\t1-bedroom: ${0:d}, {1} sqft, {2}\n\n'.format(cheapest_one_bed['price'], \
                    cheapest_one_bed['sqft'], cheapest_one_bed['absoluteUrl'])
        except IndexError:
            print('No 1-bedrooms available')

        try:
            cheapest_two_bed = sorted(two_beds, key=lambda x: x['price'])[0]
            bedroom_type = '2-bedroom (flex)' if cheapest_two_bed['isflex'] else '2-bedroom (regular)'
            print('Lowest price for {0}: ${1}'.format(bedroom_type, cheapest_two_bed['price']))
            if cheapest_two_bed['price'] < 3500:
                print('{0} sqft'.format(cheapest_two_bed['sqft']))
                print(cheapest_two_bed['absoluteUrl'])

                body += '\t{0}: ${1:d}, {2} sqft, {3}\n\n'.format(bedroom_type, cheapest_two_bed['price'], \
                    cheapest_two_bed['sqft'], cheapest_two_bed['absoluteUrl'])
        except IndexError:
            print('No 2-bedrooms available')

        subject = 'Stuytown Updates!'
        send_email(email_username, email_recipients, subject, body, email_password, smtp_server, smtp_port)

        time.sleep(60 * 30)  # Minimum interval between task executions (seconds)
    else:
        time.sleep(10)  # The else clause is not necessary but would prevent the program to
