# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/21 17:21
import subprocess


def exec_shell(command: str):
    """
    :param command:     string      命令
    :return output: string      日志
    :return error: string      错误
    :return returncode: string      返回码
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode('utf-8'), error.decode('utf-8'), process.returncode
