import numpy
import cv2
import ctypes
from . import MvImport

不回显信息 = False

def 获取海康设备列表():
	设备列表 = MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO_LIST()
	检索类别 = MvImport.MvCameraControl_class.MV_GIGE_DEVICE
	检索类别 = 检索类别 | MvImport.MV_USB_DEVICE
	检索成败 = MvImport.MvCameraControl_class.MvCamera.MV_CC_EnumDevices(检索类别, 设备列表)
	if (检索成败 != 0):
		raise Exception("检索设备失败，失败代码：0x{:x}".format(检索成败))
	elif(设备列表.nDeviceNum == 0):
		raise Exception("检测到 0 台设备，请确认设备正确连接")
	else:
		设备数量 = 设备列表.nDeviceNum
		if not(不回显信息):
			print("检索到 {} 台摄像头".format(设备数量))
		所有设备 = []
		for 设备编号 in range(0, 设备数量):
			设备信息数据 = 设备列表.pDeviceInfo[设备编号]
			信息结构体指针类型 = ctypes.POINTER(MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO)
			设备信息 = ctypes.cast(设备信息数据, 信息结构体指针类型).contents
			所有设备.append(设备信息)
		return 设备数量, tuple(所有设备)

def 获取设备型号(设备信息: MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO):
	设备型号 = "".join(map(chr,设备信息.SpecialInfo.stGigEInfo.chModelName))
	设备型号 = 设备型号.strip()
	return 设备型号

def 获取IP信息(设备信息: MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO):
	if 设备信息.nTLayerType==MvImport.MvCameraControl_class.MV_GIGE_DEVICE:
		设备IP地址 = 设备信息.SpecialInfo.stGigEInfo.nCurrentIp
		return 设备IP地址
	else:
		return None

def 打开摄像机(设备信息: MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO):
	摄像机对象 = MvImport.MvCameraControl_class.MvCamera()
	创建成败 = 摄像机对象.MV_CC_CreateHandle(设备信息)
	if (创建成败 != 0):
		print("摄像机对象创建失败")
		raise ValueError("摄像机对象创建失败，失败代码：0x{:x}".format(创建成败))
	else:
		if not(不回显信息):
			print("摄像机对象创建成功")
	打开成败 = 摄像机对象.MV_CC_OpenDevice(MvImport.MvCameraControl_class.MV_ACCESS_Exclusive, 0)
	if (打开成败 != 0):
		print("摄像机对象打开失败，失败代码：0x{:x}".format(打开成败))
		raise ValueError("摄像机对象打开失败，失败代码：0x{:x}".format(打开成败))
	else:
		if not(不回显信息):
			print("摄像机对象打开成功")
	return 摄像机对象

def 综合设置(摄像机对象:MvImport.MvCameraControl_class.MvCamera, 曝光毫秒数:float = 50, 增益:float = 20):
	# 网络包大小设置
	网络包大小 = 摄像机对象.MV_CC_GetOptimalPacketSize()
	if (int(网络包大小)>0):
		设定成败 = 摄像机对象.MV_CC_SetIntValue("GevSCPSPacketSize", 网络包大小)
		if (设定成败 != 0):
			print("Warning: 设定包大小失败，失败代码：0x{:x}".format(设定成败))
			return 设定成败
		else:
			if not(不回显信息):
				print("成功设定包大小为{}".format(网络包大小))
	else:
		if not(不回显信息):
			print("Warning: 包大小获取失败，失败代码：0x{:x}".format(网络包大小))

	# 设定触发模式为 off
	设定成败 = 摄像机对象.MV_CC_SetEnumValue("TriggerMode",MvImport.MvCameraControl_class.MV_TRIGGER_MODE_OFF)
	if (设定成败 != 0):
		print("Warning: 设定触发模式失败，失败代码：0x{:x}".format(设定成败))
	else:
		if not(不回显信息):
			print("成功设定触发模式为 off")
	# 设定颜色为转化方式（0：快速，有锯齿；1：适中；2：速度慢，效果好）
	设定成败 = 摄像机对象.MV_CC_SetBayerCvtQuality(2)
	if (设定成败 != 0):
		print("Warning: 设定颜色转化模式失败，失败代码：0x{:x}".format(设定成败))
	else:
		if not(不回显信息):
			print("成功设定颜色转化为 0 号模式")
	# 设定曝光时间为 50 ms
	设定成败 = 摄像机对象.MV_CC_SetFloatValue("ExposureTime", 曝光毫秒数*1000.0)
	if (设定成败 != 0):
		print("Warning: 设定曝光时间失败，失败代码：0x{:x}".format(设定成败))
	else:
		if not(不回显信息):
			print("成功设定曝光时间为 {} ms,即 {} s".format(曝光毫秒数, 曝光毫秒数/1000))
	# 设定增益为 20
	设定成败 = 摄像机对象.MV_CC_SetFloatValue("Gain", 增益)
	if (设定成败 != 0):
		print("Warning: 设定增益设置失败，失败代码：0x{:x}".format(设定成败))
	else:
		if not(不回显信息):
			print("成功设定增益转化为 {}".format(增益))

# 若数据存在多组，采用 nCurValue 对应的数值为准
def 获取数据(摄像机对象:MvImport.MvCameraControl_class.MvCamera, 数据名称:str):
	match(数据名称):
		case "网络包大小":
			网络包大小 = MvImport.MvCameraControl_class.MVCC_INTVALUE()
			ctypes.memset(ctypes.byref(网络包大小), 0, ctypes.sizeof(MvImport.MvCameraControl_class.MVCC_INTVALUE))
			获取成败 = 摄像机对象.MV_CC_GetIntValue("GevSCPSPacketSize", 网络包大小)
			if (获取成败 != 0):
				print("Warning: 获取包大小失败，失败代码：0x{:x}".format(获取成败))
			else:
				return 网络包大小.nCurValue
		case "数据包大小":
			数据包大小 = MvImport.MvCameraControl_class.MVCC_INTVALUE()
			ctypes.memset(ctypes.byref(数据包大小),0,ctypes.sizeof(MvImport.MvCameraControl_class.MVCC_INTVALUE))
			# Pay load size：流通道上的数据有效负载包中的一个块ID发送的最大数据字节数
			# 例如：480p -> 640像素 x 480像素 -> Pay load size 为 307200
			获取成败 = 摄像机对象.MV_CC_GetIntValue("PayloadSize",数据包大小)
			if (获取成败 != 0):
				raise ValueError("数据包大小获取失败，失败代码：0x{:x}".format(获取成败))
			else:
				return 数据包大小.nCurValue
		case 其他:
			print("暂时无法获取“{}”的数值".format(其他))

def 开始抓取(摄像机对象:MvImport.MvCameraControl_class.MvCamera):
	开始抓取成败 = 摄像机对象.MV_CC_StartGrabbing()
	if (开始抓取成败 != 0):
		raise ValueError("开始抓取失败，失败代码：0x{:x}".format(开始抓取成败))
	else:
		if not(不回显信息):
			print("开始抓取成功")
		return True

def 获取当前图像(摄像机对象:MvImport.MvCameraControl_class.MvCamera):
	帧数据 = MvImport.MvCameraControl_class.MV_FRAME_OUT_INFO_EX()
	ctypes.memset(ctypes.byref(帧数据), 0, ctypes.sizeof(帧数据))
	当前图片像素数 = 获取数据(摄像机对象, "数据包大小")
	图像数据缓冲 = (ctypes.c_ubyte * 当前图片像素数)()
	# 1000？
	图像获取成败 = 摄像机对象.MV_CC_GetOneFrameTimeout(ctypes.byref(图像数据缓冲), 当前图片像素数, 帧数据, 1000)
	if (图像获取成败 != 0):
		raise ValueError("图像获取失败，失败代码：0x{:x}".format(图像获取成败))
	else:
		if not(不回显信息):
			print("成功获取图像，该图像长 {} 像素，宽 {} 像素，nFrameNum = {}".format(帧数据.nWidth,帧数据.nHeight,帧数据.nFrameNum))
		opencv黑白图像 = numpy.asarray(图像数据缓冲).reshape((帧数据.nHeight,帧数据.nWidth))
		opencv图像 = cv2.cvtColor(opencv黑白图像,cv2.COLOR_BayerBG2BGR)
		return opencv图像

def 结束抓取(摄像机对象:MvImport.MvCameraControl_class.MvCamera):
	摄像机对象.MV_CC_StopGrabbing()

def 关闭摄像机(摄像机对象: MvImport.MvCameraControl_class.MvCamera,抓取已结束:bool=True):
	if not(抓取已结束):
		结束抓取(摄像机对象)
	摄像机对象.MV_CC_CloseDevice()
	摄像机对象.MV_CC_DestroyHandle()

def 关闭系统():
	MvImport.MvCameraControl_class.MvCamera.MV_CC_Finalize()

def IP分段(IP地址:int):
	分段IP地址 = (
		(IP地址 & 0xff000000) >> 24,
		(IP地址 & 0x00ff0000) >> 16,
		(IP地址 & 0x0000ff00) >> 8 ,
		(IP地址 & 0x000000ff),
		)
	return 分段IP地址
