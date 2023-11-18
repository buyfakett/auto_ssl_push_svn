# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/9 9:37

import base64
from Crypto.Cipher import AES


def addStrToSpecifyLen(s, specifyLen=0):
    """
    s不是specifyLen的倍数那就补足为specifyLen的倍数
    :param s: 需要加密的参数
    :param specifyLen: 指定参数的位数
    :return: 补足位数的参数
    """
    if specifyLen <= 0:
        specifyLen = 1;
    while len(s) % specifyLen != 0:
        s += '\0'
    return s.encode(encoding='utf-8')


def encrypt_aes(data: str = '', aes_key: str = ''):
    """
    aes的ecb模式加密
    :param data: 加密数据
    :param aes_key: 加密的秘钥
    :return: 加密之后的密文
    """
    # 初始化加密器
    aes = AES.new(addStrToSpecifyLen(aes_key, 16), AES.MODE_ECB)
    # 先进行aes加密
    encrypt = aes.encrypt(addStrToSpecifyLen(data, 16))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt), encoding='utf-8').replace('\n', '')  # 执行加密并转码返回bytes
    return encrypted_text


def decrypt_aes(data: str, aes_key: str = ''):
    """
    aes的ecb模式解密
    :param data: 待解密数据
    :param aes_key: 加密的秘钥
    :return: 解密之后的数据
    """
    # 初始化加密器
    aes = AES.new(addStrToSpecifyLen(aes_key, 16), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(addStrToSpecifyLen(data, 16))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text

