
import cohere
import os
import json

# Initialize the Cohere client
# Make sure to set your API key as an environment variable
co = cohere.Client(os.environ.get('Cohere_API_KEY', ''))

def generate_recipe(name,nutrition_info):
    prompt = f"""Generate a recipe for a meal that meets the following nutritional requirements:
    name:{name}
    Calories: {nutrition_info['calories']}
    Carbohydrates: {nutrition_info['carbs']}g
    Protein: {nutrition_info['protein']}g
    Fat: {nutrition_info['fat']}g

    Please provide:
    2. List of ingredients with amounts
    3. Step-by-step instructions for preparation

    Format the output as a JSON object with the following structure:
    {{
        "name": "Dish Name",
        "ingredients": [
            {{"item": "Ingredient 1", "amount": "Amount 1"}},
            {{"item": "Ingredient 2", "amount": "Amount 2"}},
            ...
        ],
        "instructions": [
            "Step 1",
            "Step 2",
            ...
        ]
    }}
    """

    response = co.generate(
        model='command',
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE'
    )

    return json.loads(response.generations[0].text)

