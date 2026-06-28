#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 设备类型定义
MV_UNKNOW_DEVICE           = 0x00000000  # 未知设备类型，保留意义
MV_GIGE_DEVICE             = 0x00000001  # GigE 设备
MV_1394_DEVICE             = 0x00000002  # 1394-a/b 设备
MV_USB_DEVICE              = 0x00000004  # USB 设备
MV_CAMERALINK_DEVICE       = 0x00000008  # CameraLink 设备
MV_VIR_GIGE_DEVICE         = 0x00000010  # 虚拟 GigE 设备
MV_VIR_USB_DEVICE          = 0x00000020  # 虚拟 USB 设备
MV_GENTL_GIGE_DEVICE       = 0x00000040  # 自研网卡下 GigE 设备
MV_GENTL_CAMERALINK_DEVICE = 0x00000080  # CameraLink 设备
MV_GENTL_CXP_DEVICE        = 0x00000100  # CoaXPress 设备
MV_GENTL_XOF_DEVICE        = 0x00000200  # XoF 设备

# 采集卡类型
MV_GIGE_INTERFACE       = 0x00000001 # GigE Vision采集卡
MV_CAMERALINK_INTERFACE = 0x00000004 # Camera Link采集卡
MV_CXP_INTERFACE        = 0x00000008 # CoaXPress采集卡
MV_XOF_INTERFACE        = 0x00000010 # XoFLink采集卡


INFO_MAX_BUFFER_SIZE   = 64  # 最大的数据信息大小

MV_MAX_TLS_NUM         = 8   # 最多支持的传输层实例个数
MV_MAX_DEVICE_NUM      = 256 # 最大支持的设备个数

MV_MAX_INTERFACE_NUM   = 64  # 最大支持的采集卡数量

MV_MAX_SERIAL_PORT_NUM = 64  # 最大支持的串口数量

MV_MAX_GENTL_IF_NUM    = 256 # 最大支持的 GenTL 数量
MV_MAX_GENTL_DEV_NUM   = 256 # 最大支持的 GenTL 设备数量

# 设备的访问模式
# 独占权限，其他 APP 只允许读CCP寄存器
MV_ACCESS_Exclusive                          = 1
# 可以从5模式下抢占权限，然后以独占权限打开
MV_ACCESS_ExclusiveWithSwitch                = 2
# 控制权限，其他 APP 允许读所有寄存器
MV_ACCESS_Control                            = 3
# 可以从 5 的模式下抢占权限，然后以控制权限打开
MV_ACCESS_ControlWithSwitch                  = 4
# 以可被抢占的控制权限打开
MV_ACCESS_ControlSwitchEnable                = 5
# 可以从5的模式下抢占权限，然后以可被抢占的控制权限打开
MV_ACCESS_ControlSwitchEnableWithKey         = 6
# 读模式打开设备，适用于控制权限下
MV_ACCESS_Monitor                            = 7

MV_MATCH_TYPE_NET_DETECT = 0x00000001  # 网络流量和丢包信息              \~english Network traffic and packet loss information
MV_MATCH_TYPE_USB_DETECT = 0x00000002  # host接收到来自U3V设备的字节总数 \~english The total number of bytes host received from U3V device

# GigEVision IP配置
MV_IP_CFG_STATIC = 0x05000000  # 静态
MV_IP_CFG_DHCP   = 0x06000000  # DHCP
MV_IP_CFG_LLA    = 0x04000000  # LLA

# GigEVision 网络传输模式
MV_NET_TRANS_DRIVER = 0x00000001  # < \~chinese 驱动
MV_NET_TRANS_SOCKET = 0x00000002  # < \~chinese Socket

# CameraLink 波特率（Baud Rates） (CLUINT32)
MV_CAML_BAUDRATE_9600    = 0x00000001  # 9600
MV_CAML_BAUDRATE_19200   = 0x00000002  # 19200
MV_CAML_BAUDRATE_38400   = 0x00000004  # 38400
MV_CAML_BAUDRATE_57600   = 0x00000008  # 57600
MV_CAML_BAUDRATE_115200  = 0x00000010  # 115200
MV_CAML_BAUDRATE_230400  = 0x00000020  # 230400
MV_CAML_BAUDRATE_460800  = 0x00000040  # 460800
MV_CAML_BAUDRATE_921600  = 0x00000080  # 921600
MV_CAML_BAUDRATE_AUTOMAX = 0x40000000  # 自动最大值

# \~chinese 异常消息类型    \~english Exception message type
MV_EXCEPTION_DEV_DISCONNECT = 0x00008001  # 设备断开连接
MV_EXCEPTION_VERSION_CHECK  = 0x00008002  # SDK与驱动版本不匹配

MAX_EVENT_NAME_SIZE     = 128 # 设备Event事件名称最大长度
MV_MAX_XML_SYMBOLIC_NUM = 64  # 最大XML符号数
MV_MAX_SYMBOLIC_LEN     = 64  # 最大枚举条目对应的符号长度

MV_MAX_SPLIT_NUM        = 8   # 分时曝光时最多将源图像拆分的个数
