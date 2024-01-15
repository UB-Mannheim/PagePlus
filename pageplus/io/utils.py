from __future__ import annotations

from pathlib import Path
from typing import Tuple, Iterator, List

import lxml.etree as ET


def collect_xml_files(inputpaths: Iterator[Path], exclude: Tuple[str, ...] = ('metadata.xml', 'mets.xml', 'METS.xml')) -> List[Path]:
    """
    Collects XML files from given input paths, excluding specified filenames.

    Args:
    - inputpaths: An iterator of Path objects representing files or directories to search.
    - exclude: A tuple of filenames to exclude from the search.

    Returns:
    - A sorted list of Path objects for the XML files found.
    """
    xml_files = []
    for inputpath in inputpaths:
        if inputpath.is_file() and inputpath.suffix == '.xml' and inputpath.name not in exclude and is_page_xml(inputpath):
            xml_files.append(inputpath)
        elif inputpath.is_dir():
            xml_files.extend([xml_file for xml_file in inputpath.rglob('*.xml') if xml_file.name not in exclude and is_page_xml(xml_file)])
    return sorted(xml_files)

def is_page_xml(file_path: Path) -> bool:
    """
    Check if file is a page xml file
    """
    if not file_path.suffix.lower() == '.xml':
        return False

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check for PAGE XML namespace or specific elements
        # Typical namespace URI for PAGE is something like: "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
        # Adjust the namespace URI according to the version of PAGE XML you're expecting
        page_namespace = "http://schema.primaresearch.org/PAGE/gts/pagecontent/"
        return root.tag.startswith(f"{{{page_namespace}")

    except ET.ParseError:
        # Not an XML file, or XML is malformed
        return False

def determine_output_path(xml_file, outputdir, filename):
    """
    Determines the output path for the repaired XML file.

    Args:
        xml_file: The original XML file.
        outputdir: The specified output directory.
        filename: The name of the XML file.

    Returns:
        The Path object for the output file.
    """
    if outputdir is None:
        return xml_file.parent / 'PagePlusOutput' / filename
    else:
        return Path(outputdir) / filename


