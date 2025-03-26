import random
from config import MONGO_URI, DB_NAME
from database import get_db_connection
from shopping_list import ShoppingListManager

def main():
    db = get_db_connection(MONGO_URI, DB_NAME)
    shopping_list_manager = ShoppingListManager(db)
    
    user_ids = [f"user_{i}" for i in range(1, 6)]
    item_ids = [f"item_{i}" for i in range(1, 11)]
    
    for _ in range(10):
        user_id = random.choice(user_ids)
        operation = random.choice(["add", "delete", "clear"])
        
        if operation == "add":
            items_to_add = random.sample(item_ids, random.randint(1, len(item_ids)))
            print(f"Adding items {items_to_add} to user {user_id}'s shopping list.")
            if shopping_list_manager.add_items(user_id, items_to_add):
                print("Items successfully added.")
            else:
                print("Failed to add items.")
        
        elif operation == "delete":
            items_to_delete = random.sample(item_ids, random.randint(1, len(item_ids)))
            print(f"Deleting items {items_to_delete} from user {user_id}'s shopping list.")
            if shopping_list_manager.delete_items(user_id, items_to_delete):
                print("Items successfully deleted.")
            else:
                print("Failed to delete items.")
        
        elif operation == "clear":
            print(f"Clearing shopping list for user {user_id}.")
            if shopping_list_manager.clear_shopping_list(user_id):
                print("Shopping list successfully cleared.")
            else:
                print("Failed to clear shopping list.")

if __name__ == "__main__":
    main()