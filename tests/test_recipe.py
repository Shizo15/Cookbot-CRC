import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import src.commands.recipe as RecipeModule

@pytest.mark.asyncio
@mock.patch("src.commands.recipe.sender")
@mock.patch("src.commands.recipe.requests.get")
async def test_recipe(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "offset": 0,
        "number": 1,
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
        "totalResults": 11
    }
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    recipe_cog=RecipeModule.Recipe(bot_mock)

    await recipe_cog.recipe_by_name.callback(recipe_cog,ctx, dish_name="pasta")

    mock_sender.assert_awaited()

    mock_get.assert_called()

@pytest.mark.asyncio
@mock.patch("src.commands.recipe.sender")
@mock.patch("src.commands.recipe.requests.get")
async def test_api_fail(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    recipe_cog=RecipeModule.Recipe(bot_mock)

    await recipe_cog.recipe_by_name.callback(recipe_cog,ctx, dish_name="pasta")

    ctx.send.assert_awaited_once_with("Failed to get recipes 😕")

    mock_sender.assert_not_awaited()

@pytest.mark.asyncio
@mock.patch("src.commands.recipe.sender")
@mock.patch("src.commands.recipe.requests.get")
async def test_no_results(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "offset": 0,
        "number": 1,
        "results": [],
        "totalResults": 0
    }
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    recipe_cog=RecipeModule.Recipe(bot_mock)

    await recipe_cog.recipe_by_name.callback(recipe_cog,ctx, dish_name="pasta")

    ctx.send.assert_awaited_once_with("Cannot find recipe for: **pasta**")
