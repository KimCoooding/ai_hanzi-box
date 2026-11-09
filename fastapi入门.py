from fastapi import FastAPI

#创建fastapi实例
app = FastAPI()

#定义路由
# app.get("/") 定义一个GET请求的路由，路径为 "/"
#Python Web 开发里的路由，就是告诉程序收到什么请求，就调用哪个函数处理。
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/user")
def read_user():
    return {"user": "ZhangSan"}

#第三种启动服务方式，使用uvicorn 是 python中的轻量级web服务器
if __name__ == '__main__':
    import uvicorn
    #运行这个服务器  0.0.0.0 IP地址，表示这个服务器可以被任何IP访问，而不仅仅是127.0.0.1
    uvicorn.run(app, host="0.0.0.0", port=8000)

# uvicorn 是一个服务器，访问这个服务器需要通过浏览器发送请求
# 而这个服务器正好运行在本机上 所以本机的ip地址也就是这个服务器的ip地址
# 所以本机通过浏览器访问这个服务器 通过 127.0.0.1也就是localhost 就可以访问到  浏览器访问的地址就是 http://127.0.0.1:8000
# 本机在校园网的ip是10.198.85.163 所以服务器的ip也是这个  所以链接校园网的手机通过这个ip地址也可以访问到这个服务器 http://10.198.85.163:8000

#更改测试

