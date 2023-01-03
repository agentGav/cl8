import requests


def send_simple_message():
    return requests.post(
        "https://api.eu.mailgun.net/v3/mg.greening.digital/messages",
        auth=("api", "0a7d5001025bb3d09649511c478889be-a83a87a9-cb42dc2e"),
        data={
            "from": "Constellation robot <icebreaderone@mg.greening.digital>",
            "to": ["chris@productscience.co.uk"],
            "subject": "Hello",
            "text": "Testing some Mailgun.",
        },
    )


res = send_simple_message()

print(res)
