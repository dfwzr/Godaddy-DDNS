#!/usr/bin/env python
# coding=utf-8
#ver:1.0
#by:浮尘青竹
import urllib.request
import json
import re
import time
import configparser
#DNS解析记录的IP地址读入内存，避免反复请求API
global log_ip
def log_NS(text):
    fo = open("gd_ddns.log","a")
    fo.write("##"+time.asctime(time.localtime(time.time()))+"##\n")
    fo.write("NEW IP:"+text+"\n")
    fo.close()
#初始化配置文件，将DNS解析的数据存入本地。
def config_init(): 
    cf = configparser.ConfigParser()
    cf.read("gd_ddns.cfg")
    if "user" in cf :
#初始化配置文件
        if config_get("user","key") == "XXXXXXXXXXXXXXX:XXXXXXXXX" :
            exit("请编辑默认配置文件gd_ddns.cfg中的地址与key后再试")
        """
        暂时不用该功能
        key = ['data','name','ttl','type']
        text = get_NS()
        for i in range(0,4):
            if i ==  0:
                head = "domain"
            elif i == 1:
                head = "dns1"
            elif i == 2:
                head = "dns2"
            elif i == 3:
                head = "dns3"
            if i in cf:
                pass
            else:
                for index in key:
                    config_set(head,index,str(text[i][index]))
            return 2
        """
    else:
        print("配置文件缺失，请选择以下操作：\n1.脚本所在位置新建默认配置文件\n2.输入domain与key值\n")
        while 1:
            a = input("请选择:")
            if a == "1":
                config_set("user","domain","exampel.com")
                config_set("user","key","XXXXXXXXXXXXXXX:XXXXXXXXX")
                config_set("user","ttl","0")
                print("已创建gd_ddns.cfg，请设置[user]中domain与key的值。\n")
                input("按任意建退出")
                exit()
            elif a == "2":
                print("请确保输入的正确性，若输入错误，请在gd_ddns.cfg中修改\n")
                t_url = str(input("输入您的域名[例如abc.com]:"))
                t_key = str(input("输入您的KEY[格式为:XXXXXXXX:XXXXX]:"))
                t_ttl = str(input("输入时间间隔,若输入值为0,则不进行循环:"))
                while 1:
                    b = str(input("确认输入无误(确定并继续/保存并退出/取消并重输)？Y/N/C:"))
                    if b == "Y" or a == "y":
                        config_set("user","domain",t_url)
                        config_set("user","key",t_key)
                        config_set("user","ttl",t_ttl)
                        pass
                    elif b == "n" or a== "N":     
                        config_set("user","domain",t_url)
                        config_set("user","key",t_key)
                        config_set("user","ttl",t_ttl)
                        exit("退出后请编辑gd_ddns.cfg文件")
                    elif b == "c" or a == "C":
                        config_init()

        return 1
    return 0
#读配置文件
def config_get(head,key):
    cf = configparser.ConfigParser()
    cf.read("gd_ddns.cfg")
    has_head = head in cf
    return cf[head][key]
#写入配置文件
def config_set(head,key,value):
    cf = configparser.ConfigParser()
    cf.read("gd_ddns.cfg")
    has_head = head in cf
    if has_head:
        cf.set(head,key,value)
    else:
        cf.add_section(head)
        cf.set(head,key,value)
    cf.write(open("gd_ddns.cfg","w"))
#通过API抓取域名解析配置
def get_NS():
    head = {}
    head['Accept'] = 'application/json'
    head['Content-Type'] = 'application/json'
    head['Authorization'] = "sso-key " + config_get("user","key")
    req = urllib.request.Request("https://api.godaddy.com/v1/domains/"+config_get("user","domain")+"/records",headers = head,method = "GET")
    rsp = urllib.request.urlopen(req)
    code = rsp.getcode()
    text = json.loads(rsp.read())
    text[0]["ttl"] = int(text[0]["ttl"])
    text[1]["ttl"] = int(text[1]["ttl"])
    text[2]["ttl"] = int(text[2]["ttl"])
    text[3]["ttl"] = int(text[3]["ttl"])
    global log_ip
    log_ip = text[0]["data"]
    return text
#通过API将配置写入域名解析
def update_NS(text):   
    head = {}
    head['Accept'] = 'application/json'
    head['Content-Type'] = 'application/json'
    head['Authorization'] = "sso-key " + config_get("user","key")
    req = urllib.request.Request("https://api.godaddy.com/v1/domains/"+config_get("user","domain")+"/records",headers = head,data = json.dumps(text).encode(),method = "PUT")
    rsp = urllib.request.urlopen(req)
    code = rsp.getcode()
    if code == 200:
        log_NS(text[0]["data"])
    else:
        log_NS("failed")
#获取当前公网IP
def get_IP():
    return json.load(urllib.request.urlopen('http://jsonip.com'))['ip']
#主过程
code = config_init()
text = get_NS()
ttl = config_get("user","ttl")
while 1 == 1:
    now_ip = get_IP()
    if log_ip == now_ip:
        pass
    else:
        text[0]["data"] = now_ip
        update_NS(text)
    print("done&wating...")
    if int(ttl) ==0 :
        exit()
    time.sleep(int(ttl))
