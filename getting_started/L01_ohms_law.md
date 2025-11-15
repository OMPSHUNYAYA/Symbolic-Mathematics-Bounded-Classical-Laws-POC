# **Getting Started — Law L01: Ohm's Law (Bounded Classical Law POC)**

**Domain.** Electrical / Lab Bench Test  

**Classical law.** `V = I * R`

**What this shows.**

In this law POC, we take Ohm's Law and show how:

- The **Classical** calculation gives the correct scalar voltage `V`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that voltage magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular `V = I * R` situation is **calm**, **borderline**, or **stressed**.

When the supply and load are calm, SSM collapses to Classical and you effectively get the same answer.

When current and resistance are drifting or noisy, the alignment lane `a` and its band surface posture that the classical scalar `V` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so that larger printed `a` means more drift / more risk. This is a display choice only. You can flip the semantics (for example, make `+a` mean more stability) without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a **12 V DC bench supply** driving a small device (for example, a motor or pump).

You take **two current readings** a few seconds apart; the device is slightly noisy on start-up, then calms down. The load resistance is approximately steady but not perfect.

We model:

- **Current measurements (instantaneous):**  
  - `I1_m = 1.92 A`, `I1_a = +0.72` — noisy moment (spin-up, higher jitter)  
  - `I2_m = 1.98 A`, `I2_a = +0.05` — calmer moment (near steady-state)

- **Load resistance (approximate):**  
  - `R_m = 6.10 ohms`, `R_a = +0.10` — a real resistor with small tolerance and mild heating

For **SSM**:

- Each quantity is represented as `(m,a)` with `a in (-1,+1)`.  
- Collapse rule: `phi((m,a)) = m` (drop the alignment lane, keep the magnitude).

**Our goal.**

- Use Ohm's law `V = I * R`.  
- Compare **Classical** voltage vs. **SSM** voltage `(m_V, a_V)`.

---

## **2) Classical calculation**

First, ignore alignment and just do the usual Ohm's law.

We average the two current readings and treat resistance as a scalar:

```python
# classical illustration (no external packages required)

I1 = 1.92  # amps
I2 = 1.98  # amps
R  = 6.10  # ohms

I_avg = 0.5 * (I1 + I2)
V     = I_avg * R
print(I_avg)  # 1.95
print(V)      # 11.895

```

**Classical result.**

- `I_avg = 1.95 A`
- `V = 11.895 V`

A typical lab report would say "`~11.9 V`", with no extra information about how stable this situation is.

---

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **SSM**, we:

1. Treat each measurement as `(m,a)` with `a in (-1,+1)`.
2. Compute an alignment for current using **sum pooling**:
   - `a_c := clamp(a, -1+eps, +1-eps)`
   - `u := atanh(a_c)`
   - `w := |m|^gamma`  (default `gamma = 1`)
   - `U += w * u`
   - `W += w`
   - `a_I_out := tanh( U / max(W, eps) )`
3. Combine the current alignment with the resistance alignment using a **product chaining rule** for the law `V = I * R`:
   - `a_V := tanh(atanh(a_I_out_c) + atanh(a_R_c))`
4. Keep the voltage magnitude as `m_V = I_avg * R_m` — **exactly the classical result**:
   - `phi((m_V, a_V)) = m_V = I_avg * R_m`

So:

- The magnitude is still `11.895 V`.  
- The bounded alignment lane `a_V` tells us how **stressed** or **calm** the `V = I * R` relationship is in this situation, given one **noisy** current reading and one **relatively calm** one.

**Intuition.**

- Because `I1` has high drift (`a ≈ +0.72` under drift-positive semantics) and `I2` is calmer (`a ≈ +0.05`), their pooled alignment `a_I_out` lands in a **moderate range**.  
- Combining this with a **mildly drifting** resistor (`R_a ≈ +0.10`) gives a voltage alignment `a_V` that is still moderate — not catastrophic, but certainly not **perfectly calm**.

---

## **4) Tiny script (copy-paste)**

Below is a small script implementing this logic in **ASCII-only Python**.

```python
# scenario_L01_ohms_law.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Ohm's law V = I * R
# current measurements (m, a) at two instants
I1_m, I1_a = 1.92, +0.72   # amps, noisy instant
I2_m, I2_a = 1.98, +0.05   # amps, calmer instant

# load resistance (m, a)
R_m,  R_a  = 6.10, +0.10   # ohms, mild drift

# 2) classical magnitude: average current, then V = I * R
I_avg = 0.5 * (I1_m + I2_m)
V_m   = I_avg * R_m

# 3) SSM alignments
a_I = ssm_align_weighted(
    [(I1_a, I1_m), (I2_a, I2_m)],
    gamma=1.0,
    eps=1e-12,
)

a_V = ssm_align_product(a_I, R_a, eps=1e-6)

print("Classical:", f"{V_m:.4f}")                 # 11.8950
print("SSM:", f"m={V_m:.4f}, a={a_V:+.4f}")       # a_V ~ +0.5173 (drift-positive)

```

You can later add **band assignment** in a runner script, for example:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed)

---

## **5) What to expect**

Running the script gives:

- `Classical: V ≈ 11.8950`  
- `SSM: m = 11.8950, a ≈ +0.52` (drift-positive semantics)

Under a simple band policy (for example, `|a| >= 0.50` → `A-`):

- `band = A-` (moderately stressed)

So:

- **Magnitude:** same as classical (`phi((m_V, a_V)) = m_V = 11.8950`).  
- **Posture:** clearly not calm; one reading is noisy enough that we treat this Ohm's law instance as “working, but in a stressed posture”.

If both current readings were calm and the resistor nearly ideal, we would see:

- `a_I ≈ 0`, `a_V ≈ 0`, and **SSM ≡ Classical** (same number, posture neutral).

---

## **6) Why this helps in the real world**

- Lab technicians and students can see that two “valid” currents (`1.92 A` and `1.98 A`) generating a seemingly neat voltage (`~11.9 V`) may still hide different levels of **stress** in the measurement setup.  
- Engineers can use `a` or its band to decide whether a given `V = I * R` condition is **calm enough to trust** for calibration, or whether they should re-measure, average longer, or adjust experimental conditions.  
- Dashboards can color identical voltage magnitudes differently using `a` or its band, improving **trust** and **interpretability** without changing any of the underlying arithmetic or the law itself.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

ohms-law • electrical-measurement • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • posture-lane • ssm-poc • getting-started
