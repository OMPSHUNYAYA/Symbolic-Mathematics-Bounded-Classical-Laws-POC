# **Getting Started — Law L03: Hooke's Law (Bounded Classical Law POC)**

**Domain.** Mechanics / Materials Testing / Lab Bench  

**Classical law.** `F = k * x`

**What this shows.**

In this law POC, we take Hooke's Law and show how:

- The **Classical** calculation gives the correct scalar force `F`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that force magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular `F = k * x` situation is **calm**, **borderline**, or **stressed**.

When the extension measurements are clean and the spring constant is well-characterized, SSM collapses to Classical and you effectively get the same answer.

When the displacement readings are noisy or the spring is behaving non-ideally, the alignment lane `a` and its band surface posture that the classical scalar `F` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only. You can flip the semantics (for example, make `+a` mean more stability) without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a **simple spring test** on a lab bench:

- You hang a small weight on a coil spring and measure how far it stretches.  
- You take **two displacement readings** as the system settles: the first is a bit jerky (you just released the weight), the second is more calm.  
- The spring constant `k` is known from prior calibration but not perfectly exact.

We model:

- **Spring constant (approximate):**  
  - `k_m = 200.0 N/m`, `k_a = +0.08`  
    - Reasonably well-known spring; small uncertainty in calibration and temperature.

- **Displacement measurements (instantaneous):**  
  - `x1_m = 0.045 m`, `x1_a = +0.60` — slightly jerky reading (still settling)  
  - `x2_m = 0.055 m`, `x2_a = +0.10` — calmer reading (closer to steady-state)

In **SSM**:

- Each quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m` — drop the alignment lane, keep the magnitude.

**Our target.**

- Use Hooke's law `F = k * x`.  
- Compare **Classical** force vs **SSM** force `(m_F, a_F)`.

---

## **2) Classical calculation**

Ignoring alignment, we do the usual Hooke's law with an average displacement:

```python
# classical illustration (no external packages required)

k  = 200.0      # N/m (approx spring constant)
x1 = 0.045      # m (jerkier reading)
x2 = 0.055      # m (calmer reading)

x_avg = 0.5 * (x1 + x2)
F     = k * x_avg

print(x_avg)  # 0.05
print(F)      # 10.0

```

**Classical result.**

- x_avg = 0.050 m  
- F = 10.0 N  

A standard lab sheet would simply record: **Force ≈ 10 N**, with no sense of whether the spring behaviour during measurement was stable or twitchy.

---

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat each displacement sample as `(m,a)` with `a in (-1,+1)`.  
2. Compute an alignment for displacement using the **sum pooling rule**:
   - `a_c := clamp(a, -1+eps, +1-eps)`
   - `u := atanh(a_c)`
   - `w := |m|^gamma`  (default `gamma = 1`)
   - `U += w * u`
   - `W += w`
   - `a_x_out := tanh( U / max(W, eps) )`
3. Combine the displacement alignment with the spring constant alignment using **product chaining** for the law `F = k * x`:
   - `a_F := tanh(atanh(a_k_c) + atanh(a_x_out_c))`
4. Keep the force magnitude as `m_F = k_m * x_avg` — **exactly the classical result**:
   - `phi((m_F, a_F)) = m_F = k_m * x_avg`

So:

- The magnitude of force is still `10.0 N`.  
- The bounded alignment lane `a_F` tells us how **“ideal”** this Hooke's law instance is, given one **jerky** displacement sample and one **calmer** one, plus a slightly uncertain `k`.

**Intuition.**

- One displacement reading is relatively noisy (`x1_a ≈ +0.60` under drift-positive semantics).  
- The other is close to calm (`x2_a ≈ +0.10`).  
- Their pooled displacement alignment `a_x_out` lands in a **moderate risk region**.  
- Combining this with a mildly uncertain spring constant (`k_a ≈ +0.08`) yields a force alignment `a_F` that is clearly non-zero, but not catastrophic.

---

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Hooke's law POC in **ASCII-only Python**.

```python
# scenario_L03_hookes_law.py  (ASCII-only, top-level prints)

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

def ssm_align_product(a1_raw, a2_raw, eps=1e-6):
    """
    Product chaining for alignment lane:
    a_out := tanh(atanh(a1_c) + atanh(a2_c))
    """
    a1 = clamp(a1_raw, eps)
    a2 = clamp(a2_raw, eps)
    u1 = 0.5 * math.log((1.0 + a1) / (1.0 - a1))
    u2 = 0.5 * math.log((1.0 + a2) / (1.0 - a2))
    return math.tanh(u1 + u2)

# 1) law-specific inputs: Hooke's law F = k * x

# spring constant (m, a)
k_m, k_a = 200.0, +0.08   # N/m, mildly uncertain

# displacement measurements (m, a) at two instants
x1_m, x1_a = 0.045, +0.60  # m, jerkier reading
x2_m, x2_a = 0.055, +0.10  # m, calmer reading

# 2) classical magnitude: average displacement, then F = k * x
x_avg = 0.5 * (x1_m + x2_m)
F_m   = k_m * x_avg

# 3) SSM alignments
# pooled displacement alignment
a_x = ssm_align_weighted(
    [(x1_a, x1_m), (x2_a, x2_m)],
    gamma=1.0,
    eps=1e-12,
)

# force alignment from spring constant and displacement
a_F = ssm_align_product(k_a, a_x, eps=1e-6)

print("Classical:", f"{F_m:.4f}")            # 10.0000
print("SSM:", f"m={F_m:.4f}, a={a_F:+.4f}")  # a_F ~ +0.45 (drift-positive)

```

You can later add **band assignment** in your shared runner, for example:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed)

---

## **5) What to expect**

Running the script gives roughly:

- `Classical: F ≈ 10.0000 N`  
- `SSM: m = 10.0000 N, a ≈ +0.42` (under drift-positive semantics)

Under the sample band policy:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)

So:

- `a ≈ +0.42` falls in `A0` (borderline). The spring behaves acceptably, but not perfectly calmly; the initial jerkiness shows up in the bounded alignment lane, even though the final force value of `10 N` looks perfectly reasonable.

If both displacement readings were calm and the spring constant alignment small, we would get:

- `a_x ≈ 0`, `a_F ≈ 0`, and **SSM ≡ Classical** (both in magnitude and posture).

---

## **6) Why this helps in the real world**

- **Lab instructors** can use the alignment lane `a` to distinguish between “10 N from a clean, well-controlled stretch” versus “10 N from a jerky or poorly controlled setup.”  
- **Test engineers** can quickly see which Hooke's law measurements are reliable for calibration and which ones should be repeated or averaged over longer windows.  
- **Dashboards in materials testing rigs** can color or band force values by alignment, so operators can see at a glance which measurements came from ideal spring-like behaviour and which came from noisy, marginal, or fatigued springs — all without changing the underlying law `F = k * x`.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

hookes-law • spring-test • materials-testing • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • posture-lane • ssm-poc • getting-started

