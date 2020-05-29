# System Libs
import os
import time
import pathlib
from urllib.parse import urlparse, unquote
from typing import List
# External Libs
import pygls.types as types
import pygls.features as features
from pygls.server import LanguageServer


class DRCLanguageServer(LanguageServer):

    CMD_HELLO_WORD = "extension.helloWorld"

    def __init__(self):
        super().__init__()


drc_server = DRCLanguageServer()


@drc_server.command(DRCLanguageServer.CMD_HELLO_WORD)
def command_hellow_word(ls: DRCLanguageServer, *args):
    ls.show_message("Hellow World")


@drc_server.feature(features.COMPLETION, trigger_characters=[" "])
def completions(ls: DRCLanguageServer, params: types.CompletionParams):
    uri = params.textDocument.uri
    position = params.position
    document = ls.workspace.get_document(params.textDocument.uri)
    prev_position = types.Position(
        line=position.line, character=position.character-1)
    word = document.word_at_position(prev_position)
    line = document.lines[position.line]
    trigger = types.Command(
        title="Trigger Suggest", command="editor.action.triggerSuggest")
    if word == "EXT":
        return types.CompletionList(True, [
            types.CompletionItem('M1', insert_text="M1 ", command=trigger),
            types.CompletionItem('M2', insert_text="M2 ", command=trigger)
        ])
    elif word == "M1":
        return types.CompletionList(True, [
            types.CompletionItem('M2', insert_text="M2 ", command=trigger)
        ])
    elif word == "M2":
        return types.CompletionList(True, [
            types.CompletionItem('>', insert_text="> ", command=trigger),
            types.CompletionItem('<=', insert_text="<= ", command=trigger),
        ])
    elif line.find("<=") > 0:
        return types.CompletionList(True, [
            types.CompletionItem('1.0', insert_text="1.0"),
        ])
    else:
        return types.CompletionList(True, [
            types.CompletionItem('EXT', insert_text="EXT ", command=trigger),
            types.CompletionItem('INT', insert_text="INT ", command=trigger)
        ])
