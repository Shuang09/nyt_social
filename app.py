#coding=gbk
import os
from app import create_app

app=create_app()

if __name__=='__main__':
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8002)
    IOLoop.instance().start()
