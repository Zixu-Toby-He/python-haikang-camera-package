import typing
import ctypes

import cv2
import numpy
import termcolor

from . import MvImport
from . import 海康相机图片

_报警告:typing.Callable[[str], None] = lambda 警告信息: print(termcolor.colored("Warning：", "yellow") + 警告信息)
def 注册警告函数(警告函数:typing.Callable[[str], None]):
	global _报警告
	_报警告 = 警告函数


不回显信息 = False
_取图报告间隔 = 1
def 设定取图报告间隔(间隔:int):
	global _取图报告间隔
	_取图报告间隔 = 间隔

class 海康GigE工业相机:
	__slots__ = [
		"_设备信息",       # MvImport.MV_CC_DEVICE_INFO
		"_摄像机对象",     # MvImport.MvCamera
		"_开启状态",       # bool
		"_抓取状态",       # bool
		"_插值算法类型",   # 插值算法枚举类
		"_参数设置任务"    # 
	]
	def __init__(self, 设备信息: MvImport.MV_CC_DEVICE_INFO):
		if 设备信息.nTLayerType==MvImport.MvCameraControl_class.MV_GIGE_DEVICE:
			self._设备信息 = 设备信息
			self._开启状态 = False
			self._抓取状态 = False
			self._摄像机对象 = MvImport.MvCamera()
			self._参数设置任务 = {
				"插值算法类型": None,
				"增益":         None,
				"曝光时间":     None,
				"图像捕获帧率": None
			}
			self.插值算法类型 = 2
			创建成败 = self._摄像机对象.MV_CC_CreateHandle(设备信息)
			if (创建成败 != 0):
				print("摄像机对象创建失败")
				print()
				raise ValueError("摄像机对象创建失败，失败代码：0x{:x}".format(创建成败))
			else:
				if not(不回显信息):
					print("摄像机对象创建成功")
		else:
			raise ValueError("不是GigE设备")

	@property
	def 相机ID(self):
		return self._摄像机对象.handle
	
	@property
	def IP(self):
		return self._设备信息.SpecialInfo.stGigEInfo.nCurrentIp

	@property
	def IP分段(self):
		IP地址 = self._设备信息.SpecialInfo.stGigEInfo.nCurrentIp
		分段IP地址 = (
			(IP地址 & 0xff000000) >> 24,
			(IP地址 & 0x00ff0000) >> 16,
			(IP地址 & 0x0000ff00) >> 8 ,
			(IP地址 & 0x000000ff),
		)
		return 分段IP地址

	@property
	def IP字符串(self):
		IP地址 = self._设备信息.SpecialInfo.stGigEInfo.nCurrentIp
		分段IP地址 = (
			str((IP地址 & 0xff000000) >> 24),
			str((IP地址 & 0x00ff0000) >> 16),
			str((IP地址 & 0x0000ff00) >> 8 ),
			str((IP地址 & 0x000000ff)      ),
		)
		return ".".join(分段IP地址)
	
	@property
	def 名称(self):
		return ("".join(map(chr, self._设备信息.SpecialInfo.stGigEInfo.chUserDefinedName))).strip("\t\n \x00")
	
	@property
	def 型号(self):
		return ("".join(map(chr, self._设备信息.SpecialInfo.stGigEInfo.chModelName))).strip("\t\n \x00")
	
	@property
	def 开启状态(self):
		return self._开启状态
	
	@property
	def 抓取状态(self):
		return self._抓取状态
	
	@property
	def 网络包大小(self):
		网络包大小   = self._摄像机对象.MV_CC_GetOptimalPacketSize()
		网络包大小_1 = MvImport.MvCameraControl_class.MVCC_INTVALUE()
		ctypes.memset(ctypes.byref(网络包大小_1), 0, ctypes.sizeof(MvImport.MVCC_INTVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetIntValue("GevSCPSPacketSize", 网络包大小_1)
		if (获取成败 != 0):
			raise ValueError("获取包大小失败，失败代码：0x{:x}".format(获取成败))
		else:
			if ((网络包大小_1 != 网络包大小) and (网络包大小 > 0)):
				设定成败 = self._摄像机对象.MV_CC_SetIntValue("GevSCPSPacketSize", 网络包大小)
		return 网络包大小

	@property
	def 数据包大小(self):
		数据包大小 = MvImport.MvCameraControl_class.MVCC_INTVALUE()
		ctypes.memset(ctypes.byref(数据包大小),0,ctypes.sizeof(MvImport.MvCameraControl_class.MVCC_INTVALUE))
		# Pay load size：流通道上的数据有效负载包中的一个块ID发送的最大数据字节数
		# 例如：480p -> 640像素 x 480像素 -> Pay load size 为 307200
		获取成败 = self._摄像机对象.MV_CC_GetIntValue("PayloadSize", 数据包大小)
		if (获取成败 != 0):
			raise ValueError("数据包大小获取失败，失败代码：0x{:x}".format(获取成败))
		else:
			return 数据包大小.nCurValue

	@property
	def 插值算法类型(self):
		match(self._插值算法类型):
			case None:
				return "未设置"
			case 0:
				return "低画质"
			case 1:
				return "中画质"
			case 2:
				return "高画质"
			case 其他:
				raise ValueError("插值算法类型错误：{}".format(repr(self._插值算法类型)))

	@插值算法类型.setter
	def 插值算法类型(self, 插值算法类型: int | str = 2):
		if (isinstance(插值算法类型, int)):
			if 插值算法类型 in range(3):
				self._插值算法类型 = 插值算法类型
			else:
				raise ValueError("插值算法类型错误：试图设置为 {}".format(repr(插值算法类型)))
		elif (isinstance(插值算法类型, str)):
			self._插值算法类型 = {
				"低画质": 0,
				"low":    0,
				"中画质": 1,
				"middle": 1,
				"高画质": 2,
				"high":   2,
			}[插值算法类型.lower()]
		else:
			raise ValueError("插值算法类型错误：试图设置为 {}".format(repr(插值算法类型)))
		if self._开启状态:
			设定成败 = self._摄像机对象.MV_CC_SetBayerCvtQuality(self._插值算法类型)
			if (设定成败 != 0):
				_报警告("设定插值算法模式失败，失败代码：0x{:x}".format(设定成败))
			else:
				if not(不回显信息):
					print("成功设定插值算法为{}号模式".format(self._插值算法类型))
			self._参数设置任务["插值算法类型"] = None
		else:
			self._参数设置任务["插值算法类型"] = self._插值算法类型

	# 单位：毫秒
	@property
	def 曝光时间(self):
		曝光时间数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(曝光时间数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("ExposureTime", 曝光时间数据)
		if (获取成败 != 0):
			if self._参数设置任务["曝光时间"] != None:
				return self._参数设置任务["曝光时间"]
			else:
				_报警告("获取曝光时间失败，失败代码：0x{:x}".format(获取成败))
				return 0
		else:
			# 转化为毫秒
			return (float)(曝光时间数据.fCurValue) / 1000

	@property
	def 最大曝光时间(self):
		曝光时间数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(曝光时间数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("ExposureTime", 曝光时间数据)
		if (获取成败 != 0):
			_报警告("获取曝光时间失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			# 转化为毫秒
			return (float)(曝光时间数据.fMax) / 1000
		
	@property
	def 最小曝光时间(self):
		曝光时间数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(曝光时间数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("ExposureTime", 曝光时间数据)
		if (获取成败 != 0):
			_报警告("获取曝光时间失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			# 转化为毫秒
			return (float)(曝光时间数据.fMin) / 1000

	# 单位：毫秒
	@曝光时间.setter
	def 曝光时间(self, 曝光时间: float):
		# self._摄像机对象.MV_CC_SetEnumValue("ExposureAuto", 0) # demo里面有该段代码，实际用处未知
		if self._开启状态:
			设定成败 = self._摄像机对象.MV_CC_SetFloatValue("ExposureTime", 曝光时间 * 1000.0)
			if (设定成败 != 0):
				raise Exception("设定曝光时间失败，失败代码：0x{:x}".format(设定成败))
			self._参数设置任务["曝光时间"] = None
		else:
			self._参数设置任务["曝光时间"] = 曝光时间

	@property
	def 增益(self):
		增益数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(增益数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("Gain", 增益数据)
		if (获取成败 != 0):
			if self._参数设置任务["增益"] != None:
				return self._参数设置任务["增益"]
			else:
				_报警告("获取增益失败，失败代码：0x{:x}".format(获取成败))
				return 0
		else:
			return 增益数据.fCurValue

	@property
	def 最大增益(self):
		增益数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(增益数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("Gain", 增益数据)
		if (获取成败 != 0):
			print("Warning: 获取增益失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			return 增益数据.fMax
		
	@property
	def 最小增益(self):
		增益数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(增益数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("Gain", 增益数据)
		if (获取成败 != 0):
			print("Warning: 获取增益失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			return 增益数据.fMin

	@增益.setter
	def 增益(self, 增益: float):
		# self._摄像机对象.MV_CC_SetEnumValue("ExposureAuto", 0) # demo里面有该段代码，实际用处未知
		if self._开启状态:
			设定成败 = self._摄像机对象.MV_CC_SetFloatValue("Gain", 增益)
			if (设定成败 != 0):
				raise Exception("设定增益失败，失败代码：0x{:x}".format(设定成败))
			self._参数设置任务["增益"] = None
		else:
			self._参数设置任务["增益"] = 增益

	@property
	def 图像捕获帧率(self):
		图像捕获帧率数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(图像捕获帧率数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("AcquisitionFrameRate", 图像捕获帧率数据)
		if (获取成败 != 0):
			if self._参数设置任务["图像捕获帧率"] != None:
				return self._参数设置任务["图像捕获帧率"]
			else:
				_报警告("获取图像捕获帧率失败，失败代码：0x{:x}".format(获取成败))
				return 0
		else:
			return 图像捕获帧率数据.fCurValue

	@property
	def 最大图像捕获帧率(self):
		图像捕获帧率数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(图像捕获帧率数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("AcquisitionFrameRate", 图像捕获帧率数据)
		if (获取成败 != 0):
			_报警告("获取图像捕获帧率失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			return 图像捕获帧率数据.fMax
	
	@property
	def 最小图像捕获帧率(self):
		图像捕获帧率数据 = MvImport.MVCC_FLOATVALUE()
		ctypes.memset(ctypes.byref(图像捕获帧率数据), 0, ctypes.sizeof(MvImport.MVCC_FLOATVALUE))
		获取成败 = self._摄像机对象.MV_CC_GetFloatValue("AcquisitionFrameRate", 图像捕获帧率数据)
		if (获取成败 != 0):
			_报警告("获取图像捕获帧率失败，失败代码：0x{:x}".format(获取成败))
			return 0
		else:
			return 图像捕获帧率数据.fMin

	@图像捕获帧率.setter
	def 图像捕获帧率(self, 图像捕获帧率: float):
		# self._摄像机对象.MV_CC_SetEnumValue("ExposureAuto", 0) # demo里面有该段代码，实际用处未知
		if self._开启状态:
			设定成败 = self._摄像机对象.MV_CC_SetFloatValue("AcquisitionFrameRate", 图像捕获帧率)
			if (设定成败 != 0):
				raise Exception("设定图像捕获帧率失败，失败代码：0x{:x}".format(设定成败))
			self._参数设置任务["图像捕获帧率"] = None
		else:
			self._参数设置任务["图像捕获帧率"] = 图像捕获帧率

	def 打开摄像头(self):
		if self._开启状态:
			return
		打开成败 = self._摄像机对象.MV_CC_OpenDevice(MvImport.MvCameraControl_class.MV_ACCESS_Exclusive, 0)
		if (打开成败 != 0):
			print("摄像机对象打开失败，失败代码：0x{:x}".format(打开成败))
			print()
			raise ValueError("摄像机对象打开失败，失败代码：0x{:x}".format(打开成败))
		else:
			self._开启状态 = True
			for 参数, 数值 in self._参数设置任务.items():
				if 数值 != None:
					setattr(self, 参数, 数值)
			for 参数 in self._参数设置任务.keys():
				self._参数设置任务[参数] = None
			if not(不回显信息):
				print("摄像机对象打开成功")

	def 开始抓取(self):
		if self._抓取状态:
			return
		if (not(self._开启状态)):
			self.打开摄像头()
		开始抓取成败 = self._摄像机对象.MV_CC_StartGrabbing()
		if (开始抓取成败 != 0):
			raise ValueError("开始抓取失败，失败代码：0x{:x}".format(开始抓取成败))
		else:
			self._抓取状态 = True
			if not(不回显信息):
				print("开始抓取成功")

	def 结束抓取(self):
		if self._抓取状态:
			结束抓取成败 = self._摄像机对象.MV_CC_StopGrabbing()
			if (结束抓取成败 != 0):
				raise Exception("结束抓取失败，错误代码：0x{:x}".format(结束抓取成败))
			else:
				if not(不回显信息):
					print("结束抓取成功")
				self._抓取状态 = False

	def 关闭摄像头(self):
		if self._抓取状态:
			self.结束抓取()
		if self._开启状态:
			关闭摄像头成败 = self._摄像机对象.MV_CC_CloseDevice()
			if (关闭摄像头成败 != 0):
				raise Exception("关闭摄像头失败，错误代码：0x{:x}".format(关闭摄像头成败))
			else:
				if not(不回显信息):
					print("关闭摄像头成功")
				self._开启状态 = False

	def 获取当前图像(self):
		初始状态 = 0
		if (not(self._开启状态)):
			self.打开摄像头()
			初始状态 += 2
		if (not(self._抓取状态)):
			self.开始抓取()
			初始状态 += 1
		帧信息 = MvImport.MV_FRAME_OUT_INFO_EX()
		ctypes.memset(ctypes.byref(帧信息), 0, ctypes.sizeof(帧信息))
		当前图片像素数 = self.数据包大小
		图像数据缓冲 = (ctypes.c_ubyte * 当前图片像素数)()
		# 1000？
		图像获取成败 = self._摄像机对象.MV_CC_GetOneFrameTimeout(ctypes.byref(图像数据缓冲), 当前图片像素数, 帧信息, 1000)
		if (图像获取成败 != 0):
			match(初始状态):
				case 0:
					#不做任何事
					pass
				case 1:
					self.结束抓取()
				case 2:
					self.关闭摄像头()
				case 3:
					self.结束抓取()
					self.关闭摄像头()
			raise ValueError("图像获取失败，失败代码：0x{:x}".format(图像获取成败))
		else:
			if not(不回显信息):
				global _取图报告间隔
				if ((帧信息.nFrameNum % _取图报告间隔) == 0):
					print("成功获取图像，该图像长 {} 像素，宽 {} 像素，nFrameNum = {}".format(帧信息.nWidth,帧信息.nHeight,帧信息.nFrameNum))
			
			match(初始状态):
				case 0:
					#不做任何事
					pass
				case 1:
					self.结束抓取()
				case 2:
					self.关闭摄像头()
				case 3:
					self.结束抓取()
					self.关闭摄像头()
			return 海康相机图片.海康相机图片(图片信息 = 帧信息, 图片数据 = 图像数据缓冲, 相机ID = self.相机ID)

	def 销毁摄像头(self):
		if self._抓取状态:
			self._摄像机对象.MV_CC_StopGrabbing()
		if self._开启状态:
			self._摄像机对象.MV_CC_CloseDevice()
		self._摄像机对象.MV_CC_DestroyHandle()
		#self._摄像机对象 = None
		#self._设备信息   = None
		self._开启状态   = False


class 海康设备列表:
	__slots__=[
		"相机列表", # tuple(海康GigE工业相机)
		"可用",     # bool
	]
	_实例个数:int = 0
	def __init__(self, 检索类别: list[str|int] | None = None):
		if (海康设备列表._实例个数 < 1):
			if (检索类别 == None):
				检索类别 = ["GigE设备"]
			self.设备启动()
			设备列表 = MvImport.MV_CC_DEVICE_INFO_LIST()
			设备类别校验表 = {
				"未知设备"                 : MvImport.MV_UNKNOW_DEVICE,
				"GigE设备"                 : MvImport.MV_GIGE_DEVICE,
				"GigE设备_虚拟"            : MvImport.MV_VIR_GIGE_DEVICE,
				"GigE设备_自研网卡"        : MvImport.MV_CAMERALINK_DEVICE,
				"1394设备"                 : MvImport.MV_1394_DEVICE,
				"USB设备"                  : MvImport.MV_USB_DEVICE,
				"虚拟USB设备"              : MvImport.MV_VIR_USB_DEVICE,
				"Camera Link设备"          : MvImport.MV_GENTL_GIGE_DEVICE,
				"Camera Link设备_自研网卡" : MvImport.MV_GENTL_CAMERALINK_DEVICE,
				"CoaXPress设备_自研网卡"   : MvImport.MV_GENTL_CXP_DEVICE,
				"XoF设备_自研网卡"         : MvImport.MV_GENTL_XOF_DEVICE,
			}
			检索代码 = 0
			for 类别 in 检索类别:
				try:
					检索代码 |= 设备类别校验表[类别]
				except KeyError:
					if 类别 in 设备类别校验表.values():
						检索代码 |= 类别
					else:
						raise ValueError("检索类别设置错误，错误点：{}".format(repr(类别)))
				except:
					raise ValueError("检索类别设置错误，错误点：{}".format(repr(类别)))
			#检索类别 = 检索类别 | MvImport.MV_USB_DEVICE
			检索成败 = MvImport.MvCamera.MV_CC_EnumDevices(检索代码, 设备列表)
			if (检索成败 != 0):
				raise Exception("检索设备失败，失败代码：0x{:x}".format(检索成败))
			elif(设备列表.nDeviceNum == 0):
				raise Exception("检测到 0 台设备，请确认设备正确连接")
			else:
				设备数量 = 设备列表.nDeviceNum
				if not(不回显信息):
					print("检索到 {} 台摄像头".format(设备数量))
				self.相机列表 = []
				for 设备编号 in range(0, 设备数量):
					设备信息数据 = 设备列表.pDeviceInfo[设备编号]
					信息结构体指针类型 = ctypes.POINTER(MvImport.MvCameraControl_class.MV_CC_DEVICE_INFO)
					设备信息 = ctypes.cast(设备信息数据, 信息结构体指针类型).contents
					self.相机列表.append(海康GigE工业相机(设备信息))
				self.相机列表 = tuple(self.相机列表)
		else:
			raise ValueError("已经存在海康设备列表实例，请勿重复生成")
	def __len__(self):
		return len(self.相机列表)
	def __getitem__(self, i: typing.SupportsIndex | slice):
		return self.相机列表[i]
	def __iter__(self):
		return iter(self.相机列表)
	def 设备启动(self):
		MvImport.MvCamera.MV_CC_Initialize()
	def 关闭列表(self):
		for 相机 in self.相机列表:
			相机.销毁摄像头()
		MvImport.MvCamera.MV_CC_Finalize()

def test():
	所有设备 = 海康设备列表(["GigE设备"])
	眼A:海康GigE工业相机 = 所有设备[0]
	眼B:海康GigE工业相机 = 所有设备[1]
	眼A.打开摄像头()
	眼A.曝光时间 = 100
	眼B.曝光时间 = 100
	眼A.增益 = 23
	眼B.增益 = 23
	print(眼A)
	print("   ", 眼A.IP字符串)
	print("   ", 眼A.名称)
	print("   ", 眼A.型号)
	print("   ", 眼A.插值算法类型)
	print("   ", 眼A.曝光时间)
	print("   ", 眼A.增益)
	print("   ", 眼A.图像捕获帧率)
	print(眼B)
	print("   ", 眼B.IP字符串)
	print("   ", 眼B.名称)
	print("   ", 眼B.型号)
	print("   ", 眼B.插值算法类型)
	print("   ", 眼B.曝光时间)
	print("   ", 眼B.增益)
	print("   ", 眼B.图像捕获帧率)
	眼A.打开摄像头()
	眼B.打开摄像头()
	cv2.imshow("A", cv2.resize(眼A.获取当前图像().BGR图像,dsize=None,fx=0.3,fy=0.3))
	cv2.imshow("B", cv2.resize(眼B.获取当前图像().BGR图像,dsize=None,fx=0.3,fy=0.3))
	眼A.关闭摄像头()
	眼B.关闭摄像头()
	cv2.waitKey()
	cv2.destroyAllWindows()