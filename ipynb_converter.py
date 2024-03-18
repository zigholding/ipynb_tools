
# <code\>
import datetime
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta as td
# <\code>

# <code\>
import sys
from tqdm import tqdm
tqdm.pandas()
if 'ipykernel' in sys.modules:
    from tqdm import tqdm_notebook as tqdm
    from tqdm._tqdm_notebook import tqdm_notebook
    tqdm_notebook.pandas(desc="Example Desc")
# <\code>

'''<markdown\>
# IpynbPyConverter
<\markdown>'''


# <code\>
import json
import fnmatch
import os
import autopep8
# <\code>

# <code\>


class IpynbPyConverter(object):
    '''
    ipynb和py相互转换
    nbformat:4
    nbformat_minor:2
    '''

    def __init__(self, autopep8_option={'ignore': ['E402']}):
        self.autopep8_option = autopep8_option
        pass

    def str_to_file(self, s, file_path, overwrite=False, encoding='utf-8'):
        '''
        str存成文本文件
        '''
        if isinstance(s, str):
            s = s.encode(encoding)
        if overwrite or (not os.path.isfile(file_path)):
            with open(file_path, 'wb') as fout:
                fout.write(s)
                return True
        else:
            return False

    def file_to_str(self, file_path, encoding='utf-8'):
        '''
        读取文件文件
        '''
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as fin:
                s = fin.read().decode(encoding)
                return s
        else:
            return ''

    def ipynb_str2py_str(self, ipynb_str, drop_empty=True, with_code_flag=True, by_autopep=True):
        '''
        将ipynb文本转换成py文本
        params:
            drop_empty：True，不转换空的单元格
            with_code_flag，True，code型的单元格前后分别增加标识，标识为【###<code>】和【###<\code>】
        '''
        info = json.loads(ipynb_str)
        py_str = ''
        for cell in info['cells']:
            if cell['cell_type'] == 'code':
                s = ''.join(cell['source']) + '\n'
                if not drop_empty or (len(s.strip()) != 0):
                    if with_code_flag:
                        py_str = py_str + ('\n###<code\>\n%s###<\code>\n' % s)
                    else:
                        py_str = py_str + s
            else:
                cell_type = cell['cell_type']
                s = '.'.join([l.replace('\'', '\\\'').replace(
                    '\"', '\\\"') for l in cell['source']])
                if not drop_empty or (len(s.strip()) != 0):
                    s = ('\n\'\'\'<%s\>\n' % cell_type) + \
                        s + ('\n<\%s>\'\'\'\n\n' % cell_type)
                    py_str = py_str + s
        if by_autopep:
            py_str = autopep8.fix_code(py_str, options=self.autopep8_option)
        return py_str

    def build_a_cell(self, cell_type, source):
        '''
        构建一个cell
        '''
        if not isinstance(source, list):
            source = [source]
        if cell_type == 'code':
            return {
                'cell_type': cell_type,
                'source': source,
                'metadata': {},
                'outputs': [],
                'execution_count': None
            }
        else:
            return {
                'cell_type': cell_type,
                'source': source,
                'metadata': {}
            }

    def py_str2ipynb_str_with_single_cell(self, py_str):
        '''
        将py文本转换成ipynb文本，仅使用一个cell
        params:
            py_str：py文本
        '''
        source = [s + '\n' for s in py_str.split('\n')]
        s = {
            'cells': [
                self.build_a_cell('code', source)
            ],
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 2
        }
        s = json.dumps(s)
        return s

    def py_str2ipynb_str(self, py_str):
        '''
        将py文本转换为ipynb文本
        '''
        def _get_cur_cell_(cur_cell_type, cur_source):
            if len(cur_source) == 0:
                return None
            if len(cur_source[-1].strip()) == 0:
                cur_source = cur_source[:-1]
            else:
                cur_source[-1] = cur_source[-1].replace('\n', '')

            cur_cell = self.build_a_cell(cur_cell_type, cur_source)
            return cur_cell

        def _append_cur_cell_(cells, cur_cell_type, cur_source):
            if len(cur_source) != 0:
                cur_cell = _get_cur_cell_(cur_cell_type, cur_source)
                cells.append(cur_cell)

        code_sflag = ['###<code\>', '# <code\>', '#<code\>']
        code_eflag = ['###<\code>', '# <\code>', '#<\code>']
        py_lines = py_str.strip().split('\n')

        cells = []
        cur_source = []
        cur_cell_type = 'code'
        for line in py_lines:
            if line in code_sflag:
                _append_cur_cell_(cells, cur_cell_type, cur_source)
                cur_source = []
                cur_cell_type = 'code'
            elif line in code_eflag:
                _append_cur_cell_(cells, cur_cell_type, cur_source)
                cur_source = []
                cur_cell_type = 'code'
            elif fnmatch.fnmatch(line, "'''<*\>"):
                _append_cur_cell_(cells, cur_cell_type, cur_source)
                cur_source = []
                cur_cell_type = line[4:-2]
            elif fnmatch.fnmatch(line, "<\*>'''"):
                _append_cur_cell_(cells, cur_cell_type, cur_source)
                cur_source = []
                cur_cell_type = 'code'
                continue
            elif len(cur_source) != 0 or len(line.strip()) != 0:
                cur_source.append(line + '\n')
        _append_cur_cell_(cells, cur_cell_type, cur_source)

        s = {
            'cells': cells,
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 2
        }
        s = json.dumps(s)
        return s

    def convert_ipynb_file(self, ipynb_path, py_path,
                           drop_empty=True, with_code_flag=True, by_autopep=True,
                           overwrite=False, encoding='utf-8'):
        '''
        将ipynb文件转换为py文件
        '''
        ipynb_str = self.file_to_str(ipynb_path, encoding=encoding)
        py_str = self.ipynb_str2py_str(
            ipynb_str, drop_empty=drop_empty, with_code_flag=with_code_flag, by_autopep=by_autopep)
        flag = self.str_to_file(
            py_str, py_path, overwrite=overwrite, encoding=encoding)
        return flag

    def convert_py_file(self, py_path, ipynb_path, by_single_cell=False,
                        overwrite=False, encoding='utf-8'
                        ):
        '''
        将py文件转换成ipynb文件
        '''
        py_str = self.file_to_str(py_path, encoding=encoding)
        if by_single_cell:
            ipynb_str = self.py_str2ipynb_str_with_single_cell(py_str)
        else:
            ipynb_str = self.py_str2ipynb_str(py_str)
        flag = self.str_to_file(ipynb_str, ipynb_path,
                                overwrite=overwrite, encoding=encoding)
        return flag
# <\code>


'''<markdown\>
# FolderConverter
<\markdown>'''


# <code\>
import glob
import shutil
import re
# <\code>

# <code\>


class CInfo(object):
    MSG_LT_LAST_CTIME = 'Less than last coverted time.'
    MSG_LT_OUT_MTIME = 'Less than modify time of out path'
    MSG_WRONG_DIR = 'Out path is wrong.'
    MSG_SOFT_SUCCESS = 'Success Soft'
    MSG_SOFT_FAIL = 'Fail Soft'
    MSG_HARD_SUCCESS = 'Success Hard'
    MSG_HARD_FAIL = 'Fail Hard'
    MSG_RULE_SKIP = 'Skip the file'
    RULE_SKIP = 'rule_skip'
    RULE_COPY = 'rule_copy'
    RULE_IPYNB2PY = 'rule_ipynb2py'
    RULE_PY2IPYNB = 'rule_py2ipynb'


class PATTERNS(object):
    # 第一个字符是下划线或字母，之后由下划线、字母和数字组成
    PY_VALID_NAME = '[_A-z][_A-z\d]*'


class FolderConverter(object):
    '''
    按一定规则将文件夹A中的文件转换到文件夹B中
    '''

    def __init__(self, in_dir, out_dir,
                 is_py_with_code_flag=True,
                 is_ipynb_single_cell=False,
                 autopep8_option={'ignore': ['E402']}
                 ):
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.ipynb_py_converter = IpynbPyConverter(autopep8_option)
        self.is_py_with_code_flag = is_py_with_code_flag
        self.is_ipynb_single_cell = is_ipynb_single_cell
        self.autopep8_option = autopep8_option

    def init(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir

    def rule_skip(self, in_path, out_path):
        return out_path

    def rule_copy(self, in_path, out_path):
        shutil.copy(in_path, out_path)
        return out_path

    def rule_ipynb2py(self, in_path, out_path):
        if out_path.endswith('.ipynb'):
            out_path = out_path[:-6] + '.py'
        self.ipynb_py_converter.convert_ipynb_file(in_path, out_path,
                                                   with_code_flag=self.is_py_with_code_flag, overwrite=True)
        return out_path

    def rule_py2ipynb(self, in_path, out_path):
        if out_path.endswith('.py'):
            out_path = out_path[:-3] + '.ipynb'
        self.ipynb_py_converter.convert_py_file(in_path, out_path,
                                                by_single_cell=self.is_ipynb_single_cell, overwrite=True)
        return out_path

    def _inpath2outpath_(self, in_path, rule_func=None):
        out_path = in_path.replace(self.in_dir, self.out_dir)
        if rule_func == getattr(self, 'rule_py2ipynb'):
            if out_path.endswith('.py'):
                out_path = out_path[:-3] + '.ipynb'
        if rule_func == getattr(self, 'rule_ipynb2py'):
            if out_path.endswith('.ipynb'):
                out_path = out_path[:-6] + '.py'
        return out_path

    def _makedirs_for_outpath_(self, out_path):
        '''
        output:
            1，文件夹已存在
            2，新建文件夹
            -1，新建文件夹失败
        '''
        dir_name = os.path.dirname(out_path)
        if os.path.isdir(dir_name):
            return 1
        try:
            os.makedirs(dir_name)
            return 2
        except:
            return -1

    def _modify_time_(self, file):
        return dt.fromtimestamp(os.path.getmtime(file))

    def convert_file_soft(self, in_path, rule_func, last_convert_time):
        '''
        按特征规则时转换文件，规则为：
            ——原始文件更新时间<最近一次转换时间，不转换，返回CInfo.MSG_LT_LAST_CTIME；
            ——原始文件更新时间<目标文件更新时间，不转换，返回CInfo.MSG_LT_OUT_MTIME；
            ——执行转换文件：成功，返回CInfo.MSG_SOFT_SUCCESS；失败，返回CInfo.MSG_SOFT_FAIL；
            ——目标文件的路径有误时，不转换，返回CInfo.MSG_WRONG_DIR；
        params:
            last_convert_time，dt，最近一次转换时间
            rule_func，执行文件转换函数，用法为rule_func(in_path,out_path)
        '''
        modify_dt = self._modify_time_(in_path)
        if modify_dt <= last_convert_time:
            return CInfo.MSG_LT_LAST_CTIME

        out_path = self._inpath2outpath_(in_path, rule_func)

        if os.path.isfile(out_path):
            modify_dt2 = self._modify_time_(out_path)
            if modify_dt <= modify_dt2:
                return CInfo.MSG_LT_OUT_MTIME

        if self._makedirs_for_outpath_(out_path) == -1:
            return CInfo.MSG_WRONG_DIR

        out_path = rule_func(in_path, out_path)

        if os.path.isfile(out_path):
            return CInfo.MSG_SOFT_SUCCESS
        else:
            return CInfo.MSG_SOFT_FAIL

    def convert_file_hard(self, in_path, rule_func):
        '''
        强制转换文件：
            ——执行转换文件：成功，返回CInfo.MSG_HARD_SUCCESS；失败，返回CInfo.MSG_HARD_FAIL；
            ——目标文件的路径有误时，不转换，返回CInfo.MSG_WRONG_DIR；
        params:
            last_convert_time，dt，最近一次转换时间
            rule_func，执行文件转换函数，用法为rule_func(in_path,out_path)
        '''
        out_path = self._inpath2outpath_(in_path, rule_func)
        if self._makedirs_for_outpath_(out_path) == -1:
            return CInfo.MSG_WRONG_DIR

        out_path = rule_func(in_path, out_path)

        if os.path.isfile(out_path):
            return CInfo.MSG_HARD_SUCCESS
        else:
            return CInfo.MSG_HARD_FAIL

    def convert_file(self, in_path, rule_func, last_convert_time, is_soft=True):
        '''
        转换文件，详见convert_file_soft/convert_file_hard
        '''
        if is_soft:
            return self.convert_file_soft(in_path, rule_func, last_convert_time)
        else:
            return self.convert_file_hard(in_path, rule_func)

    def origin_files_and_dirs(self, recursive=True, dirname=None):
        '''
        返回所有文件和文件夹列表
        '''
        files = []
        dirs = []
        if dirname is None:
            dirname = self.in_dir
        if recursive:
            paths = glob.glob(os.path.join(
                dirname, '**', '*'), recursive=recursive)
        else:
            paths = glob.glob(os.path.join(dirname, '*'), recursive=recursive)
        for f in paths:
            if os.path.isfile(f):
                files.append(f)
            elif os.path.isdir(f):
                dirs.append(f)
        return files, dirs

    def loads_json_dict(self, in_path, encoding='utf-8'):
        '''
        读取dict的json文件，若k以_dt结尾，转换成datetime格式，'%Y%m%d%H%M'
        '''
        if not os.path.isfile(in_path):
            return {}
        s = self.ipynb_py_converter.file_to_str(in_path, encoding=encoding)
        if len(s) == 0:
            return {}
        info = json.loads(s)
        for k in info.keys():
            if k.endswith('_dt') or k.endswith('_time'):
                info[k] = dt.strptime(info[k], '%Y%m%d%H%M')
        return info

    def dumps_json_dict(self, info, out_path, overwrite=True, encoding='utf-8'):
        '''
        保存dict的json文件，若值为datetime，转换成文本格式'%Y%m%d%H%M'
        '''
        out_info = {}
        for k in info.keys():
            if isinstance(info[k], dt):
                out_info[k] = info[k].strftime('%Y%m%d%H%M')
            else:
                out_info[k] = info[k]
        s = json.dumps(out_info)
        self.ipynb_py_converter.str_to_file(
            s, out_path, overwrite=overwrite, encoding=encoding)
        return s

    def convert_indir2outdir(self, exec_items, last_convert_time,
                             path_match_pattern='.*',
                             is_soft=True, to_debug=False, show_bar=True,
                             print_exec_flag=False, print_success_flag=True
                             ):
        '''
        转换整个文件夹
        params:
            path_match_pattern, 优先过滤文件
            exec_items，list，映射表，每个item是个dict，由basename_pat和rule_func组成
        '''
        exec_res = {}
        files, dirs = self.origin_files_and_dirs()
        is_skip = True

        files = [f for f in files if (
            re.match(path_match_pattern, f) is not None)]
        for f in tqdm(files) if show_bar else files:
            basename = os.path.basename(f)
            for item in exec_items:
                if re.match(item['basename_pat'], basename) is not None:
                    if to_debug:
                        if print_exec_flag:
                            print(item['basename_pat'], '\t\t',
                                  basename, '\t\t', item['rule_func'])
                    else:
                        try:
                            rule_func = item['rule_func']
                            if isinstance(rule_func, str):
                                rule_func = getattr(self, rule_func)
                            flag = self.convert_file(
                                f, rule_func, last_convert_time=last_convert_time, is_soft=is_soft)
                            cur_res = exec_res.get(flag, [])
                            cur_res.append(f)
                            exec_res[flag] = cur_res
                            if (print_success_flag and (flag in [CInfo.MSG_SOFT_SUCCESS, CInfo.MSG_HARD_SUCCESS])):
                                print(f, '\n\t', item['rule_func'], '\t\t', flag)
                            elif print_exec_flag:
                                print(basename, '\t\t',
                                      item['rule_func'], '\t\t', flag)
                        except Exception as e:
                            print(e)
                    is_skip = False
                    break
            if is_skip:
                exec_res[CInfo.MSG_RULE_SKIP] = exec_res.get(
                    CInfo.MSG_RULE_SKIP, [])
                if print_exec_flag:
                    print(basename, '\t\t', CInfo.MSG_RULE_SKIP)
                exec_res[CInfo.MSG_RULE_SKIP].append(f)
            is_skip = True
        return exec_res
# <\code>


'''<markdown\>
## Git
<\markdown>'''


# <code\>
class GitItems(object):
    py2nb_items = [
        {
            'basename_pat': '^__init__\.py$',
            'rule_func': 'rule_copy'
        },
        {
            'basename_pat': '^(?!__init__\.py$).*\.py$',
            'rule_func': 'rule_py2ipynb'
        },
        {
            'basename_pat': '^.*((\\.txt)|(\\.config))$',
            'rule_func': 'rule_copy'
        },
    ]

    nb2py_items = [
        {
            'basename_pat': '^.*((\\.py)|(\\.txt)|(\\.config))$',
            'rule_func': 'rule_copy'
        },
        {
            'basename_pat': '^.*\.ipynb$',
            'rule_func': 'rule_ipynb2py'
        },
    ]

    @staticmethod
    def get_items(direction, prefix_items=None, suffix_items=None):
        '''
        '''
        if prefix_items is None:
            prefix_items = {}
        if suffix_items is None:
            suffix_items = {}

        if direction == 'py2nb':
            middle_items = GitItems.py2nb_items
        elif direction == 'nb2py':
            middle_items = GitItems.nb2py_items
        else:
            middle_items = {}

        items = []
        for item in [prefix_items, middle_items, suffix_items]:
            for i in item:
                items.append(i)
        return items
# <\code>

# <code\>


class GitConverter(object):
    def __init__(self, py_dir, nb_dir, exec_json_file,
                 prefix_items=None, suffix_items=None,
                 direction='py2nb>nb2py', autopep8_option={}):
        self.direction = direction.split('>')[0]
        if self.direction == 'py2nb':
            in_dir = py_dir
            out_dir = nb_dir
        else:
            in_dir = nb_dir
            out_dir = py_dir
        self.converter = FolderConverter(
            in_dir, out_dir, autopep8_option=autopep8_option)
        self.exec_json_file = exec_json_file
        self.exec_items = GitItems.get_items(
            self.direction, prefix_items, suffix_items)

    def get_last_ctime(self, default=dt(2010, 1, 1)):
        '''
        最后一次转换时间
        '''
        info = self.converter.loads_json_dict(self.exec_json_file)
        info['last_nb2py_dt'] = info.get('last_nb2py_|dt', default)
        info['last_py2nb_dt'] = info.get('last_py2nb_dt', default)
        last_convert_time = max(info['last_py2nb_dt'], info['last_nb2py_dt'])
        return last_convert_time

    def update_last_ctime(self):
        '''
        更新最后一次转换时间
        '''
        info = self.converter.loads_json_dict(self.exec_json_file)
        info['last_%s_dt' % self.direction] = dt.now()
        print(self.converter.dumps_json_dict(info, self.exec_json_file))

    def exec(self, **kwargs):
        '''
        执行转换
        '''
        last_convert_time = self.get_last_ctime()
        exec_res = self.converter.convert_indir2outdir(
            self.exec_items, last_convert_time,
            **kwargs
        )
        self.update_last_ctime()

        for k in exec_res.keys():
            print(k, len(exec_res[k]))
        return exec_res
# <\code>
