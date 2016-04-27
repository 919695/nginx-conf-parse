# -*- coding: utf8 -*-
import os
import re


class NProperty(object):
    """
    nginx中的配置项
    key:配置参数名
    value:配置参数值
    note:注释信息，位于配置项右侧否则不会被解析
    """

    def __init__(self):
        self.__propertys = {}
        self.note = None

    def add_property(self, name, value):
        """
        添加一个属性，如果属性存在会添加失败
        """
        if self.__propertys.has_key(name):
            return False
        self.__propertys.setdefault(name, value)
        return True

    def remove_property(self, name):
        """
        删除一个属性,如果属性不存在会删除失败
        """
        if not self.__propertys.has_key(name):
            return False
        del self.__propertys[name]
        return True

    def set_property(self, name, value):
        """
        更新一个属性,如果属性不存在会删除失败
        """
        if not self.__propertys.has_key(name):
            return False
        self.__propertys[name] = value
        return True

    def clear_propertys(self):
        """
        删除所有属性
        """
        self.__propertys.clear()

    def get_property_one(self, name):
        """
        获取单个属性值
        """
        return self.__propertys[name]

    def get_property_all(self):
        """
        获取所有属性
        """
        return self.__propertys


class Location(NProperty):
    """
    nginx http配置中的server配置
    propertys:配置属性集合
    locations:路由集合
    note:注释信息，位于配置项右侧否则不会被解析
    """

    def __init__(self, path='/'):
        super(Location, self).__init__()
        self.path = path
        self.note = None


class Server(NProperty):
    """
    nginx http配置中的server配置
    propertys:配置属性集合
    locations:路由集合
    note:注释信息，位于配置项右侧否则不会被解析
    """

    def __init__(self, server_name):
        super(Server, self).__init__()
        self.server_name = server_name
        self.__locations = {}
        self.note = None

    def add_location(self, location):
        """
        添加一个location，以path为键，如果已存在则失败
        """
        if self.__locations.has_key(location.path):
            return False
        self.__locations[location.path] = location
        return True

    def remove_location(self, path):
        """
        删除一个loacation，以path为键，如果不存在则失败
        """
        if not self.__locations.has_key(path):
            return False
        del self.__locations[path]
        return True

    def update_location(self, location):
        """
        更新一个loacation，以path为键，如果不存在则失败
        """
        if not self.__locations.has_key(location.path):
            return False

    def get_location_one(self, path):
        """
        获取指定loacation
        """
        return self.__locations[path]

    def get_location_all(self):
        """
        获取loacation集合
        """
        return self.__locations

    def cleer_locations(self):
        """
        删除所有location
        """
        self.__locations.clear()


class Upstream(NProperty):
    """
    nginx中的upstream配置项
    name:upstream名字
    propertys:服务器集合
    note:注释信息，位于配置项右侧否则不会被解析
    """

    def __init__(self, name):
        super(Upstream, self).__init__()
        self.name = name
        self.note = None


class Http(NProperty):
    """
    nginx中的http配置
    propertys:配置属性集合
    servers:虚拟机集合
    upstream:负载服务器配置项
    note:注释信息，位于配置项右侧否则不会被解析
    """

    def __init__(self, upstream=None):
        super(Http, self).__init__()
        self.__servers = {}
        self.upstream = upstream
        self.note = None

    def add_server(self, server):
        """
        添加一个server，以server_name为键，如果server已存在则会添加失败
        """
        if self.__servers.has_key(server.server_name):
            return False
        self.__servers[server.server_name] = server
        return True

    def remove_server(self, server_name):
        """
        删除一个server，以server_name为键，如果server不存在则会删除失败
        """
        if not self.__servers.has_key(server_name):
            return False
        del self.__servers[server_name]
        return True

    def update_servers(self, server):
        """
        更新一个server，以server_name为键，如果server不存在则会更新失败
        """
        if not self.__servers.has_key(server.server_name):
            return False
        self.__servers[server.server_name] = server
        return True

    def get_server_one(self, server_name):
        """
        获取指定server
        """
        return self.__servers[server_name]

    def get_server_all(self):
        """
        获取所有server
        """
        return self.__servers

    def clear_servers(self):
        """
        删除所有server
        """
        self.__servers.clear()


class NginxConf(NProperty):
    """
    nginx config配置控制
    """

    def __init__(self):
        super(NginxConf, self).__init__()
        self.events = NProperty()
        self.http = Http()

    def create_new(self):
        """
        创建一个新的nginx配置文件
        """
        self.add_property('worker_processes', '1')
        self.events.add_property('worker_connections', '1024')

        self.http.add_property('include', 'mime.types')
        self.http.add_property('default_type', 'application/octet-stream')
        self.http.add_property('sendfile', 'on')
        self.http.add_property('keepalive_timeout', '65')

        server = Server('location')
        server.add_property('listen', '80')
        server.add_property('error_page', '500 502 503 504  /50x.html')

        location = Location()
        location.add_property('proxy_pass', 'http://location')
        location.add_property('root', 'html')
        location.add_property('index', 'index.html index.htm')
        server.add_location(location)

        location = Location('/50x.html')
        location.add_property('root', 'html')
        server.add_location(location)
        # upstream = Upstream('localhost')
        # upstream.add_property('server', '192.168.0.1')
        # upstream.add_property('server', '192.168.0.2')
        # self.http.upstream = upstream
        self.http.add_server(server)

    def dump(self):
        """
        将nginx conf实体转换为字符
        """
        conf = ''
        # 构建conf的属性项
        for property in self.get_property_all():
            line = '{0} {1};\n'.format(
                property, self.get_property_one(property))
            conf += line
        # 构建conf的events
        events = ''
        for property in self.events.get_property_all():
            line = '{0} {1};\n'.format(
                property, self.events.get_property_one(property))
            events += line

        events = 'events {{\n\t{0}}}\n'.format(events)
        conf += events

        # 构建server
        servers = ''
        for temp_server in self.http.get_server_all():
            temp_server = self.http.get_server_one(temp_server)
            server = ''
            for property in temp_server.get_property_all():
                line = '\t\t{0} {1};\n'.format(
                    property, temp_server.get_property_one(property))
                server += line
            # 构建location
            locations = ''
            for temp_location in temp_server.get_location_all():
                location = ''
                temp_location = temp_server.get_location_one(temp_location)
                for property in temp_location.get_property_all():
                    line = '\t\t\t{0} {1};\n'.format(
                        property, temp_location.get_property_one(property))
                    location += line
                location = '\t\tlocation {0} {{\n{1}\t\t}}\n'.format(
                    temp_location.path, location)
                locations += location

            server = '\tserver {{\n\t\tserver_name {0};\n{1}\n{2}\t}}\n'.format(temp_server.server_name, server,
                                                                                locations)
            servers += server

        # 构建upstream
        upstream = ''
        if self.http.upstream:
            for property in self.http.upstream.get_property_all():
                line = '\t{0} {1};\n'.format(property, self.http.upstream.get_property_one(property))
                upstream += line
            upstream = '\tupstream {0} {{\n\t{1}\t}}\n'.format(self.http.upstream.name, upstream)

        # 构建http
        http = ''
        for property in self.http.get_property_all():
            line = '\t{0} {1};\n'.format(property, self.http.get_property_one(property))
            http += line
        http += upstream
        http += servers
        http = 'http {{\n{0}}}'.format(http)
        conf += http
        print conf

    def load(self, conf_path):
        if not os.path.isfile(conf_path):
            return False
        with open(conf_path) as conf:
            lines = conf.readlines()
        for line in lines:
            if len(line) < 5 and line.find('}') == -1:
                continue
            if line.find('#') > -1:
                continue
            line = line.strip()
            line = line.replace(';', '')
            if line.find('{') == -1 and line.find('}') == -1:
                temp_line = line.split(' ')
                while '' in temp_line:
                    temp_line.remove('')
                if len(temp_line) == 2:
                    temp_doc = '"{0}":"{1}",'.format(temp_line[0], temp_line[1])
                else:
                    temp_doc = '"{0}":"{1}",'.format(temp_line[0], ' '.join(temp_line[1:]))
                print(temp_doc)
            elif line.find('{') > -1:
                temp_line = line.split(' ')
                while '' in temp_line:
                    temp_line.remove('')
                if temp_line[0].lower() == 'upstream':
                    temp_doc = '"upstream":{{"name":"{0}",'.format(temp_line[1])
                elif temp_line[0].lower() == 'location':
                    temp_doc = '"location":{{"path":"{0}",'.format(' '.join(temp_line[1:-1]))
                else:
                    temp_doc = '"{0}":{{'.format(temp_line[0], temp_line[1])
                print(temp_doc)
            else:
                line = line + ','
                print(line)
                # print(line)
        pass

    def __get_center_str(self, left, right, str):
        s = re.compile(left + '(.|[\s\S]*?)' + right).search(str)
        try:
            return s.group(1)
        except:
            return ''


nc = NginxConf()
# nc.create_new()
# nc.dump()
nc.load('nginx.conf')
print('ok!')
