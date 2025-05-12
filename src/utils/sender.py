import logging
import discord


async def sender(ctx, *args, **kwargs):
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            logging.warning(
                f"No permission to send messages on this channel {ctx.channel} (ID: {ctx.channel.id})."
            )
            return None

    try:
        message = await ctx.send(*args, **kwargs)
        return message
    except discord.Forbidden:
        logging.warning(
            f"No permission to send messages on this channel {ctx.channel} (ID: {ctx.channel.id})."
        )
        return None