# Bishoujo Mangekyou Translate
Tool for machine translating text in scenario files from Bishoujo Mangekyou games.

## **Overview**
This tool was developed against the version distributed by Steam, which has full Japanese audio but Simplified Chinese subtitles.

Lines of text from the scenario files are read and all translatable dialogue text is sent to a translating service
and the resulting translation replaces the original text. The modified text is written to a new file.

```
Usage: biman-tl.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  generate-translation-scheme  Generate pre-filled TranslationScheme.py file.
  translate-file               Translates a scenario file.
  translate-folder             Translate scenario files in folder.
```
```
Usage: biman-tl.py generate-translation-scheme [OPTIONS] DIRECTORY
                                               OUTPUT_PYTHON_FILE

  Generates a pre-filled TranslationScheme based on the scenario files in the
  specified folder and sub-folders. User needs to manually fill out the
  translated string for each dialogue title by modifying the second argument
  of each DialogueTitle entry.

  They also need to flip the third argument to True for each DialogueTitle
  that should be replaced in the dialogue lines before translation.

  The readied Python file should be added to the `translate` package,
  imported, and mapped to a scheme name in SCHEME_MAP.

Options:
  --encoding TEXT           The text encoding to use.  [default: utf-16]
  --biman-path-prefix TEXT  The path to prepend the DIRECTORY with.
  --scheme-template TEXT    The path to a python file template to fill out.
```
```
Usage: biman-tl.py translate-folder [OPTIONS] SCHEME_NAME DIRECTORY
                                    OUT_DIRECTORY

  Translates all scenario files in this folder and sub-folders.

Options:
  --deepl-api-token TEXT    The DeepL API key for the DeepL REST API. This is
                            required.
  --deepl-pro               Use the paid DeepL Pro REST API instead of the
                            free one.
  --biman-path-prefix TEXT  The path to prepend DIRECTORY and OUT_DIRECTORY
                            with.
  --max-threads INTEGER     Maximum number of threads for concurrent
                            translation requests.
```
```
Usage: biman-tl.py translate-file [OPTIONS] SCHEME_NAME FILENAME OUT_FILENAME

  Translates a single scenario file.

Options:
  --deepl-api-token TEXT    The DeepL API key for the DeepL REST API. This is
                            required.
  --deepl-pro               Use the paid DeepL Pro REST API instead of the
                            free one.
  --biman-path-prefix TEXT  The path to prepend FILENAME and OUT_FILENAME
                            with.
  --max-threads INTEGER     Maximum number of threads for concurrent
                            translation requests.
```

## **File and Format Details**
- The dialogue strings are stored in scenario files with the `.s` extension.
- The scenario files are plain text files encoded in `utf-16-le`. It is possible this may differ depending on the specific distribution of the game.
- These files are packed in FilePack format (`FilePackVer3.1` in Biman5) into `.pack` files.

## **Translation Process Details**
For each scenario file, a pre-process is performed on the lines before sending the translatable lines to the translation service.
### **Condition for determining if a line is "translatable"**
- Each line of text in the scenario is iterated through, and checked if it is Translatable.
    - Lines that are empty or start with special characters that denote game engine directives are ignored; otherwise the line is Translatable.
    - The function to check each line is supplied in the TranslationScheme; check out `schemes.biman5:should_translate()` function.
    - Special characters include the `^` `@` `???` characters. Note that some of these characters are not standard ASCII characters (like the percent).
        - It also includes the special bracket characters surrounding DialogueTitles, since DialogueTitles are not sent out for translation.
### **Pre-processing: replacing DialogueTitles and/or dialogue titles found in main dialogue lines.**
- If a line starts with `??? `, it is assumed to be a DialogueTitle.
    - The text between the brackets are extracted and matched against a DialogueTitle in the TranslationScheme.
    - Each dialogue title is replaced with the target replacement text, preserving the bracket characters:`??? ` `???`.
    - Note that this line is not sent to the translation service, and is only translated via this direct replacement.
- If the line is otherwise Translatable, check if the line contains any DialogueTitle text where `DialogueTitle.sub_in_dialog=True`,
  and replace with the corresponding text if it is.
    - This helps increase translation accuracy by forcing more consistent handling of proper nouns.
    - The TranslationScheme generated by the `generate-translation-scheme` command defaults each `DialogueTitle.sub_in_dialog` to `False`.
      When manually finishing the scheme, flip that third argument to `True` for all proper names of individual characters.
      - Since there are many non-proper-noun DialogueTitles, they are not `sub_in_dialog=True` by default so the machine translator can
        properly handle the noun in a sentence.
### **Translation: send translatable lines off to be translated, and replace the original line.**
- Iterate through each line, and if the line is Translatable, the text between the line start and line end is extracted and sent to the translation service for translation.
    - The text captured in group 1 of the `^(.+)$` regex is sent.
    - The translated text replaces the originally matched text in the line, to avoid potential problems from invisible/new line characters.

## **References**
|Name|Description|
|---|---|
|[hz86/filepack](https://github.com/hz86/filepack)|`filepack31.exe` from this repositiory was used for unpacking and repacking `.pack` files.|
|[GARbro](https://github.com/morkt/GARbro)|Utilities for exploring packed video game data archives like for Biman.|
|[sudonull](https://sudonull.com/post/9841-Qlie-visual-story-engine-disassembly)|Blog post with insights and details from the comprehensive translation of Biman 1.|
