from pymongo import MongoClient

class ShoppingListManager:
    def __init__(self, db):
        self.db = db

    def add_items(self, user_id, items):
        shopping_list_collection = self.db['shopping_list']
        result = shopping_list_collection.update_one(
            {'user_id': user_id},
            {'$addToSet': {'items': {'$each': items}}},
            upsert=True
        )
        return result.acknowledged

    def delete_items(self, user_id, items):
        shopping_list_collection = self.db['shopping_list']
        result = shopping_list_collection.update_one(
            {'user_id': user_id},
            {'$pull': {'items': {'$in': items}}}
        )
        return result.acknowledged

    def clear_shopping_list(self, user_id):
        shopping_list_collection = self.db['shopping_list']
        result = shopping_list_collection.update_one(
            {'user_id': user_id},
            {'$set': {'items': []}}
        )
        return result.acknowledged

    def get_shopping_list(self, user_id):
        shopping_list_collection = self.db['shopping_list']
        shopping_list = shopping_list_collection.find_one({'user_id': user_id})
        if shopping_list:
            return shopping_list.get('items', [])
        else:
            return []
