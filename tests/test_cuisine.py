import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import src.commands.cuisine as CuisineModule

@pytest.mark.asyncio
@mock.patch("src.commands.cuisine.sender")
@mock.patch("src.commands.cuisine.requests.get")
async def test_cuisine(mock_get, mock_sender):
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
        "totalResults": 86
    }
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    cuisine_cog=CuisineModule.Cuisine(bot_mock)

    await cuisine_cog.search_by_cuisine.callback(cuisine_cog, ctx, cuisine = "italian 2")

    mock_sender.assert_awaited()

    mock_get.assert_called()


@pytest.mark.asyncio
@mock.patch("src.commands.cuisine.sender")
@mock.patch("src.commands.cuisine.requests.get")
async def test_api_failure(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    cuisine_cog=CuisineModule.Cuisine(bot_mock)

    await cuisine_cog.search_by_cuisine.callback(cuisine_cog, ctx, cuisine = "italian 2")

    ctx.send.assert_awaited_once_with("Failed to get recipes 😕")

    mock_sender.assert_not_awaited()



@pytest.mark.asyncio
@mock.patch("src.commands.cuisine.sender")
@mock.patch("src.commands.cuisine.requests.get")
async def test_invalid_recipe_count(mock_get, mock_sender):
    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    cuisine_cog=CuisineModule.Cuisine(bot_mock)

    await cuisine_cog.search_by_cuisine.callback(cuisine_cog, mock_sender, cuisine = "italian 6")
    mock_sender.send.assert_called_once_with("❗ Please request between 1 and 5 recipes.")

    # Making sure there was no API request
    mock_get.assert_not_called()

    # Making sure that sender wasn't called
    mock_sender.assert_not_awaited()


@pytest.mark.asyncio
@mock.patch("src.commands.cuisine.sender")
@mock.patch("src.commands.cuisine.requests.get")
async def test_no_results(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "offset": 0,
        "number": 2,
        "results": [],
        "totalResults": 0
    }
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    cuisine_cog = CuisineModule.Cuisine(bot_mock)

    await cuisine_cog.search_by_cuisine.callback(cuisine_cog, ctx, cuisine="italian 1")

    ctx.send.assert_awaited_once_with("Cannot find recipes for: **italian 1**")


