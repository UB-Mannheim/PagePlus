from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from pageplus.models.basic_elements import Region
from pageplus.models.text_elements import TextRegion


@dataclass
class TableRegion(Region):
    parent: None = field(default_factory=Any) # Page object
    tablecells: list = field(default_factory=list)
    textlines: list = field(default_factory=list)

    def __post_init__(self):
        """
        Initializes the TableRegion by extracting TableCell elements and their text lines.
        """
        self.tablecells = [TableCell(ele, self.ns, parent=self) \
                           for ele in self.xml_element.iter(f"{{{self.ns}}}TableCell")]
        [self.textlines.append(tc.textlines) for tc in self.tablecells]


@dataclass
class TableCell(TextRegion):
    parent: Optional[TableRegion] = None
