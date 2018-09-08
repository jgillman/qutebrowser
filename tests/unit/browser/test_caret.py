# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2018 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for caret browsing mode."""

import os.path
import textwrap

import pytest
from PyQt5.QtCore import QUrl

from qutebrowser.utils import usertypes
from helpers import utils


@pytest.fixture
def caret(web_tab, qtbot, mode_manager):
    path = os.path.join(utils.abs_datapath(), 'caret.html')
    with qtbot.wait_signal(web_tab.load_finished):
        web_tab.openurl(QUrl.fromLocalFile(path))

    mode_manager.enter(usertypes.KeyMode.caret)

    return web_tab.caret


class Selection:

    """Helper to interact with the caret selection."""

    def __init__(self, qtbot, caret):
        self._qtbot = qtbot
        self._caret = caret
        self._callback_checker = utils.CallbackChecker(qtbot)

    def check(self, expected):
        self._caret.selection(self._callback_checker.callback)
        self._callback_checker.check(expected)

    def check_multiline(self, expected):
        self.check(textwrap.dedent(expected).strip())

    def toggle(self):
        with self._qtbot.wait_signal(self._caret.selection_toggled):
            self._caret.toggle_selection()


@pytest.fixture
def selection(qtbot, caret, callback_checker):
    return Selection(qtbot, caret)


class TestDocument:

    def test_selecting_entire_document(self, caret, selection):
        selection.toggle()
        caret.move_to_end_of_document()
        selection.check_multiline("""
            one two three
            eins zwei drei

            four five six
            vier fünf sechs
        """)

    def test_moving_to_end_and_start(self, caret, selection):
        caret.move_to_end_of_document()
        caret.move_to_start_of_document()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("one")

    def test_moving_to_end_and_start_with_selection(self, caret, selection):
        caret.move_to_end_of_document()
        selection.toggle()
        caret.move_to_start_of_document()
        selection.check_multiline("""
            one two three
            eins zwei drei

            four five six
            vier fünf sechs
        """)


class TestBlock:

    def test_selecting_block(self, caret, selection):
        selection.toggle()
        caret.move_to_end_of_next_block()
        selection.check_multiline("""
            one two three
            eins zwei drei
        """)

    def test_selecting_a_block(self, caret, selection):
        selection.toggle()
        caret.move_to_end_of_next_block()
        selection.check_multiline("""
            one two three
            eins zwei drei
        """)

    def test_moving_back_to_the_end_of_prev_block_with_sel(self, caret, selection):
        caret.move_to_end_of_next_block(2)
        selection.toggle()
        caret.move_to_end_of_prev_block()
        caret.move_to_prev_word()
        selection.check_multiline("""
            drei

            four five six
        """)

    def test_moving_back_to_the_end_of_prev_block(self, caret, selection):
        caret.move_to_end_of_next_block(2)
        caret.move_to_end_of_prev_block()
        selection.toggle()
        caret.move_to_prev_word()
        selection.check("drei")

    def test_moving_back_to_the_start_of_prev_block_with_sel(self, caret, selection):
        caret.move_to_end_of_next_block(2)
        selection.toggle()
        caret.move_to_start_of_prev_block()
        selection.check_multiline("""
            eins zwei drei

            four five six
        """)

    def test_moving_back_to_the_start_of_prev_block(self, caret, selection):
        caret.move_to_end_of_next_block(2)
        caret.move_to_start_of_prev_block()
        selection.toggle()
        caret.move_to_next_word()
        selection.check("eins ")

    def test_moving_to_the_start_of_next_block_with_sel(self, caret, selection):
        selection.toggle()
        caret.move_to_start_of_next_block()
        selection.check("one two three\n")

    def test_moving_to_the_start_of_next_block(self, caret, selection):
        caret.move_to_start_of_next_block()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("eins")


class TestLine:

    def test_selecting_a_line(self, caret, selection):
        selection.toggle()
        caret.move_to_end_of_line()
        selection.check("one two three")

    def test_moving_and_selecting_a_line(self, caret, selection):
        caret.move_to_next_line()
        selection.toggle()
        caret.move_to_end_of_line()
        selection.check("eins zwei drei")

    def test_selecting_next_line(self, caret, selection):
        selection.toggle()
        caret.move_to_next_line()
        selection.check("one two three\n")

    def test_moving_to_end_and_to_start_of_line(self, caret, selection):
        caret.move_to_end_of_line()
        caret.move_to_start_of_line()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("one")

    def test_selecting_a_line_backwards(self, caret, selection):
        caret.move_to_end_of_line()
        selection.toggle()
        caret.move_to_start_of_line()
        selection.check("one two three")

    def test_selecting_previous_line(self, caret, selection):
        caret.move_to_next_line()
        selection.toggle()
        caret.move_to_prev_line()
        selection.check("one two three\n")

    def test_moving_to_previous_line(self, caret, selection):
        caret.move_to_next_line()
        caret.move_to_prev_line()
        selection.toggle()
        caret.move_to_next_line()
        selection.check("one two three\n")


class TestWord:

    def test_selecting_a_word(self, caret, selection):
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("one")

    def test_moving_to_end_and_selecting_a_word(self, caret, selection):
        caret.move_to_end_of_word()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check(" two")

    def test_moving_to_next_word_and_selecting_a_word(self, caret, selection):
        caret.move_to_next_word()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("two")

    def test_moving_to_next_word_and_selecting_until_next_word(self, caret, selection):
        caret.move_to_next_word()
        selection.toggle()
        caret.move_to_next_word()
        selection.check("two ")

    def test_moving_to_previous_word_and_selecting_a_word(self, caret, selection):
        caret.move_to_end_of_word()
        selection.toggle()
        caret.move_to_prev_word()
        selection.check("one")

    def test_moving_to_previous_word(self, caret, selection):
        caret.move_to_end_of_word()
        caret.move_to_prev_word()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("one")


class TestChar:

    def test_selecting_a_char(self, caret, selection):
        selection.toggle()
        caret.move_to_next_char()
        selection.check("o")

    def test_moving_and_selecting_a_char(self, caret, selection):
        caret.move_to_next_char()
        selection.toggle()
        caret.move_to_next_char()
        selection.check("n")

    def test_selecting_previous_char(self, caret, selection):
        caret.move_to_end_of_word()
        selection.toggle()
        caret.move_to_prev_char()
        selection.check("e")

    def test_moving_to_previous_char(self, caret, selection):
        caret.move_to_end_of_word()
        caret.move_to_prev_char()
        selection.toggle()
        caret.move_to_end_of_word()
        selection.check("e")


def test_drop_selection(caret, selection):
    selection.toggle()
    caret.move_to_end_of_word()
    caret.drop_selection()
    selection.check("")


class TestSearch:

    # https://bugreports.qt.io/browse/QTBUG-60673

    @pytest.mark.qtbug60673
    @pytest.mark.no_xvfb
    def test_yanking_a_searched_line(self, caret, selection, mode_manager, callback_checker, web_tab, qtbot):
        web_tab.show()
        mode_manager.leave(usertypes.KeyMode.caret)

        web_tab.search.search('fiv', result_cb=callback_checker.callback)
        callback_checker.check(True)

        mode_manager.enter(usertypes.KeyMode.caret)
        caret.move_to_end_of_line()
        selection.check('five six')

    @pytest.mark.qtbug60673
    @pytest.mark.no_xvfb
    def test_yanking_a_searched_line_with_multiple_matches(self, caret, selection, mode_manager, callback_checker, web_tab, qtbot):
        web_tab.show()
        mode_manager.leave(usertypes.KeyMode.caret)

        web_tab.search.search('w', result_cb=callback_checker.callback)
        callback_checker.check(True)

        web_tab.search.next_result(result_cb=callback_checker.callback)
        callback_checker.check(True)

        mode_manager.enter(usertypes.KeyMode.caret)

        caret.move_to_end_of_line()
        selection.check('wei drei')