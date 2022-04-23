message_dict = {
    "sender": ["Enter a valid email address."],
    "subject": ["This field is required."],
}

messages = "\n".join(
    [f"{key}: {', '.join(value)}" for key, value in message_dict.items()]
)


print(messages)
