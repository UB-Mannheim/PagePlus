from __future__ import annotations

import difflib
import logging
import re
from collections import defaultdict, Counter
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Tuple, Optional, Iterator, Any, List

from pageplus.models.basic_elements import Region
from pageplus.models.text_elements import TextRegion

from pageplus.io.logger import logging

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
