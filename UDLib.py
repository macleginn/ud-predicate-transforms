from dataclasses import dataclass
from collections import defaultdict
from typing import List, Dict


@dataclass
class UDNode:
    """
    Stores all UD fields under their canonical names according
    to the CoNLL-U format.
    """
    # Word index, integer starting at 1 for each new sentence; may be
    # a range for multiword tokens; may be a decimal number for empty
    # nodes (decimal numbers can be lower than 1 but must be greater
    # than 0).
    ID: str
    FORM: str   # Word form or punctuation symbol.
    LEMMA: str  # Lemma or stem of word form.
    UPOS: str   # Universal part-of-speech tag.
    # Language-specific part-of-speech tag; underscore if not available.
    XPOS: str
    # List of morphological features from the universal feature
    # inventory or from a defined language-specific extension;
    # underscore if not available.
    FEATS: str
    # Head of the current word, which is either a value of ID or zero (0).
    HEAD: str
    # Universal dependency relation to the HEAD (root iff HEAD = 0)
    # or a defined language-specific subtype of one.
    DEPREL: str
    # Enhanced dependency graph in the form of a list of head-deprel pairs.
    DEPS: str
    MISC: str  # Any other annotation.

    def __str__(self):
        fields = list(self.__dataclass_fields__)
        return '\t'.join(self.__dict__[f] for f in fields)


@dataclass
class UDEdge:
    head: str
    relation: str
    directionality: str


@dataclass
class UDTree:
    # The list of commented out lines at the beginning of a record.
    id_lines: List[str]
    keys: List[str]           # The canonical order of keys.
    nodes: Dict[str, UDNode]  # Nodes with UD attributes indexed by keys.
    # Lists of edges indexed by keys.
    graph: Dict[str, List[UDEdge]]

    def __str__(self):
        lines = self.id_lines + [str(self.nodes[key]) for key in self.keys]
        return '\n'.join(lines)

    def get_sentence(self) -> str:
        return ' '.join(self.nodes[key].FORM.lower() for key in self.keys)

    def get_node_children(self, node_idx) -> List[str]:
        return [el.head for el in self.graph[node_idx]
                if el.directionality == "down"]

    def get_real_root(self) -> str:
        # A well-formed UD tree has a virtual root with a single child.
        return self.get_node_children('0')[0]


def conllu2graph(record):
    """
    Converts sentences described using CoNLL-U format
    (http://universaldependencies.org/format.html) to a graph.
    Returns a tuple of (id_lines, keys, nodes, graph), which
    may be used by a UDTree constructor.
    """
    id_lines = []
    keys = []                  # To preserve the key ordering
    nodes = {}                 # Nodes with UD fields
    # The graph of dependency relations. The root is indexed with '0'.
    graph = defaultdict(list)

    for line in record.splitlines():
        if line.startswith("#"):
            id_lines.append(line)
            continue
        fields = line.strip("\n").split("\t")
        assert len(fields) == 10
        key = fields[0]
        keys.append(key)
        ud_node = UDNode(*fields)
        nodes[key] = ud_node
        parent = ud_node.HEAD
        if parent == '_':
            continue
        relation = ud_node.DEPREL
        graph[key].append(UDEdge(
            head=parent,
            relation=relation,
            directionality="up"))
        graph[parent].append(UDEdge(
            head=key,
            relation=relation,
            directionality="down"))
    return id_lines, keys, nodes, graph


def conllu2trees(path):
    with open(path, 'r', encoding='utf-8') as inp:
        txt = inp.read().strip()
        blocks = txt.split('\n\n')
    return [UDTree(*conllu2graph(block)) for block in blocks]


if __name__ == '__main__':
    test_record = """# sent_id = panc0.s4
# text = तत् यथानुश्रूयते।
# translit = tat yathānuśrūyate.
# text_fr = Voilà ce qui nous est parvenu par la tradition orale.
# text_en = This is what is heard.
1	तत्	तद्	DET	_	Case=Nom|…|PronType=Dem	3	nsubj	_	Translit=tat|LTranslit=tad|Gloss=it
2-3	यथानुश्रूयते	_	_	_	_	_	_	_	SpaceAfter=No
2	यथा	यथा	ADV	_	PronType=Rel	3	advmod	_	Translit=yathā|LTranslit=yathā|Gloss=how
3	अनुश्रूयते	अनु-श्रु	VERB	_	Mood=Ind|…|Voice=Pass	0	root	_	Translit=anuśrūyate|LTranslit=anu-śru|Gloss=it-is-heard
4	।	।	PUNCT	_	_	3	punct	_	Translit=.|LTranslit=.|Gloss=."""
    ud_tree = UDTree(*conllu2graph(test_record))
    print(ud_tree)
