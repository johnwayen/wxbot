#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
import time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#设置需要自动回复的微信联系人
global wx_contacts
wx_contacts = [u'六戒',u'Melin']
#微信群设置
global wx_groups
wx_groups = [u'同舟共舞',u'机器人测试群']


class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key


    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            print 'msg:', msg
            if msg['user']['name'] in wx_contacts:
               print 'source:', msg['user']['name']
               self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
            else:
               return;
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            print 'msg:', msg
            if not msg['user']['name'] in wx_groups:
                return;
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    group_name = msg['user']['name']
                    reply = 'to ' + src_name + ': '
                    if msg['user']['name'] in wx_groups:
                        if msg['content']['type'] == 0:  # text message

                            if msg['content']['desc'].find("打卡") == -1:
                                reply += '格式不正确，请重新输入'
                            else:
                                reply += '打卡成功，再接再励！'
                                f=file("logs/clockin.txt","a+")
                                f.write(str(src_name + ':' + msg['content']['desc'] + '\n'))
                                f.close()
                            #打卡记录写入到文件中
                        else:
                            reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                        self.send_msg_by_uid(reply, msg['user']['id'])
                    else:
                        if msg['content']['type'] == 0:  # text message
                            reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        else:
                            reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                        self.send_msg_by_uid(reply, msg['user']['id'])
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 3:  # group img message
            if msg['user']['name'] == wx_groups:
                self.get_msg_img(msg['msg_id'])

#定时任务
    def schedule(self):
        current_time = time.localtime(time.time())
        if((current_time.tm_hour == 23 and current_time.tm_min == 36)):
            self.send_img_msg_by_uid('img/girl/' + bytes(random.randint(1, 19)) + '.jpeg', self.get_user_id('六戒'))
            time.sleep(1)

def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'

    bot.run()


if __name__ == '__main__':
    main()
