from typing import Optional

import hebi

bridge = hebi.Bridge(
    command="echo hi; read a; echo yeah $a", channel=16700394, token="aaa.bbb.c"
)


@bridge.input
def on_input(content: str) -> Optional[str]:
    return content


@bridge.output
def on_output(content: str) -> Optional[str]:
    return content


bridge.run()
