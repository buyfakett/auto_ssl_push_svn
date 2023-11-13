import os, yaml, logging


# 读取yaml
def read_yaml(key: str, filename: str):
    """
    :param key:     string      要读取的值的名称
    :param filename: string     配置文件的名字
    :return         *           要读取的值
    """
    try:
        with open(os.getcwd() + '/config/' + filename + '.yaml', encoding="utf-8") as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)
            return value[key]
    except:
        logging.error("读取配置文件的时候异常，请检查配置文件！！！")
        raise SystemExit(0)


# 追加写入yaml
def write_yaml(data: str, filename: str):
    with open(os.getcwd() + '/config/' + filename, encoding="utf-8", mode="a") as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)


# 写入yaml
def write_yaml_value(data: str, filename: str):
    with open(os.getcwd() + '/config/' + filename, encoding="utf-8", mode="w") as f:
        yaml.safe_dump(data=data, stream=f, allow_unicode=True)


# 清空yaml
def clear_yaml(filename: str):
    with open(os.getcwd() + '/config/' + filename, encoding="utf-8", mode="w") as f:
        f.truncate()


# 读取全部yaml配置
def read_all_yaml(filename: str):
    with open(os.getcwd() + '/config/' + filename, encoding="utf-8") as f:
        value: object = yaml.load(stream=f, Loader=yaml.FullLoader)
        return value
