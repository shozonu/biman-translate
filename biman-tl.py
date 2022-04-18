#!/usr/bin/env python3
import os
import logging
from glob import glob

import click
from schemes import TranslationScheme

from schemes.biman5 import biman5
from schemes.generate import from_template as scheme_from_template
from translate.deepl import DeeplTranslator

SCHEME_MAP = {
    'biman5': biman5
}

@click.group()
def cli():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')

@cli.command(short_help='Translates a scenario file.')
@click.argument('scheme_name')
@click.argument('filename')
@click.argument('out_filename')
@click.option('--deepl-api-token', envvar='DEEPL_API_TOKEN', help='The DeepL API key for the DeepL REST API. This is required.')
@click.option('--deepl-pro', is_flag=True, help='Use the paid DeepL Pro REST API instead of the free one.')
@click.option('--biman-path-prefix', type=str, envvar='BIMAN_PATH_PREFIX', help='The path to prepend FILENAME and OUT_FILENAME with.')
def translate_file(scheme_name: str, filename: str, out_filename: str,
                   deepl_api_token: str, deepl_pro: bool,
                   biman_path_prefix: str):
    """
    Translates a single scenario file.
    """
    logger = logging.getLogger('translate-file')
    scheme: TranslationScheme = SCHEME_MAP.get(scheme_name)
    if not scheme:
        logger.error(f'No TranslationScheme found with name: {scheme}')
        return
    if not deepl_api_token:
        logger.error('DEEPL_API_TOKEN is required from option or envvar.')
        return

    filepath = f'{biman_path_prefix}/{filename.strip()}' if biman_path_prefix else filename.strip()
    deepl = DeeplTranslator(api_key=deepl_api_token, scheme=scheme, free_api=(not deepl_pro))
    lines = deepl.translate(filepath)
    if not lines:
        logger.info('No lines returned from deepl.translate.')
        return
    logger.info(f'Writing translated file to {out_filename}')
    os.makedirs(f'{out_filename.rsplit("/")[0]}', exist_ok=True)
    with open(out_filename, 'w', encoding=scheme.encoding) as file:
        file.writelines(lines)

# Scripts in biman5 should be in data6.pack under "scenario\本編"
@cli.command(short_help='Translate scenario files in folder.')
@click.argument('scheme_name')
@click.argument('directory', type=str)
@click.argument('out_directory', type=str)
@click.option('--deepl-api-token', envvar='DEEPL_API_TOKEN', help='The DeepL API key for the DeepL REST API. This is required.')
@click.option('--deepl-pro', is_flag=True, help='Use the paid DeepL Pro REST API instead of the free one.')
@click.option('--biman-path-prefix', type=str, envvar='BIMAN_PATH_PREFIX', help='The path to prepend DIRECTORY and OUT_DIRECTORY with.')
def translate_folder(scheme_name: str, directory: str, out_directory: str,
                     deepl_api_token: str, deepl_pro: bool,
                     biman_path_prefix: str):
    """
    Translates all scenario files in this folder and sub-folders.
    """
    logger = logging.getLogger('translate-folder')
    scheme: TranslationScheme = SCHEME_MAP.get(scheme_name)
    if not scheme:
        logger.error(f'No TranslationScheme found with name: {scheme}')
        return
    if not deepl_api_token:
        logger.error('DEEPL_API_TOKEN is required from option or envvar.')
        return

    game_path = f'{biman_path_prefix}{directory.strip()}' if biman_path_prefix else directory.strip()
    logger.info(f'Searching for "*.s" files in directory: {game_path}')
    input_filenames = glob(f'{game_path}/**/*.s', recursive=True)
    logger.info(f'Found {len(input_filenames)} matching "*.s" files.\n')
    if not input_filenames:
        logger.info('Did not find any files to process.')
        return

    deepl = DeeplTranslator(api_key=deepl_api_token, scheme=scheme, free_api=(not deepl_pro))
    for filename in input_filenames:
        lines = deepl.translate(filename)
        outfilename = filename.removeprefix(game_path)
        outfilename = f'{biman_path_prefix}{out_directory}{outfilename}'
        os.makedirs(f'{outfilename.rsplit("/")[0]}', exist_ok=True)
        logger.info(f'Writing translated file to: {outfilename}\n')
        with open(outfilename, 'w', encoding=scheme.encoding) as file:
            file.writelines(lines)

@cli.command(short_help='Generate pre-filled TranslationScheme.py file.')
@click.argument('directory')
@click.argument('output_python_file')
@click.option('--encoding', default='utf-16', help='The text encoding to use.', show_default=True)
@click.option('--biman-path-prefix', type=str, envvar='BIMAN_PATH_PREFIX', help='The path to prepend the DIRECTORY with.')
@click.option('--scheme-template', default='resources/scheme_template.txt', help='The path to a python file template to fill out.')
def generate_translation_scheme(directory: str, output_python_file: str,
                                encoding: str, biman_path_prefix: str,
                                scheme_template: str):
    """
    Generates a pre-filled TranslationScheme based on the scenario files in the specified folder and sub-folders.
    User needs to manually fill out the translated string for each dialogue title by
    modifying the second argument of each DialogueTitle entry.

    They also need to flip the third argument to True for each DialogueTitle that should be replaced in the
    dialogue lines before translation.

    The readied Python file should be added to the `translate` package, imported, and mapped to a scheme name in SCHEME_MAP.
    """
    game_path = f'{biman_path_prefix}{directory.strip()}' if biman_path_prefix else directory.strip()
    scheme_from_template(game_path, output_python_file, encoding=encoding, template_fp=scheme_template)

def main():
    cli()

if __name__ == '__main__':
    main()
