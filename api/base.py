from fastapi import status
from fastapi.responses import JSONResponse
from typing import Union, List
import logging


# 定义响应统一结构体

def resp_200(code: int = 0, data: Union[List[dict], list, dict, str] = None, message='Success'):
    """
    200系列的响应结构体
    *：代表调用方法时必须传参数
    Union：代表传入的参数可以是多种类型
    """
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'code': code,
                'message': message,
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': data,
        }
    )


def resp_400(code: int = 400, message='错误，请重试！'):
    """
    400系列的响应结构体
    *：代表调用方法时必须传参数
    """
    logging.error(message)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': code,
            'message': message,
        }
    )
