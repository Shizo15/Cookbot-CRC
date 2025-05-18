import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
import src.commands.random as RandomModule

#Testing request
@pytest.mark.asyncio
@mock.patch("src.commands.random.sender", new_callable=AsyncMock)
@mock.patch("src.commands.random.requests.get")
async def test_random_recipe_success(mock_get, mock_sender):
    # API response mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "recipes": [
            {
                "title": "Test Recipe",
                "image": "http://example.com/image.jpg",
                "sourceUrl": "http://example.com",
                "servings": 2,
                "readyInMinutes": 30,
                "cuisines": ["TestCuisine"],
                "dishTypes": ["main course"],
                "pricePerServing": 500,
                "diets": ["vegetarian"],
                "sourceName": "TestSource"
            }
        ]
    }
    mock_get.return_value = mock_response

    # Mocking discord context
    ctx = MagicMock()
    ctx.send = AsyncMock()

    # Creating cog instance and calling command
    bot_mock = MagicMock()
    random_cog = RandomModule.Random(bot_mock)

    await random_cog.random_recipe.callback(random_cog, ctx, number=1)

    #Check if sender was called
    mock_sender.assert_awaited()


#Testing failed request
@pytest.mark.asyncio
@mock.patch("src.commands.random.sender", new_callable=AsyncMock)
@mock.patch("src.commands.random.requests.get")
async def test_random_recipe_failure(mock_get, mock_sender):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_get.return_value = mock_response

    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    random_cog = RandomModule.Random(bot_mock)

    await random_cog.random_recipe.callback(random_cog, ctx, number=1)

    ctx.send.assert_awaited_once_with("⚠️ Failed to get recipes.")

    mock_sender.assert_not_awaited()

@pytest.mark.asyncio
@mock.patch("src.commands.random.sender", new_callable=AsyncMock)
@mock.patch("src.commands.random.requests.get")
async def test_random_recipe_number_range(mock_get, mock_sender):
    ctx = MagicMock()
    ctx.send = AsyncMock()

    bot_mock = MagicMock()
    random_cog = RandomModule.Random(bot_mock)

    await random_cog.random_recipe.callback(random_cog, ctx, number=6)#more than limit - 5

    ctx.send.assert_awaited_once_with("❗ Please request between 1 and 5 recipes.")

    #Making sure there was no API request
    mock_get.assert_not_called()

    #Making sure that sender wasn't called
    mock_sender.assert_not_awaited()