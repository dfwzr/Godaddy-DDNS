#!/usr/bin/env python
# coding=utf-8
import urllib.request
import json
import re
import time

api_url = 'https://api.godaddy.com/v1/domains/dfwzr.com/records'
#获取log结尾ip地址
def get_IP():                                                                                                   
    fo = open("/home/wzr/ddns.log","rb")
    fo.seek(-18, 2)
    str = bytes.decode(fo.read(18))
    ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", str)[0]
    fo.close()
    return ip

#写入log新ip
def log_NS(ip):
    fo = open("/home/wzr/ddns.log","a")
    fo.write("--"+time.asctime(time.localtime(time.time()))+"--\n")
    fo.write(ip)
    fo.close()

#网络获取外网ip
def cg_NS():
    return json.load(urllib.request.urlopen('http://jsonip.com'))['ip']

#api获取当前解析数据
def get_NS(api_url):
#    print("Get start")
    ip_addr = cg_NS()
    ip_log = get_IP()
    if ip_addr  == ip_log:
#        print("log = now")
        return 1
    print("IP:",ip_addr)
    head = {}

    head['Accept'] = 'application/json'

    head['Content-Type'] = 'application/json'
#ote-key
#    head['Authorization'] = 'sso-key 3mM44UaBuj8ira_9TMcNM8REbkkQ2UWGwvP7u:9TMhrXKbFXtSu7SpoTnztw'
#key
    head['Authorization'] = 'sso-key e4MxmNsHkYxf_JcBkeaEB3i2xxtYELhhMvK:JcBq3SuVPtbrYD6bFh2ejd'


    req = urllib.request.Request(api_url,headers = head,method = "GET")
    rsp = urllib.request.urlopen(req)
    code = rsp.getcode()
    text = json.loads(rsp.read())
#    print(text)
    flag = False
    for tmptext in text:
        if tmptext['data'] == ip_addr:
            flag = True
            break
    if flag:
#        print("no need to change")
#        log_NS("nothing to do\n")
        return 2
    else:
        print("测试与记录不符，更新记录中……")
        update_NS(api_url,ip_addr)
#        log_NS("--"+time.asctime(time.localtime(time.time()))+"--\n")
        log_NS("Last dns:"+ip_addr+"\n")
        return 100
    print("end")
    if code == 200:
        pass
#        print("ok")
    else:
        log_NS("\nfail\n")

#api更新解析数据
def update_NS(api_url,ip_addr):
#    print("Put start")
    head = {}

    head['Accept'] = 'application/json'

    head['Content-Type'] = 'application/json'
#ote-key
#    head['Authorization'] = 'sso-key 3mM44UaBuj8ira_9TMcNM8REbkkQ2UWGwvP7u:9TMhrXKbFXtSu7SpoTnztw'
#key
    head['Authorization'] = 'sso-key e4MxmNsHkYxf_JcBkeaEB3i2xxtYELhhMvK:JcBq3SuVPtbrYD6bFh2ejd'
    
    records_a = {
        "data" : ip_addr,
        "name" : "@",
        "ttl" : 600,
        "type" : 'A',
    }

    records_NS01 = {
        "data" : "ns59.domaincontrol.com",
        "name" : "@",
        "ttl" : 3600,
        "type" : 'NS',
    }


    records_NS02 = {
        "data" : "ns60.domaincontrol.com",
        "name" : "@",
        "ttl" : 3600,
        "type" : 'NS',
    }

    put_data = [records_a,records_NS01,records_NS02]
    req = urllib.request.Request(api_url,headers = head,data = json.dumps(put_data).encode(),method = "PUT")
    rsp = urllib.request.urlopen(req)
    code = rsp.getcode()
    if code == 200:
        pass
#        print("ok")
    else:
        log_NS("\nfail\n")

#主循环
while 1==1:
    print("自动解析开始测试……")
    i = get_NS(api_url)
    if i == 1:
        print("log与实际一致")
    elif i == 2:
        print("测试与解析一致")
    elif i == 100:
        print("更新成功！")
    print("10分钟后重新测试……")
    time.sleep(600)
