
# <code\>
import io
import os
import re
import imp
import sys
import glob
import types
from IPython import get_ipython
from nbformat import read
from IPython.core.interactiveshell import InteractiveShell

PRINT_INFO = False


def find_notebook(fullname, path=None):
    """find a notebook, given its fully qualified name and an optional path

    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo Bar" if Foo_Bar
    does not exist.
    """
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for d in path:
        nb_path = os.path.join(d, name + ".ipynb")
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find "Notebook Name.ipynb"
        nb_path = nb_path.replace("_", " ")
        if os.path.isfile(nb_path):
            return nb_path


class NotebookLoader(object):
    """Module Loader for Jupyter Notebooks"""

    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path

    def load_module(self, fullname):
        """import a notebook as a module"""
        path = find_notebook(fullname, self.path)

        if PRINT_INFO:
            print(("importing Jupyter notebook from %s" % path))

        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = read(f, 4)

        # create the module and add it to sys.modules
        # if name in sys.modules:
        #    return sys.modules[name]
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(
                        cell.source)
                    # run the code in themodule
                    exec(code, mod.__dict__)
        finally:
            self.shell.user_ns = save_user_ns
        return mod


class NotebookFinder(object):
    """Module finder that locates Jupyter Notebooks"""

    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return

        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]


def load_ipynb_module(path, as_target=None):
    """import a notebook as a module"""
    if PRINT_INFO:
        print(("importing Jupyter notebook from %s" % path))
    if as_target is None:
        fullname = os.path.basename(path).replace('.ipynb', '')
    else:
        fullname = as_target
    # load the notebook object
    with io.open(path, 'r', encoding='utf-8') as f:
        nb = read(f, 4)

    mod = types.ModuleType(fullname)
    mod.__file__ = os.path.abspath(path)
    mod.__dict__['get_ipython'] = get_ipython
    sys.modules[fullname] = mod

    # extra work to ensure that magics that would affect the user_ns
    # actually affect the notebook module's ns
    shell = InteractiveShell.instance()
    save_user_ns = shell.user_ns
    shell.user_ns = mod.__dict__

    try:
        for cell in nb.cells:
            if cell.cell_type == 'code':
                # transform the input to executable Python
                code = shell.input_transformer_manager.transform_cell(
                    cell.source)
                # run the code in themodule
                exec(code, mod.__dict__)
    finally:
        shell.user_ns = save_user_ns
    return mod


def load_py_module(root, target, as_target=None):
    '''
    从py文件中加载模块，多个同名模块，导入第一个
    params:
        [root],根文件夹
        [target],模块名称
        [as_target],导入的模块名称，默认与target相同
    '''
    if as_target is None:
        as_target = target
    pyfile = glob.glob(
        os.path.join(root, '**', '*' + target + '.py'),
        recursive=True
    )
    if len(pyfile) == 0:
        return None
    as_target = imp.load_source(as_target, pyfile[0])
    return as_target


def reload_module(module):
    '''
    重新加载模块，若输入的是某模块的变量，返回该模块
    '''
    fname = getattr(module,'__file__',None)
    if fname is not None:
        if module.__file__.endswith('.py'):
            return imp.reload(module)
        if module.__file__.endswith('.ipynb'):
            return load_ipynb_module(module.__file__,module.__name__)
    
    fname = getattr(module,'__module__',None)
    if fname is not None and fname != '__main__':
        pmodule = sys.modules[fname]
        pmodule = reload_module(pmodule)
        return pmodule
    
    raise Exception('Fail to reload %s' % module)


def run(remove_pre_finder=True, not_ipykernel=True):
    if remove_pre_finder:
        ps = [s for s in sys.meta_path]
        for s in ps:
            if 'NotebookFinder' in str(type(s)):
                sys.meta_path.remove(s)
    if 'ipykernel' in sys.modules or not_ipykernel:
        sys.meta_path.append(NotebookFinder())


def init_module(target, globals_info=None, pattern='[^_].*[^_]'):
    if globals_info is None:
        globals_info = globals()
    if isinstance(target, str):
        target_module = globals_info[target]
    else:
        target_module = target
    for s in globals_info.keys():
        if isinstance(s, str):
            if re.match(pattern, s):
                setattr(target_module, s, globals_info[s])
        elif isinstance(s, list):
            if s in pattern:
                setattr(target_module, s, globals_info[s])
                
run()
# <\code>
