#! /usr/bin/env python3
#title       :Demo Builder
#description :Build, execute and store Jupyter Notebook RISE slides
#author      :Kacper Sokol <kacper@xmlx.io>
#license     :new BSD
#source      :https://github.com/xmlx-io/xml-slides
#==============================================================================#

import glob
import os
import re
import shutil
import sys
import yaml

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

DISCARD_CELL_KEYS = {
    'id': 'del',
    'execution_count': None,
    'outputs': []
}

METADATA = {
    'kernelspec': {
        'display_name': 'Python 3 (ipykernel)',
        'language': 'python',
        'name': 'python3'
    },
    'rise': {
        'start_slideshow_at': 'beginning',
        'transition': 'none',
        'theme': 'solarized',
        'width': '1680px'
    }
}

CSS_RISE = 'demos/rise.css'
IPYNB_GLOB = 'demos/**/*.ipynb'
BUILD_DIR = '_build'

QUARTO_CONFIG = '_quarto.yml'
REPLACE_VAR = re.compile('{{<\s*meta\s*(?P<var>\S+)\s*>}}')

with open(QUARTO_CONFIG, 'r') as quarto_config:
    try:
        REPLACE_DIR = yaml.safe_load(quarto_config)
    except yaml.YAMLError as exc:
        print(exc)

def replace_var(matchobj):
    matches = matchobj.groupdict()
    if 'var' not in matches:
        raise Exception('Missing replacement matches')

    _current_sub_dict = REPLACE_DIR
    for key in matches['var'].strip().split('.'):
        _current_sub_dict = _current_sub_dict.get(key, None)
        if _current_sub_dict is None:
            raise Exception(f'Missing replacement dir key: {key}')

    assert isinstance(_current_sub_dict, str), 'Expect string replacement'
    return _current_sub_dict

# Build the notebooks
def build_demos():
    # TODO: implement support for MyST Markdown notebooks
    for notebook_path in glob.glob(IPYNB_GLOB):
        with open(notebook_path) as f_read:
            nb = nbformat.read(f_read, as_version=4)

            # replace figure patterns in-place
            if _replace:
                for cell in nb.get('cells', []):
                    if cell.get('cell_type', '') == 'markdown':
                        if 'source' in cell:
                            cell['source'] = REPLACE_VAR.sub(
                                replace_var, cell['source'])

            # execute in-place and save
            notebook_dir = os.path.dirname(notebook_path)
            save_path = os.path.join(BUILD_DIR, notebook_path)
            save_dir = os.path.dirname(save_path)
            save_file = os.path.basename(save_path)
            save_filebase = os.path.splitext(save_file)[0]
            if _execute:
                ep = ExecutePreprocessor()
                ep.preprocess(nb, {'metadata': {'path': save_dir}})
            if _save:
                if not os.path.isdir(save_dir):
                    os.makedirs(save_dir)

                # copy the metadata dictionary
                if _meta:
                    nb['metadata'] = dict(METADATA)

                # save notebook
                with open(save_path, 'w', encoding='utf-8') as f_write:
                    nbformat.write(nb, f_write)

                # copy the rise.css and notebook.css
                shutil.copy2(CSS_RISE, save_dir)
                css_notebook = os.path.join(notebook_dir, f'{save_filebase}.css')
                if os.path.isfile(css_notebook):
                    shutil.copy2(css_notebook, save_dir)

# Clean up the notebooks
def clean_demos():
    for notebook_path in glob.glob(IPYNB_GLOB):
        with open(notebook_path) as f_read:
            nb = nbformat.read(f_read, as_version=4)
        
        for cell in nb.get('cells', []):
            for id_, val_ in DISCARD_CELL_KEYS.items():
                if id_ in cell:
                    if val_ == 'del':
                        del cell[id_]
                    else:
                        cell[id_] = val_

        nb['metadata'] = dict()
        nb['nbformat_minor'] = 4  # to prevent random cell IDs

        with open(notebook_path, 'w', encoding='utf-8') as f_write:
            nbformat.write(nb, f_write)

if __name__ == '__main__':
    _replace = True
    _execute = not True
    _save = True
    _meta = True

    assert len(sys.argv) == 2, 'Expect one argument: *build* or *clean*'
    if sys.argv[1].lower() == 'build':
        build_demos()
    elif sys.argv[1].lower() == 'clean':
        clean_demos()
    else:
        assert False, f'Unrecognised argument {sys.argv[1]}'
