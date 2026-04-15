import tiktoken
from config.Token import TOKEN


def get_token_prices(model_name='Claude 3.5 Sonnet', provider='anthropic'):
    """根据模型名称和提供商获取token价格"""
    prices = TOKEN.get(provider, TOKEN['default'])
    return prices.get(model_name, prices['default'])

def count_tokens(text, model_name="gpt-4"):
    """计算给定文本的token数量"""
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

def calculate_cost(input_tokens, output_tokens, model_name="gpt-4o-mini", provider='openai'):
    """计算给定token数量的成本"""
    prices = get_token_prices(model_name, provider)
    input_price = prices["input"]
    output_price = prices["output"]

    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost
    
    return input_cost, output_cost, total_cost
