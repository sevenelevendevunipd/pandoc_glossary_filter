import re
from typing import Optional

from panflute import Doc, Element, MetaMap, RawInline, Str

from .data import (
    AcronymEntry,
    GlossaryEntry,
    get_acronym_entry,
    get_glossary_entry,
    set_acronym_entry,
    set_glossary_entry,
)

filter_cmd_re = re.compile(r"{(\w+):(\w+)}")
glossary_cmds = {
    "g": "gls",
    "gs": "glspl",
    "G": "Gls",
    "Gs": "Glspl",
}
acronym_cmds = {
    "a": "gls",
}


def glossary(elem: Element, doc: Doc) -> Optional[Element]:
    """Pandoc filter that does all the magic :D

    Args:
        elem (Element): Pandoc element
        doc (Doc): Pandoc document

    Returns:
        Optional[Element]: Pandoc element iff the current element is a glossary entry or an acronym
    """
    if doc.format not in {"latex", "json"} or not isinstance(elem, Str):
        return None

    value: str = elem.text
    match = filter_cmd_re.search(value)
    if match is None:
        return None
    cmd: str = match.groups()[0]
    is_acronym = cmd in acronym_cmds
    is_glossary = cmd in glossary_cmds
    if not is_acronym and not is_glossary:
        return None
    cmd = (glossary_cmds if is_glossary else acronym_cmds)[cmd]
    label: str = match.groups()[1]

    doc.metadata["has-glossary"] = True
    if is_glossary:
        entry = get_glossary_entry(label)
        if entry is None:
            entry = GlossaryEntry("", "")
            set_glossary_entry(label, entry)

        if label not in doc.metadata["glossary-entries"]:  # type: ignore
            entry.add_to_doc(label, doc)
    else:
        entry = get_acronym_entry(label)
        if entry is None:
            entry = AcronymEntry("", "")
            set_acronym_entry(label, entry)
        acronym_entries: MetaMap = doc.metadata["acronym-entries"]  # type: ignore
        if label not in acronym_entries:
            entry.add_to_doc(label, doc)

    return RawInline(
        filter_cmd_re.sub(f"\\\\{cmd}{{{label}}}" + ("{$_A$}" if is_acronym else "{$_G$}"), value), "latex"
    )
