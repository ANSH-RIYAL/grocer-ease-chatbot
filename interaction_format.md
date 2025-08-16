# GrocerEase Chatbot API Interaction Format

This document contains the exact JSON request and response formats for all API endpoints based on manual testing.

## Base URL
```
http://localhost:8000
```

## API Version
```
/api/v1
```

---

## 1. Health Check

### Endpoint
```
GET /health
```

### Response
```json
{
  "status": "healthy",
  "service": "GrocerEase Chatbot"
}
```

---

## 2. Chat Endpoint

### Endpoint
```
POST /api/v1/chat
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "user_message": "Hello, I need to buy milk and bread"
}
```

### Response
```json
{
  "bot_response": "Okay, I've added milk and bread to your shopping list.  \n\nI see you have pasta, tomatoes, garlic, olive oil, salt, and pepper already on your list.  Are you planning a pasta dish?  I noticed you previously considered lasagna and a simpler pasta dish.  If you're still thinking about pasta, do you need any other ingredients like onions, mushrooms, or cheese (remembering your vegetarian preference)?  Or perhaps a different type of pasta than what you currently have?  I can also suggest some nut-free pesto recipes if you're interested, given your nut allergy.\n\nAdded to your list: milk, bread",
  "shopping_list": [
    "pasta",
    "tomatoes",
    "garlic",
    "olive oil",
    "salt",
    "pepper",
    "peanuts",
    "milk",
    "bread"
  ],
  "preferences": {}
}
```

### Error Response (Validation Error)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "user_id"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1},
      "url": "https://errors.pydantic.dev/2.11/v/string_too_short"
    },
    {
      "type": "string_too_short",
      "loc": ["body", "user_message"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1},
      "url": "https://errors.pydantic.dev/2.11/v/string_too_short"
    }
  ]
}
```

### Error Response (Missing Field)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "user_message"],
      "msg": "Field required",
      "input": {"user_id": "test_user_001"},
      "url": "https://errors.pydantic.dev/2.11/v/missing"
    }
  ]
}
```

---

## 3. Enhanced User Preferences

### Endpoint
```
POST /api/v1/preferences/enhanced
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "dietary": "vegetarian",
  "allergies": ["nuts", "shellfish"],
  "preferences": ["organic", "local"],
  "restrictions": ["gluten-free"]
}
```

### Response
```json
{
  "success": true
}
```

---

## 4. Get User Preferences

### Endpoint
```
GET /api/v1/preferences/{user_id}
```

### Response (With Preferences)
```json
{
  "dietary": "vegetarian",
  "allergies": "nuts,shellfish",
  "preferences": "organic,local",
  "restrictions": "gluten-free"
}
```

### Response (No Preferences)
```json
{}
```

---

## 5. Set User Preference

### Endpoint
```
POST /api/v1/preferences
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "preference": "dietary",
  "value": "vegetarian"
}
```

### Response
```json
{
  "success": false
}
```

---

## 6. Get Context Summary

### Endpoint
```
GET /api/v1/context/{user_id}
```

### Response
```json
{
  "user_id": "test_user_001",
  "context_summary": "Allergies: nuts, shellfish. Dietary: vegetarian. Current list: pasta, tomatoes, garlic, olive oil, salt, pepper, peanuts, milk, bread Recent: added milk, added bread.",
  "suggestions": [
    "You have 9 items in your list.",
    "I'll make sure to suggest vegetarian alternatives.",
    "I'll avoid items with nuts, shellfish."
  ]
}
```

---

## 7. Get Shopping List State

### Endpoint
```
GET /api/v1/shopping-list/state/{user_id}
```

### Response
```json
{
  "user_id": "test_user_001",
  "items": [
    {
      "name": "pasta",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.379000",
      "removed": false
    },
    {
      "name": "tomatoes",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.386000",
      "removed": false
    },
    {
      "name": "garlic",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.391000",
      "removed": false
    },
    {
      "name": "olive oil",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.394000",
      "removed": false
    },
    {
      "name": "salt",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.397000",
      "removed": false
    },
    {
      "name": "pepper",
      "quantity": 1,
      "unit": "",
      "source": "recipe_suggestion",
      "added_at": "2025-08-06T00:36:47.399000",
      "removed": false
    },
    {
      "name": "peanuts",
      "quantity": 1,
      "unit": "",
      "source": "direct_addition",
      "added_at": "2025-08-06T00:37:45.921000",
      "removed": false
    },
    {
      "name": "milk",
      "quantity": 1,
      "unit": "",
      "source": "ai_extraction",
      "added_at": "2025-08-16T04:29:42.603000",
      "removed": false
    },
    {
      "name": "bread",
      "quantity": 1,
      "unit": "",
      "source": "ai_extraction",
      "added_at": "2025-08-16T04:29:42.631000",
      "removed": false
    }
  ],
  "removed_items": [],
  "action_history": [
    {
      "type": "preference_update",
      "items": [],
      "quantity": null,
      "reason": "user_update",
      "timestamp": "2025-08-06T00:36:42.690000"
    },
    {
      "type": "item_addition",
      "items": ["pasta"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.382000"
    },
    {
      "type": "item_addition",
      "items": ["tomatoes"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.388000"
    },
    {
      "type": "item_addition",
      "items": ["garlic"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.392000"
    },
    {
      "type": "item_addition",
      "items": ["olive oil"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.395000"
    },
    {
      "type": "item_addition",
      "items": ["salt"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.398000"
    },
    {
      "type": "item_addition",
      "items": ["pepper"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:36:47.400000"
    },
    {
      "type": "recipe_request",
      "items": ["Simple Pasta"],
      "quantity": null,
      "reason": "user_request",
      "timestamp": "2025-08-06T00:36:47.401000"
    },
    {
      "type": "item_addition",
      "items": ["peanuts"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-06T00:37:45.923000"
    },
    {
      "type": "item_addition",
      "items": ["milk"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-16T04:29:42.628000"
    },
    {
      "type": "item_addition",
      "items": ["bread"],
      "quantity": 1,
      "reason": null,
      "timestamp": "2025-08-16T04:29:42.633000"
    },
    {
      "type": "preference_update",
      "items": [],
      "quantity": null,
      "reason": "user_update",
      "timestamp": "2025-08-16T04:29:50.948000"
    }
  ],
  "user_preferences": {
    "dietary": "vegetarian",
    "allergies": ["nuts", "shellfish"],
    "preferences": ["organic", "local"],
    "restrictions": ["gluten-free"]
  },
  "last_updated": "2025-08-16T04:29:50.935000"
}
```

---

## 8. Recipe Suggestions

### Endpoint
```
POST /api/v1/recipe/suggest
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "recipe_query": "I want to make a vegetarian pasta dish"
}
```

### Response
```json
{
  "user_id": "test_user_001",
  "recipe_suggestion": {
    "name": "Simple Pasta",
    "ingredients": [
      "pasta",
      "tomatoes",
      "garlic",
      "olive oil",
      "salt",
      "pepper"
    ],
    "vegetarian": true,
    "vegan": true,
    "allergen_free": ["nuts", "dairy"],
    "difficulty": "easy",
    "cook_time": "20 minutes"
  },
  "missing_ingredients": [],
  "reason": "Perfect for your none diet",
  "alternatives": [
    "lasagna",
    "vegetarian_lasagna"
  ]
}
```

---

## 9. AI Recipe Generation

### Endpoint
```
POST /api/v1/recipe/generate
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "recipe_query": "Create a quick vegetarian breakfast recipe"
}
```

### Response
```json
{
  "user_id": "test_user_001",
  "recipe": {
    "recipe_name": "Quick Scrambled Eggs with Toast",
    "ingredients": [
      "2 large eggs",
      "1 tablespoon milk (optional)",
      "Salt and pepper to taste",
      "1 tablespoon butter or oil",
      "2 slices of bread"
    ],
    "instructions": [
      "Whisk the eggs with milk (if using), salt, and pepper in a bowl.",
      "Heat the butter or oil in a non-stick pan over medium heat.",
      "Pour the egg mixture into the pan and cook, stirring occasionally, until set but still slightly moist.",
      "While the eggs are cooking, toast the bread.",
      "Serve the scrambled eggs on the toast."
    ],
    "cook_time": "5-7 minutes",
    "difficulty": "easy",
    "dietary_info": "vegetarian"
  },
  "missing_ingredients": [
    "2 large eggs",
    "1 tablespoon milk (optional)",
    "Salt and pepper to taste",
    "1 tablespoon butter or oil",
    "2 slices of bread"
  ],
  "reason": "AI-generated recipe based on your request",
  "error": null
}
```

---

## 10. Substitution Suggestions

### Endpoint
```
POST /api/v1/substitutions
```

### Request Body
```json
{
  "user_id": "test_user_001",
  "item": "milk"
}
```

### Response
```json
{
  "user_id": "test_user_001",
  "original_item": "milk",
  "substitutions": [
    "almond milk",
    "soy milk",
    "oat milk",
    "coconut milk"
  ],
  "reason": "Based on none diet and allergies: none"
}
```

---

## 11. Clear User Preferences

### Endpoint
```
DELETE /api/v1/preferences/{user_id}
```

### Response
```json
{
  "success": false
}
```

---

## 12. Error Responses

### Not Found (404)
```json
{
  "detail": "Not Found"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## Data Models

### ChatRequest
```json
{
  "user_id": "string (min_length: 1)",
  "user_message": "string (min_length: 1)"
}
```

### PreferenceRequest
```json
{
  "user_id": "string (min_length: 1)",
  "preference": "string (min_length: 1)",
  "value": "string (min_length: 1)"
}
```

### EnhancedUserPreferencesRequest
```json
{
  "user_id": "string (min_length: 1)",
  "dietary": "string (default: 'none')",
  "allergies": ["string"],
  "preferences": ["string"],
  "restrictions": ["string"]"
}
```

### RecipeRequest
```json
{
  "user_id": "string (min_length: 1)",
  "recipe_query": "string (min_length: 1)"
}
```

### SubstitutionRequest
```json
{
  "user_id": "string (min_length: 1)",
  "item": "string (min_length: 1)"
}
```

---

## Notes

1. **User ID Format**: All endpoints require a valid user ID string with minimum length of 1 character
2. **Error Handling**: The API returns detailed validation errors for malformed requests
3. **Shopping List State**: Includes comprehensive tracking of items, action history, and user preferences
4. **AI Integration**: Recipe generation and chat responses use AI services for intelligent suggestions
5. **Preference Management**: Supports both simple key-value preferences and enhanced dietary/allergy preferences
6. **Context Awareness**: The system maintains conversation context and shopping list state across interactions
