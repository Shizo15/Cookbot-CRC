import pytest
from unittest.mock import AsyncMock, MagicMock
from src.main import user_favorites, favorites


@pytest.mark.asyncio
async def test_favorites_command_with_items():
    mock_ctx = MagicMock()
    mock_ctx.author.id = 789
    mock_ctx.guild.id = 1
    mock_ctx.channel.id = 2
    user_favorites[789] = [100, 200]

    mock_ctx.send = AsyncMock()

    await favorites(mock_ctx)

    mock_ctx.send.assert_awaited_once()
    sent_message = mock_ctx.send.call_args[0][0]

    assert "100" in sent_message
    assert "200" in sent_message

@pytest.mark.asyncio
async def test_favorites_command_without_items():
    mock_ctx = MagicMock()
    mock_ctx.author.id = 789
    mock_ctx.guild.id = 1
    mock_ctx.channel.id = 2
    user_favorites[789] = []

    mock_ctx.send = AsyncMock()

    await favorites(mock_ctx)

    mock_ctx.send.assert_awaited_once()
    sent_message = mock_ctx.send.call_args[0][0]

    assert sent_message == "You don't have any favorite recipes yet.❤️"

