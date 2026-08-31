from app.services.ai_services import analyse_message


test_messages = [
    {
        "text": "Have a nice day",
        "expected": False,
    },
    {
        "text": "Thank you for helping me",
        "expected": False,
    },
    {
        "text": "You are an idiot",
        "expected": True,
    },
    {
        "text": "I hate you",
        "expected": True,
    },
    {
        "text": "Can we meet tomorrow?",
        "expected": False,
    },
]


correct = 0


for test in test_messages:
    result = analyse_message(
        test["text"]
    )

    predicted = result["warning"]

    if predicted == test["expected"]:
        correct += 1

    print(
        "Text:",
        test["text"]
    )

    print(
        "Expected:",
        test["expected"]
    )

    print(
        "Predicted:",
        predicted
    )

    print(
        "Label:",
        result["label"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "--------------------"
    )


accuracy = (
    correct /
    len(test_messages)
) * 100


print(
    f"Accuracy: {accuracy:.2f}%"
)