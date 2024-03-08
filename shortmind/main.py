from shortmind.loader.epub import EPUBBookLoader
from shortmind.agent.claude import ask_cluade_opus
from shortmind.prompt import make_mindmap_prompt


if __name__ == "__main__":
    epub = EPUBBookLoader("test.epub")
    items = epub.list_items()
    body = "".join(items[4])
    resp = ask_cluade_opus({"role": "user", "content": make_mindmap_prompt(body)})
    print(resp.content[0].text)
    