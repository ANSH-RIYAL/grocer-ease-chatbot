from typing import List, Dict, Optional, Any
from datetime import datetime
from src.core.logging import get_logger
from src.models.shopping_list import UserPreferences, ShoppingListState
from src.services.ai_service import ai_service

logger = get_logger(__name__)

class RecipeService:
    """Handles intelligent recipe suggestions and ingredient management."""
    
    def __init__(self):
        # Simple recipe database - in production this would be a proper database
        self.recipe_database = {
            "pasta": {
                "name": "Simple Pasta",
                "ingredients": ["pasta", "tomatoes", "garlic", "olive oil", "salt", "pepper"],
                "vegetarian": True,
                "vegan": True,
                "allergen_free": ["nuts", "dairy"],
                "difficulty": "easy",
                "cook_time": "20 minutes"
            },
            "lasagna": {
                "name": "Classic Lasagna",
                "ingredients": ["lasagna sheets", "ground beef", "tomatoes", "cheese", "garlic", "olive oil"],
                "vegetarian": False,
                "vegan": False,
                "allergen_free": ["nuts"],
                "difficulty": "medium",
                "cook_time": "60 minutes"
            },
            "vegetarian_lasagna": {
                "name": "Vegetarian Lasagna",
                "ingredients": ["lasagna sheets", "mushrooms", "tomatoes", "cheese", "garlic", "olive oil"],
                "vegetarian": True,
                "vegan": False,
                "allergen_free": ["nuts"],
                "difficulty": "medium",
                "cook_time": "60 minutes"
            },
            "salad": {
                "name": "Fresh Garden Salad",
                "ingredients": ["lettuce", "tomatoes", "cucumber", "onions", "olive oil", "vinegar"],
                "vegetarian": True,
                "vegan": True,
                "allergen_free": ["nuts", "dairy", "gluten"],
                "difficulty": "easy",
                "cook_time": "10 minutes"
            },
            "chicken_stir_fry": {
                "name": "Chicken Stir Fry",
                "ingredients": ["chicken", "broccoli", "carrots", "soy sauce", "garlic", "oil"],
                "vegetarian": False,
                "vegan": False,
                "allergen_free": ["nuts", "dairy"],
                "difficulty": "medium",
                "cook_time": "25 minutes"
            }
        }
    
    def suggest_recipe(self, user_preferences: UserPreferences, current_list: List[str] = None) -> Dict[str, Any]:
        """Suggest a recipe based on user preferences and current shopping list."""
        try:
            # Filter recipes based on dietary preferences
            suitable_recipes = []
            
            for recipe_id, recipe in self.recipe_database.items():
                # Check dietary restrictions
                if user_preferences.dietary == "vegetarian" and not recipe["vegetarian"]:
                    continue
                elif user_preferences.dietary == "vegan" and not recipe["vegan"]:
                    continue
                
                # Check allergies
                has_allergy_conflict = False
                for allergy in user_preferences.allergies:
                    if allergy.lower() in [ingredient.lower() for ingredient in recipe["ingredients"]]:
                        has_allergy_conflict = True
                        break
                
                if has_allergy_conflict:
                    continue
                
                suitable_recipes.append(recipe_id)
            
            if not suitable_recipes:
                return {
                    "suggestion": None,
                    "reason": "No suitable recipes found for your preferences",
                    "alternatives": []
                }
            
            # Select best recipe (for now, just pick the first suitable one)
            selected_recipe_id = suitable_recipes[0]
            selected_recipe = self.recipe_database[selected_recipe_id]
            
            # Check what ingredients are already in the shopping list
            missing_ingredients = []
            if current_list:
                for ingredient in selected_recipe["ingredients"]:
                    if ingredient.lower() not in [item.lower() for item in current_list]:
                        missing_ingredients.append(ingredient)
            else:
                missing_ingredients = selected_recipe["ingredients"]
            
            return {
                "suggestion": selected_recipe,
                "missing_ingredients": missing_ingredients,
                "reason": f"Perfect for your {user_preferences.dietary} diet",
                "alternatives": suitable_recipes[1:3] if len(suitable_recipes) > 1 else []
            }
            
        except Exception as e:
            logger.error(f"Error suggesting recipe: {str(e)}")
            return {"suggestion": None, "reason": "Error generating suggestion", "alternatives": []}
    
    def generate_recipe_with_ai(self, user_message: str, user_preferences: UserPreferences) -> Dict[str, Any]:
        """Generate a custom recipe using AI based on user request."""
        try:
            prompt = f"""
            Generate a simple recipe based on the user's request and preferences.
            
            User request: "{user_message}"
            User preferences: {user_preferences.dietary} diet
            Allergies: {', '.join(user_preferences.allergies) if user_preferences.allergies else 'None'}
            
            Return a JSON response with:
            {{
                "recipe_name": "Name of the recipe",
                "ingredients": ["ingredient1", "ingredient2", ...],
                "instructions": ["Step 1", "Step 2", ...],
                "cook_time": "estimated time",
                "difficulty": "easy/medium/hard",
                "dietary_info": "vegetarian/vegan/regular"
            }}
            """
            
            response = ai_service.model.generate_content(prompt)
            if not response or not response.text:
                return {"error": "Failed to generate recipe"}
            
            # Parse JSON response
            import json
            try:
                recipe_data = json.loads(response.text.strip())
                return {
                    "suggestion": recipe_data,
                    "missing_ingredients": recipe_data.get("ingredients", []),
                    "reason": "AI-generated recipe based on your request",
                    "alternatives": []
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse AI recipe response")
                return {"error": "Failed to parse recipe response"}
                
        except Exception as e:
            logger.error(f"Error generating AI recipe: {str(e)}")
            return {"error": "Failed to generate recipe"}
    
    def suggest_substitutions(self, item: str, user_preferences: UserPreferences) -> List[str]:
        """Suggest substitutions for items based on user preferences."""
        substitutions = {
            "beef": ["mushrooms", "tofu", "tempeh", "lentils"],
            "chicken": ["tofu", "tempeh", "seitan", "chickpeas"],
            "cheese": ["nutritional yeast", "cashew cheese", "dairy-free cheese"],
            "milk": ["almond milk", "soy milk", "oat milk", "coconut milk"],
            "eggs": ["flax eggs", "chia eggs", "banana", "applesauce"],
            "butter": ["olive oil", "coconut oil", "avocado", "nut butter"]
        }
        
        # Check for direct substitutions
        if item.lower() in substitutions:
            return substitutions[item.lower()]
        
        # Check for allergy-based substitutions
        if user_preferences.allergies:
            for allergy in user_preferences.allergies:
                if allergy.lower() in item.lower():
                    # Suggest alternatives that don't contain the allergen
                    if "nut" in allergy.lower():
                        return ["seeds", "sunflower seeds", "pumpkin seeds"]
                    elif "dairy" in allergy.lower():
                        return ["plant-based alternatives", "coconut-based products"]
        
        # Check for dietary restrictions
        if user_preferences.dietary == "vegetarian" and any(meat in item.lower() for meat in ["beef", "pork", "chicken", "meat"]):
            return ["mushrooms", "tofu", "tempeh", "lentils", "chickpeas"]
        
        return []
    
    def get_recipe_ingredients(self, recipe_name: str) -> List[str]:
        """Get ingredients for a specific recipe."""
        for recipe_id, recipe in self.recipe_database.items():
            if recipe["name"].lower() == recipe_name.lower():
                return recipe["ingredients"]
        
        return []
    
    def validate_recipe_against_preferences(self, recipe_ingredients: List[str], user_preferences: UserPreferences) -> Dict[str, Any]:
        """Validate if a recipe is suitable for user preferences."""
        issues = []
        substitutions = {}
        
        for ingredient in recipe_ingredients:
            # Check for allergy conflicts
            for allergy in user_preferences.allergies:
                if allergy.lower() in ingredient.lower():
                    issues.append(f"Contains {allergy}")
                    sub = self.suggest_substitutions(ingredient, user_preferences)
                    if sub:
                        substitutions[ingredient] = sub
            
            # Check for dietary restrictions
            if user_preferences.dietary == "vegetarian" and any(meat in ingredient.lower() for meat in ["beef", "pork", "chicken", "meat"]):
                issues.append("Contains meat")
                sub = self.suggest_substitutions(ingredient, user_preferences)
                if sub:
                    substitutions[ingredient] = sub
        
        return {
            "suitable": len(issues) == 0,
            "issues": issues,
            "substitutions": substitutions
        }

# Create a singleton instance
recipe_service = RecipeService() 