# AIpy(love-python): Seamless AI Integration into Python

**AIpy** is a third-party library designed to effortlessly embed AI capabilities into Python, allowing users to solve problems through natural language descriptions and gradually transition to writing code. Inspired by the GitHub project [vibesort](https://github.com/vibesort), AIpy aims to go beyond simple sorting by enabling AI to handle a wide range of tasks directly.

## Key Features

- **@ai_func**: Directly uses AI to perform calculations. Ideal for complex problems (slower but low error rate).
- **@ai_act**: Generates Python code from natural language descriptions. Best for simple tasks (faster but moderate error rate).
- **@ai_code**: Automatically selects the most suitable method (AI calculation or code generation) for any problem (fast and low error rate).

## How It Works

1. **Function Documentation**: AIpy parses the function's docstring, parameters, and return types.
2. **AI Invocation**: Based on the analysis, it calls the large language model to generate either:
   - A direct calculation result (`@ai_func`)
   - Executable Python code (`@ai_act`)
   - Optimized code generation (`@ai_code`)
3. **Result Handling**: The result is automatically converted to the expected type and returned.

## Installation

```bash
pip install love-python
```

## Quick Start

### Example: Solving a Problem with @ai_code

```python
from lovepython import ai_code

@ai_code
def find_max(numbers: list[int]) -> int:
    """
    Find the maximum number in a list.
    """
    # AI will fill this in

print(find_max([3, 1, 4, 1, 5]))  # Output: 5
```

### Example: Using @ai_func for Calculation

```python
from lovepython import ai_func

@ai_func
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle with the given radius.
    """
    # AI will compute the result directly

print(calculate_area(5.0))  # Output: 78.53981633974483
```

## Model Configuration

AIpy supports using OpenAI format APIs for computation and code generation. You can configure the model information used in the current path at `./__pycache__/.aipy/meta.json`, or modify the `meta.json` file in the directory where this library is located to set default configurations. If no changes are made, the local ollama will be used as the inference API by default, for example:

```json
{
    "model": "qwen2.5:32b",
    "url": "http://localhost:11434/",
    "temperature": 0.7,
    "api_key": "ollama"
}
```

## Performance Optimization

To minimize token usage and execution time, AIpy caches generated code in `./__pycache__/.aipy/`. If the function name and prompt remain unchanged, the cached code is reused. You can force regeneration by setting `force=True` in the decorator.


---

# AIpy(爱-Python)：让AI无缝嵌入Python

**AIpy** 是一个第三方库，旨在将AI能力无缝嵌入Python，使用户能够通过自然语言描述解决问题，并逐步过渡到编写代码。灵感来源于GitHub项目[vibesort](https://github.com/vibesort)，AIpy的目标是超越简单的排序，让AI直接处理各种任务。

## 主要功能

- **@ai_func**：直接使用AI完成计算。适合复杂问题（速度较慢但错误率低）。
- **@ai_act**：从自然语言描述生成Python代码。适合简单任务（速度快但错误率中等）。
- **@ai_code**：自动选择最合适的处理方式（AI计算或代码生成），适用于任何问题（速度快且错误率低）。

## 工作原理

1. **函数文档解析**：AIpy解析函数的注释、参数和返回类型。
2. **调用AI**：根据分析，调用大语言模型生成：
   - 直接计算结果（`@ai_func`）
   - 可执行Python代码（`@ai_act`）
   - 优化后的代码生成（`@ai_code`）
3. **结果处理**：结果自动转换为预期类型并返回。

## 安装

```bash
pip install love-python
```

## 快速入门

### 示例：使用@ai_code解决问题

```python
from lovepython import ai_code

@ai_code
def find_max(numbers: list[int]) -> int:
    """
    找出列表中的最大数。
    """

print(find_max([3, 1, 4, 1, 5]))  # 输出: 5
```

### 示例：使用@ai_func进行计算

```python
from lovepython import ai_func

@ai_func
def calculate_area(radius: float) -> float:
    """
    计算给定半径的圆的面积。
    """

print(calculate_area(5.0))  # 输出: 78.53981633974483
```

## 模型配置

AIpy支持使用OpenAI格式的API进行计算和代码生成。您可以在`./__pycache__/.aipy/meta.json`中配置当前路径下使用的模型信息，或修改本库所在的文件目录中的`meta.json`的文件，以设置默认配置。如无修改，默认使用本地ollama作为推理API，样例如下：

```json
{
    "model": "qwen2.5:32b",
    "url": "http://localhost:11434/",
    "temperature": 0.7,
    "api_key": "ollama"
}
```


## 性能优化

为减少Token消耗和运行时间，AIpy将生成的代码缓存到`./__pycache__/.aipy/`。如果函数名和提示词不变，将重用缓存代码。您可以在装饰器参数中设置`force=True`强制更新。
