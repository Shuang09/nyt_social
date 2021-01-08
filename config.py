#coding=gbk
import os,time

basedir=os.path.abspath(os.path.dirname(__name__))
BASE_DIR = os.path.dirname(__file__)
class Config:
    notes_page=10
    comment_page=10
    SECRET_KEY='lightA0Zr98j/3yX R~XHH!jmN]LWX/,?RTbean'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/nyt_social'
    current_date=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    current_datetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

config=Config()


def get_local_ip():
    import socket
    ret = socket.gethostbyname_ex(socket.gethostname())
    return ret
