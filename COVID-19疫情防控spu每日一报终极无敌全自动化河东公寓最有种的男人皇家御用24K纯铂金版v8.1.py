#! /usr/bin/env python
# coding=utf-8
import os
import requests
from selenium import webdriver
from email.header import Header
from smtplib import SMTP_SSL
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart, MIMEBase
import time
import zhenzismsclient as smsclient  #第三方发短信api模块
import json
import re


def load_info():
    filename = os.path.abspath('.') + '/information.txt'
    global info_str
    with open(filename, 'r', encoding='utf-8-sig') as f:
        info_str = f.read()
        RE = re.sub('\n', '', info_str)  # 导入的info_str有换行符号，用正则表达式代清洗标准格式以便转换成json
    info_json = json.loads(RE)
    global userName, userNum, userPassword, userEmail, userPhone, runTime
    userName = info_json['姓名']
    userNum = info_json['学号']
    userPassword = info_json['密码']
    userEmail = info_json['邮箱']
    userPhone = info_json['手机']
    runTime = info_json['运行时间']




def get_setting_time(runtime):
    return runTime


def get_net_time(position):
    url = 'http://quan.suning.com/getSysTime.do'
    r = requests.get(url)
    now_time_minute = r.json()['sysTime2'][11:-3]
    now_time_second = r.json()['sysTime2'][11:]
    now_time_date = r.json()['sysTime2'][:]
    if position == 'minute':
        return now_time_minute
    if position == 'second':
        return now_time_second
    if position == 'date':
        return now_time_date


def auto_click():
    global driver  # driver = webdriver.Chrome() #设置成了全局变量为的是在捕获异常时候能够调用driver.close()把异常处理掉
    driver = webdriver.Chrome()
    
    delay = 1  # 设置延时时间0.5s
    driver.get('https://hsm.sspu.edu.cn/selfreport/Default.aspx')
    time.sleep(delay)  # 为保证网络通性不畅导致自动化失败因此设置延时以提高成功率
    driver.find_element_by_id('username').send_keys(userNum)
    time.sleep(delay)
    driver.find_element_by_name('password').send_keys(userPassword)
    time.sleep(delay)
    driver.find_element_by_class_name('submit_button').click()
    time.sleep(delay)
    driver.find_element_by_xpath('//*[@id="form1"]/div[6]/ul/li[1]/a/div').click()
    time.sleep(delay)
    driver.find_element_by_class_name('f-btn-text').click()
    time.sleep(delay)
    driver.find_element_by_id('fineui_33').click()
    time.sleep(delay)
    driver.find_element_by_id('fineui_38').click()  # .id('fineui_38')
    time.sleep(delay)
    driver.find_element_by_xpath('//*[@id="form1"]/div[6]/ul/li[2]/a/div').click()
    filename_screenshot = os.path.abspath('.') + 'screenshot.png'
    driver.get_screenshot_as_file('screenshot.png')
    driver.close()


def send_email_successful():
    # qq邮箱smtp服务器
    host_server = 'smtp.qq.com'
    host_port = '465'
    # sender_qq为发件人的qq号码
    sender_qq = '填写QQ号'
    # pwd为qq邮箱的授权码
    pwd = '填写授权码'  # qq授权码
    # 发件人的邮箱
    # 有三种填写方式，经测试，要在web端和app端同时正常显示昵称和发件人，请使用第三种方法
    # sender_qq_mail = '1640891173@qq.com'
    # sender_qq_mail = '发件人昵称 <1640891173@qq.com>'
    sender_qq_mail = formataddr(["你的邮箱昵称", "填写邮箱号@qq.com"])  # [昵称,邮箱]格式
    # 收件人邮箱
    receiver = f'{userEmail}'
    
    mail_object = '你好呀小可爱~这是你的自动化每日一报程序结果报告，mua~'
    
    # ssl登录
    smtp = SMTP_SSL(host_server, host_port)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)
    
    def load_image(path, cid):
        data = open(path, 'rb')
        message_img = MIMEImage(data.read())
        data.close()
        
        # 给图片绑定cid，将来根据这个cid的值，找到标签内部对应的img标签。
        message_img.add_header('Content-ID', cid)
        
        # 返回MIMEImage的对象，将该对象放入message中
        return message_img
    
    # 实例化邮件对象为多功能对象
    message = MIMEMultipart()  # 默认'related'
    #     '''邮件类型为”multipart/alternative”的邮件正文中包括纯文本正文（text/plain）和超文本正文（text/html）。
    # 邮件类型为”multipart/related”的邮件正文中包括图片，声音等内嵌资源。
    # 邮件类型为”multipart/mixed”的邮件包含附件，图片，文本等都可以添加，所以发的内容多的话一般是用这个的，选择mixed类型，什么内容都可以发。
    #     '''
    
    # 发送内容是html的邮件，邮件中含有图片。
    # 参数2：指定邮件内容类型，默认是plain，表示没有任何格式的纯文本内容。
    now_time = get_net_time('date')
    chr12288 = chr(12288)  # 中文空格chr(122880)或者'\u3000'
    mail_content = MIMEText(f'<h3>{now_time}成功</h3>'
                            f'<p>{chr12288}{chr12288}亲爱的{userName}小可爱，很开心地通知你，你的自动签到我已经帮你签到好了哦(｡･ω･｡)ﾉ♡  帮你节省的宝贵时间记得用来想我吖，爱你么么哒😘mua~</p>'
                            '<img src="cid:images">', 'html', 'utf8')
    
    # 2> 需要将message_html对象，添加至message中，等待被发送。
    message.attach(mail_content)
    # 向img标签中指定图片
    path = os.path.abspath('.') + '/img1.jpg'
    message.attach(load_image(path, 'images'))
    
    path = os.path.abspath('.') + '/screenshot.png'
    message.attach(load_image(path, 'images_screenshot'))
    
    message["Subject"] = Header(mail_object, 'utf-8')
    message["From"] = sender_qq_mail
    message["To"] = receiver
    smtp.sendmail(sender_qq_mail, receiver, message.as_string())
    smtp.quit()
    print('每日一报成功后发送成功邮件模块运行成功！')


def send_email_failed():
    # qq邮箱smtp服务器
    host_server = 'smtp.qq.com'
    host_port = '465'
    # sender_qq为发件人的qq号码
    sender_qq = '填写QQ号'
    # pwd为qq邮箱的授权码
    pwd = '填写授权码'  # qq授权码
    # 发件人的邮箱
    # 有三种填写方式，经测试，要在web端和app端同时正常显示昵称和发件人，请使用第三种方法
    # sender_qq_mail = '1640891173@qq.com'
    # sender_qq_mail = '发件人昵称 <1640891173@qq.com>'
    sender_qq_mail = formataddr(["你的邮箱昵称", "填写邮箱号@qq.com"])  # [昵称,邮箱]格式
    # 收件人邮箱
    receiver = f'{userEmail}'
    
    mail_object = '你好呀小可爱~这是你的自动化每日一报程序结果报告，mua~'
    
    # ssl登录
    smtp = SMTP_SSL(host_server, host_port)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)
    
    def load_image(path, cid):
        data = open(path, 'rb')
        message_img = MIMEImage(data.read())
        data.close()
        
        # 给图片绑定cid，将来根据这个cid的值，找到标签内部对应的img标签。
        message_img.add_header('Content-ID', cid)
        
        # 返回MIMEImage的对象，将该对象放入message中
        return message_img
    
    # 实例化邮件对象为多功能对象
    message = MIMEMultipart()  # 默认'related'
    #     '''邮件类型为”multipart/alternative”的邮件正文中包括纯文本正文（text/plain）和超文本正文（text/html）。
    # 邮件类型为”multipart/related”的邮件正文中包括图片，声音等内嵌资源。
    # 邮件类型为”multipart/mixed”的邮件包含附件，图片，文本等都可以添加，所以发的内容多的话一般是用这个的，选择mixed类型，什么内容都可以发。
    #     '''
    
    # 发送内容是html的邮件，邮件中含有图片。
    # 参数2：指定邮件内容类型，默认是plain，表示没有任何格式的纯文本内容。
    now_time = get_net_time('date')
    chr12288 = chr(12288)  # 中文空格chr(122880)或者'\u3000'
    mail_content = MIMEText(f'<h3>{now_time}失败</h3>'
                            f'<p>{chr12288}{chr12288}亲爱的{userName}小可爱，不好意思呀 今天帮你的签到没签成功，你自己签到一下可以嘛|･ω･｀)   你别不开心惹，我送你花花 呐~😊</p>'
                            '<img src="cid:images">', 'html', 'utf8')
    
    # 2> 需要将message_html对象，添加至message中，等待被发送。
    message.attach(mail_content)
    # 向img标签中指定图片
    path = os.path.abspath('.') + '/img2.jpg'
    message.attach(load_image(path, 'images'))
    
    path = os.path.abspath('.') + '/screenshot.png'
    message.attach(load_image(path, 'images_screenshot'))
    
    message["Subject"] = Header(mail_object, 'utf-8')
    message["From"] = sender_qq_mail
    message["To"] = receiver
    smtp.sendmail(sender_qq_mail, receiver, message.as_string())
    smtp.quit()
    print('每日一报失败后发送失败邮件模块运行成功！')


def send_SMS_successful():
    apiUrl = 'https://sms_developer.zhenzikj.com' #榛子云短信apiUrl'https://sms_developer.zhenzikj.com' 官网http://smsow.zhenzikj.com/
    appId = '账号授权id'
    appSecret = '账号授权码'
    client = smsclient.ZhenziSmsClient(apiUrl, appId, appSecret);
    now_time = get_net_time('date')
    # message = f'|{now_time}|成功|亲爱的{userName}同学，您好。很郑重地通知您，您的自动签到已完成！'
    message = f'亲爱的{userName}小可爱，很开心地通知你，你的自动签到我已经帮你签到好了哦(｡･ω･｡)ﾉ♡  帮你节省的宝贵时间记得用来想我吖，爱你么么哒😘mua~\n更多详情请登入邮箱查看叭~'
    phone_number = f'{userPhone}'
    params = {'message': message, 'number': phone_number};
    result = client.send(params);
    print('每日一报成功后发送成功短信模块运行成功！')


def send_SMS_failed():
    apiUrl = 'https://sms_developer.zhenzikj.com'
    appId = '104633'
    appSecret = '0f0a6eff-9773-4385-af58-4eac50c31fc1'
    client = smsclient.ZhenziSmsClient(apiUrl, appId, appSecret);
    now_time = get_net_time('date')
    # message = f'|{now_time}|成功|亲爱的{userName}同学，您好。很郑重地通知你，您的自动签到未完成！请您登陆电脑端查看具体结果，谢谢！'
    message = f'亲爱的{userName}小可爱，不好意思呀 今天帮你的签到没签成功，你自己签到一下可以嘛|･ω･｀)   你别不开心惹，我送你花花 🌹呐~😊\n更多详情请登入邮箱查看叭~'
    phone_number = f'{userPhone}'
    params = {'message': message, 'number': phone_number};
    result = client.send(params);
    print('每日一报失败后发送失败短信模块运行成功！')


def main():  # 主程序
    load_info()
    flag_successful = 0
    count_failed = 0

    print('程序正在执行中...')
    while True:
        try:
            now_time = get_net_time('minute')
            time.sleep(0.2)  # 延时1s获取api时间，以减少对api的访问
            
            if now_time == get_setting_time(runTime):  # 此处设置每天定时的时间
                if flag_successful == 0:  # 成功并且第一次成功，继续执行auto_click()并发送短信
                    auto_click()
                    flag_successful = 1
                    print('签到模块运行成功！')
                    send_email_successful()
                    send_SMS_successful()
                    now_time = get_net_time('second')
                    print('您在{0}每日一报自动报送成功！'.format(now_time))
                    print('\r您在GMT+08:00中国标准时间{0}每日一报自动报送成功！ 请勿关闭窗口，等待次日报送...'.format(now_time), end='')
                if flag_successful == 1:
                    now_time = get_net_time('second')
                    print('\r当前时间:GMT+08:00中国标准时间{0}每日一报自动报送成功！ 请勿关闭窗口，等待次日报送...'.format(now_time), end='')
        
        
        
        except:
            flag_failed = 1
            count_failed = count_failed + 1
            count_print = 0
            
            driver.close()
            
            if flag_failed == 1 and count_failed <= 2:
                now_time = get_net_time('second')
                if count_print < 2:
                    count_print = count_print + 1
                    print(
                        'GMT+08:00中国标准时间{0} 第{1}次报送失败，正在进行第{2}次尝试...'.format(
                            now_time, count_failed, count_failed + 1))
                if count_print == 2:
                    print(
                        '\rGMT+08:00中国标准时间{0} 第{1}次报送失败。'.format(
                            now_time, count_failed), end='')
            if count_failed == 3:
                now_time = get_net_time('second')
                print(
                    '\rGMT+08:00中国标准时间{0} 第3次报送失败。'.format(
                        now_time))
                send_email_failed()
                send_SMS_failed()
            
            if count_failed > 2:
                while True:
                    time.sleep(0.2)
                    now_time = get_net_time('date')
                    print(
                        '\r当前时间:GMT+08:00中国标准时间{0} 今日3次报送都失败，请您手动签到。不需要重启程序，次日及之后的自动签到不会受影响。'.format(
                            now_time), end='')


if __name__ == '__main__':
    main()
