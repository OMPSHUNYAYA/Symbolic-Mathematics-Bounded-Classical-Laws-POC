# scenario_L01_ohms_law.py  (ASCII-only, top-level prints)
# Law L01: Ohm's Law bounded with Shunyaya Symbolic Mathematics (SSM)

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


# 1) law-specific inputs: Ohm's law V = I * R
# current measurements (m, a) at two instants
I1_m, I1_a = 1.92, +0.72   # amps, noisy instant
I2_m, I2_a = 1.98, +0.05   # amps, calmer instant

# load resistance (m, a)
R_m,  R_a  = 6.10, +0.10   # ohms, mild drift

# 2) classical magnitude: average current, then V = I * R
I_avg = 0.5 * (I1_m + I2_m)
V_m   = I_avg * R_m

# 3) SSM alignments
a_I = ssm_align_weighted(
    [(I1_a, I1_m), (I2_a, I2_m)],
    gamma=1.0,
    eps=1e-12,
)

a_V = ssm_align_product(a_I, R_a, eps=1e-6)

print("Classical:", f"{V_m:.4f}")           # 11.8950
print("SSM:", f"m={V_m:.4f}, a={a_V:+.4f}")  # a_V ~ +0.51.. (drift-positive)
