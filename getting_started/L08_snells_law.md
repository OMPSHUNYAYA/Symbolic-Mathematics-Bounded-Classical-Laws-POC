# **Getting Started — Law L08: Snell’s Law (Bounded Classical Law POC)**

**Domain.** Optics / Refraction / Lab Bench  

**Classical law.** `n1 * sin(theta1) = n2 * sin(theta2)`  

Rearranged to estimate an unknown refractive index:  

`n2 = n1 * sin(theta1) / sin(theta2)`

---

**What this shows.**

In this law POC, we take Snell’s Law in a simple refraction setup and show how:

- The Classical calculation gives the scalar refractive index `n2` of an unknown block, and  
- The Shunyaya Symbolic Mathematics (SSM) version keeps that scalar `n2` intact but adds a bounded alignment lane `a in (-1,+1)`, indicating whether this particular estimate of `n2` is calm, borderline, or stressed.

When angle measurements are sharp and repeatable, Shunyaya Symbolic Mathematics (SSM) collapses to the classical result and you effectively get the same answer.

When the angle marks are hard to read (parallax, thick laser line, slightly warped protractor), the alignment lane `a` and its band surface posture that the classical scalar `n2` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a standard Snell’s law lab:

- A laser passes from air into a transparent block (unknown material).
- You measure the angle of incidence `theta1` and angle of refraction `theta2` at the flat surface.
- You repeat the angle measurements twice to reduce error.

We model:

- **Refractive index of air (approx.):**  
  - `n1_m = 1.000`, `n1_a = +0.01` — close to 1, tiny uncertainty.

- **Incident angle measurements (from normal):**  
  - `theta1_1_m = 30.0 deg`, `theta1_1_a = +0.25` — first reading, slightly shaky eye alignment  
  - `theta1_2_m = 30.5 deg`, `theta1_2_a = +0.35` — second reading, still some drift  

- **Refracted angle measurements:**  
  - `theta2_1_m = 19.2 deg`, `theta2_1_a = +0.20` — first reading at the outgoing beam  
  - `theta2_2_m = 19.0 deg`, `theta2_2_a = +0.12` — second, a bit calmer  

In SSM:

- Each quantity is `(m,a)` with `a in (-1,+1)`.  
- Collapse is `phi((m,a)) = m`.

**Our target.**

- Use `n2 = n1 * sin(theta1) / sin(theta2)`  
- Compare **Classical** refractive index vs **SSM** refractive index `(m_n2, a_n2)`.

---

## **2) Classical calculation**

Ignoring alignment, we compute the refractive index of the block using average angles:

```python
# classical illustration (no external packages required)
import math

n1 = 1.000   # refractive index of air

theta1_1 = 30.0   # degrees
theta1_2 = 30.5   # degrees
theta2_1 = 19.2   # degrees
theta2_2 = 19.0   # degrees

theta1_avg_deg = 0.5 * (theta1_1 + theta1_2)
theta2_avg_deg = 0.5 * (theta2_1 + theta2_2)

theta1_rad = math.radians(theta1_avg_deg)
theta2_rad = math.radians(theta2_avg_deg)

n2 = n1 * math.sin(theta1_rad) / math.sin(theta2_rad)

print(theta1_avg_deg)  # ~30.25 deg
print(theta2_avg_deg)  # ~19.10 deg
print(n2)              # ~1.53 (typical glass-like value)

```

**Classical result.**

- `theta1_avg ≈ 30.25 deg`
- `theta2_avg ≈ 19.10 deg`
- `n2 ≈ 1.53` (consistent with a glass-like material)

A typical lab sheet might simply say:

“Measured refractive index: 1.53 (close to expected).”

But it does not clearly tell you how noisy the angles were or how much to trust that 1.53.

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In Shunyaya Symbolic Mathematics (SSM), we:

1. Treat each angle as `(m,a)` with `a in (-1,+1)` and pool alignment separately for `theta1` and `theta2`.

   For incident angles:

   - `a_c := clamp(a, -1+eps, +1-eps)`  
   - `u := atanh(a_c)`  
   - `U  += w * u`  with  `w := |theta|^gamma`  (default `gamma = 1`)  
   - `W  += w`  
   - `a_theta1_out := tanh( U / max(W, eps) )`  

   For refracted angles:

   - `a_theta2_out :=` same pooling over `theta2` samples

2. Use Snell’s law written as:

   - `n2 = n1 * sin(theta1) / sin(theta2)`

   For this POC we treat the alignment of `sin(theta)` as inheriting alignment from the angle itself (the nonlinearity is reflected in the magnitude, not the lane structure).

3. Build a numerator alignment `a_num` from `n1` and `theta1`:

   - `a_num := tanh(atanh(a_n1_c) + atanh(a_theta1_out_c))`

4. Use a division alignment rule for `n2 = num / den`:

   - `a_n2 := tanh(atanh(a_num_c) - atanh(a_theta2_out_c))`

5. Keep the refractive index magnitude as the classical `n2_m`:

   - `n2_m = n1_m * sin(theta1_avg) / sin(theta2_avg)`  
   - `phi((n2_m, a_n2)) = n2_m`

So:

- The scalar refractive index remains `~1.53`.  
- The bounded alignment lane `a_n2` tells you whether that `1.53` came from clean, repeatable angles or from noisy markings and reading drift.

---

## **4) Tiny script (copy-paste)**

```python
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

# denominator alignment: sin(theta2)
a_den = a_theta2

# refractive index alignment from division
a_n2 = ssm_align_div(a_num, a_den, eps=1e-6)

print("Classical:")
print("  theta1_avg =", f"{theta1_avg_deg:.2f}", "deg")
print("  theta2_avg =", f"{theta2_avg_deg:.2f}", "deg")
print("  n2         =", f"{n2_m:.3f}")

print("SSM (refractive index lane):")
print("  n2 =", f"m={n2_m:.3f}, a={a_n2:+.4f}")

```

Your shared runner can later attach bands:

- `|a| < 0.20` → `A+` (calm optical measurement)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed / noisy measurement)`

## **5) What to expect**

Numerically:

- Classical:  
  - `theta1_avg ≈ 30.25 deg`, `theta2_avg ≈ 19.10 deg`  
  - `n2 ≈ 1.53`  

- SSM (refractive index lane):  
  - `m = 1.53` (same as classical)  
  - `a_n2` comes out around `+0.16` (a small positive value under drift-positive semantics).

Under the sample band policy:

- `|a| < 0.20` → `A+` (calm optical measurement)

So in this setup:

- `a_n2 ≈ +0.16` falls in `A+` (calm) — the refractive index `1.53` is not only plausible but also based on reasonably clean, repeatable angles, with only mild drift.

If markings were read even more precisely (smaller `a` values for the angles), you could get:

- `a_theta1 ≈ 0`, `a_theta2 ≈ 0`, `a_n2 ≈ 0`  
- The same index `1.53` would then be marked as a perfectly calm, high-confidence optical measurement.

---

## **6) Why this helps in the real world**

- Teaching labs can distinguish between “Snell’s law fits nicely” and “Snell’s law fits but the readings were shaky” using the bounded alignment lane.  
- Optical engineers can quickly see which refractive index estimates are solid enough for design, and which are just approximate due to noisy angle measurement.  
- Automated rigs can color derived indices by band, highlighting which runs are good candidates for calibration and which should be repeated.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for thinking, experimentation, and education around bounded classical laws. It is not a safety case, design guarantee, or regulatory tool.

---

