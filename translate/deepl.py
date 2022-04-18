import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Sequence

from click import progressbar
from deep_translator import DeeplTranslator as dpl

from utils.helpers import dialog_title_text
from utils import special_chars as chars
from schemes import TranslationScheme

class DeeplTranslator:
    def __init__(self, api_key: str,
                 scheme: TranslationScheme,
                 free_api: bool = True,
                 max_threads: int = 128):
        self.deepl = dpl(api_key=api_key, use_free_api=free_api,
                         source=scheme.lang_source, target=scheme.lang_target)
        self.max_threads = max_threads
        self.scheme = scheme
        self.logger = logging.getLogger('DeeplTranslator')

    def pre_process(self, lines: Sequence[str]):
        """
        Replaces the scenario lines' dialogue title with known replacements from the scheme in-place.
        Also replaces occurances of the dialogue title within the main text itself if the DialogueTitle.sub_in_dialog is True.
        """
        logger = logging.getLogger('DeeplTranslator.pre_process')
        title_map = self.scheme.dialog_title_map
        translate_condition = self.scheme.translate_line_condition
        originals = title_map.originals
        title_count = 0
        in_dialog_count = 0
        logger.info('preprocessing lines...')
        for index in range(len(lines)):
            line = lines[index]
            if line.startswith(chars.bracket_start):
                # Replace bracketed names.
                name = dialog_title_text(line)
                if name in originals:
                    new_name = title_map[name].new.title()
                    new_line = line.replace(name, new_name)
                    lines[index] = new_line
                    title_count += 1
                    # logger.info(f'replaced bracketed name on line {index}: {line.strip()} -> {new_line.strip()}')
            elif translate_condition(line) and (matching_names := [n for n in originals if n in line and title_map[n].sub_in_dialog]):
                # Replace all occurences of proper names in dialog.
                new_line = line
                for name in matching_names:
                    new_line = new_line.replace(name, title_map[name].new.title())
                lines[index] = new_line
                in_dialog_count += 1
        logger.info(f'replaced {title_count} dialogue title names.')
        logger.info(f'replaced title names in {in_dialog_count} dialogue lines.')

    def process(self, lines: Sequence[str]):
        """
        Replaces translatable dialogue lines in-place.
        Each translatable line is translated using DeepL with the DeeplTranslator client from the deep_translator library.
        """
        logger = logging.getLogger('DeeplTranslator.process')
        translate_condition = self.scheme.translate_line_condition
        target_lines = list()
        # Identify lines to translate.
        with progressbar(enumerate(lines), label='Gathering target lines to be translated...') as enum_line:
            for index, line in enum_line:
                if translate_condition(line):
                    text_only = re.search(r"^(.+)$", line, re.UNICODE).groups()[0]
                    target_lines.append((index, line, text_only))
        logger.info(f'finished gathering {len(target_lines)} target lines.')

        # Translate lines in parallel.
        with ThreadPoolExecutor(self.max_threads, thread_name_prefix='translate_worker') as pool:
            logger.info(f'DeepL translation request thread pool started with {self.max_threads} workers.')
            futures = {pool.submit(self._translate_task, original_text): (linenum, line, original_text) for linenum, line, original_text in target_lines}
            linecount = 0
            linetotal = len(futures)
            logger.info(f'{linetotal} tasks submitted.')
            with progressbar(as_completed(futures), label='Translating lines of dialogue...', item_show_func=lambda e: f'line {linecount}/{linetotal}') as pbar:
                for future in pbar:
                    linecount += 1
                    linenum, line, original_text = futures[future]
                    if future.exception():
                        continue
                    translated = future.result()
                    lines[linenum] = line.replace(original_text, translated)
        logger.info(f'finished translating {linecount} lines of dialogue.')

    def translate(self, fp) -> Sequence[str]:
        """
        Reads the file specified in `fp` and performs processing to translate the contents and return a list of translated lines.
        """
        logging.getLogger('DeeplTranslator.translate').info(f'translating file: {fp}')
        with open(fp, 'r', encoding=self.scheme.encoding) as file:
            lines = file.readlines()
            if not lines:
                return None
            self.pre_process(lines)
            self.process(lines)
            return lines

    def _translate_task(self, text: str):
        """Thread worker task for translating a line of text."""
        translated = self.deepl.translate(text)
        return translated
