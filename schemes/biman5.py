from utils import special_chars as chars
from schemes import DialogueTitle, DialogueTitleMap, TranslationScheme

dialog_map = DialogueTitleMap([
    DialogueTitle('もよか＠？？？', 'moyoka＠？？？'),
    DialogueTitle('和音', 'kazune'),
    DialogueTitle('和音的母亲', 'kazune\'s mother', False),
    DialogueTitle('奏', 'kana'),
    DialogueTitle('奏＠？？？', 'kana＠？？？'),
    DialogueTitle('女儿', 'daughter', False),
    DialogueTitle('女子学生Ａ', 'female student Ａ'),
    DialogueTitle('女子学生Ｂ', 'female student Ｂ'),
    DialogueTitle('女子学生Ｃ', 'female student Ｃ'),
    DialogueTitle('女学生', 'schoolgirl', False),
    DialogueTitle('女学生们', 'schoolgirls', False),
    DialogueTitle('女学生Ａ', 'schoolgirl Ａ', False),
    DialogueTitle('女学生Ａ／Ｂ', 'schoolgirl Ａ／Ｂ', False),
    DialogueTitle('女学生Ｂ', 'schoolgirl Ｂ', False),
    DialogueTitle('女学生Ｃ', 'schoolgirl Ｃ', False),
    DialogueTitle('女学生Ｄ', 'schoolgirl Ｄ', False),
    DialogueTitle('女学生Ｅ', 'schoolgirl Ｅ', False),
    DialogueTitle('女学生Ｆ', 'schoolgirl Ｆ', False),
    DialogueTitle('女老师', 'female teacher', False),
    DialogueTitle('小狐', 'little fox', False),
    DialogueTitle('少女', 'girl', False),
    DialogueTitle('新人厨师', 'newbie chef'),
    DialogueTitle('春', 'haru', False),
    DialogueTitle('校长', 'principal', False),
    DialogueTitle('母亲', 'mother'),
    DialogueTitle('沙织', 'saori'),
    DialogueTitle('深見', 'takami'),
    DialogueTitle('深见', 'fukami'),
    DialogueTitle('狗', 'dog', False),
    DialogueTitle('男性教師', 'male teachers', False),
    DialogueTitle('男老师', 'male teacher', False),
    DialogueTitle('皇', 'sumeragi'),
    DialogueTitle('皇／深见', 'sumeragi／fukami'),
    DialogueTitle('皇＠？？？', 'sumeragi＠？？？'),
    DialogueTitle('老师们', 'teachers', False),
    DialogueTitle('舞斗', 'maito'),
    DialogueTitle('舞斗＠？？？', 'maito＠？？？'),
    DialogueTitle('莲华', 'renge'),
    DialogueTitle('莲华／深见', 'renge／fukami'),
    DialogueTitle('莲华＠？？？', 'renge＠？？？'),
    DialogueTitle('萌世歌', 'moyoka'),
    DialogueTitle('萌世歌＠？？？', 'moyoka＠？？？'),
    DialogueTitle('蓮華', 'renge'),
    DialogueTitle('香恋', 'karen'),
    DialogueTitle('香恋／深见', 'karen／fukami'),
    DialogueTitle('香恋＠？？？', 'karen＠？？？'),
    DialogueTitle('＄ユーザー＄', '＄ユーザー＄'),
    DialogueTitle('歌', 'song', False),
    DialogueTitle('狐', 'fox', False)
])
# Script missed picking up the '歌' character? Manually added it back in.

def should_translate(line: str) -> bool:
    """
    If the line has text that should be translated, returns True.
    Otherwise, returns False.
    """
    # Lines that aren't blank and don't start with directives or dialogue title brackets.
    excluded_chars = (chars.caret, chars.pct, chars.jp_at, chars.bracket_start, chars.bracket_end)
    return bool(line.strip()) and not line.startswith(excluded_chars)

biman5 = TranslationScheme(dialog_map, should_translate, 'utf-16', 'zh', 'en')
