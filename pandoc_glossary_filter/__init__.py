import sys

from loguru import logger
from panflute import toJSONFilter

from pandoc_glossary_filter.filter import glossary

from .data import get_acronym_entries, get_glossary_entries, load_data, save_data


def main():
    """Main"""
    load_data()
    toJSONFilter(glossary)
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
