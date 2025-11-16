# **Getting Started — Law L07: Bernoulli's Equation (Bounded Classical Law POC)**

**Domain.** Fluids / Pipe Flow / Lab Rig  

**Classical law.**  

For steady, incompressible, inviscid flow along a streamline (take a mostly horizontal pipe so heights are nearly equal):

- `P1 + 0.5 * rho * v1^2 ≈ P2 + 0.5 * rho * v2^2`  

Rearranged to solve for downstream pressure:

- `P2 = P1 + 0.5 * rho * (v1^2 - v2^2)`

---

## **What this shows**

In this law POC, we take **Bernoulli's Equation** in a simple horizontal pipe and show how:

- The **Classical** calculation gives the scalar downstream pressure `P2`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that pressure magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular Bernoulli snapshot is **calm**, **borderline**, or **stressed**.

When pressures and flow velocities are measured cleanly, **Shunyaya Symbolic Mathematics (SSM)** collapses to the classical result and you effectively get the same answer.

When gauge readings jump a bit or velocity estimates are noisy (pulsating pump, bubbles, sensor jitter), the alignment lane `a` and its band surface posture that the classical scalar `P2` alone does **not** show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means **more drift / more risk**. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a **water flow rig** in a lab:

- A pump drives water through a pipe that narrows from a **wider section (1)** to a **narrower section (2)**.  
- You measure pressure at section `(1)` with a gauge, and estimate pressure at section `(2)` from Bernoulli.  
- You measure flow rates or velocities with some jitter (due to pump ripple, small bubbles, etc.).

We model:

- **Fluid density (water, approx.):**  
  - `rho_m = 1000 kg/m^3`, `rho_a = +0.02` — nearly constant, small uncertainty.

- **Upstream pressure (gauge):**  
  - `P1_m = 200000 Pa` (≈`2.0 bar`), `P1_a = +0.10` — some gauge noise.

- **Velocities from flow measurement:**  
  - `v1_m = 1.5 m/s`, `v1_a = +0.30` — upstream velocity (slight jitter).  
  - `v2_m = 3.0 m/s`, `v2_a = +0.20` — higher velocity in narrower section, still somewhat noisy.

We treat the pipe as **roughly horizontal**, so `rho * g * h` terms are approximately equal and cancel out in the comparison.

In **SSM**:

- Each physical quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m`.

**Our target.**

- Use `P2 = P1 + 0.5 * rho * (v1^2 - v2^2)`  
- Compare **Classical** pressure `P2` vs **SSM** pressure `(m_P2, a_P2)`.

---

## **2) Classical calculation**

Ignoring alignment, we compute `P2` from Bernoulli between section 1 and 2:

```python
# classical illustration (no external packages required)

rho = 1000.0    # kg/m^3
P1  = 200000.0  # Pa  (section 1)
v1  = 1.5       # m/s (section 1)
v2  = 3.0       # m/s (section 2)

P2 = P1 + 0.5 * rho * (v1**2 - v2**2)

print(P2)       # ~196625 Pa (depending on rounding)

```

Compute step by step:

- `v1^2 = 1.5^2 = 2.25`
- `v2^2 = 3.0^2 = 9.00`
- `(v1^2 - v2^2) = 2.25 - 9.00 = -6.75`
- `0.5 * rho * (v1^2 - v2^2) = 0.5 * 1000 * (-6.75) = -3375 Pa`
- `P2 = 200000 - 3375 = 196625 Pa`

(Depending on rounding, you will see values around `1.97 * 10^5 Pa`.)

**Classical result.**

- `P2 ≈ 1.97 * 10^5 Pa` — slightly lower pressure in the faster region, as expected.

A typical write-up would just report this scalar `P2` and maybe a % drop, without clearly surfacing how noisy the flow measurements were.

---

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat each ingredient as `(m,a)` with `a in (-1,+1)`.

2. Build alignment lanes for the **dynamic pressure terms** at section 1 and section 2:

a_dyn1 := tanh(atanh(a_rho_c) + atanh(a_v1_c))
a_dyn2 := tanh(atanh(a_rho_c) + atanh(a_v2_c))

(Here we keep it simple and fold the `v^2` effect into the **velocity lane semantics**, not into the SSM math structure itself.)

3. Conceptually rewrite Bernoulli as P2 = P1 + 0.5 * rho * v1^2 - 0.5 * rho * v2^2, so we can treat P1, dyn1, and dyn2 as three contributing terms.

4. Then we combine the pressure and dynamic terms via a **“signed sum”** view:

   - `P2` is `P1` **plus** a contribution from `dyn1` and **minus** a contribution from `dyn2`.

   For this POC, we approximate the net alignment as a **weighted sum** over the three contributing terms:

   - `a_c := clamp(a, -1+eps, +1-eps)`  
   - `u := atanh(a_c)`  
   - `w := |contribution_magnitude|^gamma`  
   - `U += w * u`  
   - `W += w`  
   - `a_P2 := tanh( U / max(W, eps) )`

   where the contributions are roughly:

   - `+P1_m` with lane `P1_a`  
   - `+0.5 * rho_m * v1_m^2` with lane `a_dyn1`  
   - `-0.5 * rho_m * v2_m^2` with lane `a_dyn2`

5. We keep the **pressure magnitude** as the classical `P2_m`:

   - `P2_m = P1_m + 0.5 * rho_m * (v1_m**2 - v2_m**2)`  
   - `phi((P2_m, a_P2)) = P2_m`

So:

- The **pressure magnitude** stays around `1.97 * 10^5 Pa`.  
- The bounded alignment lane `a_P2` tells you how **reliable** this Bernoulli-based pressure estimate is for this particular measurement snapshot.

---

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Bernoulli POC in **ASCII-only Python**.

```python
# scenario_L07_bernoulli.py  (ASCII-only, top-level prints)

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
    where m_term is the magnitude of that contribution.
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

# 2) law-specific inputs and computations for Bernoulli between section 1 and 2
# P2 = P1 + 0.5 * rho * (v1^2 - v2^2)

# density (m, a)
rho_m, rho_a = 1000.0, +0.02    # kg/m^3

# upstream pressure (m, a)
P1_m, P1_a = 200000.0, +0.10    # Pa

# velocities (m, a)
v1_m, v1_a = 1.5, +0.30         # m/s
v2_m, v2_a = 3.0, +0.20         # m/s

# classical magnitude for P2
P2_m = P1_m + 0.5 * rho_m * (v1_m**2 - v2_m**2)

# SSM alignments

# dynamic pressure alignments for sections 1 and 2
a_dyn1 = ssm_align_sum([rho_a, v1_a])
a_dyn2 = ssm_align_sum([rho_a, v2_a])

# contribution magnitudes
dyn1_m = 0.5 * rho_m * (v1_m**2)
dyn2_m = 0.5 * rho_m * (v2_m**2)

# we treat P2 as composed of: +P1, +dyn1, -dyn2
# for posture, we use absolute magnitudes as weights
a_P2 = ssm_align_weighted(
    [
        (P1_a,   P1_m),
        (a_dyn1, dyn1_m),
        (a_dyn2, dyn2_m),
    ],
    gamma=1.0,
    eps=1e-12,
)

print("Classical:")
print("  P1 =", f"{P1_m:.0f}", "Pa")
print("  P2 =", f"{P2_m:.0f}", "Pa")

print("SSM (downstream pressure lane):")
print("  P2 =", f"m={P2_m:.0f}, a={a_P2:+.4f}")

```

You can attach bands in your shared runner, for example:

- |a| < 0.20 → A+ (calm Bernoulli snapshot)
- 0.20 <= |a| < 0.50 → A0 (borderline)
- |a| >= 0.50 → A- (stressed / noisy flow state)

---

## **5) What to expect**

Numerically:
• Classical: P2 only slightly lower than P1 (around 1.96–1.97 × 10^5 Pa).
• SSM:
  - m = P2_m (same magnitude as classical)
  - a_P2 ≈ +0.1039 under drift-positive semantics

Under the sample band policy:
• |a| < 0.20 → A+ (calm Bernoulli snapshot)
• 0.20 ≤ |a| < 0.50 → A0 (borderline)
• |a| ≥ 0.50 → A− (stressed / noisy flow state)

So for this snapshot:
• a_P2 ≈ +0.1039 → comfortably in A+ (calm).

Interpretation:
• The downstream pressure P2 is numerically reasonable and posturally calm for this snapshot.
• Even though the pump and velocities carry some drift (v1_a, v2_a, P1_a non-zero), the overall posture remains low-risk for this particular configuration.

If the pump were smoother and velocities even more stable (smaller v1_a, v2_a, P1_a), then for the same geometry and flow regime you would see:
• a_P2 move even closer to 0, and
• SSM ≡ Classical not just in magnitude, but also in posture, marking that Bernoulli snapshot as a very calm, high-confidence pressure estimate.

---

## **6) Why this helps in the real world**

• Fluid labs can distinguish between “a nice Bernoulli example” and “a numerically nice but noisy run,” using the alignment lane a as a compact, quantitative posture signal.

• Process engineers can see which P2 estimates are safe to rely on for tuning pumps, valves, or orifices, and which ones might have come from jittery operating conditions.

• Dashboards in industrial systems can color or band derived pressures by a, revealing where derived values look fine but are fed by unstable signals.

---

## **7) License and scope**

• License. CC BY-NC 4.0 (non-commercial, attribution required).

• Scope. Observation-only; not for critical use.

This POC is intended for thinking, experimentation, and education around bounded classical laws. It is not a safety case, design guarantee, or regulatory tool.

---
