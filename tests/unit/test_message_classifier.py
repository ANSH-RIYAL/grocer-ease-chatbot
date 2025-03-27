import pytest
from src.services.message_classifier import MessageClassifier
from src.core.constants import CATEGORIES, CATEGORY_EXAMPLES

@pytest.fixture
def classifier():
    return MessageClassifier()

def test_classify_message(classifier):
    """Test message classification with various examples."""
    # Test recipe type
    assert classifier.classify_message("How do I make pasta?") == "Recipe type"
    assert classifier.classify_message("What's the recipe for chocolate cake?") == "Recipe type"
    
    # Test item addition type
    assert classifier.classify_message("Add milk to my shopping list") == "Item Addition type"
    assert classifier.classify_message("Put bread on the list") == "Item Addition type"
    
    # Test item information type
    assert classifier.classify_message("What's the price of tomatoes?") == "Item Information type"
    assert classifier.classify_message("Is milk available?") == "Item Information type"
    
    # Test update cart type
    assert classifier.classify_message("Remove milk from my list") == "Update Cart type"
    assert classifier.classify_message("Clear my shopping list") == "Update Cart type"
    
    # Test others type
    assert classifier.classify_message("Hello") == "Others"
    assert classifier.classify_message("What's the weather?") == "Others"

def test_invalid_input(classifier):
    """Test handling of invalid inputs."""
    assert classifier.classify_message("") == "Others"
    assert classifier.classify_message(None) == "Others"
    assert classifier.classify_message(123) == "Others"

def test_get_category_examples(classifier):
    """Test getting examples for each category."""
    for category in CATEGORIES:
        examples = classifier.get_category_examples(category)
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all(isinstance(example, str) for example in examples)
        assert examples == CATEGORY_EXAMPLES[category] 