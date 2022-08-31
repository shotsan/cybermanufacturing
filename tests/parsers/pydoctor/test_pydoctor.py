import codecs
import os

from pathlib import Path
from unittest.mock import mock_open, patch

from bs4 import BeautifulSoup

from doc2dash.parsers.pydoctor import PyDoctorParser
from doc2dash.parsers.types import EntryType, ParserEntry


HERE = os.path.dirname(__file__)

EXAMPLE_PARSE_RESULT = [
    ParserEntry(name=t[0], type=t[1], path=t[2])
    for t in [
        (
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.A",
            EntryType.METHOD,
            "twisted.conch.insults.insults.ServerProtocol"
            ".ControlSequenceParser.html#A",
        ),
        (
            "twisted.test.myrebuilder1.A",
            EntryType.CLASS,
            "twisted.test.myrebuilder1.A.html",
        ),
        (
            "twisted.test.myrebuilder2.A",
            EntryType.CLASS,
            "twisted.test.myrebuilder2.A.html",
        ),
        (
            "twisted.test.test_jelly.A",
            EntryType.CLASS,
            "twisted.test.test_jelly.A.html",
        ),
        (
            "twisted.test.test_persisted.A",
            EntryType.CLASS,
            "twisted.test.test_persisted.A.html",
        ),
        (
            "twisted.internet.task.LoopingCall.a",
            EntryType.VARIABLE,
            "twisted.internet.task.LoopingCall.html#a",
        ),
        (
            "twisted.test.myrebuilder1.A.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder1.A.html#a",
        ),
        (
            "twisted.test.myrebuilder1.Inherit.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder1.Inherit.html#a",
        ),
        (
            "twisted.test.myrebuilder2.A.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder2.A.html#a",
        ),
        (
            "twisted.test.myrebuilder2.Inherit.a",
            EntryType.METHOD,
            "twisted.test.myrebuilder2.Inherit.html#a",
        ),
        (
            "twisted.web._newclient.HTTP11ClientProtocol.abort",
            EntryType.METHOD,
            "twisted.web._newclient.HTTP11ClientProtocol.html#abort",
        ),
    ]
]


def test_parse():
    """
    The shipped example results in the expected parsing result.
    """
    with codecs.open(
        os.path.join(HERE, "pydoctor_example.html"), mode="r", encoding="utf-8"
    ) as fp:
        example = fp.read()

    with patch(
        "doc2dash.parsers.pydoctor.codecs.open",
        mock_open(read_data=example),
        create=True,
    ):
        assert (
            list(PyDoctorParser(source="foo").parse()) == EXAMPLE_PARSE_RESULT
        )


def test_patcher():
    p = PyDoctorParser(source="foo")
    with codecs.open(
        os.path.join(HERE, "function_example.html"), mode="r", encoding="utf-8"
    ) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    assert p.find_and_patch_entry(
        soup,
        name="twisted.application.app.ApplicationRunner.startReactor",
        type=EntryType.METHOD,
        anchor="startReactor",
    )

    toc_link = soup(
        "a",
        attrs={
            "name": "//apple_ref/cpp/Method/twisted.application.app."
            "ApplicationRunner.startReactor"
        },
    )

    assert toc_link

    next_tag = toc_link[0].next_sibling

    assert next_tag.name == "a"
    assert next_tag["name"] == "startReactor"
    assert not p.find_and_patch_entry(
        soup, name="invented", type=EntryType.CLASS, anchor="nonex"
    )


def test_guess_name():
    """
    Currently guessing is not supported.
    """
    assert PyDoctorParser.guess_name(Path(".")) is None
