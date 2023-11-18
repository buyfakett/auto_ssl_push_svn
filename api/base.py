from fastapi import status
from fastapi.responses import JSONResponse
from typing import Union, List


# 定义响应统一结构体

def resp_200(*, code: int = 0, data: Union[List[dict], list, dict, str], message='Success'):
    """
    200系列的响应结构体
    *：代表调用方法时必须传参数
    Union：代表传入的参数可以是多种类型
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': data,
        }
    )


def resp_400(*, code: int = 400, message='Bad Request!'):
    """
    400系列的响应结构体
    *：代表调用方法时必须传参数
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': code,
            'message': message,
        }
    )
