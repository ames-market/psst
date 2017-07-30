import os
import logging

import traitlets as t
import traittypes as tt
import ipywidgets as ipyw
from collections import OrderedDict
import networkx as nx

from ..case.case import Case

logger = logging.getLogger(__name__)


class Network(t.HasTraits):

    case = t.Instance(Case)
    positions = t.Dict()
    graph = t.Instance(nx.Graph)

