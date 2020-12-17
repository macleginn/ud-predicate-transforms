import pytest

from ucca import layer1
from ucca.validation import validate
from .conftest import loaded, loaded_valid, multi_sent, crossing, discontiguous, l1_passage, empty, \
    create_passage, attach_terminals

"""Tests the validation module functions and classes."""


def unary_punct():
    p, l1, terms = create_passage(3, 3)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    l1.add_punct(h1, terms[2])
    attach_terminals(terms, p1, a1)
    return p


def binary_punct():
    p, l1, terms = create_passage(4, 3)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    l1.add_punct(h1, terms[2]).add(layer1.EdgeTags.Terminal, terms[3])
    attach_terminals(terms, p1, a1)
    return p


def unary_punct_under_fn():
    p, l1, terms = create_passage(3, 3)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    attach_terminals(terms, p1, a1, h1)
    return p


def punct_under_unanalyzable_fn():
    p, l1, terms = create_passage(3, 2)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    attach_terminals(terms, p1, p1, p1)
    return p

def forbid_child_of_P_fn(): # same for adverbial, linker, time, quantifier and connector
    p, l1, terms = create_passage(5, 5)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    g1 = l1.add_fnode(p1, layer1.EdgeTags.Ground)
    d1 = l1.add_fnode(p1, layer1.EdgeTags.Adverbial)
    attach_terminals(terms, p1, a1, g1, d1)
    return p

def forbid_child_of_S_fn():
    p, l1, terms = create_passage(4, 4)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    s1 = l1.add_fnode(h1, layer1.EdgeTags.State)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    h2 = l1.add_fnode(s1, layer1.EdgeTags.ParallelScene)
    attach_terminals(terms, s1, a1, h2)
    return p

def forbid_child_of_F_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    f1 = l1.add_fnode(h1, layer1.EdgeTags.Function)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    t1 = l1.add_fnode(f1, layer1.EdgeTags.Time)
    s1 = l1.add_fnode(f1, layer1.EdgeTags.State)
    attach_terminals(terms, f1, a1, p1, t1, s1)
    return p

def forbid_child_of_G_fn():
    p, l1, terms = create_passage(3, 3)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    g1 = l1.add_fnode(h1, layer1.EdgeTags.Ground)
    h2 = l1.add_fnode(g1, layer1.EdgeTags.ParallelScene)
    attach_terminals(terms, g1, h2)
    return p

def forbid_child_of_H_fn():
    p, l1, terms = create_passage(3, 3)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    link1 = l1.add_fnode(h1, layer1.EdgeTags.Linker)
    h2 = l1.add_fnode(h1, layer1.EdgeTags.ParallelScene)
    s1 = l1.add_fnode(h2, layer1.EdgeTags.State)
    a1 = l1.add_fnode(h2, layer1.EdgeTags.Participant)
    attach_terminals(terms, link1, s1, a1)
    return p

def forbid_descendant_of_P_fn(): # same for state
    p, l1, terms = create_passage(5, 5)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    c1 = l1.add_fnode(p1, layer1.EdgeTags.Center)
    e1 = l1.add_fnode(p1, layer1.EdgeTags.Elaborator)
    h2 = l1.add_fnode(c1, layer1.EdgeTags.ParallelScene)
    c2 = l1.add_fnode(e1, layer1.EdgeTags.Center)
    s2 = l1.add_fnode(c2, layer1.EdgeTags.State)
    a2 = l1.add_fnode(c2, layer1.EdgeTags.Participant)
    attach_terminals(terms, a1, e1, a2,s2,h2, e1)
    return p

def forbid_sibling_of_L_H_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    h2 = l1.add_fnode(h1, layer1.EdgeTags.ParallelScene)
    link1 = l1.add_fnode(h1, layer1.EdgeTags.Linker)
    attach_terminals(terms, p1, h2, link1)
    return p

def forbid_sibling_of_S_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    s1 = l1.add_fnode(h1, layer1.EdgeTags.State)
    h2 = l1.add_fnode(h1, layer1.EdgeTags.ParallelScene)
    link1 = l1.add_fnode(h1, layer1.EdgeTags.Linker)
    attach_terminals(terms, s1, h2, link1)
    return p

def forbid_sibling_of_D_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    d1 = l1.add_fnode(h1, layer1.EdgeTags.Adverbial)
    s1 = l1.add_fnode(h1, layer1.EdgeTags.State)
    h2 = l1.add_fnode(h1, layer1.EdgeTags.ParallelScene)
    link1 = l1.add_fnode(h1, layer1.EdgeTags.Linker)
    attach_terminals(terms, d1, s1, h2, link1)
    return p

def forbid_sibling_of_P_N_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    n1 = l1.add_fnode(h1, layer1.EdgeTags.Connector)
    attach_terminals(terms, n1, p1)
    return p

def forbid_sibling_of_Q_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    q1 = l1.add_fnode(h1, layer1.EdgeTags.Quantifier)
    attach_terminals(terms, p1, q1)
    return p

def forbid_sibling_of_E_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    e1 = l1.add_fnode(h1, layer1.EdgeTags.Elaborator)
    attach_terminals(terms, p1, e1)
    return p

def forbid_sibling_of_C_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    c1 = l1.add_fnode(h1, layer1.EdgeTags.Center)
    attach_terminals(terms, p1, c1)
    return p

def forbid_sibling_of_A_T_fn():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    t1 = l1.add_fnode(h1, layer1.EdgeTags.Time)
    n1 = l1.add_fnode(h1, layer1.EdgeTags.Connector)
    e1 = l1.add_fnode(h1, layer1.EdgeTags.Elaborator)
    c1 = l1.add_fnode(h1, layer1.EdgeTags.Center)
    attach_terminals(terms, p1, a1, t1, n1, e1, c1)
    return p

def require_sibling_of_E_Q_N():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    e1 = l1.add_fnode(h1, layer1.EdgeTags.Elaborator)
    q1 = l1.add_fnode(h1, layer1.EdgeTags.Quantifier)
    n1 = l1.add_fnode(h1, layer1.EdgeTags.Connector)
    attach_terminals(terms, e1, q1, n1)
    return p

def require_sibling_of_L():
    p, l1, terms = create_passage(6, 6)
    link1 = l1.add_fnode(None, layer1.EdgeTags.Linker)
    attach_terminals(terms, link1)
    return p

def require_sibling_of_A_T():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    t1 = l1.add_fnode(h1, layer1.EdgeTags.Time)
    attach_terminals(terms, a1, t1)
    return p

def unique_under_parent():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    p2 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    attach_terminals(terms, a1, p1, p2)
    return p

def forbid_remote():
    p, l1, terms = create_passage(6, 6)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    h2 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    link1 = l1.add_fnode(None, layer1.EdgeTags.Linker)
    p1 = l1.add_fnode(h1, layer1.EdgeTags.Process)
    p2 = l1.add_fnode(h2, layer1.EdgeTags.Process)
    a1 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    a2 = l1.add_fnode(h1, layer1.EdgeTags.Participant)
    r1 = l1.add_fnode(h1, layer1.EdgeTags.Relator)
    r2 = l1.add_remote_multiple(h2, layer1.EdgeTags.Relator, r1)
    attach_terminals(terms, link1, a2, a1, p1, p2, r2, r1)
    return p

def forbid_at_top_level():
    p, l1, terms = create_passage(1, 1)
    g1 = l1.add_fnode(None, layer1.EdgeTags.Ground)
    attach_terminals(terms, g1)
    return p

def forbid_children_of_UNA_and_alone():
    p, l1, terms = create_passage(1, 1)
    h1 = l1.add_fnode(None, layer1.EdgeTags.ParallelScene)
    u1 = l1.add_fnode(h1, layer1.EdgeTags.Unanalyzable)
    s1 = l1.add_fnode(u1, layer1.EdgeTags.State)
    a1 = l1.add_fnode(u1, layer1.EdgeTags.Participant)
    attach_terminals(terms)
    return p


@pytest.mark.parametrize("create, valid", (
        (loaded, False),
        (loaded_valid, True),
        (multi_sent, True),
        (crossing, True),
        (discontiguous, True),
        (l1_passage, True),
        (empty, False),
        (unary_punct, True),
        (binary_punct, True),
        (unary_punct_under_fn, False),
        (punct_under_unanalyzable_fn, True),
        (forbid_child_of_P_fn, False),
        (forbid_child_of_F_fn, False),
        (forbid_child_of_S_fn, False),
        (forbid_child_of_G_fn, False),
        (forbid_child_of_H_fn, False),
        (forbid_descendant_of_P_fn, False),
        (forbid_sibling_of_L_H_fn, False),
        (forbid_sibling_of_S_fn, False),
        (forbid_sibling_of_D_fn, False),
        (forbid_sibling_of_P_N_fn, False),
        (forbid_sibling_of_Q_fn, False),
        (forbid_sibling_of_E_fn, False),
        (forbid_sibling_of_C_fn, False),
        (forbid_sibling_of_A_T_fn, False),
        (require_sibling_of_E_Q_N, False),
        (require_sibling_of_L, False),
        (require_sibling_of_A_T, False),
        (unique_under_parent, False),
        (forbid_remote, False),
        (forbid_at_top_level, False),
        (forbid_children_of_UNA_and_alone, False),
))
def test_evaluate_self(create, valid):
    p = create()
    errors = list(validate(p))
    if valid:
        assert not errors, p
    else:
        assert errors, p
