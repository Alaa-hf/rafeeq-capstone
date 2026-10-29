from capstone.starter import compact, MAX_HISTORY_MESSAGES

history = []

# Simulate a long conversation
for i in range(30):
    history.append({
        "role": "user",
        "content": f"Question {i}"
    })
    history.append({
        "role": "assistant",
        "content": f"Answer {i}"
    })

result = compact(history)

print("Original messages:", len(history))
print("Compacted messages:", len(result))
print("Maximum allowed:", MAX_HISTORY_MESSAGES)
print("First message role:", result[0]["role"])

assert len(result) <= MAX_HISTORY_MESSAGES
assert result[0]["role"] == "user"

print("\nPASS: Context compaction works.")