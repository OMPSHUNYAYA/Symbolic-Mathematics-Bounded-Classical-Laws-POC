# **Getting Started — Law L10: Faraday's Law (Electromagnetic Induction, Bounded Classical Law POC)**

**Domain.** Electromagnetics / Generators / Lab Coil  

**Classical law.**

In its simplest form for a coil with `N` turns and changing magnetic flux `Phi`:

- `eps = -N * dPhi_dt`

For this POC we focus on the magnitude of induced EMF (ignore the sign):

- `|eps| = N * |dPhi_dt|`

with a finite-difference estimate:

- `dPhi_dt ≈ (Phi2 - Phi1) / dt`

---

**What this shows.**

In this law POC, we take Faraday's Law of Electromagnetic Induction and show how:

- The Classical calculation gives the scalar EMF `|eps|` induced in a coil, and  
- The Shunyaya Symbolic Mathematics (SSM) version keeps that EMF magnitude intact but adds a bounded alignment lane `a in (-1,+1)`, indicating whether this particular `eps = -N * dPhi_dt` situation is **calm**, **borderline**, or **stressed**.

When:

- The coil speed is steady,  
- Flux measurements are clean, and  
- Timing is sharp,  

Shunyaya Symbolic Mathematics (SSM) collapses to the Classical result and you effectively get the same answer.

But in real labs and machines, `dPhi_dt` is notoriously noisy:

- Jerky coil motion or shaft non-uniformity,  
- Flux probe jitter,  
- Coarse timing marks.  

The alignment lane `a` and its band reveal **posture** that the classical scalar EMF alone cannot show.

**POC display policy (simple).**

For this POC, we use:

- `a_semantics = "drift-positive"`

so larger printed `a` means more drift / more risk. This is a display choice only; you can flip semantics without changing the math or `phi((m,a)) = m`.

---

## **1) Setup (inputs)**

Imagine a lab induction coil near a changing magnetic field:

- A coil with known turns sits near a rotating magnet.  
- You sample the magnetic flux through the coil twice, a short time apart.  
- You estimate the induced EMF using a finite difference.

We model:

- **Number of turns (reasonably well known):**  
  - `N_m = 200`, `N_a = +0.02` — coil turns counted and archived; small uncertainty.

- **Flux samples (two instants):**  
  - `Phi1_m = 0.012 Wb`, `Phi1_a = +0.60` — first reading, coil still speeding up / probe noisy  
  - `Phi2_m = 0.004 Wb`, `Phi2_a = +0.25` — second reading, a bit steadier  

- **Sampling time interval:**  
  - `dt_m = 0.040 s`, `dt_a = +0.10` — timing from scope or controller, modest jitter  

In SSM:

- Each physical quantity is two-lane: `(m, a)` with `a in (-1,+1)`.  
- Collapse parity is `phi((m,a)) = m` — drop the alignment lane, keep the magnitude.

**Our target.**

- Compute classical EMF from the two flux samples, then  
- Wrap it as `(m_eps, a_eps)` with a meaningful bounded alignment lane.

---

## **2) Classical calculation**

Ignoring alignment, use a simple two-point estimate of `dPhi_dt`:

```python
# classical illustration (no external packages required)

N    = 200      # turns
Phi1 = 0.012    # Wb
Phi2 = 0.004    # Wb
dt   = 0.040    # s

dPhi_dt = (Phi2 - Phi1) / dt
eps_mag = N * abs(dPhi_dt)

print(dPhi_dt)   # -0.200 Wb/s
print(eps_mag)   # 40.0 V

```

Classical result.

dPhi_dt ≈ -0.200 Wb/s
|eps|   ≈ 40.0 V

A typical lab note might simply say:
“Induced EMF ≈ 40 V at this speed.”

There is no explicit distinction between:
• 40 V from a clean, smooth spin, and
• 40 V from a jerky, poorly timed, noisy flux measurement.

## **3) SSM calculation (same EMF magnitude + bounded alignment lane)**

In Shunyaya Symbolic Mathematics (SSM), we:

1. Treat each flux sample as `(m,a)` and build a flux-change alignment for  
   `DeltaPhi = Phi2 - Phi1`.

   Conceptually:

   - `DeltaPhi = Phi2 - Phi1`  

   For posture, both samples matter. We combine their lanes via a sum of rapidities:

   - `a_DeltaPhi := tanh(atanh(a_Phi1_c) + atanh(a_Phi2_c))`

2. Treat the time interval as `(dt_m, dt_a)` and build an alignment for  
   `dPhi_dt = DeltaPhi / dt` using a division rule:

   - `a_dPhi_dt := tanh(atanh(a_DeltaPhi_c) - atanh(a_dt_c))`

3. Combine the turns lane and derivative lane to get the EMF lane:

   - `a_eps := tanh(atanh(a_N_c) + atanh(a_dPhi_dt_c))`

4. Keep the EMF magnitude as the classical value `eps_mag_m`:

   - `eps_mag_m = N_m * abs((Phi2_m - Phi1_m) / dt_m)`  
   - `phi((eps_mag_m, a_eps)) = eps_mag_m`

So:

- The induced EMF magnitude remains `≈ 40 V`.  
- The bounded alignment lane `a_eps` tells you whether that `40 V` comes from steady, well-resolved induction or noisy, jerky induction.

---

## **4) Tiny script (copy-paste)**

```python
# scenario_L10_faraday_induction.py  (ASCII-only, top-level prints)

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

# 1) law-specific inputs: Faraday's law |eps| = N * |dPhi_dt|
# with dPhi_dt ≈ (Phi2 - Phi1) / dt

# number of turns (m, a)
N_m, N_a = 200, +0.02    # turns

# flux samples (m, a)
Phi1_m, Phi1_a = 0.012, +0.60   # Wb, noisy first sample
Phi2_m, Phi2_a = 0.004, +0.25   # Wb, calmer second sample

# time interval (m, a)
dt_m, dt_a = 0.040, +0.10       # s

# 2) classical magnitudes

dPhi_dt_m = (Phi2_m - Phi1_m) / dt_m
eps_mag_m = N_m * abs(dPhi_dt_m)

# 3) SSM alignments

# lane for DeltaPhi from two flux samples
a_dPhi = ssm_align_sum([Phi1_a, Phi2_a])

# lane for dPhi/dt = DeltaPhi / dt
a_dPhi_dt = ssm_align_div(a_dPhi, dt_a, eps=1e-6)

# EMF alignment from N * dPhi/dt
a_eps = ssm_align_sum([N_a, a_dPhi_dt])

print("Classical:")
print("  dPhi/dt ~", f"{dPhi_dt_m:.3f}", "Wb/s")
print("  |eps|   =", f"{eps_mag_m:.2f}", "V")

print("SSM (induced EMF lane):")
print("  |eps| =", f"m={eps_mag_m:.2f}, a={a_eps:+.4f}")

```

Later, your shared runner can assign bands, e.g.:

- `|a| < 0.20` → `A+` (calm induction snapshot)  
- `0.20 <= |a| < 0.50` → `A0` (borderline)  
- `|a| >= 0.50` → `A-` (stressed / noisy induction)

## **5) What to expect**

Numerically:

- Classical:  
  - `dPhi_dt ≈ -0.200 Wb/s`  
  - `|eps| ≈ 40.0 V`  

- SSM (induced EMF lane):  
  - `m = 40.0 V` (same as classical)  
  - `a_eps` will be **fairly large positive** (due to a very noisy first flux sample and a shaky `dt`).

Under the sample band policy, you will typically see:

- `a_eps` in `A-` (stressed) — indicating that although the EMF value is numerically reasonable, it comes from a noisy `dPhi_dt` estimate.

If you improved the setup:

- Smoother mechanical motion,  
- More stable flux probe (smaller `Phi1_a`, `Phi2_a`),  
- Better timing (smaller `dt_a`),  

then:

- `a_dPhi` and `a_dPhi_dt` would shrink toward `0`,  
- `a_eps` would move toward `0`,  

and the same `~40 V` would now appear as a **calmer, more trustworthy** EMF measurement.

---

## **6) Why this helps in the real world**

- Generator designers can distinguish between EMF outputs that come from **smooth, well-controlled operation** and those that come from **jerky, noisy operating points**, even when the RMS voltages look similar.  
- Lab experiments on induction can show students that `dPhi_dt` measurements are often the **weakest link**, and SSM makes that visible via `a`.  
- Condition monitoring could use `a_eps` as a simple lane for **operational posture**, highlighting when induced voltages look fine but are rooted in unstable flux dynamics.

---

## **7) License and scope**

- **License.** `CC BY-NC 4.0` (non-commercial, attribution required).  
- **Scope.** Observation-only; not for critical use.

This POC is for thinking, experimentation, and education around bounded classical laws. It is not a safety case, design guarantee, or regulatory tool.

---
