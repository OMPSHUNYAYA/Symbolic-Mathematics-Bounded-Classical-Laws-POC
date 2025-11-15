# scenario_L02_newton_fma.py  (ASCII-only, top-level prints)
# Law L02: Newton's Second Law bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical: F = m * a

import math


def clamp(a, e=1e-6):
    return max(-1 + e, min(1 - e, float(a)))


def ssm_align_weighted(pairs, gamma=1.0, eps=1e-12):
    """
    pairs: iterable of (a_raw, m)
    weight w := |m|^gamma
    """
    U = 0.0
    W = 0.0
    for a_raw, m in pairs:
        a = clamp(a_raw)
        # atanh(a) = 0.5 * ln((1+a)/(1-a))
        u = 0.5 * math.log((1.0 + a) / (1.0 - a))
        w = abs(float(m)) ** gamma
        U += w * u
        W += w
    return math.tanh(U / max(W, eps))


def ssm_align_product(a1_raw, a2_raw, eps=1e-6):
    """
    Product chaining for alignment lane:
    a_out := tanh(atanh(a1_c) + atanh(a2_c))
    """
    a1 = clamp(a1_raw, eps)
    a2 = clamp(a2_raw, eps)
    u1 = 0.5 * math.log((1.0 + a1) / (1.0 - a1))
    u2 = 0.5 * math.log((1.0 + a2) / (1.0 - a2))
    return math.tanh(u1 + u2)


# 1) law-specific inputs: Newton's second law F = m * a

# mass (m, a) of the cart
m_m, m_a = 20.0, +0.05   # kg, mostly calm

# acceleration measurements (m, a) at two instants
a1_m, a1_a = 0.90, +0.65  # m/s^2, jerkier instant
a2_m, a2_a = 1.10, +0.10  # m/s^2, calmer instant


# 2) classical magnitude: average acceleration, then F = m * a
a_avg = 0.5 * (a1_m + a2_m)
F_m   = m_m * a_avg


# 3) SSM alignments

# pooled acceleration alignment
a_accel = ssm_align_weighted(
    [(a1_a, a1_m), (a2_a, a2_m)],
    gamma=1.0,
    eps=1e-12,
)

# force alignment from mass and acceleration
a_F = ssm_align_product(m_a, a_accel, eps=1e-6)


print("Classical:", f"{F_m:.4f}")            # 20.0000
print("SSM:", f"m={F_m:.4f}, a={a_F:+.4f}")  # a_F ~ +0.48 (drift-positive)
