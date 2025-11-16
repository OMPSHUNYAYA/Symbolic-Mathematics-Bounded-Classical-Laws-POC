# **Getting Started — Law L05: Conservation of Energy (Bounded Classical Law POC)**

**Domain.** Energy Balance / Small Machines / Lab Bench  

**Classical law.** `E_in = E_out + E_loss`

**What this shows**

In this law POC, we take a simple **Conservation of Energy** balance and show how:

- The **Classical** calculation gives a consistent scalar energy loss `E_loss`, and  
- The **Shunyaya Symbolic Mathematics (SSM)** version keeps that loss magnitude intact but adds a **bounded alignment lane** `a in (-1,+1)`, indicating whether this particular `E_in = E_out + E_loss` situation is **calm**, **borderline**, or **stressed**.

When input power, output work, and loss estimates are all well-behaved, SSM collapses to Classical and you effectively get the same answer.

When measurements are noisy (supply jitter, jerky motion, crude loss estimation), the alignment lane `a` and its band surface posture that the classical scalar `E_loss` alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

## **1) Setup (inputs)**

Imagine a **small DC motor** on a lab bench lifting a weight:

- A `12 V` supply powers the motor through a simple driver.  
- You measure **current twice** over a short lift.  
- You know approximately how far a weight is lifted.  
- From that, you estimate **input energy**, **useful output work**, and **losses** (heat, sound, friction).

We model:

- **Supply voltage (approximate but steady):**  
  - `V_m = 12.0 V`, `V_a = +0.10` — decent bench supply, mild uncertainty.

- **Current measurements (instantaneous, motor start and near steady-state):**  
  - `I1_m = 1.80 A`, `I1_a = +0.70` — jerkier start, higher jitter.  
  - `I2_m = 1.60 A`, `I2_a = +0.15` — later, more stable.

- **Lift time:**  
  - `t_m = 3.0 s`, `t_a = +0.05` — stopwatch and control timing are reasonably good.

- **Lifted weight and height (useful mechanical output):**  
  - `m_load_m = 2.0 kg`, `m_load_a = +0.05` — small mass uncertainty.  
  - `h_m = 0.50 m`, `h_a = +0.10` — tape measure + eye estimate.

We will look at:

- Input energy from the supply: `E_in = V * I_avg * t`  
- Useful mechanical output: `E_out = m_load * g * h` (with `g ≈ 9.81 m/s^2`)  
- Energy loss (by conservation): `E_loss = E_in - E_out`

## **2) Classical calculation**

First, ignore alignment and do an ordinary energy balance:

```python
# classical illustration (no external packages required)

V   = 12.0      # volts
I1  = 1.80      # amps
I2  = 1.60      # amps
t   = 3.0       # seconds

m_load = 2.0    # kg
h      = 0.50   # m
g      = 9.81   # m/s^2

I_avg   = 0.5 * (I1 + I2)
E_in    = V * I_avg * t             # input electrical energy
E_out   = m_load * g * h            # useful mechanical energy
E_loss  = E_in - E_out              # everything else (heat, noise, friction)

print(I_avg)   # 1.70 A
print(E_in)    # 61.2 J
print(E_out)   # 9.81 J
print(E_loss)  # 51.39 J

```

**Classical result.**

- `I_avg = 1.70 A`  
- `E_in ≈ 61.20 J`  
- `E_out ≈ 9.81 J`  
- `E_loss ≈ 51.39 J`  

A normal lab sheet might simply say:  
**"Input ≈ 61 J, output ≈ 9.8 J, losses ≈ 51 J (≈84% losses)."**

There is no explicit distinction between **clean, trustworthy measurements** and **borderline, noisy ones**.

## **3) SSM calculation (same magnitude + bounded alignment lane)**

In **Shunyaya Symbolic Mathematics (SSM)**, we:

1. Treat all relevant quantities as `(m,a)` with `a in (-1,+1)`.

2. Pool the **current alignment** from the two samples using the weighted rule:

   - `a_c := clamp(a, -1+eps, +1-eps)`  
   - `u := atanh(a_c)`  
   - `w := |m|^gamma`  (default `gamma = 1`)  
   - `U += w * u`  
   - `W += w`  
   - `a_I_out := tanh( U / max(W, eps) )`

3. Combine `V`, `I_avg`, and `t` to get the **input energy alignment** `a_Ein` using a product-style (sum-of-rapidities) rule:

   - `a_Ein := tanh(atanh(a_V_c) + atanh(a_I_out_c) + atanh(a_t_c))`

4. Combine `m_load`, `g`, and `h` to get the **output energy alignment** `a_Eout`:

   - `a_Eout := tanh(atanh(a_m_c) + atanh(a_g_c) + atanh(a_h_c))`  

   Here we treat `g` as effectively exact, so `a_g = 0`.

5. Compute the **scalar loss** classically (same as before):

   - `m_E_loss = E_in - E_out`

6. For this POC, define a simple SSM rule for the **loss alignment**:

   - `a_E_loss := tanh(atanh(a_Ein_c) + atanh(a_Eout_c))`

   *Intuition:* if either side of the energy balance is shaky, the loss lane should carry that shakiness.

7. Collapse parity remains:

   - `phi((m_E_loss, a_E_loss)) = m_E_loss`

So:

- The magnitude of losses is still `≈ 51.39 J`.  
- The bounded alignment lane `a_E_loss` reports how **“firm” or “soft”** that loss figure is, given the **noisy supply** and **approximate output measurements**.

## **4) Tiny script (copy-paste)**

Below is a small script implementing this Conservation of Energy POC in **ASCII-only Python**.

```python
# scenario_L05_conservation_of_energy.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Conservation of Energy
# E_in = E_out + E_loss, solve for E_loss

# supply voltage (m, a)
V_m, V_a = 12.0, +0.10     # volts

# current measurements (m, a)
I1_m, I1_a = 1.80, +0.70   # amps, noisy start
I2_m, I2_a = 1.60, +0.15   # amps, calmer

# time (m, a)
t_m, t_a = 3.0, +0.05      # seconds

# load mass and height (m, a)
m_load_m, m_load_a = 2.0, +0.05   # kg
h_m,      h_a       = 0.50, +0.10 # m

# gravitational acceleration (m, a)
g_m, g_a = 9.81, 0.0       # m/s^2, treated as exact

# 2) classical magnitudes

I_avg_m  = 0.5 * (I1_m + I2_m)
E_in_m   = V_m * I_avg_m * t_m      # input electrical energy

E_out_m  = m_load_m * g_m * h_m     # useful mechanical energy
E_loss_m = E_in_m - E_out_m         # classical loss

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

```

You can attach a **band** in the shared runner, for example:

- `|a| < 0.20` → `A+` (calm energy balance)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed / shaky balance)

## **5) What to expect**

Numerically:

- **Classical:**  
  - `E_in ≈ 61.20 J`  
  - `E_out ≈ 9.81 J`  
  - `E_loss ≈ 51.39 J`

- **SSM (loss lane):**  
  - `E_loss = 51.39 J` (same magnitude)  
  - `a_Eloss ≈ +0.6810` under drift-positive semantics

Under the sample band policy:

- `|a| < 0.20` → `A+` (calm)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A−` (stressed / shaky balance)

we get:

- `a_Eloss ≈ +0.6810` → **A− (stressed)**.

**Interpretation.**

The energy balance closes numerically, but the bounded alignment lane reveals that it was computed from:

- a **noisy supply current**,  
- an **approximate lift height**,  
- an **approximate mass**.

So the headline loss (`≈ 51 J`) should be treated as **posturally shaky**, not a crisp calibration number.

If the motor current, timing, and geometry were recorded with lower drift, you would see:

- `a_Eloss` move closer to `0`,  
- the same classical loss appearing as **calmer and more reliable**.

## **6) Why this helps in the real world**

- **R&D teams evaluating small machines** can separate **“losses we trust”** from **“losses that are numerically plausible but measurement-noisy”**, using the bounded alignment lane on `E_loss`.  
- **Test benches** can color identical loss values differently by `a` or by band, pointing engineers toward trials that deserve **deeper investigation or repeat runs**.  
- **Teaching labs** can demonstrate that conservation of energy is not just about numbers adding up, but also about how **stable and trustworthy** the underlying measurements are — exactly what SSM makes visible.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is intended for **thinking**, **experimentation**, and **education** around bounded classical laws. It is **not** a safety case, design guarantee, or regulatory tool.

---

## **Topics**

conservation-of-energy • energy-balance • small-machines • dc-motor-lift • classical-vs-ssm • stability-lane • drift-awareness • symbolic-math • plain-ascii-formulas • posture-lane • ssm-poc • getting-started
