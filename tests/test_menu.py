# kas - setup tool for bitbake based projects
#
# Copyright (c) Siemens AG, 2021
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import snack
import pytest
from kas import kas


@pytest.fixture(autouse=True)
def patch_kas(monkeypatch):
    INPUTS = iter([' ', None, ' ', None])
    ACTIONS = iter([None, 'build', None, 'build'])
    SELECTIONS = iter([0, 3])

    def mock_runOnce(unused1):
        return next(INPUTS)

    def mock_buttonPressed(unused1, unused2):
        return next(ACTIONS)

    def mock_current(unused1):
        return next(SELECTIONS)

    monkeypatch.setattr(snack.GridFormHelp, 'runOnce', mock_runOnce)
    monkeypatch.setattr(snack.ButtonBar, 'buttonPressed', mock_buttonPressed)
    monkeypatch.setattr(snack.Listbox, 'current', mock_current)


def file_contains(filename, expected):
    with open(filename) as file:
        for line in file.readlines():
            if line == expected:
                return True
    return False


def check_bitbake_options(expected):
    with open('build/bitbake.options') as file:
        return file.readline() == expected


def test_menu(monkeypatch, tmpdir):
    tdir = str(tmpdir / 'test_menu')
    shutil.copytree('tests/test_menu', tdir)
    monkeypatch.chdir(tdir)

    # select opt1 & build
    kas.kas(['menu'])
    assert file_contains('build/conf/local.conf', 'OPT1 = "1"\n')
    assert file_contains('.config.yaml', 'build_system: openembedded\n')
    assert check_bitbake_options('-c build target1\n')

    # rebuild test
    kas.kas(['build'])
    assert file_contains('build/conf/local.conf', 'OPT1 = "1"\n')
    assert check_bitbake_options('-c build target1\n')

    # select alternative target & build
    kas.kas(['menu'])
    assert file_contains('build/conf/local.conf', 'OPT1 = "1"\n')
    assert check_bitbake_options('-c build target2\n')


def test_menu_inc_workdir(monkeypatch, tmpdir):
    tdir = str(tmpdir / 'test_menu_inc')
    kas_workdir = str(tmpdir / 'test_menu_inc' / 'out')
    shutil.copytree('tests/test_menu', tdir)
    monkeypatch.chdir(tdir)
    os.mkdir(kas_workdir)
    os.environ['KAS_WORK_DIR'] = kas_workdir
    kas.kas(['menu'])
    del os.environ['KAS_WORK_DIR']


def test_menu_implicit_workdir(monkeypatch, tmpdir):
    tdir = str(tmpdir / 'test_menu_iwd')
    kas_workdir = str(tmpdir / 'test_menu_iwd_out')
    shutil.copytree('tests/test_menu', tdir)
    os.mkdir(kas_workdir)
    monkeypatch.chdir(kas_workdir)
    kas.kas(['menu', tdir + '/Kconfig'])
