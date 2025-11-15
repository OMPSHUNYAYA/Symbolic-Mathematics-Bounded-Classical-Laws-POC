# scenario_L08_snells_law.py  (ASCII-only, top-level prints)

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


# 1) law-specific inputs: Snell's law
# n2 = n1 * sin(theta1) / sin(theta2)

# refractive index of medium 1 (air)
n1_m, n1_a = 1.000, +0.01

# incident angle measurements (degrees, a)
theta1_1_m, theta1_1_a = 30.0, +0.25  # deg
theta1_2_m, theta1_2_a = 30.5, +0.35  # deg

# refracted angle measurements (degrees, a)
theta2_1_m, theta2_1_a = 19.2, +0.20  # deg
theta2_2_m, theta2_2_a = 19.0, +0.12  # deg


# 2) classical magnitudes

theta1_avg_deg = 0.5 * (theta1_1_m + theta1_2_m)
theta2_avg_deg = 0.5 * (theta2_1_m + theta2_2_m)

theta1_rad = math.radians(theta1_avg_deg)
theta2_rad = math.radians(theta2_avg_deg)

n2_m = n1_m * math.sin(theta1_rad) / math.sin(theta2_rad)


# 3) SSM alignments

# pooled alignments for theta1 and theta2
a_theta1 = ssm_align_weighted(
    [(theta1_1_a, theta1_1_m), (theta1_2_a, theta1_2_m)],
    gamma=1.0,
    eps=1e-12,
)

a_theta2 = ssm_align_weighted(
    [(theta2_1_a, theta2_1_m), (theta2_2_a, theta2_2_m)],
    gamma=1.0,
    eps=1e-12,
)

# numerator alignment: n1 * sin(theta1)
a_num = ssm_align_sum([n1_a, a_theta1])

# denominator alignment: sin(theta2) inherits lane from theta2
a_den = a_theta2

# refractive index alignment from division
a_n2 = ssm_align_div(a_num, a_den, eps=1e-6)


print("Classical:")
print("  theta1_avg =", f"{theta1_avg_deg:.2f}", "deg")
print("  theta2_avg =", f"{theta2_avg_deg:.2f}", "deg")
print("  n2         =", f"{n2_m:.3f}")

print("SSM (refractive index lane):")
print("  n2 =", f"m={n2_m:.3f}, a={a_n2:+.4f}")

# Final summary line for the shared runner
print("SSM:", f"m={n2_m:.3f}, a={a_n2:+.4f}")
