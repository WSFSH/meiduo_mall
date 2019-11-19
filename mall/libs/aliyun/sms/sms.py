#!/usr/bin/env python
# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def send_sms(phone_numbers, code):
    client = AcsClient('uuid', 'secret key', 'cn-hangzhou')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone_numbers)
    request.add_query_param('SignName', "xxxx")
    request.add_query_param('TemplateCode', "SMS_174812907")
    request.add_query_param('TemplateParam', "{\"code\":\"%s\"}" % code)

    response = client.do_action(request)
    response = str(response, encoding='utf-8')
    return response


if __name__ == '__main__':
    ret = send_sms("mobile", "sms_code")
    print(ret)