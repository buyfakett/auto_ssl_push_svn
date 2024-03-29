# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/22 14:10
import logging

from models.user import User


async def check_user_exists():
    count = await User.all().count()
    return count > 0


async def event_startup():
    if not await check_user_exists():
        logging.info('没有用户，现在自动插入一条')
        try:
            # 插入一条账号为admin，密码为admin123456的数据为默认管理员账号
            await User.create(user='admin', password='a66abb5684c45962d887564f08346e8d')
        except Exception as e:
            logging.error(f"插入错误: {e}")
        logging.error('插入成功')
    # 应用启动时调用的逻辑
    logging.info("服务已启动！！！")
