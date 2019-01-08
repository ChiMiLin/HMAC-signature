import numpy as np
import cv2
import hmac,hashlib
import random
import os

def getStartIndex(key, num):
	'''
	擷取金鑰0~num位做為起始位置(金鑰原為16進制)
	'''
	return int('0x'+key[0:num],16)

def getLength(key):
	'''
	擷取金鑰5~7位做為長度(金鑰原為16進制)
	'''
	return int('0x'+key[5:8],16)

def capture(imgArr, key):
	'''
	擷取訊息片段，若範圍超出則降低getStartIndex的num參數(c)
	'''
	imgLen = len(imgArr)
	c = 5
	startIndex = getStartIndex(key,c)
	length = getLength(key)
	if startIndex+length > imgLen:
		c = c - 1
		startIndex = getStartIndex(key,c)
	else:
		return imgArr[startIndex:startIndex+length]

def getSignature(msg, key):
	'''
	輸入訊息以及金鑰回傳簽章後結果
	'''
	return hmac.new(key.encode('UTF-8'), msg.encode('UTF-8'), hashlib.md5).hexdigest()

def sign(msg, key):
	partMsg = capture(msg, key)
	personalSignature = getSignature(partMsg, key)
	return personalSignature
def getMessage(path):
	'''
	輸入圖片位置得到由該圖片各像素RGB值組成的長字串
	'''
	image = cv2.imread(path)
	
	xLen = len(image[0])
	yLen = len(image)
	imgArr = ''.join([''.join([''.join([str(image[y][x][i]) for i in range(3)]) for x in range(xLen)]) for y in range(yLen)])

	return imgArr
def getRandomKey():
	subKey = hex(random.randint(0,1099511627776)).strip('0x')
	return '0'*(10-len(subKey)) + subKey

class contract():
	__signature = {}
	__msg = ''
	__LOCK = False
	def __init__(self, msg):
		self.__msg = msg
		
	def showContract(self):
		print('='*10 + '合約文本' + '='*10)
		print(self.__msg)
		print('='*10 + '簽章內容' + '='*10)
		for i in self.__signature:
			print(i, self.__signature[i])
	
	def inputSignature(self, signature):
		self.__signature[signature] = 'unconfirm'
		
	def confirmSignature(self, signature):
		if signature not in self.__signature:
			raise Exception('Signature Not Found')
		self.__signature[signature] = 'confirm'
		confirm = 0
		for s in self.__signature:
			if self.__signature[s] is 'confirm':
				confirm += 1
		if confirm >= 2:
			self.__UNLOCK()
	
	def checkSignature(self, signature):
		return signature in self.__signature
	
	def getSignatureNum(self):
		return len(self.__signature)

	def getMsg(self):
		return self.__msg
	
	def LOCK(self):
		self.__LOCK = True

	def __UNLOCK(self):
		self.__LOCK = False

	def isLOCK(self):
		return self.__LOCK

if __name__ == "__main__":
	isContractExist = False
	key = []
	for i in range(5):
		key.append(getRandomKey())
	while(True):
		os.system('cls')
		print('╔════════════════════════════════════════════════════════════════════════════════╗')
		print('║                           歡迎使用  交易簽章模擬系統 v1.0                      ║')
		print('╠═══════════════════════════════════════╦════════════════════════════════════════╣')
		print('║               1>合約建立              ║               4>產生金鑰               ║')
		print('║               2>合約簽章              ║               5>檢視金鑰               ║')
		print('║               3>解鎖合約              ║               6>檢視合約               ║')
		print('║                                       ║                                        ║')
		print('║                                       ║               0>離開                   ║')
		print('╚═══════════════════════════════════════╩════════════════════════════════════════╝')
		mode = input('請輸入命令 : ')
		os.system('cls')
		if mode is '1':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 合約建立                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')
			if not isContractExist:
				try:
					path = input('請輸入圖片位置:')
					print('提示訊息 : 合約建立中...')
					transaction = contract(getMessage(path))
					isContractExist = True
					print('提示訊息 : 合約建立成功!')
				except:
					print('錯誤代碼 001 : 圖片讀取失敗，合約建立失敗!')

			else:
				print('錯誤代碼 011 : 合約已存在，建立失敗!')

		elif mode is '2':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 合約簽章                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')
			if isContractExist: #確認合約是否存在
				if not transaction.isLOCK(): #確認合約是否上鎖
					try:
						keynum = int(input('請輸入您愈使用的金鑰編號(僅用於模擬) : '))
						if keynum not in range(5):
							raise ValueError
						if transaction.checkSignature(sign(transaction.getMsg(), key[keynum])):
							print('錯誤代碼 031 : 此金鑰已簽章成功，簽章失敗!')
						else:
							transaction.inputSignature(sign(transaction.getMsg(), key[keynum]))
							print('提示訊息 : 簽署成功!')
							if transaction.getSignatureNum() is 3:
								transaction.LOCK()
								print('提示訊息 : 合約簽署完畢，上鎖完成!')
							else:
								print('提示訊息 : 目前簽署人數 : ', transaction.getSignatureNum())
					except ValueError:
						print('錯誤代碼 042 : 金鑰編號輸入錯誤，請輸入0~4之間的整數!')
				else:
					print('錯誤代碼 021 : 合約已簽署完畢，現已上鎖!')
			else:
				print('錯誤代碼 012 : 合約不存在!')
					
		elif mode is '3':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 解鎖合約                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')

			if isContractExist: #確認合約是否存在
				if transaction.isLOCK(): #確認合約是否上鎖
					try:
						keynum = int(input('請輸入您愈使用的金鑰編號(僅用於模擬) : '))
						if keynum not in range(5):
							raise ValueError
						try:
							transaction.confirmSignature(sign(transaction.getMsg(), key[keynum]))
							print('提示訊息 : 簽章驗證通過!')
						except Exception:
							print('錯誤代碼 041 : 您輸入的金鑰未簽署此合約，請確認後重新輸入!')
						if not transaction.isLOCK():
							print('提示訊息 : 合約解鎖成功，已可提取其中現金!')
							print('╔════════════════════════════════════════════════════════════════════════════════╗')
							print('║                    感謝您使用本模擬程式，期待我們下次再會                      ║')
							print('╠════════════════════════════════════════════════════════════════════════════════╣')
							print('║                             指導老師  李添福 老師                              ║')
							print('║                             設計      林一源                                   ║')
							print('║                                       王子溦                           20190108║')
							print('╚════════════════════════════════════════════════════════════════════════════════╝')
							os.system('pause')
							break
					except ValueError:
						print('錯誤代碼 042 : 金鑰編號輸入錯誤，請輸入0~4之間的整數!')


				else:
					print('錯誤代碼 022 : 合約未簽署完畢，無法解鎖!')
			else:
				print('錯誤代碼 012 : 合約不存在!')

		elif mode is '4':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 產生金鑰                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')

			for i in range(5):
				key[i] = getRandomKey()
			print('提示訊息 : 金鑰更新成功!(僅用於模擬)')


		elif mode is '5':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 檢視金鑰                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')

			for i, k in enumerate(key):
				print(i,k)
				
		elif mode is '6':
			print('╔════════════════════════════════════════════════════════════════════════════════╗')
			print('║                          交易簽章模擬系統 > 檢視合約                           ║')
			print('╚════════════════════════════════════════════════════════════════════════════════╝')

			transaction.showContract()

		elif mode is '0':
			break
		else:
			print('錯誤代碼 111 : 命令不存在，請重新輸入!')
		os.system('pause')