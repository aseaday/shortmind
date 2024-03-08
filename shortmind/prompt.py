
def make_mindmap_prompt(content, lang="zh"):
    mindmap_prompt = """为下列内容生成一个思维导图用来方便读者了解全文
要求：
1. 使用markdown格式回答，并用 ```markdown 和 ``` 标记
2. 每个节点先提供一个情节的梗概，然后
3. 尽可能详细的覆盖全文的细节内容
章节内容如下:
"""
    return mindmap_prompt + content
