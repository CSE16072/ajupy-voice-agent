
from modules.memory import (
    create_database,
    save_message,
    get_messages
)

create_database()

save_message("user", "What is AI?")
save_message("assistant", "AI stands for Artificial Intelligence.")

messages = get_messages()

for message in messages:
    print(message["role"], ":", message["content"])
