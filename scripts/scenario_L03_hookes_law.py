# scenario_L03_hookes_law.py  (ASCII-only, top-level prints)
# Law L03: Hooke's Law bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical: F = k * x

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


# 1) law-specific inputs: Hooke's law F = k * x

# spring constant (m, a)
k_m, k_a = 200.0, +0.08   # N/m, mildly uncertain

# displacement measurements (m, a) at two instants
x1_m, x1_a = 0.045, +0.60  # m, jerkier reading
x2_m, x2_a = 0.055, +0.10  # m, calmer reading


# 2) classical magnitude: average displacement, then F = k * x
x_avg = 0.5 * (x1_m + x2_m)
F_m   = k_m * x_avg


# 3) SSM alignments

# pooled displacement alignment
a_x = ssm_align_weighted(
    [(x1_a, x1_m), (x2_a, x2_m)],
    gamma=1.0,
    eps=1e-12,
)

# force alignment from spring constant and displacement
a_F = ssm_align_product(k_a, a_x, eps=1e-6)


print("Classical:", f"{F_m:.4f}")            # 10.0000
print("SSM:", f"m={F_m:.4f}, a={a_F:+.4f}")  # a_F ~ +0.45 (drift-positive)
