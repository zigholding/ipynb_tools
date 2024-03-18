
# <code\>
import os
# <\code>

# <code\>
import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor
# <\code>

# <code\>
from IPython.display import display, HTML
# <\code>

# <code\>
from datetime import datetime as dt
# <\code>

# <code\>
ENCODING = 'utf8'
# <\code>

# <code\>


def read_txt_str(path):
    '''
    读取txt文件内容
    '''
    with open(path, 'r', encoding=ENCODING) as fin:
        s = ''.join(fin.readlines())
    return s


def write_txt_str(s, path):
    '''
    将字符串写入文本文件
    '''
    with open(path, 'w', encoding=ENCODING) as fout:
        fout.write(s)
# <\code>

# <code\>


def _save_nb_object_(nb, path):
    '''
    保存nb对象
    params:
        [nb],notebook object
        [path],.html/.ipynb，根据后缀名保存文件
    '''
    if path.endswith('.ipynb'):
        with open(path, 'wt', encoding=ENCODING) as f:
            nbformat.write(nb, f)
        return
    if path.endswith('.html'):
        html = nbconvert.exporters.HTMLExporter().from_notebook_node(nb)
        write_txt_str(html[0], path)
        return


def exec_ipynb(notebook_filename, to_filename=None,
               as_version=4, timeout=600, kernel_name='python3',
               allow_errors=False, args_cell=[]
               ):
    '''
    运行
    os.system("jupyter nbconvert --ExecutePreprocessor.allow_errors=False --execute --to html your_notebook.ipynb")
    params:
        [notebook_filename],str,ipynb文件路径
        [to_filename],None/str,保存文件
        [timeout],int,每个单元格允许的最长秒数,None/-1为不限制
        [allow_errors],bool，单元格是否允许error
        [args_cell],list of list,[[cell_no,old_str,new_str]]
    '''
    path = os.path.dirname(notebook_filename)
    if path == '':
        path = '.'
    if to_filename is None:
        to_filename = os.path.basename(notebook_filename) + '#exec.ipynb'
    save_path = os.path.join(path, to_filename)

    print('exec %s to %s' % (notebook_filename, to_filename))
    t1 = dt.now()
    print('----- start at ', t1)

    with open(notebook_filename, encoding=ENCODING) as f:
        nb = nbformat.read(f, as_version=as_version)

    if isinstance(args_cell, list):
        for cell in args_cell:
            if not isinstance(cell, list):
                continue
            idx_of_cell = cell[0]
            old_str = cell[1]
            new_str = cell[2]
            if old_str in nb['cells'][idx_of_cell]['source']:
                nb['cells'][idx_of_cell]['source'] = nb['cells'][idx_of_cell]['source'].replace(
                    old_str, new_str)
                print('----- cell{%s}:Repalce 【%s】 with 【%s】' %
                      (idx_of_cell, old_str, new_str))

    ep = ExecutePreprocessor(
        timeout=timeout, kernel_name=kernel_name, allow_errors=allow_errors)
    try:
        ep.preprocess(nb, {'metadata': {'path': path}})
    except Exception as e:
        print(e)

    _save_nb_object_(nb, save_path)
    t2 = dt.now()
    print('----- finished at ', t2, ' with ', t2 - t1)
    return nb

def catch_error(nb):
    '''
    获取结果中的error
    '''
    for c in nb['cells']:
        if 'outputs' not in c:
            continue
        for o in c['outputs']:
            if o['output_type'] == 'error':
                try:
                    e='%s("%s")' %(o['ename'],o['evalue'])
                    e = BaseException(e)
                    return e
                except Exception as e:
                    return e
# <\code>
