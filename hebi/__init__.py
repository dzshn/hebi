import asyncio
import asyncio.subprocess
from asyncio.subprocess import PIPE, STDOUT

import hikari


class Bridge:
    def __init__(self, command: str, channel: hikari.Snowflakeish, token: str):
        self.command = command
        self.channel_id = hikari.Snowflake(channel)
        self.bot = hikari.GatewayBot(token=token)
        self.process = None
        self._in = lambda _: None
        self._out = lambda _: None
        self.bot.listen()(self._on_message)
        self.bot.listen()(self._on_ready)

    async def _on_ready(self, event: hikari.ShardReadyEvent):
        self.process = await asyncio.subprocess.create_subprocess_shell(
            self.command, stdin=PIPE, stdout=PIPE, stderr=STDOUT
        )
        channel = await self.bot.rest.fetch_channel(self.channel_id)

        while True:
            try:
                line = self._in((await self.process.stdout.readuntil(b"\n")).decode())
                if line:
                    await channel.send(line)

            except (asyncio.IncompleteReadError, EOFError, ConnectionError):
                await self.bot.close()

    async def _on_message(self, event: hikari.GuildMessageCreateEvent):
        if event.channel_id != self.channel_id:
            return

        if event.is_bot:
            return

        line = self._out(event.content).encode()
        if line:
            self.process.stdin.write(line + b"\n")
            await self.process.stdin.drain()

    def run(self):
        self.bot.run()

    def input(self, func):
        self._in = func

    def output(self, func):
        self._out = func
