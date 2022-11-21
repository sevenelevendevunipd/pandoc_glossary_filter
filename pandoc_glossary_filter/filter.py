import re

from pandocfilters import RawInline

from .data import (
    AcronymEntry,
    GlossaryEntry,
    get_glossary_entry,
    set_glossary_entry,
    get_acronym_entry,
    set_acronym_entry,
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


def glossary(key: str, value: str, format_: str, meta: dict):
    """Pandoc filter that does all the magic :D

    Args:
        key (str): Pandoc element type
        value (str): Pandoc element content
        format_ (str): Output file format
        meta (dict): File metadata

    Returns:
        _type_: Pandoc element iff the current element is a glossary entry or an acronym
    """
    if format_ not in {"latex", "json"} or key != "Str":
        return None
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
    meta["has-glossary"] = {"t": "MetaBool", "c": True}
    if is_glossary:
        if "glossary-entries" not in meta:
            meta["glossary-entries"] = {"t": "MetaMap", "c": {}}
        entry = get_glossary_entry(label)
        if entry is None:
            entry = GlossaryEntry("", "")
            set_glossary_entry(label, entry)
        if label not in meta["glossary-entries"]["c"]:
            entry = get_glossary_entry(label)
            assert entry is not None
            meta["glossary-entries"]["c"][label] = {
                "t": "MetaMap",
                "c": {
                    "name": {"t": "MetaString", "c": entry.name},
                    "description": {"t": "MetaString", "c": entry.description},
                },
            }
            if entry.plural:
                meta["glossary-entries"]["c"][label]["c"]["plural"] = {"t": "MetaString", "c": entry.plural}
    else:
        if "acronym-entries" not in meta:
            meta["acronym-entries"] = {"t": "MetaMap", "c": {}}
        entry = get_acronym_entry(label)
        if entry is None:
            entry = AcronymEntry("", "")
            set_acronym_entry(label, entry)
        if label not in meta["acronym-entries"]["c"]:
            meta["acronym-entries"]["c"][label] = {
                "t": "MetaMap",
                "c": {
                    "name": {"t": "MetaString", "c": entry.name},
                    "description": {"t": "MetaString", "c": entry.description},
                },
            }

    return RawInline(
        "latex", filter_cmd_re.sub(f"\\\\{cmd}{{{label}}}" + ("{$_A$}" if is_acronym else "{$_G$}"), value)
    )
