from src.services.message_classifier import message_classifier

test_messages = [
    'How do I make pasta?',
    'Add milk to my shopping list',
    'What\'s the price of tomatoes?',
    'Remove milk from my list',
    'Hello, how are you?'
]

print('Message Classification Results:')
print('-' * 50)
for msg in test_messages:
    result = message_classifier.classify_message(msg)
    print(f'Message: {msg}')
    print(f'Classification: {result}\n') 