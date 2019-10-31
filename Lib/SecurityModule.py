import hashlib


class Security(object):
    """description of class"""
    def GenerateMD5(s):
        return hashlib.md5(s.encode('utf-8')).hexdigest()


    def check_pid(pid):        
        #import psutil
        return True #psutil.pid_exists(pid)

    