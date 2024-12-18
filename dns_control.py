import sys
import requests
import hashlib
import json
import warnings

warnings.filterwarnings("ignore")

api_url = 'https://api.west.cn/API/v2/domain/dns/'  # 接口地址
user_name = ''  # 账号
api_password = ''  # api 密码或使用apidomainkey



def format_dns_info(d):
    body = d.get("body", {})
    print(body)
    formatted_info = []
    items = body.get("items", [])
    for item in items:
        hostname = item.get("hostname")
        record_type = item.get("record_type")
        record_value = item.get("record_value")
        record_ttl = item.get("record_ttl")
        formatted_info.append(
            f"\n___________________\n主机名  : {hostname}\n___________________\n记录类型: {record_type}\n___________________\n记录值  : {record_value}\n___________________\nTTL     : {record_ttl}\n___________________\n"
        )
    return formatted_info

class DomainApiUtils:
    def __init__(self, api_url: str, user_name: str = None, api_password: str = None):
        """ 初始化类，用户认证和域名apidomainkey必选其一

        :param api_url  :       接口地址
        :param user_name:       在西部数码的账号
        :param api_password:    SSL的专用api 密码
        """
        self.api_url = api_url
        self.user_name = user_name
        self.api_password = api_password

    
    def get_public_parm(self, apidomainkey: str = None) -> dict:
        """ 获取公共参数 """
        if apidomainkey:
            return {"apidomainkey": apidomainkey}
        if not self.user_name or not self.api_password:
            print("API 认证参数错误, 请选择用户认证或apidomainkey认证。程序退出")
            sys.exit(0)
        __apikey = self.get_convert_md5(self.api_password)
        return {"username": self.user_name, "apikey": __apikey}

    def get_convert_md5(self, __string: str, upper: bool = False) -> str:
        """ 计算字符串md5值 """
        __my_hash = hashlib.md5()
        __my_hash.update(__string.encode('GBK'))
        __hash = __my_hash.hexdigest()
        return __hash.upper() if upper else __hash

    def encode_parm(self, __rep_parm: dict, charset: str = 'GBK') -> dict:
        """ 统一转换参数编码 """
        __encoded_data = {}
        for k, v in __rep_parm.items():
            if isinstance(v, str):
                __encoded_data[k] = v.encode(charset).decode(charset)
            else:
                __encoded_data[k] = v
        return __encoded_data

    def do_api(self, __act_url: str, rep_parm: dict = {}, apidomainkey: str = None, isget: bool = True):
        ''' 调用接口 '''
        __api_url = self.api_url + __act_url if __act_url else self.api_url
        __rep_status, __respon = self.request_act(__api_url, rep_parm, apidomainkey, isget)
        return __rep_status, __respon

    def request_act(self, __url: str, __rep_parm: dict, apidomainkey: str = None, isget: bool = True, timeout: int = 10, charset: str = 'GBK'):
        ''' 发起请求 '''
        try:
            session = requests.Session()
            session.keep_alive = False
            if isget:
                __rep_parm.update(self.get_public_parm(apidomainkey))
                __respon = session.get(__url, params=self.encode_parm(__rep_parm), timeout=timeout)
            else:
                __rep_parm = self.encode_parm(__rep_parm)
                __respon = session.post(__url, data=__rep_parm, params=self.get_public_parm(apidomainkey), timeout=timeout)
            return True, __respon
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def domain_dnsrec_add(self, __domain: str, __record_type: str, __hostname: str, __record_value: str, record_line: str = None, record_ttl: int = 900, record_level: int = None, apidomainkey: str = None):
        """ 域名添加解析 """
        print("############### 添加域名解析    #####################")
        __rep_parm = {
            "act": "dnsrec.add",
            "domain": __domain,
            "record_type": __record_type,
            "hostname": __hostname,
            "record_value": __record_value,
            "record_line": record_line,
            "record_ttl": record_ttl,
            "record_level": record_level,
        }
        __rep_status, __respon = self.do_api(None, __rep_parm, apidomainkey=apidomainkey, isget=False)
        if __rep_status:
            __json_data = __respon.json()
            print(json.dumps(__json_data, indent=4, sort_keys=True))
            if __json_data.get('code') == 200:
                return True, __json_data.get('body').get('record_id')
            else:
                return False, __json_data.get('msg')
        else:
            return False, "请求失败"
            
    def domain_dnsrec_update(self, __domain: str, __record_type: str, __hostname: str, __record_value: str, record_line: str = None, record_ttl: int = 60, record_level: int = None, apidomainkey: str = None):
        """ 域名更新解析 """
        print("############### 更新域名解析    #####################")
        __rep_parm = {
            "act": "dnsrec.modify",
            "domain": __domain,
            "record_type": __record_type,
            "hostname": __hostname,
            "record_value": __record_value,
            "record_line": record_line,
            "record_level": record_level,
        }
        __rep_status, __respon = self.do_api(None, __rep_parm, apidomainkey=apidomainkey, isget=False)
        if __rep_status:
            __json_data = __respon.json()
            print(json.dumps(__json_data, indent=4, sort_keys=True))
            if __json_data.get('code') == 200:
                return True, __json_data.get('body').get('record_id')
            else:
                return False, __json_data.get('msg')
        else:
            return False, "请求失败"

    def domain_dnsrec_list(self, __domain: str, __record_type: str, __hostname: str, __record_value: str, record_line: str = None, record_ttl: int = 60, record_level: int = None, apidomainkey: str = None):
        """ 域名添加解析 """
        print("############### 查询域名解析    #####################")
        __rep_parm = {
            "act": "dnsrec.list",
            "domain": __domain,
            "hostname": __hostname,
        }
        __rep_status, __respon = self.do_api(None, __rep_parm, apidomainkey=apidomainkey, isget=False)
        if __rep_status:
            __json_data = __respon.json()
            print(json.dumps(__json_data, indent=4, sort_keys=True))
            if __json_data.get('code') == 200:
                return True, __json_data.get('body').get('record_id'), __json_data
            else:
                return False, __json_data.get('msg'), {}
        else:
            return False, "请求失败"

__util = DomainApiUtils(api_url, user_name, api_password)

def get_list():
    __status, __body, d = __util.domain_dnsrec_list("YOUR DOMAIN", "RECORD", "SLD", "IP OF TYPE A")
    formatted_dns_info = format_dns_info(d)
    return formatted_dns_info[0]

def update_dns(newip):
    __status, __body = __util.domain_dnsrec_update("YOUR DOMAIN", "RECORD", "SLD", newip)
    
    print( __status)
    return  __status

# print(get_list())
# print(update_dns("192.168.1.1"))

