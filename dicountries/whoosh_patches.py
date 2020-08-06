"""Monkey patch for the whoosh library to have two next symbol transpositions
   as one error while searching

Note:
    This file should be imported first, before any other whoosh imports
    Use isort:skip comment to prevent isort from reordering the import placement

"""

# pylint: skip-file

import whoosh.automata.lev

if not hasattr(whoosh.automata.lev, 'transposition_levenshtein_automaton'):

    def new_levenshtein_automaton(term, k, prefix=0):
        from whoosh.automata.fsa import ANY, EPSILON, NFA
        from whoosh.compat import xrange

        nfa = NFA((0, 0))
        if prefix:
            for i in xrange(prefix):
                c = term[i]
                nfa.add_transition((i, 0), c, (i + 1, 0))

        tlm1 = len(term) - 1
        for i in xrange(prefix, len(term)):
            c = term[i]
            if i < tlm1:
                nc = term[i + 1]
            else:
                nc = None
            for e in xrange(k + 1):
                # Correct character
                nfa.add_transition((i, e), c, (i + 1, e))
                if e < k:
                    # Deletion
                    nfa.add_transition((i, e), ANY, (i, e + 1))
                    # Insertion
                    nfa.add_transition((i, e), EPSILON, (i + 1, e + 1))
                    # Substitution
                    nfa.add_transition((i, e), ANY, (i + 1, e + 1))
                    # Transposition
                    if nc is not None:
                        nfa.add_transition((i, e), nc, (i + 1, e + k + 1))
                        nfa.add_transition((i + 1, e + k + 1), c, (i + 2, e + 1))

        for e in xrange(k + 1):
            if e < k:
                nfa.add_transition((len(term), e), ANY, (len(term), e + 1))
            nfa.add_final_state((len(term), e))
        return nfa


    whoosh.automata.lev.origin_levenshtein_automaton = whoosh.automata.lev.levenshtein_automaton
    whoosh.automata.lev.levenshtein_automaton = new_levenshtein_automaton
    whoosh.automata.lev.transposition_levenshtein_automaton = new_levenshtein_automaton
