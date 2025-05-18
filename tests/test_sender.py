import pytest
from unittest.mock import AsyncMock, MagicMock
from src.utils.sender import sender


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock() #default value is None
    ctx.guild = MagicMock()
    ctx.channel = MagicMock()
    ctx.channel.id = 123
    ctx.channel.permissions_for.return_value.send_messages = True  #overwrite in tests
    return ctx

#Have permission adn message was sent
@pytest.mark.asyncio
async def test_sender_with_permission(mock_ctx):
    mock_ctx.send.return_value = "Message sent"

    result = await sender(mock_ctx, content="Hi!")
    mock_ctx.send.assert_called_once_with(content="Hi!")

    assert result == "Message sent"



#Don't have permission
@pytest.mark.asyncio
async def test_sender_without_permission(mock_ctx):
    mock_ctx.channel.permissions_for.return_value.send_messages = False

    result = await sender(mock_ctx, content="Blocked")
    mock_ctx.send.assert_not_awaited()

    assert result is None

