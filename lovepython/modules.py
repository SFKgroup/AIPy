import requests 
import json
import time
import copy
import os

def args_format(args:dict,has_value = True):
    res = "输入参数如下: \n"
    multi_args = []
    for name,value in args.items(): 
        if name[0] == "*":
            multi_args = value
        else:res += f" - 参数{name}，格式为: {type(value).__name__}" + f"，取值为: {value}\n" if has_value else "\n"
    if multi_args and has_value:res += f"此外还输入多个参数，分别为: {', '.join([f'{v}' for v in multi_args])}\n"

    return res

class chat_api(object):
    def __init__(self,sys_prompt = None,model = None,temperature = 1,url="http://localhost:11434/api/chat",api_key="ollama"):
        self.model = model if model is not None else "qwen2.5:32b"
        current_date = time.strftime("%Y-%m-%d %A", time.localtime())
        self.url = url
        if "v1" not in url and "chat" not in url:self.url += "/v1/chat/completions"
        self.temperature = temperature
        self.api_key = api_key

        self.msg = [{
            'role': 'system', 
            'content': sys_prompt if sys_prompt else f'今天是{current_date}，一年中最有生产力的一天。\n请深呼吸，一步一步地思考。'
        }]
        #self.send_stream()

    def chat(self,message):
        self.msg.append({'role': 'user', 'content': message})
        res = self.send_stream()
        res = res.replace("*", "")
        return res

    def send_stream(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization":"Bearer " + self.api_key
        }
        data = {
            "model": self.model,
            "messages": self.msg,
            "stream": False,
            "temperature": self.temperature
        }
        
        response = requests.post(self.url, headers=headers, data=json.dumps(data),timeout=600)

        if response.status_code == 200:
            response_text = response.text
            #print('text:',response_text)
            data = json.loads(response_text)
            actual_response = data["choices"][0]["message"]
            self.msg.append(actual_response)
            #print(self.msg)
            return actual_response['content']
        else:
            raise Exception(f"Network error {response.status_code} : {response.text}")

    def get_msg(self):return copy.deepcopy(self.msg)
    
    def load_msg(self,msg):self.msg = msg
    
    def clear_msg(self):self.msg = self.msg[:1]

# will be removed
class generate_api(object):
    def __init__(self,sys_prompt = None,model = None,temperature = 1,url = "http://localhost:11434/api/generate",api_key="ollama"):
        self.model = model if model is not None else "qwen2.5:32b"
        self.temperature = temperature
        self.url = url
        
        if "v1" not in url and "generate" not in url:self.url += "/v1/completions"
        self.api_key = api_key
        self.sys_prompt = sys_prompt if sys_prompt else f'请补全以下内容'

    def send_stream(self,prompt):
        
        headers = {
            "Content-Type": "application/json",
            "Authorization":"Bearer " + self.api_key
        }
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": self.sys_prompt,
            "temperature": self.temperature
        }
        
        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["text"]
        else:
            raise Exception(f"Network error {response.status_code} : {response.text}")

class mode_select(chat_api):
    def __init__(self,model = None,temperature = 1,url = "http://localhost:11434/api/generate",api_key="ollama"):
        super().__init__(f"""
你是一个高级软件工程师，你可以解决一切软件相关的问题。
我们会给你一个需求，你需要判断这个需求能否使用30行以内的简单python代码实现。(不定义函数和类，不调用任何第三方Python库)
请从代码复杂程度，代码长度，可读性等多个角度对这个需求进行判断，并充分考虑边缘情况。
如果该需求可以使用30行以内的简单python代码实现，请返回"可以"，否则请返回"不行"。
请确保只返回"可以"或"不行"这两个字符，**请勿返回其他内容**。

例1：
Q : 生成输入数字区间范围内的斐波那契数列
A : 可以

例2：
Q : 根据输入的二维棋盘数组，返回最优的五子棋落子位置
A : 不行

例3：
Q : 输出现在是今年的第几周
A : 可以
""",model,temperature,url,api_key)
    def choose(self,describe):
        res = self.chat(f"""{describe}
请判断这个需求能否使用30行以内的简单python代码实现，如果可以请返回"可以"，否则请返回"不行"。""")
        # print(res)
        self.clear_msg()
        return "可以" in res
    
class code_writer(chat_api):
    def __init__(self,model = None,temperature = 1,url = "http://localhost:11434/api/generate",api_key="ollama"):
        super().__init__(f"""
你是一个高级软件工程师，你可以解决一切软件相关的问题。
我们会给你一个需求，请你使用尽可能简单的python代码实现。(不定义函数和类，不调用任何第三方Python库)
请注意输入参数和输出参数的类型，代码中不要定义任何的函数和类，结果储存在名为ans的变量中。
你只需要输出可执行的代码，不要输出任何解释性的文本和不可执行的文本。
请直接使用输入参数作为变量，不要自己定义输入变量或使用其他变量名。
Python代码的返回结果不必print输出或return输出，结果必须赋值给ans变量。

#### 具体案例如下：
#### 输入 : 
返回一个从小到大排序的随机列表
输入参数如下:
 - 参数length，格式为: int，
 - 参数max_value，格式为: float
 - 参数min_value，格式为: float
输出值格式为: list
#### 输出 : 
import random
data = [random.random()*(max_value-min_value) + min_value for i in range(length)]
ans = sorted(data)

**注意** : 请直接输出可以执行的Python代码，输出内容严格符号Python语法，不需要任何额外的解释。
""",model,temperature,url,api_key)
    def generate(self,describe,args,ret_type):
        res = self.chat(f"{describe}\n{args_format(args)}\n" + f"输出值格式为: {ret_type.__name__}\n" if ret_type is not None else "\n" + "注：请直接使用输入参数作为变量，将返回结果赋值给ans变量") 
        # print(res)
        self.clear_msg()
        return res

class code_cvt(chat_api):
    def __init__(self,model = None,temperature = 1,url = "http://localhost:11434/api/generate",api_key="ollama"):
        super().__init__(f"""
你是一个高级软件工程师，你可以解决一切软件相关的问题。
我们会给你一段描述运行逻辑的文本，请你使用尽可能简单的python代码实现。(不定义函数和类，不调用任何第三方Python库)
请注意输入参数和输出参数的类型，代码中不要定义任何的函数和类，结果储存在名为ans的变量中，请注意逻辑描述文本与Python代码的含义需要严格对应。
你只需要输出可执行的代码，不要输出任何解释性的文本和不可执行的文本。
Python代码的返回结果不必print输出或return输出，结果必须赋值给ans变量。

#### 具体案例如下：
#### 输入 : 
输入参数如下:
 - 参数length，格式为: int，
 - 参数max_value，格式为: int
 - 参数min_value，格式为: int
功能逻辑为: 
建立一个data数组。
循环length次，每次生成一个随机的数，范围在min_value和max_value之间，加入数组中
对数组从小到大排序并返回
输出值格式为: list
#### 输出 : 
import random
data = []
for i in range(length):
    data.append(random.randint(min_value,max_value))
ans = sorted(data)


**注意** : 请直接输出可以执行的Python代码，输出内容严格符号Python语法，不需要任何额外的解释。
""",model,temperature,url,api_key)
    def generate(self,describe,args,ret_type):
        res = self.chat(f"{args_format(args,has_value=False)}\n功能逻辑为: \n{describe}\n" + f"输出值格式为: {ret_type.__name__}\n" if ret_type is not None else ""+ "注：请将返回结果赋值给ans变量")
        # print(res)
        self.clear_msg()
        return res

class func_actuator(chat_api):
    def __init__(self,model = None,temperature = 1,url = "http://localhost:11434/api/generate",api_key="ollama"):
        current_date = time.strftime("%Y-%m-%d %A", time.localtime())
        super().__init__(f"""今天是{current_date}，一年中最有生产力的一天。你是一个智能助理，负责处理各种需求。请深呼吸，一步一步地思考。
你需要根据给定的一系列输入，根据需求描述，返回输出结果。
输出结果必须是JSON格式(或要求的Python格式)，请确保JSON格式正确，不要出现除JSON字符串以外的任何字符。不需要解释性文本和不可解析的字符。

#### 具体案例如下：
#### 输入 : 
请返回列表中第2大、第4大和第5大的数字
输入参数如下:
 - 参数array，格式为: list，取值为: [7,4,6,5,8,2,4,1,10,3,0]
输出值格式为: list
#### 输出 :
[8,6,5]

**注意** : 返回结果中不得出现除JSON字符串以外的任何字符。
""",model,temperature,url,api_key)
        
    def generate(self,describe,args,ret_type):
        res = self.chat(f"{describe}\n{args_format(args)}\n" + f"输出值格式为: {ret_type.__name__}\n" if ret_type is not None else "\n") 
        # print(res)
        self.clear_msg()
        return res


if __name__ == '__main__':
    pass