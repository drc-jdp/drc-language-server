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
        self._word_count = 0

    async def get_server(self) -> str:
        if self._drc_server is not None:
            return self._drc_server
        # config = await self.get_configuration_async(
        #     params=types.ConfigurationParams(
        #         [
        #             types.ConfigurationItem(
        #                 "server",
        #                 "drc"
        #             )
        #         ]
        #     )
        # )
        # self._drc_server = config[0].server
        # self._drc_server = self._drc_server.strip('/')
        self._drc_server = "http://10.234.8.22:8080/tensorflow"
        return self._drc_server

    @property
    def word_count(self):
        return self._word_count

    @word_count.setter
    def word_count(self, wc):
        self._word_count = wc


drc_server = DRCLanguageServer()


@drc_server.command(DRCLanguageServer.CMD_HELLO_WORD)
def command_hellow_word(ls: DRCLanguageServer, *args):
    ls.show_message("Hellow World")


# TODO: order of autocomplete list
# TODO: trigger characters-> A-Z, a-z
# TODO: hide number suggested by autocomplete
@drc_server.feature(features.COMPLETION, trigger_characters=[' '])
async def completions(ls: DRCLanguageServer, params: types.CompletionParams):
    server = await drc_server.get_server()
    
    document = ls.workspace.get_document(params.textDocument.uri)
    word = document.word_at_position(params.position)
    model_input: str = ''
    cursor_line: int = params.position.line
    cl: int = cursor_line
    while cl > 0:
        if document.lines[cl].find('}') != -1:  # find }
            cl = cl + 1
            break
        cl = cl - 1
    for li in range(cl, cursor_line):
        model_input = model_input + document.lines[li]
    model_input += document.lines[cursor_line][:params.position.character]

    response = requests.post(
        f"{server}/autocomplete",
        json=dict(text=model_input))

    if response.status_code != 200:
        return types.CompletionList(False, [])
    result = response.json()
    suggestions: List[str] = result.get("result", [])

    items = []
    output = {}
    id = 0
    for i in range(len(suggestions)):
        suggest = suggestions[i]
        suggest = suggest.strip()

        fixed = False
        endoftext_p = suggest.find("<|end")  # <|endoftext|>
        if endoftext_p >= 0:
            endoftext: str = ''
            for t in range(endoftext_p, len(suggest)):
                if not suggest[t].isspace():
                    endoftext = endoftext + suggest[t]
                else:
                    suggest = suggest[:t+1]
                    break
            suggest = suggest.replace(endoftext, "\n")
            fixed = True

        if not fixed:
            enter = suggest.find("\n")
            if enter > 0:  # \n not the first word
                suggest = suggest[:enter+1]

        if not fixed:
            for i in range(len(suggest)):
                if suggest[i].isalnum():
                    break
            for j in range(i, len(suggest)):
                if suggest[j].isspace():
                    sug = suggest[:j]
                    sug = sug.rstrip()
                    if sug not in output:
                        output[sug] = True
                        items.append(
                            types.CompletionItem(
                                sug,
                                insert_text=word+sug,
                                sort_text=str(id)
                            )
                        )
                        id += 1

        if suggest not in output:
            output[suggest] = True
        else:
            continue

        if fixed:
            items.append(
                types.CompletionItem(
                    suggest,
                    insert_text=word+suggest,
                    sort_text=str(id)
                )
            )
            id += 1
    return types.CompletionList(False, items)
