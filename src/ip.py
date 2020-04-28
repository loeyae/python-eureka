# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

"""
:author:  Zhang Yi <loeyae@gmail.com>
:date:    2020/4/5 14:41
"""
import os
import tempfile
import urllib.request
import smtplib
import json
from email.mime.text import MIMEText
from email.header import Header
from Config import config

url = 'http://httpbin.org/ip'


def get_ip():
    response = urllib.request.urlopen(url)
    js = json.loads(response.read().decode())
    if js['origin']:
        return js['origin']
    return None

def send_mail(ip_address):
    message = MIMEText("当前IP为: {ip}, 服务器：{host}发送".format(ip=ip_address, host=config.IP_ADDRESS), 'plain', 'utf-8')
    message['From'] = Header("loeye <loeye@qq.com>", 'utf-8')  # 发送者
    message['To'] = Header("loeyae", 'utf-8')  # 接收者

    subject = 'IP变更提醒'
    message['Subject'] = Header(subject, 'utf-8')
    sender = "loeye@qq.com"
    receivers = ["loeye@foxmail.com", "5650146@qq.com"]
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect("smtp.qq.com", 587)
        smtpObj.login("loeye@qq.com", "")
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print("Error: 无法发送邮件")


def check_ip(ip):
    tempdir = tempfile.gettempdir()
    temple = os.path.join(tempdir, "ip-txt")
    if not os.path.exists(temple):
        os.mkfifo(temple, 0X777)
    with open(temple, "r+") as f:
        c = f.read()
        if c != ip:
            f.seek(0)
            f.truncate()
            f.write(ip)
            f.close()
            return False
        f.close()
        return True


def main():
    ip = get_ip()
    if ip is None:
        print("got ip failed")
        return

    if not check_ip(ip):
        send_mail(ip)


if __name__ == "__main__":
    main()
