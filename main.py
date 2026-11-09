import json
import os
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from fastapi import FastAPI
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles

#创建fastapi实例对象
app = FastAPI(title="汉字谜盒")


#挂载静态文件的存放目录
#参数一：以 "/static" 开头的URL路径都会交给这里处理
#参数二：静态文件存放目录
#参数三：fastapi内部使用的名称可以自定义
#负责处理 /static/ 下的资源请求。
app.mount("/static", StaticFiles(directory="static"), name="static")

#创建历史对话文件夹
if not os.path.exists("sessions"):
    os.makedirs("sessions")

#创建返回数据的类对象
class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any

#定义路径操作函数 ---》http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return FileResponse("static/index.html")   #把服务器上的 HTML 文件作为响应发出去

@app.post("/api/sessions")
def create_session():
    """
    通过抓包
    发现请求 URL  http://127.0.0.1:8000/api/sessions
    Request method post
    所以 这个接口的路径就是 /api/sessions
    模式是post 增加

    1.获取对话的id，以时间命名
    2.组装会话信息 会话信息由id和内容组成 把对话存在sessions目录下
    3.返回响应 json格式{"code":200,"message":"对话创建成功" ,data:对话id} 用fastapi自带的类完成 会把传入的参数转化为json格式
    :return:
    """

    #1.
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #2.
    session_data = {
        "current_session": session_id,
        "messages": []
    }
    with open(f"sessions/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f,ensure_ascii=False, indent=2)

    #3.
    return ApiResponse(code=200, message="对话创建成功", data= session_id)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
