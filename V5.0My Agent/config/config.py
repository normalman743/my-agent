# config.py
import os
config = {
    'apis': {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'OpenWeather_API': os.getenv('OPENWEATHER_API_KEY', ''),
        'Google_Search_API': os.getenv('GOOGLE_SEARCH_API_KEY', ''),
        'SCE_ID': os.getenv('GOOGLE_CSE_ID', '')
    },
    'allowed_libraries': {
        'requests': True,  # 请求库，用于 HTTP 请求
        'numpy': True,     # 数值计算库
        'pandas': True,    # 数据分析库
        'matplotlib': True, # 绘图库
        'scipy': True,     # 科学计算库
        'json': True,      # JSON 处理库
        're': True,        # 正则表达式库
        'datetime': True,  # 日期时间处理库
        'itertools': True, # 迭代器操作库
        'os': True,        # 操作系统接口库
    }
}
