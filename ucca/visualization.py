import re
import warnings
from collections import defaultdict
from operator import attrgetter

from ucca import layer0, layer1


def node_label(node):
    return re.sub("[^(]*\((.*)\)", "\\1", node.attrib.get("label", ""))


def draw(passage, node_ids=False):
    import matplotlib.cbook
    import networkx as nx
    warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
    warnings.filterwarnings("ignore", category=UserWarning)
    g = nx.DiGraph()
    g.add_nodes_from([(n.ID, {"label": n.text, "color": "white"}) for n in passage.layer(layer0.LAYER_ID).all])
    g.add_nodes_from([(n.ID, {"label": "IMPLICIT", "color": "white"}) for n in passage.layer(layer1.LAYER_ID).all
                      if n.attrib.get("implicit")])
    g.add_nodes_from([(n.ID, {"label": node_label(n) or (n.ID if node_ids else ""),
                              "color": "gray" if n.tag == layer1.NodeTags.Linkage else
                              ("white" if node_label(n) or (n.ID and node_ids) else "black")})
                      for n in passage.layer(layer1.LAYER_ID).all if not n.attrib.get("implicit")])
    g.add_edges_from([(n.ID, e.child.ID, {"label": "|".join(e.tags),
                                          "style": "dashed" if e.attrib.get("remote") else "solid"})
                      for layer in passage.layers for n in layer.all for e in n])
    pos = topological_layout(passage)
    nx.draw(g, pos, arrows=False, font_size=10,
            node_color=[d["color"] for _, d in g.nodes(data=True)],
            labels={n: d["label"] for n, d in g.nodes(data=True) if d["label"]},
            style=[d["style"] for _, _, d in g.edges(data=True)])
    nx.draw_networkx_edge_labels(g, pos, font_size=8,
                                 edge_labels={(u, v): d["label"] for u, v, d in g.edges(data=True)})


def topological_layout(passage):
    visited = defaultdict(set)
    pos = {}
    terminals = passage.layer(layer0.LAYER_ID).all
    if terminals:
        implicit_offset = list(range(0, 1 + max(n.position for n in terminals)))
        leaves = sorted([n for layer in passage.layers for n in layer.all if not n.children],
                        key=lambda n: getattr(n, "position", None) or (n.fparent.end_position if n.fparent else -1))
        for node in leaves:  # draw leaves first to establish ordering
            if node.layer.ID == layer0.LAYER_ID:  # terminal
                x = node.position
                pos[node.ID] = (x + sum(implicit_offset[:x + 1]), 0)
            elif node.fparent:  # implicit
                implicit_offset[node.fparent.end_position] += 1
    else:
        implicit_offset = [0]
    remaining = [n for n in passage.layer(layer1.LAYER_ID).all if not n.parents]
    implicits = []
    while remaining:  # draw non-terminals
        node = remaining.pop()
        if node.ID in pos:  # done already
            continue
        children = [c for c in node.children if c.ID not in pos and c not in visited[node.ID]]
        if children:
            visited[node.ID].update(children)  # to avoid cycles
            remaining += [node] + children
            continue
        if node.children:
            xs, ys = zip(*(pos[c.ID] for c in node.children if not c.attrib.get("implicit")))
            pos[node.ID] = sum(xs) / len(xs), 1 + max(ys)  # done with children
        else:
            implicits.append(node)
    for node in implicits:
        fparent = node.fparent or passage.layer(layer1.LAYER_ID).heads[0]
        x = fparent.end_position
        x += sum(implicit_offset[:x + 1])
        _, y = pos.get(fparent.ID, (0, 0))
        pos[node.ID] = (x, y - 1)
    pos = {i: (x, y ** 1.01)for i, (x, y) in pos.items()}  # stretch up to avoid over cluttering
    return pos


TEX_ESCAPE_TABLE = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\^{}",
    "\\": r"\textbackslash{}",
    "<": r"\textless ",
    ">": r"\textgreater ",
}
TEX_ESCAPE_PATTERN = re.compile("|".join(map(re.escape, sorted(TEX_ESCAPE_TABLE, key=len, reverse=True))))


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    return TEX_ESCAPE_PATTERN.sub(lambda match: TEX_ESCAPE_TABLE[match.group()], text)


def tikz(p, indent=None, node_ids=False):
    """
    Visualize to TikZ format
    :param p: Passage
    :param indent: indentation size or None for no indentation
    :param node_ids: whether to include node IDs
    :return: string in TikZ format
    """
    if indent is None:
        l1 = p.layer(layer1.LAYER_ID)
        return r"""
\begin{tikzpicture}[->,level distance=1cm,
  level 1/.style={sibling distance=4cm},
  level 2/.style={sibling distance=15mm},
  level 3/.style={sibling distance=15mm},
  every circle node/.append style={%s=black},
  every node/.append style={text height=.6ex,text depth=0}]
  \tikzstyle{word} = [font=\rmfamily,color=black]
  """ % ("draw" if node_ids else "fill") + "\\" + tikz(l1.heads[0], indent=1, node_ids=node_ids) + \
            "\n".join([";"] + [r"  \draw[dashed,->] (%s) to node [auto] {%s} (%s);" %
                               (e.parent.ID.replace(".", "_"), "|".join(e.tags), e.child.ID.replace(".", "_"))
                               for n in l1.all for e in n if e.attrib.get("remote")] + [r"\end{tikzpicture}"])
    return "node (" + p.ID.replace(".", "_") + ") " + (
        ("[word] {" +
         (" ".join(tex_escape(t.text)
                   for t in sorted(p.terminals, key=attrgetter("position"))) or r"\textbf{IMPLICIT}")
         + "} ") if p.terminals or p.attrib.get("implicit") else ("\n" + indent * "  ").join(
            ["[circle] {%s}" % (node_label(p) or (p.ID if node_ids else "")), "{"] +
            ["child {" + tikz(e.child, indent + 1) +
             " edge from parent node[auto]  {" + "|".join(e.tags) + "}}"
             for e in sorted(p, key=lambda f: f.child.start_position)
             if not e.attrib.get("remote")] +
            ["}"]))


def standoff(p):
    """
    Visualize to Standoff .ann format, which can be presented with brat
    :param p: Passage
    :return: string in Standoff format
    """
    l0 = p.layer(layer0.LAYER_ID)
    terminal_start = {}
    terminal_end = {}
    start = end = 0
    for terminal in sorted(l0.all, key=attrgetter("position")):
        terminal_start[terminal.ID] = start
        end += len(terminal.text)
        terminal_end[terminal.ID] = end
        end += 1
        start = end
    tag_to_category = {v: k for k, v in layer1.EdgeTags.__dict__.items() if not k.startswith("__")}
    l1 = p.layer(layer1.LAYER_ID)
    remote_counter = 1
    lines = [l1.heads[0].to_text()]
    units = [unit for unit in l1.all if unit.tag == layer1.NodeTags.Foundational and unit.ftags]
    units = sorted(units, key=attrgetter("start_position", "end_position"))
    unit_to_id = {unit.ID: str(i) for i, unit in enumerate(units, start=1)}
    for unit in units:
        terminals = unit.get_terminals()
        if terminals:
            spans = []
            for terminal in terminals:
                start = terminal_start[terminal.ID]
                end = terminal_end[terminal.ID]
                if not spans or spans[-1][1] < start - 1:
                    spans.append((start, end))
                else:
                    spans[-1] = (spans[-1][0], end)
            lines.append("\t".join(("T" + unit_to_id[unit.ID],
                                    "|".join(tag_to_category.get(tag, tag) for tag in unit.ftags) + " " +
                                    ";".join("%d %d" % (s, e) for s, e in spans),
                                    unit.to_text())))
        for edge in unit.incoming:
            if edge.attrib.get("remote"):
                lines.append("\t".join(("R%d" % remote_counter,
                                        " ".join(("|".join(tag_to_category.get(tag, tag) for tag in edge.tags),
                                                  "parent:T" + unit_to_id[edge.parent.ID],
                                                  "child:T" + unit_to_id[edge.child.ID])))))
                remote_counter += 1
    return "\n".join(lines)
