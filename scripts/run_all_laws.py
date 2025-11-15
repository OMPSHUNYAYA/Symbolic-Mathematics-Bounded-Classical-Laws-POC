# run_all_laws.py  (ASCII-only)
# Runner for bounded classical law POCs (L01..L10)

import subprocess
import sys
import os


def classify_band(a):
    """Simple band policy based on |a|."""
    x = abs(a)
    if x < 0.20:
        return "A+ (calm)"
    elif x < 0.50:
        return "A0 (borderline)"
    else:
        return "A- (stressed)"


def parse_ssm_line(line):
    """
    Expect a line like:
        SSM: m=11.8950, a=+0.5173
    Returns (m, a) as floats, or (None, None) on failure.
    """
    try:
        if line.startswith("SSM:"):
            line = line[len("SSM:"):].strip()
        parts = [p.strip() for p in line.split(",")]
        m_part = [p for p in parts if p.startswith("m=")][0]
        a_part = [p for p in parts if p.startswith("a=")][0]
        m_val = float(m_part.split("=", 1)[1])
        a_val = float(a_part.split("=", 1)[1])
        return m_val, a_val
    except Exception:
        return None, None


def run_script(script_name):
    """Run one law scenario script and print a runner summary."""
    print(f"--- {script_name} ---")
    if not os.path.exists(script_name):
        print(f"[runner] ERROR: script not found: {script_name}")
        print()
        return

    proc = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True,
    )

    # Echo stdout
    if proc.stdout:
        print(proc.stdout.rstrip())

    # Echo stderr if any
    if proc.stderr:
        print("[runner] STDERR:")
        print(proc.stderr.rstrip())

    # Try to parse the SSM line
    m_val = None
    a_val = None
    for line in proc.stdout.splitlines():
        if line.startswith("SSM:"):
            m_val, a_val = parse_ssm_line(line)
            break

    if m_val is None or a_val is None:
        print("[runner] summary: could not parse SSM line.")
    else:
        band = classify_band(a_val)
        print(
            "[runner] summary:",
            f"m={m_val:.4f}, a={a_val:+.4f} [{band}]"
        )

    print()  # blank line


def main():
    all_scenarios = [
    "scenario_L01_ohms_law.py",
    "scenario_L02_newton_fma.py",
    "scenario_L03_hookes_law.py",
    "scenario_L04_ideal_gas_law.py",
    "scenario_L05_conservation_of_energy.py",
    "scenario_L06_conservation_of_momentum.py",
    "scenario_L07_bernoulli.py",
    "scenario_L08_snells_law.py",
    "scenario_L09_continuity_equation.py",
    "scenario_L10_faraday_induction.py",
]

    import sys
    if len(sys.argv) > 1:
        scenarios = sys.argv[1:]
    else:
        scenarios = all_scenarios

    print("Running bounded classical law scenarios...\n")
    for script in scenarios:
        run_script(script)


if __name__ == "__main__":
    main()
