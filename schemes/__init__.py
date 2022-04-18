from dataclasses import dataclass, field
from typing import Callable, List, Set, Dict

@dataclass
class DialogueTitle:
    original: str
    new: str
    sub_in_dialog: bool = True

@dataclass
class DialogueTitleMap:
    _body: List[DialogueTitle]
    _mapping: Dict[str, DialogueTitle] = field(init=False)
    originals: Set[str] = field(init=False)
    def __post_init__(self):
        self.originals = set(sorted([title.original for title in self._body]))
        self._mapping = {title.original: title for title in self._body}
        self._mapping = {orig: self._mapping[orig] for orig in self.originals}
    def __getitem__(self, name):
        if name in self.originals:
            return self._mapping[name]

@dataclass
class TranslationScheme:
    dialog_title_map: DialogueTitleMap
    translate_line_condition: Callable[[str], bool]
    encoding: str
    lang_source: str
    lang_target: str
