# **Getting Started — Law L02: Newton's Second Law (Bounded Classical Law POC)**

**Domain.** Mechanics / Robotics / Motion Control  

**Classical law.** `F = m * a`

**What this shows.**

In this law POC, we take Newton's Second Law and show how:

- The **Classical** calculation gives the correct scalar force `F`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that force magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular `F = m * a` situation is **calm**, **borderline**, or **stressed**.

When the motion is smooth and mass is well-known, SSM collapses to Classical and you effectively get the same answer.

When acceleration is jerky or mass is uncertain, the alignment lane `a` and its band surface posture that the classical scalar `F` alone does not show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only. You can flip the semantics (for example, make `+a` mean more stability) without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a **small robotic cart** on a test rig. The cart is commanded to move forward gently. You know its mass to a reasonable approximation, and you record two acceleration samples a short time apart:

- The first sample is during a **slightly jerky start**.  
- The second sample is when motion is **more settled**.

We model:

- **Mass of the cart (approximate):**  
  - `m_m = 20.0 kg`, `m_a = +0.05`  
    - The cart mass is fairly well known (small alignment, near-calm).

- **Acceleration measurements (instantaneous):**  
  - `a1_m = 0.90 m/s^2`, `a1_a = +0.65` — jerkier instant (controller still settling)  
  - `a2_m = 1.10 m/s^2`, `a2_a = +0.10` — smoother instant (steady push)

In **SSM**:

- Each quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m` — we drop the alignment lane and keep the magnitude.

**Our target.**

- Use `F = m * a`.  
- Compare **Classical** force vs **SSM** force `(m_F, a_F)`.

---

## **2) Classical calculation**

Ignoring alignment, we do the usual Newton's law with an average acceleration:

```python
# classical illustration (no external packages required)

m  = 20.0       # kg (approx mass of the cart)
a1 = 0.90       # m/s^2 (jerkier instant)
a2 = 1.10       # m/s^2 (calmer instant)

a_avg = 0.5 * (a1 + a2)
F     = m * a_avg

print(a_avg)  # 1.0
print(F)      # 20.0

```

**Classical result.**

- a_avg = 1.0 m/s^2
- F = 20.0 N

A standard lab report would simply state: Force ≈ 20 N, with no indication of how jerky or smooth the motion really was.

---

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat each acceleration sample as `(m,a)` with `a in (-1,+1)`.
2. Compute an alignment for acceleration using the **sum pooling rule**:
   - `a_c := clamp(a, -1+eps, +1-eps)`
   - `u := atanh(a_c)`
   - `w := |m|^gamma`  (default `gamma = 1`)
   - `U += w * u`
   - `W += w`
   - `a_a_out := tanh( U / max(W, eps) )`
3. Combine the acceleration alignment with the mass alignment using **product chaining** for the law `F = m * a`:
   - `a_F := tanh(atanh(a_m_c) + atanh(a_a_out_c))`
4. Keep the force magnitude as `m_F = m_m * a_avg` — **exactly the classical result**:
   - `phi((m_F, a_F)) = m_F = m_m * a_avg`

So:

- The magnitude of force is still `20.0 N`.  
- The bounded alignment lane `a_F` tells us how **smooth** or **jerky** the realized `F = m * a` is, given our two acceleration samples and the slightly uncertain mass.

**Intuition.**

- One acceleration sample has high drift (`a1_a ≈ +0.65` under drift-positive semantics).  
- The other is closer to calm (`a2_a ≈ +0.10`).  
- Their pooled acceleration alignment `a_a_out` lands in a **moderate risk region**.  
- Combining this with a mostly calm mass (`m_a ≈ +0.05`) yields a force alignment `a_F` that is noticeably non-zero, but not “worst case”.

---

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Newton's law POC in **ASCII-only Python**.

```python
# scenario_L02_newton_fma.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Newton's second law F = m * a

# mass (m, a) of the cart
m_m, m_a = 20.0, +0.05   # kg, mostly calm

# acceleration measurements (m, a) at two instants
a1_m, a1_a = 0.90, +0.65  # m/s^2, jerkier instant
a2_m, a2_a = 1.10, +0.10  # m/s^2, calmer instant

# 2) classical magnitude: average acceleration, then F = m * a
a_avg = 0.5 * (a1_m + a2_m)
F_m   = m_m * a_avg

# 3) SSM alignments
# pooled acceleration alignment
a_accel = ssm_align_weighted(
    [(a1_a, a1_m), (a2_a, a2_m)],
    gamma=1.0,
    eps=1e-12,
)

# force alignment from mass and acceleration
a_F = ssm_align_product(m_a, a_accel, eps=1e-6)

print("Classical:", f"{F_m:.4f}")            # 20.0000
print("SSM:", f"m={F_m:.4f}, a={a_F:+.4f}")  # a_F ~ +0.48 (drift-positive)

```

You can later add **band assignment** in the overall runner, for example:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed)

---

## **5) What to expect**

Running the script gives:

- `Classical: F ≈ 20.0000 N`  
- `SSM: m = 20.0000 N, a ≈ +0.43` (under drift-positive semantics)

Under a simple policy:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)

So in this example:

- `a ≈ +0.43` sits in the upper part of `A0` (borderline), below the stressed `A-` region.  
- The underlying force magnitude `F = 20 N` is perfectly classical, but SSM makes visible that the underlying acceleration samples are **not uniformly calm**.

If both acceleration samples were smooth and mass alignment small, we would get:

- `a_accel ≈ 0`, `a_F ≈ 0`, and **SSM ≡ Classical** in posture as well.

---

## **6) Why this helps in the real world**

- Robotics engineers can distinguish between **“20 N applied smoothly”** vs **“20 N coming from jerky control”**, using the alignment lane `a` as a quick indicator of motion quality.  
- Testing teams can flag borderline or stressed `F = m * a` situations even when the scalar force looks fine, prompting better tuning of controllers and actuators.  
- Dashboards and logs can color or band force values by alignment, making it easier to spot which trials or operating points were genuinely **smooth** and which were **numerically correct but posturally noisy**.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

newtons-second-law • force • motion-control • robotics • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • ssm-poc • getting-started

