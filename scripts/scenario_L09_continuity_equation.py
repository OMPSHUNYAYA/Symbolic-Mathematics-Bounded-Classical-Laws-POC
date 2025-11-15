# scenario_L09_continuity_equation.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Continuity equation A1 v1 = A2 v2
# We solve for v2 = (A1 / A2) * v1

# areas (m, a)
A1_m, A1_a = 0.0100, +0.10   # m^2, inlet
A2_m, A2_a = 0.0060, +0.15   # m^2, throat

# upstream velocity measurements (m, a)
v1_1_m, v1_1_a = 1.80, +0.45  # m/s, early, more jitter
v1_2_m, v1_2_a = 2.00, +0.20  # m/s, later, calmer

# 2) classical magnitude

v1_avg_m = 0.5 * (v1_1_m + v1_2_m)
v2_m     = (A1_m / A2_m) * v1_avg_m

# 3) SSM alignments

# pooled upstream velocity alignment
a_v1 = ssm_align_weighted(
    [(v1_1_a, v1_1_m), (v1_2_a, v1_2_m)],
    gamma=1.0,
    eps=1e-12,
)

# area ratio alignment: A1 / A2
a_ratio = ssm_align_div(A1_a, A2_a, eps=1e-6)

# downstream velocity alignment from ratio and v1
a_v2 = ssm_align_sum([a_ratio, a_v1])

print("Classical:")
print("  v1_avg =", f"{v1_avg_m:.3f}", "m/s")
print("  v2     =", f"{v2_m:.3f}", "m/s")

print("SSM (downstream velocity lane):")
print("  v2 =", f"m={v2_m:.3f}, a={a_v2:+.4f}")

# final one-line summary for the shared runner
print(f"SSM: m={v2_m:.3f}, a={a_v2:+.4f}")
