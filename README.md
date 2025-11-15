# **Shunyaya Symbolic Mathematics (SSM) — Bounded Classical Laws — Proof of Concept**

![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue?style=flat&logo=creative-commons) ![GitHub Stars](https://img.shields.io/github/stars/OMPSHUNYAYA/Symbolic-Mathematics-Bounded-Classical-Laws-POC?style=flat&logo=github) ![CI](https://github.com/OMPSHUNYAYA/Symbolic-Mathematics-Bounded-Classical-Laws-POC/actions/workflows/run_all_laws.yml/badge.svg)

**Tiny Python examples that apply Shunyaya Symbolic Mathematics to popular classical laws, keeping `m` the same while adding a bounded posture lane `a in (-1,+1)` (calm / borderline / stressed).**

---

## **Potential impact (observation-only)**

Classical laws can tell you not only **what number** they produce, but also **how calmly** they are being satisfied in a given situation.

By extending classical values from `m` to `(m,a)` with `a in (-1,+1)`, SSM keeps the usual results intact while adding a human-readable sense of posture (stable, drifting, unreliable). In simple terms, this can support:

- Fewer surprises in devices and field systems  
- Calmer, faster experimentation in labs  
- Clearer safety margins in mechanical and electrical design  
- Steadier operational decisions, separating law correctness from situational stress  

These are **simple, reproducible examples**; all results are **observation-only** and must be independently validated before any production or critical use.

---

## **SSM one-line primer**

Extend numbers from `m` to `(m,a)` with `a in (-1,+1)` and **collapse parity**:

`phi((m,a)) = m`

The classical value is always preserved.  
SSM simply adds a bounded alignment / posture lane `a` beside it.

---

## **SSMS one-line primer**

**Shunyaya Symbolic Mathematical Symbols (SSMS)** is a shared, plain-text symbolic layer where classical operators (`+`, `-`, `*`, `/`) lift to structured, alignment-preserving verbs.

This keeps formulas:

- **Portable** across documentation, code, and hardware  
- **Unambiguous**, even when we add posture `a`  
- **Consistent**, so the same ASCII formula means the same thing everywhere

---

## **What this repository contains**

This repository is a **bounded classical laws POC**:

- Each law keeps its **classical formula** intact  
- The same law is then **lifted** into SSM / SSMS form  
- A tiny Python script prints **Classical vs SSM** side-by-side  
- A short explanation shows how the alignment lane `a` helps reasoning

Each law is a **bounded conservative extension**:

- The underlying physics remains unchanged  
- `phi((m,a)) = m` ensures classical magnitudes are preserved  
- The alignment lane `a` reports how **calm vs stressed** this particular instance appears  

**Laws currently covered:**

- Ohm’s Law  
- Newton’s Second Law  
- Hooke’s Law  
- Ideal Gas Law  
- Conservation of Energy  
- Conservation of Momentum  
- Bernoulli’s Equation  
- Snell’s Law  
- Continuity (incompressible flow)  
- Faraday’s Law (electromagnetic induction)  

The `getting_started/` directory lists the currently implemented laws and walks through each one.

---

## **How to navigate**

- This **README** introduces the concept and lists the laws.
- Each **Getting Started — Law LXX** page:
  - States the classical law in plain ASCII
  - Shows the SSM / SSMS-lifted form
  - Explains the meaning of the alignment lane `a`
- Each **scenario script** prints:
  - Classical result
  - SSM result `(m,a)`
  - A band label (`A+`, `A0`, `A-`) indicating calm vs stressed posture

**Typical reading flow:**

- When both methods agree → “Classically OK and posture calm.”  
- When posture disagrees → we explain why SSM surfaces useful information that classical arithmetic alone cannot (without changing the physics).

---

## **Formulas and pooling rules (ASCII-only)**

All scripts use the same tiny set of SSM helper formulas for the alignment lane `a`.

### **Clamp and defaults**

```text
eps_a := 1e-6
eps_w := 1e-12
gamma := 1

clamp_a(z, eps_a) := max(-1+eps_a, min(+1-eps_a, z))

```

### **Sum pooling (alignment lane)**

Used when combining multiple contributions (for example, multiple readings of the same quantity):

```text
# inputs: (m_i, a_i) for i = 1..N

a_i_c := clamp_a(a_i, eps_a)
u_i   := atanh(a_i_c)
w_i   := |m_i|^gamma

U := SUM_i (w_i * u_i)
W := SUM_i (w_i)

m_out := SUM_i m_i
a_out := tanh( U / max(W, eps_w) )

```

### **Product and division (alignment lane)**

Used in laws like `V = I * R`, `P = V * I`, or when forming ratios:

```text
# Product chaining
(m1,a1) * (m2,a2) :=
(
  m1*m2,
  tanh( atanh(a1) + atanh(a2) )
)

# Division chaining
(m1,a1) / (m2,a2) :=
(
  m1/m2,
  tanh( atanh(a1) - atanh(a2) )
)

```

Magnitudes follow the usual arithmetic; only the posture lane `a` changes to reflect how stable or shaky the combined quantity is.

## **How subtraction and division affect alignment**

To make the extensions intuitive:

- **Subtraction amplifies drift when terms oppose.**  
  If `(m1,a1)` is calm but `(m2,a2)` is shaky, the difference inherits the shakier posture.

- **Division behaves like a difference of rapidities.**  
  Opposing lane signs in numerator and denominator increase `|a|`, revealing unstable ratios.

These behaviors match the SSMS treatment of `s_sum`, `s_diff`, and `s_div`.

## **Relation to SSMS operators**

The POC helper functions correspond directly to SSMS primitives:

- `ssm_align_product` → analogous to `s_mul`  
- `ssm_align_sum` → analogous to `s_sum`  
- `ssm_align_div` → analogous to `s_div`  
- Posture semantics (`a_semantics = "drift-positive"` or `"stability-positive"`) are display-layer only.

The underlying two-lane math is invariant.

## **How to derive `a` from real data (optional hook)**

These POCs use hand-assigned `a` values, but real deployments can compute `a` from:

- Time-series variance or jitter (e.g., window variance of `I(t)` or `V(t)`)
- Across-trial variability (e.g., consistency of repeated `F = m * a` measurements)
- Residual drift (difference between theoretical vs observed law balance)

Once computed, real-world `a` values can flow directly into other Shunyaya components (SSM-Audit, SSMDE, dashboards).

## **How to run everything (one command)**

**Prerequisite:** Python 3.10+

From the repository root:

```text
python scripts/run_all_laws.py
```

## **Law POC template (consistent)**

Each Law POC contains:

1. Classical law + units  
2. SSM / SSMS-lifted form (ASCII)  
3. Micro-scenario with checkable numbers  
4. Python script printing Classical and SSM `(m,a)`  
5. Interpretation: what the band means here  

**Shared knobs:**

```text
eps_a      := 1e-6
eps_w      := 1e-12
gamma      := 1
a_semantics := "stability-positive" or "drift-positive"

```

**Rules:**

```text
a_out := tanh( U / max(W, eps_w) )
a_out := tanh( atanh(a1) + atanh(a2) )
phi((m,a)) = m

```

This keeps the law intact while surfacing posture.

## **Safety and scope**

- Observation-only: not a safety case or approval mechanism  
- Reproducible: tiny scripts, ASCII formulas  
- Portable: same meaning across docs, code, and hardware  
- Respectful of classical laws: SSM never alters the physics; it only adds a bounded lens on top

**License.** CC BY-NC 4.0 • Observation-only; not for critical use.
