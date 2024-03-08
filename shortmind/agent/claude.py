import anthropic
import os

def ask_cluade_opus(message):
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=2048,
    messages=[
        message
        # {"role": "user", "content": "Hello, Claude"}
    ]
    )
    return message

if __name__ == "__main__":
    msg = ask_cluade_opus(
        {
            "role": "user",
            "content": "Hello",
        })
    print(msg.content[0].text)

