# IMPLEMENTATION GUIDE

## Development Rules for Cursor

### Project Structure Constraints
- **NO folder name changes** - Keep existing src/ structure exactly as is
- **NO new directories** - Work within api/, services/, core/, models/
- **Maintain existing patterns** - Follow the same structure as current services
- **Keep it simple** - Don't over-engineer or add unnecessary abstractions

### Code Organization Rules
- **Services in /services/** - All business logic goes here
- **API routes in /api/main.py** - Only route definitions, no business logic
- **Models in /models/** - Pydantic schemas only
- **Core in /core/** - Config, database, logging, safety
- **Keep existing imports** - Don't change import patterns

### Implementation Guidelines
- **Start simple** - Get basic functionality working first
- **Add complexity gradually** - Don't build everything at once
- **Follow existing patterns** - Look at how current services are structured
- **Keep functions focused** - One clear purpose per function
- **Use existing error handling** - Follow the same patterns as current code

### AI Service Integration Rules
- **Use existing AIService patterns** - Don't reinvent the wheel
- **Keep retry logic** - Maintain existing error handling
- **Follow prompt safety** - Use existing validation patterns
- **Don't over-optimize** - Get it working first, optimize later

### Database Rules
- **Use existing models** - Don't change Pydantic schemas unnecessarily
- **Follow current patterns** - Use same database connection approach
- **Keep it simple** - Don't add complex queries unless needed

## Cursor Prompts for Development

### When Adding New Features
```
"Add [feature] to [service] following the existing patterns:
1. Use the same structure as other services in /services/
2. Keep it simple - get basic functionality working first
3. Follow existing error handling patterns
4. Don't change the project structure
5. Use existing imports and patterns"
```

### When Modifying Existing Services
```
"Enhance [service] to [new functionality]:
1. Keep the existing structure and patterns
2. Add new methods without breaking existing ones
3. Follow the same error handling approach
4. Don't over-engineer - keep it simple
5. Maintain compatibility with existing code"
```

### When Integrating Services
```
"Connect [service A] to [service B]:
1. Use existing integration patterns
2. Keep the same data flow structure
3. Don't add unnecessary complexity
4. Follow existing error handling
5. Maintain the current API structure"
```

## Agentic Shopping List Implementation Focus

### **Phase 1: Core Action Tracking (Week 1)**
```python
# 1. Enhanced Shopping List Data Structure
class ShoppingListItem:
    name: str
    quantity: int = 1
    unit: str = ""
    source: str = "direct_addition"
    added_at: datetime
    removed: bool = False

# 2. Action Logging System
class ActionLogger:
    def log_action(self, action_type, items, quantity=None, reason=None):
        # Log action to conversation context

# 3. User Preferences Integration
user_preferences = {
    "allergies": ["nut allergy"],
    "dietary": "",
    "preferences": []
}
```

### **Phase 2: Context Management (Week 2)**
```python
# 1. Action Summaries for AI
def generate_action_summary(conversation_actions, current_list, user_preferences):
    # Create concise summary for AI context
    return f"User has {user_preferences['allergies']}. Current list: {current_list}. Recent: {recent_actions}"

# 2. Context-Aware Item Management
def process_item_request(item, action_type, context):
    # Check if item was recently removed
    # Consider user preferences (nut allergy)
    # Make intelligent decision about adding/removing
```

### **Phase 3: Intelligent Decision Making (Week 3)**
```python
# 1. Smart Item Addition with History
def add_item_with_context(item, quantity, context):
    # Check removal history
    # Consider user preferences
    # Log action appropriately

# 2. Smart Item Removal with Tracking
def remove_item_with_tracking(item, reason, context):
    # Remove from list
    # Add to removal history
    # Log removal action
```

## Specific Implementation Focus

### Shopping List Enhancements
- **Add action tracking** - Log all add/remove/recipe operations
- **Add removal history** - Track removed items to prevent re-addition
- **Add user preferences** - Include allergies and dietary restrictions
- **Keep existing CRUD** - Don't rewrite, just enhance
- **Use existing prompts** - Extend current AI prompts

### AI Service Improvements
- **Enhance existing prompts** - Don't create new prompt systems
- **Improve extraction** - Better item recognition using current patterns
- **Add action summaries** - Clean context for AI instead of full history
- **Keep retry logic** - Maintain existing error handling
- **Follow existing patterns** - Use same AI service structure

### Context Management
- **Extend existing context** - Don't rebuild context system
- **Keep conversation history** - Use existing storage patterns
- **Add action logging** - Track all user interactions
- **Don't over-complicate** - Simple context awareness

## What NOT to Do

### Don't Add Unnecessary Complexity
- ❌ Don't create new testing frameworks
- ❌ Don't add complex validation layers
- ❌ Don't create new directory structures
- ❌ Don't over-engineer simple features
- ❌ Don't add unnecessary abstractions

### Don't Break Existing Patterns
- ❌ Don't change import structures
- ❌ Don't modify existing API responses
- ❌ Don't rewrite working services
- ❌ Don't add complex error handling
- ❌ Don't change database schemas unnecessarily

### Don't Over-Optimize
- ❌ Don't add caching unless needed
- ❌ Don't optimize before it's working
- ❌ Don't add complex monitoring
- ❌ Don't create elaborate logging
- ❌ Don't add performance features prematurely

## Simple Development Process

### 1. Start with Basic Functionality
- Get the core feature working
- Use existing patterns and structures
- Keep it simple and focused

### 2. Enhance Gradually
- Add complexity only when needed
- Follow existing code patterns
- Don't over-engineer

### 3. Test Manually
- Test the feature works
- Fix obvious issues
- Don't create elaborate test suites

### 4. Integrate with Existing Code
- Connect to existing services
- Follow current integration patterns
- Maintain compatibility

## ChatGPT Prompt Templates

### For Planning Features
- "What's the simplest way to add action tracking to our existing ShoppingListService?"
- "How can I enhance the shopping list data structure without changing the project structure?"
- "What's the minimal change needed to add user preferences to the conversation context?"

### For Implementation Help
- "Help me add action logging to ShoppingListService following existing patterns"
- "How do I integrate user preferences with the existing AI service?"
- "What's the simplest approach to add removal history tracking?"

### For Problem Solving
- "I need to add action tracking but keep it simple - what's the approach?"
- "How do I enhance the shopping list without over-engineering?"
- "What's the minimal change to achieve agentic shopping list management?"

## Override Flags
- `#KEEP_SIMPLE` → focus on basic functionality, avoid over-engineering
- `#FOLLOW_PATTERNS` → use existing code structure and patterns
- `#NO_STRUCTURE_CHANGES` → don't modify project structure
- `#MINIMAL_CHANGES` → make smallest possible changes
- `#EXISTING_PATTERNS` → follow current code patterns exactly 