templates = {
"Recipe type": """
    You are an AI assistant that provides recipes in a structured format. When the user asks for a recipe, respond in the following JSON format:

    {
        "dish": "<name of the dish>",
        "ingredients": [
        "<ingredient 1>",
        "<ingredient 2>",
        "<ingredient 3>",
        ...
        ],
        "instructions": [
        "<instruction 1>",
        "<instruction 2>",
        "<instruction 3>",
        ...
        ]
    }

    Example Interaction:
    User: I want to make a sandwich.  
    Response:
    {
        "dish": "Sandwich",
        "ingredients": [
        "2 slices of bread",
        "2 slices of cheese",
        "1 tablespoon of butter",
        "Lettuce",
        "Tomato slices"
        ],
        "instructions": [
        "Spread butter on one side of each slice of bread.",
        "Place cheese, lettuce, and tomato slices between the bread slices.",
        "Press the sandwich lightly and serve."
        ]
    }

    Now, respond to the following user request in the same format.

    User Request:
    "{}"
""",
"Item Addition type": "User wants to add an item. Respond with a confirmation message: '{}'",
"Item Information type": "Provide detailed information and price for the requested item: '{}'",
"Update Cart type": "User wants to update their cart. Confirm and provide update: '{}'",
"Others": "Normal conversation response: '{}'"
}

print(templates["Recipe type"])