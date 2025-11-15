# scenario_L05_conservation_of_energy.py  (ASCII-only, top-level prints)
# Law L05: Conservation of Energy bounded with Shunyaya Symbolic Mathematics (SSM)
# Classical: E_in = E_out + E_loss  →  E_loss = E_in - E_out

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
    Sum of hyperbolic rapidities for multiple lanes:
    a_out := tanh(atanh(a1_c) + atanh(a2_c) + ...)
    """
    U = 0.0
    for a_raw in a_list:
        a = clamp(a_raw, eps)
        U += 0.5 * math.log((1.0 + a) / (1.0 - a))
    return math.tanh(U)


# 1) law-specific inputs: E_in = E_out + E_loss, solve for E_loss

# supply voltage (m, a)
V_m, V_a = 12.0, +0.10     # volts

# current measurements (m, a)
I1_m, I1_a = 1.80, +0.70   # amps, noisy start
I2_m, I2_a = 1.60, +0.15   # amps, calmer

# time (m, a)
t_m, t_a = 3.0, +0.05      # seconds

# load mass and height (m, a)
m_load_m, m_load_a = 2.0, +0.05    # kg
h_m,      h_a       = 0.50, +0.10  # m

# gravitational acceleration (m, a)
g_m, g_a = 9.81, 0.0       # m/s^2, treated as exact


# 2) classical magnitudes

I_avg_m  = 0.5 * (I1_m + I2_m)
E_in_m   = V_m * I_avg_m * t_m          # input electrical energy
E_out_m  = m_load_m * g_m * h_m         # useful mechanical energy
E_loss_m = E_in_m - E_out_m             # classical loss


# 3) SSM alignments

# pooled current alignment
a_I = ssm_align_weighted(
    [(I1_a, I1_m), (I2_a, I2_m)],
    gamma=1.0,
    eps=1e-12,
)

# input energy alignment from V, I, t
a_Ein = ssm_align_sum([V_a, a_I, t_a])

# output energy alignment from m, g, h
a_Eout = ssm_align_sum([m_load_a, g_a, h_a])

# loss alignment as combined posture of input and output
a_Eloss = ssm_align_sum([a_Ein, a_Eout])


print("Classical:")
print("  E_in   =", f"{E_in_m:.2f}", "J")
print("  E_out  =", f"{E_out_m:.2f}", "J")
print("  E_loss =", f"{E_loss_m:.2f}", "J")

print("SSM (loss lane):")
print("  E_loss =", f"m={E_loss_m:.2f}, a={a_Eloss:+.4f}")

# Standard summary line for the runner (same pattern as L01-L04)
print("SSM:", f"m={E_loss_m:.2f}, a={a_Eloss:+.4f}")
