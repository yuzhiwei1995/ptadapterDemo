import ptadapter
import socket

# 监听8000端口用于与本地I2P通信
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',8000))
server.listen(5)
i2pss, addr = server.accept()

# 使用指定的pt
pt_exec = ['/usr/bin/obfs4proxy', '-enableLogging']
state = '/var/run/obfs4-state'
transports = ['obfs4', 'obfs3']

# 获取I2P网桥端的ptserver的ip和监听的端口
# 1. 从I2P配置文件中读取网桥行
file_name = '~/.i2p/router.config'
bridgeline = ''

with open(file_name) as file_obj:
    for line in file_obj:
        if line.find('reseedBridgeLine') >= 0:
            strs = line.split('=')
            if len(strs) != 2:
                raise Exception("Please check the configuration of I2P Bridge line")
            bridgeline = strs[1]
            break
# 2. 解析ip地址,端口和证书
# obfs4 216.105.171.26:21513 2BBBD91BA796441A3C7BB6D3802083153E17C732
items = bridgeline.split(' ')
ptType = items[0]
ipAndPort = items[1].split(':')
ip = ipAndPort[0]
port = ipAndPort[1]
cert = items[2]

async with ptadapter.ClientAdapter(pt_exec, state, transports, proxy=None) as adapter:
    # 链接I2P网桥端的ptserver
    args = {'cert': cert}
    reader, writer = await adapter.open_transport_connection(ptType, ip, port, args)
    # use reader and writer as usual
    while True:
        msg = i2pss.recv(20480)
        # print("Get From I2P:" + repr(msg) + "\r\n")
        writer.send(msg)
        # print "PTClient send data %s to "%repr(msg)
        buf = reader.recv(20480)
        # print("PTClient recv data %s from "%repr(buf))
        i2pss.send(buf)
        # print("Send to I2P:" + repr(buf) + "\r\n")