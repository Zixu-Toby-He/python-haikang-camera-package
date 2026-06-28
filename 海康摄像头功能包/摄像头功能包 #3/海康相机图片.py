import typing
import ctypes

import cv2
import numpy
import termcolor

from . import MvImport

class 海康相机图片:
	__slots__ = [
		"图片信息",
		"图片数据",
		"相机ID"
	]
	def __init__(self, 图片信息:MvImport.MV_FRAME_OUT_INFO_EX, 图片数据, 相机ID):
		self.图片信息 = 图片信息
		self.图片数据 = 图片数据
		self.相机ID   = 相机ID
	@property
	def 长(self):
		return self.图片信息.nExtendWidth
	@property
	def 高(self):
		return self.图片信息.nExtendHeight
	@property
	def 像素数(self):
		return self.nFrameLenEx
	@property
	def 像素格式码(self):
		return self.图片信息.enPixelType
	@property
	def 帧号(self):
		return self.图片信息.nFrameNum
	@property
	def 时间戳(self):
		return (int(self.图片信息.nDevTimeStampHigh) << 32) | int(self.图片信息.nDevTimeStampLow)
	@property
	def 时间戳_主机生成(self):
		return self.图片信息.nHostTimeStamp
	@property
	def BGR图像(self):
		match(self.像素格式码):
			case MvImport.PixelType_Gvsp_BayerRG8:
				return cv2.cvtColor(
					src  = numpy.asarray(self.图片数据).reshape((self.图片信息.nHeight, self.图片信息.nWidth)),
					code = cv2.COLOR_BayerBG2BGR
				)
			case 无效像素格式码:
				raise ValueError("未知像素格式码：{}".format(无效像素格式码))

	def 在控件上显示(self, 控件控制ID):
		显示参数 = MvImport.MV_DISPLAY_FRAME_INFO()
		ctypes.memset(ctypes.byref(显示参数), 0, ctypes.sizeof(显示参数))
		显示参数.hWnd        = int(控件控制ID)
		显示参数.nWidth      = self.图片信息.nWidth
		显示参数.nHeight     = self.图片信息.nHeight
		显示参数.enPixelType = self.图片信息.enPixelType
		显示参数.nDataLen    = self.图片信息.nFrameLen
		显示参数.pData       = self.图片数据
		MvImport.MvCamCtrldll.MV_CC_DisplayOneFrame(self.相机ID, 显示参数)

