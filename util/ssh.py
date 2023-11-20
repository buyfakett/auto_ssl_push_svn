import logging
import paramiko


class SSHClient:
    """
    :param host:     string      ip
    :param password: string     密码
    :param port: string     端口
    :param username: string     用户名
    """

    def __init__(self, host: str,
                 password: str = None, port: int = 22, username: str = 'root'):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()

    def connect(self):
        self.client.connect(self.host, port=self.port, username=self.username, password=self.password)

    def execute_command(self, command):
        logging.info(f"即将执行命令: {command}")
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        logging.info(f"执行结果:\n{output}")
        if error:
            logging.error(f"执行错误:\n{error}")
        logging.info(f"退出代码: {exit_code}")
        return {
            'stdout': output,
            'stderr': error,
            'exit_code': exit_code
        }

    def execute_commands(self, commands):
        results = []
        for command in commands:
            result = self.execute_command(command)
            results.append(result)
        return results

    def upload_and_execute_script(self, local_path, remote_path):
        logging.info("----------------开始脚本文件----------------")
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        logging.info("----------------上传脚本结束----------------")

        # 确保脚本是可执行的
        self.execute_command(f'chmod +x {remote_path}')
        self.execute_command(f"sed -i 's/\r//' {remote_path}")

        # 执行脚本
        command_result = self.execute_command(f'/bin/bash {remote_path}')
        return command_result

    def upload_file(self, local_path, remote_path):
        logging.info("----------------开始上传文件----------------")
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        logging.info("----------------上传文件结束----------------")

    def close(self):
        self.client.close()
