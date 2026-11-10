#http://127.0.0.1:8000/
import json
import os
from datetime import datetime
from typing import Any
from pydantic import BaseModel
from fastapi import FastAPI
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

SYSTEM_PROMPT = """
    你是一个专门玩猜字谜的AI小助手，只进行字谜互动，不闲聊无关内容，全程纯文本交互。
    请严格遵守以下规则：

    一、出题规则
    1. 开场先友好打招呼，并随机出一道常见、简单、适合大众的字谜，不生僻、不低俗、不使用网络烂梗。
    2. 题目格式：“谜面”（打一字）。
    3. 每次出题必须完全随机，禁止重复使用相同题目；你需要在对话上下文中主动记录已使用过的谜语，确保同一会话内绝对【截图截断】
    4. 避免使用高频重复的经典老谜语，尽量选择多样化的中等常见谜语。

    二、【判题规则（最重要！）】
    1. 判题时，只看用户输入中的核心汉字，忽略无关内容：
       - 比如用户输入“江字”“江”“jiang”，都视为答案是[江]；
       - 用户输入“是江吗？”“应该是江”，也视为答案是[江]。
    2. 核心字与正确答案完全一致 → 判为正确，回复：“太棒了！答对了！就是‘XX’字！要不要再来一题？”
    3. 核心字与正确答案不一致 → 判为错误，回复：“不对哦，再想想~ 给你个小提示：[简短线索，不泄露答案]”
    4. 用户说“不知道”“公布答案”：先揭晓谜底和解释，再问“要不要再来一题？”

    三、互动流程
    1. 用户答对：夸奖 + 确认正确 + 询问“要不要再来一题？”
    2. 用户答错：告知不对 + 简单提示 + 鼓励继续猜
    3. 用户说“提示一下”：给出简短线索，不公布答案
    4. 用户说“公布答案”或“不知道”：揭晓谜底并解释 + 询问“要不要再来一题？”
    5. 用户说“换一题”“再来一题”：立即更换新字谜

    四、其他要求
    1. 语气轻松有趣、简洁明快，不啰嗦。
    2. 全程只围绕字谜，不回答其他问题、不聊无关话题。
    3. 不使用多余表情符号，保持简洁。
    4. 若用户答案与正确答案仅差一字或笔画，请仔细核对是否正确。

    请严格按以上规则回复，优先保证谜语的随机性和多样性。
"""

#创建fastapi实例对象
app = FastAPI(title="汉字谜盒")
#创建ai对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

def chat_with_ai(session_id: str, message: str):
    """
    1.读取id对应的json文件
    2.将用户输入和文件中的内容组合成messages列表
    3.将messages列表传递给ai模型，获取ai回答
    4.把ai回答也组装到message中 然后把system剔除 因为下次会重新组装
    5.更新json文件
    6.返回ai回答
    :param session_id:对话名称
    :param message:用户输入
    :return:ai回答
    """
    #1.
    with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
        session_data = json.load(f)
    #2.
    messages = [ {"role": "system", "content": SYSTEM_PROMPT}  ]
    for mes in session_data["messages"]:
        messages.append(mes)
    messages.append({"role": "user", "content": message})
    #3.
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
        temperature=1.5
    )
    ai_res  =response.choices[0].message.content
    #4.
    messages.pop(0)   #剔除system
    messages.append({"role": "assistant", "content": ai_res})
    session_data["messages"] = messages
    # 5.
    with open(f"sessions/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    # 6.
    return ai_res



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
#创建接收数据的类对象
class ChatRequest(BaseModel):
    session_id: str
    message: str


#定义路径操作函数 ---》http://127.0.0.1:8000/
@app.get("/")
def read_root():
    """
    浏览器输入http://127.0.0.1:8000/ 也就是向服务器发送get请求 这个请求 会 执行相应装饰器的函数

    :return: 把服务器上的 HTML 文件作为响应发出去
    """
    return FileResponse("static/index.html")

@app.post("/api/sessions")
def create_session():
    """
    通过抓包
    发现请求 URL  http://127.0.0.1:8000/api/sessions  前端像服务器发送请求就会执行相应装饰器装饰的函数
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




@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    获取前端用户的输入
    请求 URL         http://127.0.0.1:8000/api/chat
    Request method  POST
    Request pyload  {"session_id":"对话id","message":"用户输入"} 创建basemodel的类 会把json自动转化为对象(request)的属性
    将用户输入传递给模型得到模型回答
    :return:       json格式{"code":200,"message":"成功" ,data:ai返回的消息} 用fastapi自带的类完成 会把传入的参数转化为json格式
    """
    ai_res = chat_with_ai(request.session_id, request.message)

    return ApiResponse(code=200, message="成功", data=ai_res)

@app.get("/api/sessions")
def get_sessions():
    """
    获取所有对话的id
    请求 URL         http://127.0.0.1:8000/api/sessions
    Request method  GET
    :return:       json格式{"code":200,"message":"成功" ,data:对话id列表}
    """
    sessions_list = os.listdir("sessions")
    sessions = [session.split(".")[0] for session in sessions_list]
    sessions.sort(reverse=True)

    return ApiResponse(code=200, message="成功", data=sessions)

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """
    get请求 参数没有放在？后面 而是放在了路径中 这种叫做路径参数
    我们可以在装饰器中添加通配符 {session_id} 来捕获路径参数
    函数的传参要和通配符一致
    获取指定会话信息 加载出来
    请求 URL  http://127.0.0.1:8000/api/sessions/2026-11-10_15-37-27
    Request m ethod GET
    :return:       json格式{"code":200,"message":"成功" ,data:对话内容}
    """
    with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
        session_data = json.load(f)

    return ApiResponse(code=200, message="加载指定会话成功", data=session_data)

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """
    删除指定会话信息
    请求 URL  http://127.0.0.1:8000/api/sessions/2026-11-10_15-37-27
    Request method  delete
    :return:       json格式{"code":200,"message":"成功" ,data:null}
    """
    if os.path.exists(f"sessions/{session_id}.json"):
       os.remove(f"sessions/{session_id}.json")
    return ApiResponse(code=200, message="删除指定会话成功",data=None)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
