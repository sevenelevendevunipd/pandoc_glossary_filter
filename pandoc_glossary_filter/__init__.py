import sys

import panflute
from loguru import logger

from pandoc_glossary_filter.filter import glossary

from .data import get_acronym_entries, get_glossary_entries, load_data, save_data


def main():
    """Main"""
    load_data()
    doc = panflute.load()
    if "full-glossary" in doc.metadata and doc.metadata["full-glossary"]:
        doc.metadata["has-glossary"] = True
        doc.metadata["acronym-entries"] = {}
        doc.metadata["glossary-entries"] = {}
        for label, entry in get_acronym_entries():
            entry.add_to_doc(label, doc)
        for label, entry in get_glossary_entries():
            entry.add_to_doc(label, doc)
    else:
        doc.walk(glossary)
    panflute.dump(doc)
    save_data()
    incomplete_data: bool = False
    for label, entry in get_glossary_entries():
        if not entry.description:
            incomplete_data = True
            logger.error(f"Empty description for glossary label {label}")
        if not entry.name:
            incomplete_data = True
            logger.error(f"Empty name for glossary label {label}")
    for label, entry in get_acronym_entries():
        if not entry.long:
            incomplete_data = True
            logger.error(f"Empty long form for acronym label {label}")
        if not entry.name:
            incomplete_data = True
            logger.error(f"Empty name for acronym label {label}")
    if incomplete_data:
        sys.exit(1)
