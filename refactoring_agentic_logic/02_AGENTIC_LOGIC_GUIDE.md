# AGENTIC LOGIC GUIDE

## Intelligent Processing Patterns

### Context Management Architecture
- **State Preservation:** Maintain conversation history and user preferences across API requests
- **Context Cleanup:** Clear old conversation history after 10+ messages to prevent bloat
- **Context Limits:** Maximum 5 conversation entries for AI context, 1000 character limit
- **Context Security:** Sanitize user inputs, validate AI responses, protect sensitive data
- **Context Validation:** Ensure context data is valid and safe for AI processing

### Decision Making & Classification
- **Pattern Recognition:** Use BART model to identify user intent (recipe, add item, item info, etc.)
- **Confidence Scoring:** Measure certainty of classification with thresholds (0.6-0.7)
- **Fallback Strategies:** Default to "Others" category when confidence is low
- **Multi-turn Context:** Handle complex conversations with shopping list context
- **User Preference Integration:** Incorporate dietary preferences into AI responses

### Response Generation & Validation
- **Service Orchestration:** Coordinate ChatService, AIService, ShoppingListService
- **Response Validation:** Ensure responses are safe and appropriate using prompt safety
- **Fallback Responses:** Provide helpful responses when AI services fail
- **Response Enhancement:** Add context and personalization based on user preferences
- **Quality Assurance:** Monitor and improve response quality and relevance

## Enhanced Shopping List Logic

### Current System Analysis
- **Direct Extraction**: For "Item Addition type" messages, uses regex patterns and common food lists
- **AI Extraction**: For other message types, uses Gemini to extract ingredients from conversation
- **Simple Addition**: Always adds items to list, no removal or modification logic
- **Limited Context**: Only considers recent conversation history

### Identified Issues
- ❌ **No Item Removal**: Can't handle "I don't want tomatoes" or "remove X"
- ❌ **No Quantity Management**: Can't handle "2 bags of chips" or "3 apples"
- ❌ **Poor Context Awareness**: Doesn't understand recipe context vs. direct shopping
- ❌ **No List Management**: Can't handle "clear my list" or "show my list"
- ❌ **Weak Item Recognition**: Relies on hardcoded food lists and simple patterns

### Target Scenarios & Logic Routes

#### Scenario 1: Recipe → Shopping List Management
**User Flow**: "Give me a pasta recipe" → "I don't want tomatoes" → "Also add chewing gum and milk"

**Expected Behavior**:
1. Recipe provides ingredients: ["pasta", "tomatoes", "garlic", "olive oil"]
2. User removes tomatoes: List becomes ["pasta", "garlic", "olive oil"]
3. User adds items: List becomes ["pasta", "garlic", "olive oil", "chewing gum", "milk"]

#### Scenario 2: Direct Shopping List Management
**User Flow**: "Add milk and bread" → "Remove bread" → "Add 2 apples"

**Expected Behavior**:
1. Add items: List becomes ["milk", "bread"]
2. Remove bread: List becomes ["milk"]
3. Add with quantity: List becomes ["milk", "2 apples"]

#### Scenario 3: Context-Aware Shopping
**User Flow**: "I'm making lasagna" → "What do I need?" → "I have cheese already"

**Expected Behavior**:
1. AI suggests lasagna ingredients: ["pasta sheets", "ground beef", "tomatoes", "cheese", "garlic"]
2. User indicates they have cheese: List becomes ["pasta sheets", "ground beef", "tomatoes", "garlic"]

## Enhanced Prompt Engineering

### 1. Shopping List Action Recognition Prompt
```python
SHOPPING_ACTION_PROMPT = """
Analyze the user's message and determine the shopping list action needed.

Available actions:
- ADD: User wants to add items to shopping list
- REMOVE: User wants to remove items from shopping list
- CLEAR: User wants to clear entire shopping list
- SHOW: User wants to see current shopping list
- MODIFY: User wants to change quantities or items

Current shopping list: {current_list}

User message: "{user_message}"

Return JSON format:
{
    "action": "ADD|REMOVE|CLEAR|SHOW|MODIFY",
    "items": ["item1", "item2"],
    "quantities": {"item1": 2, "item2": 1},
    "confidence": 0.8
}
"""
```

### 2. Item Extraction with Context Prompt
```python
CONTEXTUAL_EXTRACTION_PROMPT = """
Extract shopping list items from the conversation with context awareness.

Conversation history:
{chat_history}

Current shopping list: {current_list}

User preferences: {user_preferences}

Instructions:
- Extract items mentioned for shopping
- Consider recipe context if applicable
- Handle quantities (e.g., "2 apples" → {"apples": 2})
- Identify removals (e.g., "I don't want X" → remove X)
- Consider user preferences (e.g., vegetarian alternatives)

Return JSON format:
{
    "items_to_add": ["item1", "item2"],
    "items_to_remove": ["item3"],
    "quantities": {"item1": 2, "item2": 1},
    "context": "recipe_shopping|direct_shopping|modification"
}
"""
```

### 3. Recipe Integration Prompt
```python
RECIPE_SHOPPING_PROMPT = """
Generate a recipe and provide shopping list items.

Recipe request: "{recipe_request}"
User preferences: {user_preferences}
Current shopping list: {current_list}

Instructions:
- Generate a detailed recipe
- Extract all ingredients needed
- Check against current shopping list
- Suggest only missing ingredients
- Consider user preferences for alternatives

Return JSON format:
{
    "recipe": {
        "name": "Recipe Name",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": ["step1", "step2"]
    },
    "shopping_items": ["missing_ingredient1", "missing_ingredient2"],
    "quantities": {"missing_ingredient1": 2}
}
"""
```

## Enhanced Logic Routes

### Route 1: Smart Item Addition
```python
def process_smart_addition(user_message: str, current_list: List[str], context: str) -> Dict:
    """
    Smart addition with context awareness.
    """
    # Extract items with AI
    extraction_result = ai_service.extract_items_with_context(
        user_message, current_list, context
    )
    
    # Handle quantities
    for item, quantity in extraction_result["quantities"].items():
        if quantity > 1:
            item_with_qty = f"{quantity} {item}"
            # Add to list with quantity
        else:
            # Add to list normally
    
    return updated_list
```

### Route 2: Intelligent Item Removal
```python
def process_smart_removal(user_message: str, current_list: List[str]) -> Dict:
    """
    Handle item removal with fuzzy matching.
    """
    # Extract items to remove
    items_to_remove = ai_service.extract_removal_items(user_message, current_list)
    
    # Fuzzy match against current list
    for item in items_to_remove:
        matched_item = fuzzy_match(item, current_list)
        if matched_item:
            current_list.remove(matched_item)
    
    return current_list
```

### Route 3: Context-Aware Recipe Shopping
```python
def process_recipe_shopping(recipe_request: str, current_list: List[str], preferences: Dict) -> Dict:
    """
    Generate recipe and suggest missing ingredients.
    """
    # Generate recipe with AI
    recipe_result = ai_service.generate_recipe_with_shopping(
        recipe_request, current_list, preferences
    )
    
    # Extract missing ingredients
    missing_items = []
    for ingredient in recipe_result["ingredients"]:
        if ingredient not in current_list:
            missing_items.append(ingredient)
    
    return {
        "recipe": recipe_result["recipe"],
        "shopping_items": missing_items,
        "response": f"I'll add {', '.join(missing_items)} to your shopping list for this recipe."
    }
```

## External Service Integration

### Service Management
- **Centralized Orchestration:** ChatService as single point of control for all services
- **Service Selection:** Use BART for classification, Gemini for response generation
- **Load Balancing:** Handle concurrent requests efficiently
- **Health Monitoring:** Track AI service availability and performance
- **Cost Management:** Monitor Gemini API usage and optimize prompts

### Error Handling & Resilience
- **Retry Mechanisms:** Exponential backoff for AI service failures (3 attempts)
- **Circuit Breakers:** Prevent cascade failures with graceful degradation
- **Graceful Degradation:** Maintain functionality when AI services fail
- **Fallback Strategies:** Manual item extraction when AI extraction fails
- **Error Recovery:** Automatic recovery from transient service failures

### Performance Optimization
- **Response Caching:** Cache common AI responses to reduce API calls
- **Request Batching:** Process multiple items in single AI calls when possible
- **Async Processing:** Non-blocking service calls for better performance
- **Rate Limiting:** Manage API usage within Gemini limits
- **Resource Management:** Efficient use of memory and CPU for AI processing

## Testing Intelligent Logic

### Flow Testing
- **Multi-step Scenarios:** Test complex user journeys (add items → ask recipe → get ingredients)
- **Context Preservation:** Verify conversation state is maintained correctly
- **Intent Recognition:** Test accuracy of message classification
- **Response Relevance:** Ensuring responses match user intent and preferences
- **Error Recovery:** Testing system behavior during AI service failures

### Performance Testing
- **Concurrent Users:** Testing system under multiple simultaneous users
- **Large Context:** Testing with extensive conversation history
- **Complex Operations:** Testing with resource-intensive AI operations
- **Service Failures:** Testing fallback mechanisms and error handling
- **Resource Usage:** Monitoring memory and CPU consumption during AI processing

### Quality Assurance
- **Response Validation:** Ensuring responses are appropriate and helpful
- **Safety Checks:** Preventing harmful or inappropriate content
- **Consistency Testing:** Verifying similar inputs produce consistent outputs
- **User Experience:** Testing overall user satisfaction with responses
- **Cost Monitoring:** Tracking and optimizing AI API usage

## Implementation Guidelines

### Code Organization
- **Separation of Concerns:** Keep intelligent logic separate from business logic
- **Modular Design:** Create reusable service components (AIService, MessageClassifier)
- **Configuration Management:** Centralize AI service configuration
- **Error Handling:** Implement comprehensive error handling for AI services
- **Logging & Monitoring:** Track AI service usage and performance

### Best Practices
- **Prompt Engineering:** Design effective prompts for Gemini AI service
- **Response Processing:** Clean and validate AI responses
- **Context Management:** Efficiently manage conversation state
- **Security:** Protect sensitive data in AI interactions
- **Scalability:** Design for growth and increased AI usage

### Common Patterns
- **Service Factory:** Create AI services dynamically based on configuration
- **Response Pipeline:** Process AI responses through multiple validation stages
- **Context Manager:** Centralized conversation state management
- **Error Handler:** Comprehensive error handling and recovery for AI services
- **Performance Monitor:** Track and optimize AI system performance

## Quality Metrics

### Success Criteria
- ✅ **Accurate Item Recognition**: 95%+ accuracy in identifying items
- ✅ **Proper Quantity Handling**: Correctly parse "2 apples", "3 bags"
- ✅ **Smart Removal**: Successfully remove items with fuzzy matching
- ✅ **Context Awareness**: Understand recipe vs. direct shopping context
- ✅ **Preference Integration**: Consider dietary preferences in suggestions

### Testing Scenarios
1. **Recipe → Shopping**: "Give me pasta recipe" → "I don't want tomatoes" → "Add milk"
2. **Direct Shopping**: "Add bread and milk" → "Remove bread" → "Add 2 apples"
3. **Context Shopping**: "I'm making lasagna" → "What do I need?" → "I have cheese"
4. **Quantity Management**: "Add 3 bags of chips" → "Change to 2 bags" → "Add 1 apple" 