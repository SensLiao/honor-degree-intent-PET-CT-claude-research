"""Enumerate all small cases and check the O-neutralised Dice-gain label g_T.

g_T(A) = Dice(M~_A, G) - Dice(M, G), where M~_A keeps M on O and takes the
executed candidate everywhere else. Checks the closed form for ADD/REMOVE and
shows that neutralising O only in the numerator gives a different number.
"""
from fractions import Fraction
from itertools import product

N = 5


def dice(m, g):
    den = len(m) + len(g)
    return None if den == 0 else Fraction(2 * len(m & g), den)


checked = mismatch = numerator_only_differs = 0
for g_bits, m_bits in product(range(1 << N), repeat=2):
    G = {i for i in range(N) if g_bits >> i & 1}
    M = {i for i in range(N) if m_bits >> i & 1}
    base = dice(M, G)
    if base is None:
        continue
    I = len(M & G)
    for sign in ("ADD", "REMOVE"):
        errors = sorted(G - M) if sign == "ADD" else sorted(M - G)
        editable = (set(range(N)) - M) if sign == "ADD" else set(M)
        P = editable - set(errors)
        for t_bits in range(1 << len(errors)):
            T = {e for k, e in enumerate(errors) if t_bits >> k & 1}
            O = set(errors) - T
            ed = sorted(editable)
            for a_bits in range(1 << len(ed)):
                A = {v for k, v in enumerate(ed) if a_bits >> k & 1}
                kept = A - O
                m_tilde = (M | kept) if sign == "ADD" else (M - kept)
                d = dice(m_tilde, G)
                if d is None:
                    continue
                direct = d - base
                a_t, a_p = len(A & T), len(A & P)
                if sign == "ADD":
                    closed = Fraction(2 * (I + a_t), len(M) + a_t + a_p + len(G)) - base
                    num_only = Fraction(2 * (I + a_t), len(M) + len(A) + len(G)) - base
                else:
                    den = len(M) - a_t - a_p + len(G)
                    closed = Fraction(2 * (I - a_p), den) - base
                    den_full = len(M) - len(A) + len(G)
                    num_only = (Fraction(2 * (I - a_p), den_full) - base) if den_full else None
                checked += 1
                mismatch += direct != closed
                numerator_only_differs += num_only is not None and num_only != direct

print(f"cases checked: {checked}")
print(f"closed form mismatches: {mismatch}")
print(f"cases where numerator-only neutralisation differs: {numerator_only_differs}")
