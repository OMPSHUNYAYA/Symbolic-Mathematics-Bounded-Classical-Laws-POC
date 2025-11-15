# scenario_L10_faraday_induction.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Faraday's law |eps| = N * |dPhi/dt|
# with dPhi/dt ≈ (Phi2 - Phi1) / dt

# number of turns (m, a)
N_m, N_a = 200, +0.02    # turns

# flux samples (m, a)
Phi1_m, Phi1_a = 0.012, +0.60   # Wb, noisy first sample
Phi2_m, Phi2_a = 0.004, +0.25   # Wb, calmer second sample

# time interval (m, a)
dt_m, dt_a = 0.040, +0.10       # s

# 2) classical magnitudes

dPhi_dt_m = (Phi2_m - Phi1_m) / dt_m
eps_mag_m = N_m * abs(dPhi_dt_m)

# 3) SSM alignments

# lane for DeltaPhi from two flux samples
a_dPhi = ssm_align_sum([Phi1_a, Phi2_a])

# lane for dPhi/dt = DeltaPhi / dt
a_dPhi_dt = ssm_align_div(a_dPhi, dt_a, eps=1e-6)

# EMF alignment from N * dPhi/dt
a_eps = ssm_align_sum([N_a, a_dPhi_dt])

print("Classical:")
print("  dPhi/dt ~", f"{dPhi_dt_m:.3f}", "Wb/s")
print("  |eps|   =", f"{eps_mag_m:.2f}", "V")

print("SSM (induced EMF lane):")
print("  |eps| =", f"m={eps_mag_m:.2f}, a={a_eps:+.4f}")

print("SSM:", f"m={eps_mag_m:.2f}, a={a_eps:+.4f}")
