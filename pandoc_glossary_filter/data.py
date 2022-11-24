import pathlib
from dataclasses import dataclass, field
from typing import Iterable, Optional, Dict, Tuple

import yaml
from loguru import logger


@dataclass
class GlossaryEntry:
    """
    A class representing a glossary entry.

    Attributes:
        name: Word(s) that should be rendered in occurences of the glossary entry
        description: Explanation of the word's meaning
        plural: Eventual word plural form
    """

    name: str
    description: str
    plural: Optional[str] = None


@dataclass
class AcronymEntry:
    """
    A class representing an acronym.

    Attributes:
        name: Acronym that should be rendered
        description: Acronym meaning
    """

    name: str
    long: str
    description: Optional[str] = None


@dataclass
class Data:
    """
    Class used for internal state storage
    """

    glossary_data: Dict[str, GlossaryEntry] = field(default_factory=dict)
    glossary_dirty: bool = False
    acronym_data: Dict[str, AcronymEntry] = field(default_factory=dict)
    acronym_dirty: bool = False


__DATA = Data()


def load_file(file_name: str):
    """Loads a .yaml file, defaulting to an empty dict if the file is not found.

    Args:
        file_name (str): name of the file to be loaded

    Returns:
        Any: loaded dict
    """
    try:
        return yaml.load(pathlib.Path(file_name).read_text(encoding="utf-8"), yaml.Loader)
    except FileNotFoundError:
        logger.warning(f"{file_name} not found, using empty one")
        return {}


def save_file(file_name: str, data):
    """Saves a .yaml file

    Args:
        file_name (str): name of the file to be loaded
        data (Any): data to be saved
    """
    pathlib.Path(file_name).write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")


def load_data():
    """Loads filter data"""
    __DATA.glossary_data = load_file("glossary.yaml")
    __DATA.acronym_data = load_file("acronyms.yaml")


def save_data():
    """Saves filter data"""
    if __DATA.glossary_dirty:
        save_file("glossary.yaml", __DATA.glossary_data)
    if __DATA.acronym_dirty:
        save_file("acronyms.yaml", __DATA.acronym_data)


def set_glossary_entry(label: str, entry: GlossaryEntry):
    """Sets a glossary entry for a label

    Args:
        label (str): entry label
        entry (GlossaryEntry): glossary entry
    """
    __DATA.glossary_dirty = True
    __DATA.glossary_data[label] = entry


def get_glossary_entry(label: str) -> Optional[GlossaryEntry]:
    """Gets a glossary entry from a label

    Args:
        label (str): entry label

    Returns:
        Optional[GlossaryEntry]: glossary entry if found, `None` otherwise
    """
    return __DATA.glossary_data.get(label, None)


def get_glossary_entries() -> Iterable[Tuple[str, GlossaryEntry]]:
    """Gets all the registered glossary entries

    Returns:
        Iterable[Tuple[str, GlossaryEntry]]: entries
    """
    return __DATA.glossary_data.items()


def set_acronym_entry(label: str, entry: AcronymEntry):
    """Sets an acronym entry for a label

    Args:
        label (str): entry label
        entry (AcronymEntry): acronym entry
    """
    __DATA.acronym_dirty = True
    __DATA.acronym_data[label] = entry


def get_acronym_entry(label: str) -> Optional[AcronymEntry]:
    """Gets an acronym entry from a label

    Args:
        label (str): entry label

    Returns:
        Optional[AcronymEntry]: acronym entry if found, `None` otherwise
    """
    return __DATA.acronym_data.get(label, None)


def get_acronym_entries() -> Iterable[Tuple[str, AcronymEntry]]:
    """Gets all the registered acronym entries

    Returns:
        Iterable[Tuple[str, AcronymEntry]]: entries
    """
    return __DATA.acronym_data.items()
