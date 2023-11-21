import subprocess


class SVNClient:
    """
    :param repo_url:     string      svn地址
    :param working_copy_path: string     检出地址
    :param username: string     用户名
    :param password: string     密码
    :return output: string      日志
    :return error: string      错误
    :return returncode: string      返回码
    """
    def __init__(self, repo_url: str, working_copy_path: str, username: str, password: str):
        self.repo_url = repo_url
        self.working_copy_path = working_copy_path
        self.username = username
        self.password = password

    def execute_svn_command(self, command):
        full_command = f'svn {command}'
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return output.decode('utf-8'), error.decode('utf-8'), process.returncode

    def checkout(self):
        return self.execute_svn_command(
            f'checkout {self.repo_url} {self.working_copy_path} --username={self.username} --password={self.password}')

    def update(self):
        return self.execute_svn_command(
            f'update {self.working_copy_path} --username={self.username} --password={self.password}')

    def add(self, route: str):
        return self.execute_svn_command(
            f'add {route}')

    def commit(self, message: str):
        return self.execute_svn_command(
            f'commit -m "{message}" {self.working_copy_path} --username={self.username} --password={self.password}')
