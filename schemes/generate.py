import logging
from glob import glob
from typing import Optional, Sequence

from click import progressbar

from utils.helpers import dialog_title_text
from utils.special_chars import bracket_start as brkt_s

def from_template(directory: Sequence[str], out_py_filename: str, encoding: Optional[str] = 'utf-16',
                  template_fp: Optional[str] = 'resources/scheme_template.txt'):
    """
    Creates a partially pre-filled TranslationScheme in a .py file based off of scenario files in the specified directory.
    """
    logger = logging.getLogger('schemes.generate.from_template')
    filenames = glob(f'{directory.removesuffix("/")}/**/*.s', recursive=True)
    if not filenames:
        raise Exception(f'No scenario files found in directory: {directory}')
    logger.info(f'Found {len(filenames)} in directory: {directory}')

    # Find all dialogue title texts in each input file.
    untranslated_names = set()
    with progressbar(filenames, label='Extracting bracket names from input files...', item_show_func=lambda e: f'file: {e}') as pbar:
        for filename in pbar:
            with open(filename, 'r', encoding=encoding) as file:
                for line in file:
                    if line.strip() and line.startswith(brkt_s) and (title_text := dialog_title_text(line)):
                        untranslated_names.add(title_text)
    logger.info(f'Found {len(untranslated_names)} unique dialogue titles.')

    # Read the .py file template.
    with open(template_fp, 'r') as file:
        content = file.read()
    # Format the DialogueTitle entries and format template content.
    titles = ",\n".join([f"    DialogueTitle('{name}', '', False)" for name in sorted(untranslated_names)])
    content = content.format(DIALOGUE_TITLES=titles)
    # Save to a `.py` file.
    logger.info(f'Saving generated TranslationScheme to {out_py_filename}')
    with open(out_py_filename, 'w') as file:
        file.write(content)
    # Note that the user will still need to manually modify the .py file contents with the target text
    # and remove the False arg if that name should be replaced into dialogue lines before translation.
