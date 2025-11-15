# scenario_L06_conservation_of_momentum.py  (ASCII-only, top-level prints)
# Law L06: Conservation of Momentum bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical: m1*u1 + m2*u2 = m1*v1 + m2*v2  ->  Delta_p = p_before - p_after

import math


def clamp(a, e=1e-6):
    return max(-1 + e, min(1 - e, float(a)))


def ssm_align_sum(a_list, eps=1e-6):
    """
    Sum of hyperbolic rapidities:
    a_out := tanh(atanh(a1_c) + atanh(a2_c) + ...)
    """
    U = 0.0
    for a_raw in a_list:
        a = clamp(a_raw, eps)
        U += 0.5 * math.log((1.0 + a) / (1.0 - a))
    return math.tanh(U)


def ssm_align_weighted(pairs, gamma=1.0, eps=1e-12):
    """
    pairs: iterable of (a_raw, m_term)
    where m_term is the magnitude associated with that lane (e.g., cart momentum).
    """
    U = 0.0
    W = 0.0
    for a_raw, m_term in pairs:
        a = clamp(a_raw)
        # atanh(a) = 0.5 * ln((1+a)/(1-a))
        u = 0.5 * math.log((1.0 + a) / (1.0 - a))
        w = abs(float(m_term)) ** gamma
        U += w * u
        W += w
    return math.tanh(U / max(W, eps))


# 1) law-specific inputs: Conservation of Momentum in 1D

# masses (m, a)
m1_m, m1_a = 1.50, +0.05   # kg
m2_m, m2_a = 1.00, +0.05   # kg

# initial velocities (u, a)
u1_m, u1_a = 1.20, +0.40   # m/s, cart 1 before
u2_m, u2_a = 0.00, +0.05   # m/s, cart 2 before

# final velocities (v, a)
v1_m, v1_a = 0.70, +0.35   # m/s, cart 1 after
v2_m, v2_a = 0.80, +0.20   # m/s, cart 2 after


# 2) classical momenta

p_before_m = m1_m * u1_m + m2_m * u2_m
p_after_m  = m1_m * v1_m + m2_m * v2_m
delta_p_m  = p_before_m - p_after_m


# 3) SSM alignments

# per-cart momentum alignments (before)
a_p1_before = ssm_align_sum([m1_a, u1_a])
a_p2_before = ssm_align_sum([m2_a, u2_a])

# per-cart momentum alignments (after)
a_p1_after  = ssm_align_sum([m1_a, v1_a])
a_p2_after  = ssm_align_sum([m2_a, v2_a])

# overall momentum alignment before and after (weighted by |p_cart|)
a_before = ssm_align_weighted(
    [(a_p1_before, m1_m * u1_m),
     (a_p2_before, m2_m * u2_m)],
    gamma=1.0,
    eps=1e-12,
)

a_after = ssm_align_weighted(
    [(a_p1_after, m1_m * v1_m),
     (a_p2_after, m2_m * v2_m)],
    gamma=1.0,
    eps=1e-12,
)

# imbalance alignment as combined posture of both sides
a_delta_p = ssm_align_sum([a_before, a_after])


print("Classical:")
print("  p_before =", f"{p_before_m:.3f}", "kg m/s")
print("  p_after  =", f"{p_after_m:.3f}", "kg m/s")
print("  Delta_p  =", f"{delta_p_m:.3f}", "kg m/s")

print("SSM (imbalance lane):")
print("  Delta_p  =", f"m={delta_p_m:.3f}, a={a_delta_p:+.4f}")

# Standard summary line for the runner
print("SSM:", f"m={delta_p_m:.3f}, a={a_delta_p:+.4f}")
