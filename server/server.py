# System Libs
import asyncio
import os
import time
import pathlib
from urllib.parse import urlparse, unquote
from typing import List
import requests
# External Libs
import pygls.types as types
import pygls.features as features
from pygls.server import LanguageServer


class DRCLanguageServer(LanguageServer):

    CMD_HELLO_WORD = "extension.helloWorld"

    def __init__(self):
        super().__init__()
        self._drc_server = None

    async def get_server(self) -> str:
        if self._drc_server is not None:
            return self._drc_server
        config = await self.get_configuration_async(
            params=types.ConfigurationParams(
                [
                    types.ConfigurationItem(
                        "server",
                        "drc"
                    )
                ]
            )
        )
        self._drc_server = config[0].server
        self._drc_server = self._drc_server.strip('/')
        return self._drc_server


drc_server = DRCLanguageServer()


@drc_server.command(DRCLanguageServer.CMD_HELLO_WORD)
def command_hellow_word(ls: DRCLanguageServer, *args):
    ls.show_message("Hellow World")


@drc_server.feature(features.COMPLETION, trigger_characters=[" "])
async def completions(ls: DRCLanguageServer, params: types.CompletionParams):
    server = await drc_server.get_server()
    document = ls.workspace.get_document(params.textDocument.uri)
    word = document.word_at_position(params.position)
    response = requests.post(
        f"{server}/autocomplete",
        json=dict(text=document.source))
    if response.status_code != 200:
        return types.CompletionList(False, [])
    result = response.json()
    suggestions: List[str] = result.get("result", [])
    items = []
    for suggest in suggestions:
        print(suggest)
        suggest = suggest.replace("<|endoftext|>", "")
        suggest = suggest.replace('<|', "")
        suggest = suggest.strip(' ')
        items.append(
            types.CompletionItem(
                suggest,
                insert_text=word+suggest
            )
        )
    return types.CompletionList(False, items)
