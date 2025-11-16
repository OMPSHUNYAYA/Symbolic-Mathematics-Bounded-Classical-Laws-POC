# **Getting Started — Law L09: Continuity Equation (Bounded Classical Law POC)**

**Domain.** Fluid Mechanics / Pipe Flow / Instrumentation  

**Classical law.**  

For steady, incompressible flow in a pipe:  
`A1 * v1 = A2 * v2`  

Rearranged to estimate an unknown downstream velocity:  

`v2 = (A1 / A2) * v1`

---

**What this shows.**

In this law POC, we take the Continuity Equation in a simple pipe with changing cross-section and show how:

- The Classical calculation gives the scalar downstream velocity `v2`, and  
- The Shunyaya Symbolic Mathematics (SSM) version keeps that velocity magnitude intact but adds a bounded alignment lane `a in (-1,+1)`, indicating whether this particular continuity-based estimate of `v2` is calm, borderline, or stressed.

When areas and upstream velocity are measured cleanly, Shunyaya Symbolic Mathematics (SSM) collapses to the classical result and you effectively get the same answer.

When flow readings are jittery (pulsating pump, bubbles, ultrasonic meter noise) or cross-sectional area is uncertain (corrosion, fouling), the alignment lane `a` and its band surface posture that the classical scalar `v2` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a process pipe that narrows slightly downstream:

- You know the inlet area from design drawings, but fouling and roughness introduce a bit of uncertainty.  
- You know the throat area from callipers, again with some uncertainty.  
- You measure upstream velocity with an ultrasonic sensor, which has visible jitter.

We model:

- **Inlet area (section 1):**  
  - `A1_m = 0.0100 m^2`, `A1_a = +0.10`  
  - Nearly `100 cm^2`; some uncertainty due to fouling and tolerance.

- **Throat area (section 2):**  
  - `A2_m = 0.0060 m^2`, `A2_a = +0.15`  
  - Narrower section; slightly more uncertain (machining + deposits).

- **Upstream velocity (section 1, two readings):**  
  - `v1_1_m = 1.80 m/s`, `v1_1_a = +0.45` — early reading, more pump ripple  
  - `v1_2_m = 2.00 m/s`, `v1_2_a = +0.20` — later reading, a bit steadier  

In SSM:

- Each quantity is `(m,a)` with `a in (-1,+1)`.  
- Collapse is `phi((m,a)) = m`.

**Our target.**

- Use `v2 = (A1 / A2) * v1`  
- Compare Classical `v2` vs SSM velocity `(m_v2, a_v2)`.

---

## **2) Classical calculation**

Ignoring alignment, we use the continuity equation to compute downstream velocity:

```python
# classical illustration (no external packages required)

A1 = 0.0100   # m^2 (inlet area)
A2 = 0.0060   # m^2 (throat area)

v1_1 = 1.80   # m/s (first reading)
v1_2 = 2.00   # m/s (second reading)

v1_avg = 0.5 * (v1_1 + v1_2)
v2     = (A1 / A2) * v1_avg

print(v1_avg)  # 1.90 m/s
print(v2)      # ~3.17 m/s

```

**Classical result.**

- `v1_avg = 1.90 m/s`
- `v2 ≈ (0.0100 / 0.0060) * 1.90 ≈ 3.17 m/s`

A typical summary might say:

“Downstream velocity ≈ 3.2 m/s by continuity.”

This looks neat, but does not show whether the inputs were calm or if the number is based on a noisy combination of jittery `v1` and uncertain geometry.

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In Shunyaya Symbolic Mathematics (SSM), we:

1. Treat all inputs as two-lane values `(m, a)` with `a in (-1,+1)`.

2. Pool the upstream velocity alignment from the two samples using a weighted rule (by magnitude):

   - For each sample, clamp and map into rapidity space:  
     - `a_c := clamp(a, -1+eps, +1-eps)`  
     - `u := atanh(a_c)`  

   - Accumulate with weights `w := |m|^gamma` (default `gamma = 1`):  
     - `U += w * u`  
     - `W += w`  

   - Collapse back to the alignment lane:  
     - `a_v1_out := tanh( U / max(W, eps) )`

3. Build an alignment for the area ratio `A1 / A2` using a division-style rule over rapidities:

   - `a_ratio := tanh(atanh(a_A1_c) - atanh(a_A2_c))`

4. Combine the ratio alignment and pooled upstream velocity alignment via a product-style sum of rapidities:

   - `a_v2 := tanh(atanh(a_ratio_c) + atanh(a_v1_out_c))`

5. Keep the downstream velocity magnitude as the classical `v2_m`:

   - `v2_m = (A1_m / A2_m) * v1_avg_m`  
   - `phi((v2_m, a_v2)) = v2_m`

So:

- The scalar downstream velocity remains `~3.17 m/s`.  
- The bounded alignment lane `a_v2` tells you whether that `3.17 m/s` comes from a calm continuity snapshot, or from noisy, borderline flow conditions plus uncertain geometry.

---

## **4) Tiny script (copy-paste)**

```python
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

```

Later, your shared runner can assign bands, for example:

- `|a| < 0.20` → `A+` (calm continuity-based estimate)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed / noisy continuity snapshot)

## **5) What to expect**

Numerically:

- Classical:  
  - `v1_avg ≈ 1.90 m/s`  
  - `v2 ≈ 3.17 m/s`  

- SSM (downstream velocity lane):  
  - `m = 3.17 m/s` (same as classical)  
  - `a_v2` will be **moderately positive**, reflecting a combination of geometry uncertainty and velocity jitter.

Under the sample band policy, you will typically see:

- `a_v2` in `A0` (borderline) or even `A-` (stressed) if jitter is large.

**Interpretation.**

- Continuity gives a reasonable `v2 ≈ 3.17 m/s`, but SSM tells you:  
  “This value depends on shaky upstream readings and uncertain area; treat as approximate.”

If:

- The ultrasonic velocity readings were calmer (smaller `a`), and  
- Pipe geometry was measured more precisely (smaller `A1_a`, `A2_a`),  

then you would see:

- `a_ratio ≈ 0`, `a_v1 ≈ 0`, `a_v2 ≈ 0`  

and that same `3.17 m/s` would be marked as a **calm, high-confidence** continuity estimate.

---

## **6) Why this helps in the real world**

- Process engineers can see which continuity-based velocities are **good enough for control tuning** and which are numerically fine but posturally noisy, using `a_v2` as a compact reliability signal.  
- Instrumentation teams can compare different meter configurations and see where continuity is satisfied with **calm posture** versus **noisy posture**, even when the scalar numbers look similar.  
- Dashboards can color continuity-based derived flows or velocities by band, helping operations teams prioritize where to **re-check instrumentation or data quality**.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for thinking, experimentation, and education around bounded classical laws. It is not a safety case, design guarantee, or regulatory tool.

---
