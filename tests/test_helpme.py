import pytest
from unittest.mock import AsyncMock, MagicMock
from src.commands.helpme import Helpme

import discord


@pytest.mark.asyncio
async def test_help_command_sends_embed():
    mock_bot = MagicMock()
    cog = Helpme(mock_bot)

    mock_ctx = MagicMock()
    mock_ctx.send = AsyncMock()

    await cog.help_command.callback(cog, mock_ctx)

    mock_ctx.send.assert_called_once()

    args, kwargs = mock_ctx.send.call_args
    assert "embed" in kwargs
    embed = kwargs["embed"]

    assert isinstance(embed, discord.Embed)
