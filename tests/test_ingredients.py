import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import src.commands.ingredients as IngredientsModule


@pytest.mark.asyncio
@mock.patch("src.commands.ingredients.sender", new_callable=AsyncMock)
@mock.patch("src.commands.ingredients.requests.get")
async def test_ingredients(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "id": 73420,
        "image": "https://img.spoonacular.com/recipes/73420-312x231.jpg",
        "imageType": "jpg",
        "likes": 0,
        "missedIngredientCount": 3,
        "missedIngredients": [
            {
                "aisle": "Baking",
                "amount": 1.0,
                "id": 18371,
                "image": "https://img.spoonacular.com/ingredients_100x100/white-powder.jpg",
                "meta": [],
                "name": "baking powder",
                "original": "1 tsp baking powder",
                "originalName": "baking powder",
                "unit": "tsp",
                "unitLong": "teaspoon",
                "unitShort": "tsp"
            },
            {
                "aisle": "Spices and Seasonings",
                "amount": 1.0,
                "id": 2010,
                "image": "https://img.spoonacular.com/ingredients_100x100/cinnamon.jpg",
                "meta": [],
                "name": "cinnamon",
                "original": "1 tsp cinnamon",
                "originalName": "cinnamon",
                "unit": "tsp",
                "unitLong": "teaspoon",
                "unitShort": "tsp"
            },
            {
                "aisle": "Milk, Eggs, Other Dairy",
                "amount": 1.0,
                "id": 1123,
                "image": "https://img.spoonacular.com/ingredients_100x100/egg.png",
                "meta": [],
                "name": "egg",
                "original": "1 egg",
                "originalName": "egg",
                "unit": "",
                "unitLong": "",
                "unitShort": ""
            }
        ],
        "title": "Apple Or Peach Strudel",
        "unusedIngredients": [],
        "usedIngredientCount": 1,
        "usedIngredients": [
            {
                "aisle": "Produce",
                "amount": 6.0,
                "id": 9003,
                "image": "https://img.spoonacular.com/ingredients_100x100/apple.jpg",
                "meta": [],
                "name": "apples",
                "original": "6 large baking apples",
                "originalName": "baking apples",
                "unit": "large",
                "unitLong": "larges",
                "unitShort": "large"
            }
        ]
    }]
    mock_get.return_value = mock_response
    mock_info_response = MagicMock()
    mock_info_response.status_code = 200
    mock_info_response.json.return_value = {
            "id": 716429,
            "title": "Pasta with Garlic, Scallions, Cauliflower & Breadcrumbs",
            "image": "https://img.spoonacular.com/recipes/716429-556x370.jpg",
            "imageType": "jpg",
            "servings": 2,
            "readyInMinutes": 45,
            "cookingMinutes": 25,
            "preparationMinutes": 20,
            "sourceName": "Full Belly Sisters",
            "sourceUrl": "http://fullbellysisters.blogspot.com/2012/06/pasta-with-garlic-scallions-cauliflower.html",
            "spoonacularSourceUrl": "https://spoonacular.com/pasta-with-garlic-scallions-cauliflower-breadcrumbs-716429",
            "spoonacularScore": 83.0,
            "pricePerServing": 163.15,
            "analyzedInstructions": [],
            "creditsText": "Full Belly Sisters",
            "cuisines": [],
            "diets": [],
            "instructions": "",
            "occasions": [],
            "dishTypes": [
                "lunch",
                "main course",
                "main dish",
                "dinner"
            ],
            "extendedIngredients": [
                {
                    "aisle": "Milk, Eggs, Other Dairy",
                    "amount": 1.0,
                    "consistency": "solid",
                    "id": 1001,
                    "image": "butter-sliced.jpg",
                    "measures": {
                        "metric": {
                            "amount": 1.0,
                            "unitLong": "Tbsp",
                            "unitShort": "Tbsp"
                        },
                        "us": {
                            "amount": 1.0,
                            "unitLong": "Tbsp",
                            "unitShort": "Tbsp"
                        }
                    },
                    "meta": [],
                    "name": "butter",
                    "original": "1 tbsp butter",
                    "originalName": "butter",
                    "unit": "tbsp"
                },
                {
                    "aisle": "Produce",
                    "amount": 2.0,
                    "consistency": "solid",
                    "id": 10011135,
                    "image": "cauliflower.jpg",
                    "measures": {
                        "metric": {
                            "amount": 473.176,
                            "unitLong": "milliliters",
                            "unitShort": "ml"
                        },
                        "us": {
                            "amount": 2.0,
                            "unitLong": "cups",
                            "unitShort": "cups"
                        }
                    },
                    "meta": [
                        "frozen",
                        "thawed",
                        "cut into bite-sized pieces"
                    ],
                    "name": "cauliflower florets",
                    "original": "about 2 cups frozen cauliflower florets, thawed, cut into bite-sized pieces",
                    "originalName": "about frozen cauliflower florets, thawed, cut into bite-sized pieces",
                    "unit": "cups"
                }

            ]
        }

    # Order of requests
    mock_get.side_effect = [mock_response, mock_info_response]

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    ingredients_cog = IngredientsModule.Ingredients(bot_mock)

    await ingredients_cog.search_by_ingredients.callback(ingredients_cog, ctx, ingredients="apples,flour,sugar 1")

    mock_sender.assert_awaited()


@pytest.mark.asyncio
@mock.patch("src.commands.ingredients.sender", new_callable=AsyncMock)
@mock.patch("src.commands.ingredients.requests.get")
async def test_invalid_recipe_count(mock_get, mock_sender):
    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    ingredients_cog= IngredientsModule.Ingredients(bot_mock)

    await ingredients_cog.search_by_ingredients.callback(ingredients_cog, mock_sender, ingredients = "apples,flour,sugar 6")
    mock_sender.send.assert_called_once_with("❗ Please request between 1 and 5 recipes.")

    mock_get.assert_not_called()

    mock_sender.assert_not_awaited()