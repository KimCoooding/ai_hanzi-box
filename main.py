from fastapi import FastAPI
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles

#创建fastapi实例对象
app = FastAPI(title="汉字谜盒")

#挂载静态文件的存放目录
#参数一：以 "/static" 开头的URL路径都会交给这里处理
#参数二：静态文件存放目录
#参数三：fastapi内部使用的名称可以自定义
app.mount("/static", StaticFiles(directory="static"), name="static")

#定义路径操作函数 ---》http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
