# scenario_L07_bernoulli.py  (ASCII-only, top-level prints)
# Law L07: Bernoulli's Equation bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical (horizontal pipe): P2 = P1 + 0.5 * rho * (v1^2 - v2^2)

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
    where m_term is the magnitude of that contribution.
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


# 1) law-specific inputs: Bernoulli between section 1 and section 2
# P2 = P1 + 0.5 * rho * (v1^2 - v2^2)

# density (m, a)
rho_m, rho_a = 1000.0, +0.02      # kg/m^3

# upstream pressure (m, a)
P1_m, P1_a = 200000.0, +0.10      # Pa

# velocities (m, a)
v1_m, v1_a = 1.5, +0.30           # m/s (section 1)
v2_m, v2_a = 3.0, +0.20           # m/s (section 2)


# 2) classical magnitude for P2

P2_m = P1_m + 0.5 * rho_m * (v1_m**2 - v2_m**2)


# 3) SSM alignments

# dynamic pressure alignments for sections 1 and 2
a_dyn1 = ssm_align_sum([rho_a, v1_a])
a_dyn2 = ssm_align_sum([rho_a, v2_a])

# contribution magnitudes (dynamic pressure terms)
dyn1_m = 0.5 * rho_m * (v1_m**2)
dyn2_m = 0.5 * rho_m * (v2_m**2)

# We treat P2 as composed of: +P1, +dyn1, -dyn2
# For posture we use absolute magnitudes as weights
a_P2 = ssm_align_weighted(
    [
        (P1_a,   P1_m),
        (a_dyn1, dyn1_m),
        (a_dyn2, dyn2_m),
    ],
    gamma=1.0,
    eps=1e-12,
)


print("Classical:")
print("  P1 =", f"{P1_m:.0f}", "Pa")
print("  P2 =", f"{P2_m:.0f}", "Pa")

print("SSM (downstream pressure lane):")
print("  P2 =", f"m={P2_m:.0f}, a={a_P2:+.4f}")

# Standard summary line for the runner
print("SSM:", f"m={P2_m:.0f}, a={a_P2:+.4f}")
