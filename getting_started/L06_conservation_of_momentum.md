# **Getting Started — Law L06: Conservation of Momentum (Bounded Classical Law POC)**

**Domain.** Mechanics / Collisions / Lab Carts  

**Classical law.** `m1 * u1 + m2 * u2 = m1 * v1 + m2 * v2`

**What this shows**

In this law POC, we take **Conservation of Momentum** in a 1D collision and show how:

- The **Classical** calculation gives you scalar momenta before and after collision (and a small imbalance `delta_p`), and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that imbalance magnitude `delta_p` intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular momentum-conservation check is **calm**, **borderline**, or **stressed**.

When masses and velocities are measured cleanly and the track is nearly frictionless, SSM collapses to Classical and you effectively get the same answer.

When the velocity readings are jittery (blurred marks, timing noise, slight track friction), the alignment lane `a` and its band surface posture that the classical scalar `delta_p` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

## **1) Setup (inputs)**

Imagine **two lab carts** on a low-friction track:

- Cart 1 moves to the right and collides gently with Cart 2, which is initially at rest.  
- After collision, both carts move to the right with different velocities.  
- You measure their masses and velocities with reasonable but not perfect accuracy.

We model:

- **Masses (fairly well known):**  
  - `m1_m = 1.50 kg`, `m1_a = +0.05`  
  - `m2_m = 1.00 kg`, `m2_a = +0.05`

- **Initial velocities (before collision):**  
  - `u1_m = 1.20 m/s`, `u1_a = +0.40` — cart 1 measured from marks + timer (a bit noisy).  
  - `u2_m = 0.00 m/s`, `u2_a = +0.05` — cart 2 nearly at rest.

- **Final velocities (after collision):**  
  - `v1_m = 0.70 m/s`, `v1_a = +0.35` — cart 1 slowed down.  
  - `v2_m = 0.80 m/s`, `v2_a = +0.20` — cart 2 sped up.

In **SSM**:

- Each physical quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m`.

We will:

- Compute **classical momenta** before and after.  
- Compute the classical momentum imbalance `delta_p = p_before - p_after`.  
- Wrap `delta_p` in a two-lane SSM form `(m_delta_p, a_delta_p)` where `a_delta_p` reports how trustworthy that conservation check feels.

## **2) Classical calculation**

Ignoring alignment, we compute scalar momentum before and after collision:

```python
# classical illustration (no external packages required)

m1 = 1.50   # kg
m2 = 1.00   # kg

u1 = 1.20   # m/s (before, cart 1)
u2 = 0.00   # m/s (before, cart 2)

v1 = 0.70   # m/s (after, cart 1)
v2 = 0.80   # m/s (after, cart 2)

p_before = m1 * u1 + m2 * u2
p_after  = m1 * v1 + m2 * v2
delta_p  = p_before - p_after

print(p_before)  # 1.80 kg m/s
print(p_after)   # 1.85 kg m/s
print(delta_p)   # -0.05 kg m/s

```

**Classical result.**

- `p_before ≈ 1.80 kg*m/s`  
- `p_after ≈ 1.85 kg*m/s`  
- `delta_p ≈ -0.05 kg*m/s`

So the law is almost satisfied — only a small mismatch, which might be explained by friction, slight misalignment, or timing errors.  
A typical lab might say:

"Momentum is conserved within experimental error."

But this is qualitative. There is no compact, quantitative **posture signal** telling you how shaky or solid this conclusion is.

## **3) SSM calculation (same imbalance magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat each mass or velocity as `(m,a)` with `a in (-1,+1)`.

2. For each cart, build a **per-cart momentum alignment** using a sum of rapidities for mass and velocity:

   - `a_p1_before := tanh(atanh(a_m1_c) + atanh(a_u1_c))`  
   - `a_p2_before := tanh(atanh(a_m2_c) + atanh(a_u2_c))`  

   - `a_p1_after  := tanh(atanh(a_m1_c) + atanh(a_v1_c))`  
   - `a_p2_after  := tanh(atanh(a_m2_c) + atanh(a_v2_c))`

3. Pool these cart-level alignments into **global momentum alignments** before and after, using a weighted sum rule:

   - `a_c := clamp(a, -1+eps, +1-eps)`  
   - `u := atanh(a_c)`  
   - `w := |p_cart|^gamma` with `p_cart = m * v` and default `gamma = 1`  
   - `U += w * u`  
   - `W += w`  
   - `a_before := tanh( U / max(W, eps) )`  over `{p1_before, p2_before}`  
   - `a_after  := tanh( U / max(W, eps) )`  over `{p1_after,  p2_after}`  

4. Compute the **classical imbalance**:

   - `m_delta_p = p_before - p_after`

5. Build an alignment lane for the imbalance by combining before and after alignments:

   - `a_delta_p := tanh(atanh(a_before_c) + atanh(a_after_c))`

6. Respect **collapse parity**:

   - `phi((m_delta_p, a_delta_p)) = m_delta_p`

So:

- The imbalance magnitude is still `delta_p ≈ -0.05 kg*m/s`.  
- The bounded alignment lane `a_delta_p` tells you whether this **“almost conserved”** result came from **calm, clean measurements** or from **noisy, borderline measurements** that just happen to nearly cancel numerically.

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Conservation of Momentum POC in **ASCII-only Python**.

```python
# scenario_L06_conservation_of_momentum.py  (ASCII-only, top-level prints)

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
    where m_term is the magnitude associated with that lane (e.g., cart momentum).
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

# 1) law-specific inputs: Conservation of Momentum in 1D

# masses (m, a)
m1_m, m1_a = 1.50, +0.05   # kg
m2_m, m2_a = 1.00, +0.05   # kg

# initial velocities (u, a)
u1_m, u1_a = 1.20, +0.40   # m/s, cart 1 before
u2_m, u2_a = 0.00, +0.05   # m/s, cart 2 before

# final velocities (v, a)
v1_m, v1_a = 0.70, +0.35   # m/s, cart 1 after
v2_m, v2_a = 0.80, +0.20   # m/s, cart 2 after

# 2) classical momenta

p_before_m = m1_m * u1_m + m2_m * u2_m
p_after_m  = m1_m * v1_m + m2_m * v2_m
delta_p_m  = p_before_m - p_after_m

# 3) SSM alignments

# per-cart momentum alignments (before)
a_p1_before = ssm_align_sum([m1_a, u1_a])
a_p2_before = ssm_align_sum([m2_a, u2_a])

# per-cart momentum alignments (after)
a_p1_after  = ssm_align_sum([m1_a, v1_a])
a_p2_after  = ssm_align_sum([m2_a, v2_a])

# overall momentum alignment before and after
a_before = ssm_align_weighted(
    [(a_p1_before, m1_m * u1_m),
     (a_p2_before, m2_m * u2_m)],
    gamma=1.0,
    eps=1e-12,
)

a_after = ssm_align_weighted(
    [(a_p1_after, m1_m * v1_m),
     (a_p2_after, m2_m * v2_m)],
    gamma=1.0,
    eps=1e-12,
)

# imbalance alignment as combined posture of both sides
a_delta_p = ssm_align_sum([a_before, a_after])

print("Classical:")
print("  p_before =", f"{p_before_m:.3f}", "kg m/s")
print("  p_after  =", f"{p_after_m:.3f}", "kg m/s")
print("  delta_p  =", f"{delta_p_m:.3f}", "kg m/s")

print("SSM (imbalance lane):")
print("  delta_p =", f"m={delta_p_m:.3f}, a={a_delta_p:+.4f}")

```

You can attach a **band** in the shared runner, for example:

- `|a| < 0.20` → `A+` (calm conservation test)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed / noisy conservation test)

## **5) What to expect**

Numerically (with the chosen values):

- **Classical:**  
  - `p_before ≈ 1.80 kg*m/s`  
  - `p_after ≈ 1.85 kg*m/s`  
  - `delta_p ≈ -0.05 kg*m/s`

- **SSM (imbalance lane):**  
  - `delta_p = -0.05 kg*m/s` (same magnitude)  
  - `a_delta_p ≈ +0.6744` under drift-positive semantics

Under the sample band policy:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A−` (stressed / noisy conservation test)

we get:

- `a_delta_p ≈ +0.6744` → clearly in **A− (stressed)**.

**Interpretation.**

- The classical law appears almost satisfied (`delta_p` small).  
- But the bounded alignment lane shows that this **“good-looking” conservation check** is actually based on **noisy velocity measurements** and **modest mass uncertainty**.  
- In other words, the numbers look good, but the **posture is shaky**.

If all velocities and masses were measured more calmly (smaller `a` values), you might see:

- `a_before ≈ 0`, `a_after ≈ 0`, `a_delta_p ≈ 0`  
- The same small `delta_p` would then be marked as a **calm, reliable conservation check**.

## **6) Why this helps in the real world**

- **Teaching labs** can go beyond *“within experimental error”* and quantify how trustworthy a conservation check is, using `a` (or its band) as a compact posture signal.  
- **Researchers running many collision trials** can automatically distinguish between **clean** and **noisy** runs, even when the scalar momenta appear similarly close.  
- **Dashboards in robotics or experimental rigs** can flag conservation tests by band, guiding attention toward trials where physics seems fine numerically but the **posture is clearly stressed**.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

conservation-of-momentum • 1d-collision • lab-carts • mechanics • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • posture-lane • ssm-poc • getting-started
