from functools import wraps  
import inspect
import json
import sys
import types
from .utils import func_cache
from .modules import func_actuator

__AIPY_MASK__ = "# __AIpy_Code_written_by_AI__ #"

def run(func,__code__,kwargs):
    try:
        if "ans" not in kwargs:kwargs["ans"] = None
        exec(__code__,kwargs)
        return kwargs["ans"]
    except Exception as e:
        raise Exception('Incorrect AI-generated code').with_traceback(e.__traceback__)

def write_code(func,__code__):
    file_path = inspect.getfile(func)
    encoding = sys.getdefaultencoding()
    with open(file_path,"r",encoding=encoding) as f:
        file_data = f.readlines()
    source_lines, starting_line_no = inspect.getsourcelines(func)
    first_line = source_lines[0]
    last_line = source_lines[-1]
    ori_length = len(source_lines)
    
    if last_line[-1] != "\n":source_lines[-1] += "\n"
    
    space_num = len(first_line) - len(first_line.lstrip())
    if last_line[0] == " ":space_num += 4
    elif last_line[0] == "\t":space_num += 1
    else:raise Exception("[Error] Unknown indentation character")
    space = last_line[0] * space_num
    
    for i,line in enumerate(source_lines):
        if line.strip() == __AIPY_MASK__:
            source_lines = source_lines[:i]
            break
        
    codes = [space + (line.replace("    ",'\t') if last_line[0] == "\t" else line) + '\n' for line in __code__.split("\n")]
    codes.append(space + "return ans\n")
    
    source_lines = file_data[:starting_line_no-1] + source_lines + [space + __AIPY_MASK__ + '\n'] + codes + file_data[starting_line_no-1+ori_length:]
    with open(file_path,"w",encoding=encoding) as f:
        for line in source_lines:
            f.write(line)


def ai_func(force=False):
    def decorator(func):
        if hasattr(sys, "ps1"): raise Exception("[Error] Please run in script mode")
        
        source_lines, starting_line_no = inspect.getsourcelines(func)   
        if not force:     
            for i,line in enumerate(source_lines):
                if line.strip() == __AIPY_MASK__:return func
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = func_cache(func,args,kwargs)
            if force:cache = cache_manager.add_cache(mode="AUTO")
            else:cache = cache_manager.get_cache(mode="AUTO")

            if cache["mode"] == "ACT":
                actuator = func_actuator(model = cache_manager.meta["model"],temperature = cache_manager.meta["temperature"],url = cache_manager.meta["url"])
                try:
                    ret = actuator.generate(cache_manager.func.__doc__,cache_manager.arguments,cache_manager.ret_type)
                except Exception as e:raise Exception(f"[Error] AI generated error ({e})").with_traceback(e.__traceback__)
                try:
                    ret = json.loads(ret)
                    try:
                        if cache_manager.ret_type in {int,str,float,complex,bool,set,list,dict,tuple}:ret = cache_manager.ret_type(ret)
                    except:pass
                except:raise Exception("[Error] Incorrect AI-generated answer")
            else:
                if hasattr(sys, "ps1"):
                    print("[warn] Run in interactive mode.")
                else:write_code(func,cache["data"])
                ret = run(func,cache["data"],cache_manager.arguments)

            return ret
        return wrapper
    return decorator

def ai_code(force = False):
    def decorator(func):        
        source_lines, starting_line_no = inspect.getsourcelines(func)   
        if not force:     
            for i,line in enumerate(source_lines):
                if line.strip() == __AIPY_MASK__:return func

        @wraps(func)
        def wrapper(*args, **kwargs):      
            cache_manager = func_cache(func,args,kwargs)
            if force:cache = cache_manager.add_cache(mode="CVT")
            else:cache = cache_manager.get_cache(mode="CVT")

            if hasattr(sys, "ps1"):
                print("[warn] Run in interactive mode.")
            else:write_code(func,cache["data"])
            ret = run(func,cache["data"],cache_manager.arguments)
        
            return ret
        
        return wrapper
    return decorator

def ai_act():
    def decorator(func):
        if hasattr(sys, "ps1"): raise Exception("[Error] Please run in script mode")
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = func_cache(func,args,kwargs)
            # cache = cache_manager.get_cache(mode="ACT")

            actuator = func_actuator(model = cache_manager.meta["model"],temperature = cache_manager.meta["temperature"],url = cache_manager.meta["url"])
            try:
                ret = actuator.generate(cache_manager.func.__doc__,cache_manager.arguments,cache_manager.ret_type)
            except Exception as e:raise Exception(f"[Error] AI generated error ({e})").with_traceback(e.__traceback__)
            try:
                ret = json.loads(ret)
                try:
                    if cache_manager.ret_type in {int,str,float,complex,set,list,dict,tuple}:ret = cache_manager.ret_type(ret)
                    elif cache_manager.ret_type == bool:ret = str(ret).lower().strip() == "true"
                except:pass
            except:raise Exception("[Error] Incorrect AI-generated answer")

            return ret
        return wrapper
    return decorator
