import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import src.commands.meal as MealModule


@pytest.mark.asyncio
@mock.patch("src.commands.meal.sender")
@mock.patch("src.commands.meal.requests.get")
async def test_meal(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "offset": 0,
        "number": 2,
        "results": [
            {
                "id": 716429,
                "title": "Pasta with Garlic, Scallions, Cauliflower & Breadcrumbs",
                "image": "https://img.spoonacular.com/recipes/716429-312x231.jpg",
                "imageType": "jpg",
            },
            {
                "id": 715538,
                "title": "What to make for dinner tonight?? Bruschetta Style Pork & Pasta",
                "image": "https://img.spoonacular.com/recipes/715538-312x231.jpg",
                "imageType": "jpg",
            }
        ],
        "totalResults": 10
    }
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    cuisine_cog = MealModule.Meal(bot_mock)

    await cuisine_cog.search_by_type.callback(cuisine_cog, ctx, recipe_type="dinner 2")

    mock_sender.assert_awaited()

    mock_get.assert_called()

@pytest.mark.asyncio
@mock.patch("src.commands.meal.sender")
@mock.patch("src.commands.meal.requests.get")
async def test_api_failure(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    meal_cog=MealModule.Meal(bot_mock)

    await meal_cog.search_by_type.callback(meal_cog, ctx, recipe_type="dinner 2")

    ctx.send.assert_awaited_once_with("Failed to get recipes 😕")

    mock_sender.assert_not_awaited()

@pytest.mark.asyncio
@mock.patch("src.commands.meal.sender")
@mock.patch("src.commands.meal.requests.get")
async def test_invalid_recipe_count(mock_get, mock_sender):
    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    meal_cog=MealModule.Meal(bot_mock)

    await meal_cog.search_by_type.callback(meal_cog, mock_sender, recipe_type="dinner 61")
    mock_sender.send.assert_called_once_with("❗ Please request between 1 and 5 recipes.")

    mock_get.assert_not_called()

    mock_sender.assert_not_awaited()

