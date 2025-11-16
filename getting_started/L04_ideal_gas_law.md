# **Getting Started — Law L04: Ideal Gas Law (Bounded Classical Law POC)**

**Domain.** Thermodynamics / Lab Cylinder Test  

**Classical law.** `P * V = n * R * T`

**What this shows.**

In this law POC, we take the Ideal Gas Law and show how:

- The **Classical** calculation gives the correct scalar pressure `P`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that pressure magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular `P * V = n * R * T` situation is **calm**, **borderline**, or **stressed**.

When temperature and volume are well-behaved and `n` is well-known, SSM collapses to Classical and you effectively get the same answer.

When readings are jittery (thermometer not settled, piston not perfectly fixed), the alignment lane `a` and its band surface posture that the classical scalar `P` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only. You can flip the semantics (for example, make `+a` mean more stability) without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a **sealed vertical cylinder** with a movable piston, containing a small amount of air:

- The amount of gas `n` is known to be close to `1 mol`.  
- Volume `V` is around `10 L`, but the piston position has some uncertainty.  
- You gently warm the cylinder and take **two temperature readings** as it equilibrates.

We model:

- **Amount of gas (approximate, but stable):**  
  - `n_m = 1.00 mol`, `n_a = +0.02` — almost exactly one mole.

- **Gas constant (treated as effectively exact here):**  
  - `R_m = 8.314 J/(mol*K)`, `R_a = +0.00`.

- **Volume (slightly uncertain piston position):**  
  - `V_m = 0.0100 m^3` (10 L), `V_a = +0.10` — piston not perfectly fixed.

- **Temperature measurements (instantaneous):**  
  - `T1_m = 295 K`, `T1_a = +0.55` — thermometer still equilibrating.  
  - `T2_m = 305 K`, `T2_a = +0.12` — later, calmer reading.

In **SSM**:

- Each quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m`.

**Our target.**

- Use the ideal gas law `P = (n * R * T) / V`.  
- Compare **Classical** pressure vs **SSM** pressure `(m_P, a_P)`.

## **2) Classical calculation**

Ignoring alignment, we just apply the ideal gas law with the **average temperature**:

```python
# classical illustration (no external packages required)

n  = 1.00      # mol
R  = 8.314     # J/(mol*K)
V  = 0.0100    # m^3  (10 L)

T1 = 295.0     # K
T2 = 305.0     # K

T_avg = 0.5 * (T1 + T2)
P     = (n * R * T_avg) / V

print(T_avg)  # 300.0
print(P)      # 249420.0 (approx)  ~2.49e5 Pa

```

**Classical result.**

- `T_avg = 300 K`  
- `P ≈ 2.49 * 10^5 Pa` (about `2.5 bar`)  

A standard report might simply say: **"Pressure ≈ 2.5 bar."** It does not indicate whether the thermodynamic state during measurement was calm or borderline.

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat each temperature sample as `(m,a)` with `a in (-1,+1)` and pool their alignments using the **weighted sum pooling rule**:
   - `a_c := clamp(a, -1+eps, +1-eps)`
   - `u := atanh(a_c)`
   - `w := |m|^gamma`  (default `gamma = 1`)
   - `U += w * u`
   - `W += w`
   - `a_T_out := tanh( U / max(W, eps) )`

2. Treat `n`, `R`, and `V` as `(m,a)` as well (some with nearly zero `a`).

3. Combine alignments for the product `n * R * T` using **sum of rapidities**:
   - `a_nRT := tanh(atanh(a_n_c) + atanh(a_R_c) + atanh(a_T_out_c))`

4. Then handle the division by `V` in the alignment lane:
   - `a_P := tanh(atanh(a_nRT_c) - atanh(a_V_c))`

5. Keep the pressure magnitude exactly at the classical value:
   - `m_P = (n_m * R_m * T_avg) / V_m`
   - `phi((m_P, a_P)) = m_P`

So:

- The magnitude of pressure stays around `2.49 * 10^5 Pa`.  
- The bounded alignment lane `a_P` tells us whether this ideal-gas snapshot comes from a **calm, well-behaved state** or from **noisy, borderline conditions** (drifting thermometer, uncertain piston position).

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Ideal Gas Law POC in **ASCII-only Python**.

```python
# scenario_L04_ideal_gas_law.py  (ASCII-only, top-level prints)

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
n_m, n_a = 1.00, +0.02     # mol

# gas constant (m, a)
R_m, R_a = 8.314, +0.00    # J/(mol*K)

# volume (m, a)
V_m, V_a = 0.0100, +0.10   # m^3 (10 L)

# temperature measurements (m, a) at two instants
T1_m, T1_a = 295.0, +0.55  # K
T2_m, T2_a = 305.0, +0.12  # K

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
print("SSM:", f"m={P_m:.2f}, a={a_P:+.4f}")   # a_P ~ +0.28 (drift-positive)

```

You can later add **band assignment** in your shared runner, for example:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed)

## **5) What to expect**

Running the script, you will see something like:

- `Classical: P ≈ 2.49 * 10^5 Pa`  
- `SSM: m = 2.49 * 10^5 Pa, a ≈ +0.2775`  (under drift-positive semantics)

Under a simple band policy such as:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)

we get:

- `a ≈ +0.2775` sitting in `A0` (borderline) — slightly above calm, but not in a stressed `A-` region.

So the ideal gas law **fits** (pressure is correct), but the bounded alignment lane tells you:

- This particular `P–V–T–n` snapshot was taken under **mildly noisy / borderline conditions** (thermometer still drifting, piston position somewhat uncertain).

If both `T1` / `T2` were very close and `V_a` small, you would instead see:

- `a_T ≈ 0`, `a_P ≈ 0`, and **SSM and Classical agree not just in magnitude but also in posture**.

## **6) Why this helps in the real world**

- **Lab instructors** can distinguish a “nice ideal-gas point” from a **numerically similar but noisy condition**, using `a` as a compact stability signal.  
- **Engineers** can tell whether a measured `P–V–T` point is good enough to use as a **calibration reference** or should be **re-measured under calmer conditions**.  
- **Dashboards in thermal test rigs** can color pressure by `a` or by band, revealing at a glance which states were **clean** and which were **nominally correct but posturally suspect**.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

ideal-gas-law • thermodynamics • lab-cylinder-test • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • posture-lane • ssm-poc • getting-started
