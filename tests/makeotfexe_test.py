from __future__ import print_function, division, absolute_import

import os
import pytest
import tempfile
import subprocess32 as subprocess

from fontTools.ttLib import TTFont

from .runner import main as runner
from .differ import main as differ

TOOL = 'makeotfexe'
CMD = ['-t', TOOL]

data_dir_path = os.path.join(os.path.split(__file__)[0], TOOL + '_data')


def _get_expected_path(file_name):
    return os.path.join(data_dir_path, 'expected_output', file_name)


def _get_input_path(file_name):
    return os.path.join(data_dir_path, 'input', file_name)


def _get_temp_file_path():
    file_descriptor, path = tempfile.mkstemp()
    os.close(file_descriptor)
    return path


def _generate_ttx_dump(font_path, tables=None):
    with TTFont(font_path) as font:
        temp_path = _get_temp_file_path()
        font.saveXML(temp_path, tables=tables)
        return temp_path


# -----
# Tests
# -----

@pytest.mark.parametrize('caret_format', [
    'bypos', 'byindex', 'mixed', 'mixed2', 'double', 'double2'])
def test_GDEF_LigatureCaret_bug155(caret_format):
    input_filename = 'bug155/font.pfa'
    feat_filename = 'bug155/caret-{}.fea'.format(caret_format)
    ttx_filename = 'bug155/caret-{}.ttx'.format(caret_format)
    actual_path = _get_temp_file_path()
    runner(CMD + ['-n', '-o',
                  'f', '_{}'.format(_get_input_path(input_filename)),
                  'ff', '_{}'.format(_get_input_path(feat_filename)),
                  'o', '_{}'.format(actual_path)])
    actual_ttx = _generate_ttx_dump(actual_path, ['GDEF'])
    expected_ttx = _get_expected_path(ttx_filename)
    assert differ([expected_ttx, actual_ttx, '-l', '2'])


@pytest.mark.parametrize(
    'feat_name',
    [
        'test_named_lookup',
        'test_singlepos_subtable_overflow',
        'test_class_pair_subtable_overflow',
        'test_class_pair_class_def_overflow',
        'test_contextual_overflow',
        'test_cursive_subtable_overflow',
        'test_mark_to_base_coverage_overflow',
        'test_mark_to_base_subtable_overflow',
        'test_mark_to_ligature_subtable_overflow',
    ])
def test_oveflow_report_bug313(feat_name):
    from shutil import copyfile
    input_filename = 'bug313/font.pfa'
    feat_filename = 'bug313/{}.fea'.format(feat_name)
    otf_path = _get_temp_file_path()

    with pytest.raises(subprocess.CalledProcessError) as err:
        """ I use -r' to send the output to a temp file.
        When the '-r' option is specified, and the there
        is a CalledProcessError exception, the output temp file
        path is returned in err.message.
        """
        log_file = runner(CMD + [
            '-r', '-e', '-n', '-o',
            'f', '_{}'.format(_get_input_path(input_filename)),
            'ff', '_{}'.format(_get_input_path(feat_filename)),
            'o', '_{}'.format(_get_input_path(otf_path)),
            'shw'])
    assert err.value.returncode == 1
    stderr_path = err.value.message
    expected_path = _get_expected_path('bug313/{}.txt'.format(feat_name))
    #copyfile(stderr_path, expected_path)
    assert differ([expected_path, stderr_path, '-l', '1'])
    
    return
    
    stderr_path = runner(
        CMD + [
            '-r', '-e', '-o',
            'f', '_{}'.format(_get_input_path(input_filename)),
            'ff', '_{}'.format(_get_input_path(feat_filename)),
            'o', '_{}'.format(actual_path),
            'shw'])
    expected_path = _get_expected_path('bug313/{}.txt'.format(feat_name))
    copyfile(stderr_path, expected_path)
    assert differ([expected_path, stderr_path, '-l', '1'])
