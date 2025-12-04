import os
import subprocess
import json
import inspect
import hashlib
import shutil
from .modules import mode_select,code_writer,code_cvt

DEFAULT_META = {
    "model" : "qwen2.5:32b",
    "url" : "http://localhost:11434/",
    "temperature" : 0.7,
    "api_key" : "ollama"
}

package_dir = os.path.dirname(os.path.abspath(__file__))
meta_path = os.path.join(package_dir,"meta.json")
if os.path.isfile(meta_path): 
    with open(meta_path,"r",encoding="utf-8") as f: 
        DEFAULT_META.update(json.load(f))
else:
    with open(meta_path,"w",encoding="utf-8") as f: 
        json.dump(DEFAULT_META,f,indent=4,ensure_ascii=False)

class func_cache(object):
    def __init__(self,func,args,kwargs):
        self.path = os.path.abspath('./')
        self.cache_path = os.path.join(self.path,"__pycache__",".aipy")
        self.init_proj()
        self.get_arguments(func,args,kwargs)

    def init_proj(self):
        self.meta = DEFAULT_META
        meta_path = os.path.join(self.cache_path,"meta.json")
        if os.path.exists(meta_path): 
            with open(meta_path,"r",encoding="utf-8") as f: 
                self.meta.update(json.load(f))
            return
        if not os.path.exists(os.path.join(self.path,"__pycache__")): os.mkdir(os.path.join(self.path,"__pycache__"))
        if not os.path.exists(self.cache_path): os.mkdir(self.cache_path)
        if os.name == 'nt': 
            subprocess.call(['attrib', '+h', self.cache_path])

        with open(meta_path,"w",encoding="utf-8") as f: 
            json.dump(self.meta,f)

    def get_cache(self,mode="AUTO"):
        file_hash = hashlib.sha224(inspect.getfile(self.func).encode("utf-8")).hexdigest()
        file_path = os.path.join(self.cache_path,file_hash+'.json')
        if not os.path.exists(file_path): return self.add_cache(mode)

        func_name = self.func.__name__
        describe  = self.func.__doc__
        func_hash = hashlib.sha224(f"{func_name}::{describe}::{self.arg_hashtext}".encode("utf-8")).hexdigest()
        with open(file_path,"r",encoding="utf-8") as f: 
            cache = json.load(f)
        if func_name in cache and cache[func_name]["hash"] == func_hash: return cache[func_name]
        else:return self.add_cache(mode)
    
    def add_cache(self,mode="AUTO"):
        file_hash = hashlib.sha224(inspect.getfile(self.func).encode("utf-8")).hexdigest()
        file_path = os.path.join(self.cache_path,file_hash+'.json')
        func_name = self.func.__name__
        describe  = self.func.__doc__

        data = {
            "mode":mode,
            "func":func_name,
            "describe":describe,
            "hash":hashlib.sha224(f"{func_name}::{describe}::{self.arg_hashtext}".encode("utf-8")).hexdigest(),
            "data":None 
        }

        if data["mode"] == "AUTO":
            selector = mode_select(**self.meta)
            data["mode"] = "WRITE" if selector.choose(describe) else "ACT"
        
        if data["mode"] == "WRITE":
            writer = code_writer(**self.meta)
            data["data"] = writer.generate(describe,self.arguments,self.ret_type)
        elif data["mode"] == "CVT":
            cvt = code_cvt(**self.meta)
            data["data"] = cvt.generate(describe,self.arguments,self.ret_type)

        if not os.path.isfile(file_path):
            with open(file_path,"w",encoding="utf-8") as f: 
                json.dump({func_name:data},f)
        else:
            with open(file_path,"r",encoding="utf-8") as f: 
                cache = json.load(f)
            cache[func_name] = data
            with open(file_path,"w",encoding="utf-8") as f: 
                json.dump(cache,f)

        return data

    def get_arguments(self,func,args,kwargs):
        sig = inspect.signature(func)
        params = sig.parameters
        arr = 0
        arguments = kwargs.copy()
        args_name = None

        is_POSITIONAL = True
        for name, param in params.items():
            if name in arguments.keys():continue
            if arr < len(args) and is_POSITIONAL:
                if str(param.kind) == "VAR_POSITIONAL":
                    args_name = "*"+name
                    arguments[args_name] = [args[arr]]
                    is_POSITIONAL = False
                else:
                    arguments[name] = args[arr]
                arr += 1
            elif param.default != param.empty:arguments[name] = param.default
        if arr < len(args):
            if args_name is None:
                raise TypeError(f"{self.func.__name__}() takes {len(params)} positional arguments but 6 were given")
            arguments[args_name] += args[arr:]
            arguments[args_name[1:]] = tuple(arguments[args_name])

        self.arguments = arguments
        self.arg_hashtext = json.dumps(list(self.arguments.keys()))
        self.func = func
        self.ret_type = func.__annotations__['return'] if 'return' in func.__annotations__ else None

    def clear_cache(self):
        shutil.rmtree(self.cache_path)