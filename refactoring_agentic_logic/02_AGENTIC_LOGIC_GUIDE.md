# AGENTIC LOGIC GUIDE

## Intelligent Processing Patterns

### Context Management Architecture
- **State Preservation:** Maintain conversation history and user preferences across API requests
- **Context Cleanup:** Clear old conversation history after 10+ messages to prevent bloat
- **Context Limits:** Maximum 5 conversation entries for AI context, 1000 character limit
- **Context Security:** Sanitize user inputs, validate AI responses, protect sensitive data
- **Context Validation:** Ensure context data is valid and safe for AI processing

### Decision Making & Classification
- **Pattern Recognition:** Use Gemini API to identify user intent (recipe, add item, item info, etc.)
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

## Agentic Shopping List Management

### Core Data Structures

#### **1. Enhanced Shopping List State**
```python
ShoppingListState = {
    "items": [
        {
            "name": "apples",
            "quantity": 2,
            "unit": "pieces",
            "source": "direct_addition",
            "added_at": "2024-01-15T10:30:00Z",
            "removed": False
        }
    ],
    "removed_items": [
        {
            "name": "tomatoes",
            "removed_at": "2024-01-15T10:31:00Z",
            "reason": "user_request"
        }
    ],
    "action_history": [
        {
            "type": "item_addition",
            "items": ["apples"],
            "quantity": 2,
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "type": "item_removal",
            "items": ["tomatoes"],
            "reason": "user_request",
            "timestamp": "2024-01-15T10:31:00Z"
        }
    ]
}
```

#### **2. User Preferences Context**
```python
UserPreferences = {
    "dietary": "vegetarian",
    "allergies": ["nut allergy"],
    "preferences": ["no_dairy"],
    "restrictions": []
}
```

#### **3. Conversation Context**
```python
ConversationContext = {
    "current_flow": "recipe_shopping",
    "active_recipe": "lasagna",
    "user_preferences": UserPreferences,
    "recent_actions": [
        {"type": "recipe_request", "recipe": "lasagna", "timestamp": "..."},
        {"type": "substitution", "from": "beef", "to": "mushrooms", "timestamp": "..."}
    ]
}
```

### Action Tracking System

#### **Action Types**
```python
ACTION_TYPES = [
    "item_addition",
    "item_removal", 
    "quantity_update",
    "recipe_request",
    "substitution",
    "list_query",
    "preference_update"
]
```

#### **Action Logging**
```python
def log_action(action_type: str, items: List[str], quantity: int = 1, reason: str = None):
    """
    Log action to conversation context for intelligent decision making.
    """
    action = {
        "type": action_type,
        "items": items,
        "quantity": quantity,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    conversation_context["action_history"].append(action)
```

### Intelligent Decision Making

#### **1. Context-Aware Item Addition**
```python
def process_smart_addition(user_message: str, current_list: List[str], context: str) -> Dict:
    """
    Smart addition with context awareness and action tracking.
    """
    # Extract items with AI
    extraction_result = ai_service.extract_items_with_context(
        user_message, current_list, context
    )
    
    # Check removal history
    for item in extraction_result["items_to_add"]:
        if item in context["removed_items"]:
            # Item was previously removed - ask for confirmation
            return {"needs_confirmation": True, "item": item}
    
    # Handle quantities
    for item, quantity in extraction_result["quantities"].items():
        if quantity > 1:
            item_with_qty = f"{quantity} {item}"
        else:
            item_with_qty = item
        
        # Add to list and log action
        current_list.append(item_with_qty)
        log_action("item_addition", [item], quantity)
    
    return {"updated_list": current_list}
```

#### **2. Intelligent Item Removal**
```python
def process_smart_removal(user_message: str, current_list: List[str]) -> Dict:
    """
    Handle item removal with fuzzy matching and history tracking.
    """
    # Extract items to remove
    items_to_remove = ai_service.extract_removal_items(user_message, current_list)
    
    # Fuzzy match against current list
    for item in items_to_remove:
        matched_item = fuzzy_match(item, current_list)
        if matched_item:
            current_list.remove(matched_item)
            # Log removal action
            log_action("item_removal", [matched_item], reason="user_request")
            # Add to removed items history
            context["removed_items"].append({
                "name": matched_item,
                "removed_at": datetime.utcnow().isoformat(),
                "reason": "user_request"
            })
    
    return current_list
```

#### **3. Recipe Context Management**
```python
def process_recipe_shopping(recipe_request: str, current_list: List[str], preferences: Dict) -> Dict:
    """
    Generate recipe and suggest missing ingredients with context awareness.
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
    
    # Log recipe request action
    log_action("recipe_request", missing_items, reason=recipe_request)
    
    return {
        "recipe": recipe_result["recipe"],
        "shopping_items": missing_items,
        "response": f"I'll add {', '.join(missing_items)} to your shopping list for this recipe."
    }
```

### Action Summary Generation

#### **For AI Context Management**
```python
def generate_action_summary(conversation_context: Dict) -> str:
    """
    Create concise action summary for AI context instead of full conversation history.
    """
    current_list = conversation_context["shopping_list"]
    recent_actions = conversation_context["action_history"][-3:]  # Last 3 actions
    user_preferences = conversation_context["user_preferences"]
    
    action_summary = f"User has {user_preferences['allergies']}. Current list: {', '.join(current_list)}. "
    action_summary += f"Recent: {', '.join([f'{action['type']} {action['items']}' for action in recent_actions])}"
    
    return action_summary
```

### Enhanced Prompt Engineering

#### **1. Shopping List Action Recognition Prompt**
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
User preferences: {user_preferences}
Recent actions: {recent_actions}

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

#### **2. Item Extraction with Context Prompt**
```python
CONTEXTUAL_EXTRACTION_PROMPT = """
Extract shopping list items from the conversation with context awareness.

Conversation history:
{action_summary}

Current shopping list: {current_list}
User preferences: {user_preferences}

Instructions:
- Extract items mentioned for shopping
- Consider recipe context if applicable
- Handle quantities (e.g., "2 apples" → {"apples": 2})
- Identify removals (e.g., "I don't want X" → remove X)
- Consider user preferences (e.g., nut allergy alternatives)

Return JSON format:
{
    "items_to_add": ["item1", "item2"],
    "items_to_remove": ["item3"],
    "quantities": {"item1": 2, "item2": 1},
    "context": "recipe_shopping|direct_shopping|modification"
}
"""
```

#### **3. Recipe Integration Prompt**
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
- Consider user preferences for alternatives (e.g., nut allergy)

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

## External Service Integration

### Service Management
- **Centralized Orchestration:** ChatService as single point of control for all services
- **Service Selection:** Use Gemini for classification and response generation
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

## Project-Specific Adaptations

### For Conversational Systems
- **Conversation History:** Maintain chat context across API sessions
- **User Preferences:** Store and use dietary preferences in AI responses
- **Intent Classification:** Identify user goals (recipe, shopping, information)
- **Response Personalization:** Tailor responses to individual user preferences
- **Multi-modal Support:** Handle text-based grocery shopping requests

### For Shopping List Management
- **Smart Item Recognition:** Extract items with quantities and context
- **Fuzzy Matching:** Handle item variations and misspellings
- **Context-Aware Updates:** Understand recipe vs. direct shopping context
- **Quantity Management:** Handle "2 apples", "3 bags of chips" properly
- **Preference Integration:** Consider dietary restrictions in suggestions

### For Analysis & Processing Tools
- **Batch Processing:** Handle multiple items in single requests
- **Result Caching:** Store AI responses for similar queries
- **Progress Tracking:** Show real-time processing status for complex requests
- **Error Recovery:** Handle partial AI service failures gracefully
- **Export Integration:** Connect AI results to shopping list updates

### For Decision Support Systems
- **Confidence Scoring:** Measure certainty of AI classifications
- **Explanation Generation:** Provide reasoning for shopping recommendations
- **Alternative Suggestions:** Offer multiple options when appropriate
- **Risk Assessment:** Evaluate potential issues with AI recommendations
- **Audit Trail:** Track AI decision history and reasoning

## Quality Metrics

### Success Criteria
- ✅ **Accurate Item Recognition**: 95%+ accuracy in identifying items
- ✅ **Proper Quantity Handling**: Correctly parse "2 apples", "3 bags"
- ✅ **Smart Removal**: Successfully remove items with fuzzy matching
- ✅ **Context Awareness**: Understand recipe vs. direct shopping context
- ✅ **Preference Integration**: Consider dietary preferences in suggestions

### Development Scenarios
1. **Recipe → Shopping**: "Give me pasta recipe" → "I don't want tomatoes" → "Add milk"
2. **Direct Shopping**: "Add bread and milk" → "Remove bread" → "Add 2 apples"
3. **Context Shopping**: "I'm making lasagna" → "What do I need?" → "I have cheese"
4. **Quantity Management**: "Add 3 bags of chips" → "Change to 2 bags" → "Add 1 apple" 