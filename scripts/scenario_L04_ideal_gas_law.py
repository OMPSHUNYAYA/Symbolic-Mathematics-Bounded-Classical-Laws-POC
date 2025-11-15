# scenario_L04_ideal_gas_law.py  (ASCII-only, top-level prints)
# Law L04: Ideal Gas Law bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical: P * V = n * R * T  →  P = (n * R * T) / V

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


def ssm_align_div(a_num_raw, a_den_raw, eps=1e-6):
    """
    Division for alignment lane:
    a_out := tanh(atanh(a_num_c) - atanh(a_den_c))
    """
    a_num = clamp(a_num_raw, eps)
    a_den = clamp(a_den_raw, eps)
    u_num = 0.5 * math.log((1.0 + a_num) / (1.0 - a_num))
    u_den = 0.5 * math.log((1.0 + a_den) / (1.0 - a_den))
    return math.tanh(u_num - u_den)


# 1) law-specific inputs: Ideal Gas Law P = (n * R * T) / V

# amount of gas (m, a)
n_m, n_a = 1.00, +0.02     # mol, almost exactly one mole

# gas constant (m, a)
R_m, R_a = 8.314, +0.00    # J/(mol*K), treated as exact

# volume (m, a)
V_m, V_a = 0.0100, +0.10   # m^3 (10 L), piston not perfectly fixed

# temperature measurements (m, a) at two instants
T1_m, T1_a = 295.0, +0.55  # K, early, more drift
T2_m, T2_a = 305.0, +0.12  # K, later, calmer


# 2) classical magnitude: average temperature, then ideal gas law
T_avg = 0.5 * (T1_m + T2_m)
P_m   = (n_m * R_m * T_avg) / V_m


# 3) SSM alignments

# pooled temperature alignment
a_T = ssm_align_weighted(
    [(T1_a, T1_m), (T2_a, T2_m)],
    gamma=1.0,
    eps=1e-12,
)

# combined alignment for n*R*T
a_nRT = ssm_align_sum([n_a, R_a, a_T])

# pressure alignment from (n*R*T) / V
a_P = ssm_align_div(a_nRT, V_a, eps=1e-6)


print("Classical:", f"{P_m:.2f}")             # ~249420.00
print("SSM:", f"m={P_m:.2f}, a={a_P:+.4f}")   # a_P ~ +0.50 (drift-positive)
