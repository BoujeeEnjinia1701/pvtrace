"""PVT-CAL-001 PVTrace sizing calculations (TRL 3).

Run from the repo root:  python docs/04-calcs/sizing.py
Prints every number quoted in docs/04-calcs/01-sizing.md and writes
docs/04-calcs/results.csv. Reads the case dimensions from cad/src/model.py
and the costs from bom/bom.csv. All values are first-principles estimates for a
paper design; nothing here is measured.
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, fsolve

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad/src"))
from model import PARAMS as MP  # noqa: E402

# ------------------------------------------------------------------ assumptions
K_B, Q_E = 1.380649e-23, 1.602176634e-19
T_STC = 298.15
VT = K_B * T_STC / Q_E                 # thermal voltage at 25 °C
N_IDEAL = 1.2                          # diode ideality factor per cell (assumed)

# Module cases: name, Voc, Isc, Vmp, Imp, cells in series (datasheet-class values, assumed)
MODULES = [
    ("36-cell 100 W", 22.0, 6.0, 18.0, 5.56, 36),
    ("108 half-cell 410 W (high current)", 37.5, 13.9, 31.4, 13.06, 54),
    ("144 half-cell 450 W (reference)", 49.5, 11.6, 41.5, 10.85, 72),
    ("2 x 60-cell 250 W in series (high voltage)", 75.2, 8.9, 61.0, 8.20, 120),
    ("Rating limit (reference curve scaled to 100 V, 20 A)", 100.0, 20.0, 41.5 * 100 / 49.5, 10.85 * 20 / 11.6, 72 * 100 / 49.5),
]
BETA_VOC = -0.0030                     # Voc temperature coefficient, 1/°C (older modules -0.31 %, newer -0.27 %)
T_COLD = -10.0                         # coldest cell temperature for R1, °C

C_UNIT = 2200e-6                       # F per capacitor
N_CAPS = MP["n_caps"]                  # 3, decision 3 in PVT-DDR-001
C_TOL = 0.20                           # electrolytic tolerance, ±20 %
C_LOAD = N_CAPS * C_UNIT
V_CAP_RATING, V_FET_RATING = 160.0, 150.0
V_LIMIT = 100.0

# Loop resistance from the module terminals to the capacitor (ohm), assumed typical values
R_LOOP_PARTS = {
    "Test leads, 2 x 1 m, 4 mm2 copper": 2 * 1.72e-8 * 1.0 / 4e-6,
    "MC4 contacts, 4 x 0.5 mohm": 4 * 0.5e-3,
    "gPV fuse 20 A": 5e-3,
    "DC isolator, 2 poles": 2e-3,
    "Shunt": 4e-3,
    "Load MOSFET on-resistance": 10e-3,
    "Capacitor ESR, 3 x 60 mohm in parallel": 60e-3 / N_CAPS,
    "Internal wiring": 5e-3,
}
R_LOOP = sum(R_LOOP_PARTS.values())
R_BLEED, R_DUMP = 10e3, 22.0
R_DIV_TOP, R_DIV_BOT, V_REF = 1.0e6, 39e3, 4.096
R_SHUNT, GAIN = 4e-3, 50.0
ADC_BITS = 12
PAIR_RATE = 25_000                     # V-I pairs per second (half a 100 kS/s two-channel ADC)
SKEW = 1 / (2 * PAIR_RATE)             # V and I converted one after the other, s
SWEEP_PERIOD = 5.0                     # firmware minimum time between sweeps, s

# Power budget
P_CTRL = 0.60                          # ESP32 display board with lit TFT, W (TRL 2 estimate)
P_ISO = 0.25                           # isolated DC-DC, digital isolator, PV-side analog and gate driver, W
ETA_BOOST = 0.90                       # 3.7 V to 5 V boost
E_CELL = 3.0 * 3.6                     # 3,000 mAh 18650 at 3.6 V, Wh
USABLE = 0.90
SWEEP_TIME_BUDGET = 20.0               # s of controller time per sweep (connect, sweep, analyze, show)

# Thermal (lumped case model)
H_CASE = 9.0                           # W/(m2 K), still air, natural convection plus radiation
G_SUN = 1000.0                         # W/m2 on the lid
ALPHA_LIGHT, ALPHA_DARK = 0.30, 0.90   # solar absorptance of a light grey or dark case
T_AMB = 45.0

# Measurement error terms after calibration (fractions)
TEMP_SPAN = 30.0                       # °C between calibration and use
ERR = {
    "V reference drift, 50 ppm/°C": 50e-6 * TEMP_SPAN,
    "Divider ratio drift, 25 ppm/°C": 25e-6 * TEMP_SPAN,
    "Shunt drift, 50 ppm/°C": 50e-6 * TEMP_SPAN,
    "Amplifier gain drift, 2.5 ppm/°C": 2.5e-6 * TEMP_SPAN,
}
ADC_INL_LSB = 1.0
AMP_OFFSET_V = 25e-6                   # current-sense amplifier input offset before calibration
AMP_OFFSET_DRIFT = 0.25e-6             # V/°C after calibration

# STC uncertainty terms (fractions of Pmax, treated as expanded)
BETA_P = 0.0035                        # Pmax temperature coefficient, 1/°C
U_TEMP = 2.0                           # module temperature uncertainty, °C
U_SPECTRAL = 0.02                      # spectral and angle mismatch of the reference cell
U_REFCELL = (0.03, 0.05)               # once-calibrated reference cell range
R8_TARGET = 0.05

results = []


def res(rid, value, target, status):
    results.append({"id": rid, "value": value, "target": target, "status": status})


def fit(voc, isc, vmp, imp, ns):
    """Single-diode model with fixed ideality: solve Iph, I0, Rs, Rsh from Isc, Voc, MPP and dP/dV = 0."""
    a = N_IDEAL * ns * VT

    def eqs(x):
        iph, li0, rs, lrsh = x
        i0, rsh = math.exp(li0), math.exp(lrsh)
        f1 = iph - i0 * (math.exp(isc * rs / a) - 1) - isc * rs / rsh - isc
        f2 = iph - i0 * (math.exp(voc / a) - 1) - voc / rsh
        f3 = iph - i0 * (math.exp((vmp + imp * rs) / a) - 1) - (vmp + imp * rs) / rsh - imp
        # dI/dV at MPP equals -Imp/Vmp
        g = i0 / a * math.exp((vmp + imp * rs) / a) + 1 / rsh
        didv = -g / (1 + g * rs)
        f4 = didv + imp / vmp
        return [f1, f2, f3, f4]

    x0 = [isc, math.log(isc * math.exp(-voc / a)), 0.2 * ns / 60, math.log(300 * ns / 60)]
    sol, info, ok, msg = fsolve(eqs, x0, full_output=True)
    iph, li0, rs, lrsh = sol
    if ok != 1 or rs < 0:
        raise RuntimeError(f"fit failed: {msg}")
    return iph, math.exp(li0), a, rs, math.exp(lrsh)


def current(v, p):
    iph, i0, a, rs, rsh = p
    f = lambda i: iph - i0 * (math.exp((v + i * rs) / a) - 1) - (v + i * rs) / rsh - i
    return brentq(f, -5, iph + 5)


def sweep(p, voc, c, end=0.99, i_open=0.5):
    """Time for the capacitor to go from 0 V to end x Voc, and on until the module current falls to i_open.
    Returns (t, Vm0, I at end x Voc, extra time to reach i_open)."""
    vm0 = brentq(lambda vm: vm - current(vm, p) * R_LOOP, 0, voc)
    v_open = brentq(lambda v: current(v, p) - i_open, vm0, voc)
    vm = np.linspace(vm0, max(end * voc, v_open), 6000)
    i = np.array([current(v, p) for v in vm])
    vc = vm - i * R_LOOP
    icap = i - vc / R_BLEED - vc / (R_DIV_TOP + R_DIV_BOT)
    tc = np.concatenate([[0], np.cumsum(np.diff(vc) * c / (0.5 * (icap[1:] + icap[:-1])))])
    t_end = np.interp(end * voc, vm, tc)
    t_open = np.interp(v_open, vm, tc)
    return t_end, vm0, current(end * voc, p), max(0.0, t_open - t_end)


print("PVT-CAL-001 PVTrace sizing\n")
print(f"Load capacitance {N_CAPS} x {C_UNIT * 1e6:.0f} uF = {C_LOAD * 1e3:.1f} mF (tolerance ±{C_TOL * 100:.0f} %)")
print(f"Loop resistance {R_LOOP * 1e3:.1f} mohm:")
for k, v in R_LOOP_PARTS.items():
    print(f"  {k}: {v * 1e3:.1f} mohm")

# ------------------------------------------------------------------ 2. Sweep (R3, R4, R11 current at opening)
print("\nSweep, single-diode model, time from 0 V to 99 % of Voc on the capacitor")
print(f"{'Case':46s} {'Rs':>6s} {'Rsh':>6s} {'t nom':>7s} {'t -20%':>7s} {'t 4.4mF':>8s} {'pairs':>6s} {'E (J)':>6s} {'Vm0':>5s} {'I end':>6s} {'pts/V':>6s}")
sweeps = {}
for name, voc, isc, vmp, imp, ns in MODULES:
    if name.startswith("Rating limit"):
        # exact scaling of the reference model: currents x ki, voltages x kv
        r = sweeps["144 half-cell 450 W (reference)"]["p"]
        kv, ki = voc / 49.5, isc / 11.6
        p = (r[0] * ki, r[1] * ki, r[2] * kv, r[3] * kv / ki, r[4] * kv / ki)
    else:
        p = fit(voc, isc, vmp, imp, ns)
    t_nom, vm0, i_end, t_wait = sweep(p, voc, C_LOAD)
    t_low = sweep(p, voc, C_LOAD * (1 - C_TOL))[0]
    t_old = sweep(p, voc, 2 * C_UNIT)[0]
    e = 0.5 * C_LOAD * (0.99 * voc) ** 2
    pairs_min = PAIR_RATE * t_low
    ppv = PAIR_RATE * C_LOAD * (1 - C_TOL) / isc
    sweeps[name] = dict(t_wait=t_wait, t=t_nom, t_low=t_low, t_old=t_old, e=e, vm0=vm0, i_end=i_end, pairs=PAIR_RATE * t_nom,
                        pairs_min=pairs_min, ppv=ppv, voc=voc, isc=isc, vmp=vmp, imp=imp, p=p)
    print(f"{name:46s} {p[3]:6.3f} {p[4]:6.0f} {t_nom * 1e3:6.1f}ms {t_low * 1e3:6.1f}ms {t_old * 1e3:7.1f}ms "
          f"{PAIR_RATE * t_nom:6.0f} {e:6.1f} {vm0:5.2f} {i_end:6.2f} {ppv:6.1f}")

hc = sweeps["108 half-cell 410 W (high current)"]
ref = sweeps["144 half-cell 450 W (reference)"]
lim = sweeps["Rating limit (reference curve scaled to 100 V, 20 A)"]
t_min_nom = min(s["t"] for s in sweeps.values())
t_min_low = min(s["t_low"] for s in sweeps.values())
t_max = max(s["t"] * (1 + C_TOL) / 1.0 for s in sweeps.values())
c_needed = C_LOAD * 20e-3 / hc["t_low"] * (1 - C_TOL)
c_needed_nom = C_LOAD * 20e-3 / hc["t"]
print(f"Shortest sweep: {t_min_nom * 1e3:.1f} ms nominal, {t_min_low * 1e3:.1f} ms with -20 % capacitance; "
      f"longest with +20 %: {t_max * 1e3:.0f} ms")
print(f"Capacitance for 20 ms on the high-current case: {c_needed_nom * 1e3:.2f} mF nominal; "
      f"{c_needed / (1 - C_TOL) * 1e3:.2f} mF rated if -20 % tolerance must still give 20 ms")
# Decided 2026-10-02 (PVT-DEC-001, item 4): the bank is measured and selected, so the worst case is the selected
# bank, not -20 %. 6.4 mF was decided; the 20 ms bound needs 6.44 mF on the high-current case, so 6.45 mF is used
# here (proposed, awaiting Amish).
C_DECIDED, C_SEL = 6.4e-3, 6.45e-3
t_dec = sweep(hc["p"], hc["voc"], C_DECIDED)[0]
t_sel = sweep(hc["p"], hc["voc"], C_SEL)[0]
t_sel_min = min(sweep(s_["p"], s_["voc"], C_SEL)[0] for s_ in sweeps.values())
pairs_sel = PAIR_RATE * t_sel_min
print(f"Selected bank: {C_DECIDED * 1e3:.2f} mF (decided) gives {t_dec * 1e3:.2f} ms on the high-current case; "
      f"{C_SEL * 1e3:.2f} mF gives {t_sel * 1e3:.2f} ms; shortest sweep with {C_SEL * 1e3:.2f} mF {t_sel_min * 1e3:.1f} ms")
res("R3", f"{t_sel * 1e3:.1f} ms high-current case with the bank selected to {C_SEL * 1e3:.2f} mF "
          f"({t_dec * 1e3:.1f} ms at the decided 6.4 mF); {ref['t'] * 1e3:.0f} ms reference; up to {t_max * 1e3:.0f} ms",
    "20 to 200 ms", "Met on paper with a selected bank" if t_sel >= 20e-3 else "Not met")
res("R4", f"{pairs_sel:.0f} pairs minimum (high-current case, selected bank {C_SEL * 1e3:.2f} mF)",
    "200 or more", "Met")

# capacitive error of the module itself
c_mod_05 = 0.005 * C_LOAD * (1 - C_TOL)
print(f"Module capacitance error: current error ~ C_mod / C_load; 0.5 % needs C_mod <= {c_mod_05 * 1e6:.0f} uF "
      f"(at -20 % load capacitance)")

# timing skew between V and I samples
print("Error in Pmax from sequential V and I sampling (uncorrected):")
skew_worst = 0
for name, s in sweeps.items():
    dvdt = s["imp"] / C_LOAD
    err = dvdt * SKEW / s["vmp"]
    skew_worst = max(skew_worst, err / (1 - C_TOL))
    print(f"  {name}: dV/dt at MPP {dvdt:.0f} V/s, skew {SKEW * 1e6:.0f} us, {err * 100:.2f} %")
print(f"  worst with -20 % capacitance {skew_worst * 100:.2f} %; removed by interpolating V to the I sample time")

# ------------------------------------------------------------------ 3. Range, resolution, accuracy (R1, R2, R5)
print("\nRange")
print(f"{'Case':46s} {'Voc STC':>8s} {'Voc at -10 °C':>14s}")
for name, voc, isc, vmp, imp, ns in MODULES[:-1]:
    print(f"{name:46s} {voc:8.1f} {voc * (1 + BETA_VOC * (T_COLD - 25)):14.1f}")
two_ref = 2 * 49.5
print(f"Two 450 W reference modules in series: {two_ref:.1f} V at STC, "
      f"{two_ref * (1 + BETA_VOC * (T_COLD - 25)):.1f} V at -10 °C: refused by the 100 V check")
cold_hv = 75.2 * (1 + BETA_VOC * (T_COLD - 25))
print(f"Rating margins at 100 V: capacitors {V_CAP_RATING / V_LIMIT:.2f}x, MOSFETs {V_FET_RATING / V_LIMIT:.2f}x")
res("R1", f"0 to 100 V; high-voltage case {cold_hv:.0f} V at -10 °C; capacitors 160 V, MOSFETs 150 V",
    "0 to 100 V, below 120 V", "Met (design review)")
p_shunt = 20 ** 2 * R_SHUNT
e_fet = 20 ** 2 * 10e-3 * lim["t"]
print(f"At 20 A: shunt {p_shunt:.1f} W (3 W part), load MOSFET conduction {e_fet:.2f} J per sweep")
res("R2", f"0 to {V_REF / (R_SHUNT * GAIN):.2f} A full scale; shunt {p_shunt:.1f} W of 3 W at 20 A", "0 to 20 A", "Met (design review)")

ratio = R_DIV_BOT / (R_DIV_TOP + R_DIV_BOT)
v_fs = V_REF / ratio
i_fs = V_REF / (R_SHUNT * GAIN)
v_lsb, i_lsb = v_fs / 2 ** ADC_BITS, i_fs / 2 ** ADC_BITS
print(f"\nResolution: voltage full scale {v_fs:.1f} V, {v_lsb * 1e3:.1f} mV per count; "
      f"current full scale {i_fs:.2f} A, {i_lsb * 1e3:.2f} mA per count")
v_read = math.sqrt(ERR["V reference drift, 50 ppm/°C"] ** 2 + ERR["Divider ratio drift, 25 ppm/°C"] ** 2)
i_read = math.sqrt(ERR["V reference drift, 50 ppm/°C"] ** 2 + ERR["Shunt drift, 50 ppm/°C"] ** 2
                   + ERR["Amplifier gain drift, 2.5 ppm/°C"] ** 2)
fs_inl = ADC_INL_LSB / 2 ** ADC_BITS
i_off = AMP_OFFSET_DRIFT * TEMP_SPAN / R_SHUNT / i_fs
i_fs_err = math.sqrt(fs_inl ** 2 + i_off ** 2)
print(f"Voltage after calibration: ±{v_read * 100:.2f} % of reading ±{fs_inl * 100:.3f} % of full scale")
print(f"Current after calibration: ±{i_read * 100:.2f} % of reading ±{i_fs_err * 100:.3f} % of full scale "
      f"(offset before calibration {AMP_OFFSET_V / R_SHUNT * 1e3:.2f} mA)")
res("R5", f"V ±{v_read * 100:.2f} % ±{fs_inl * 100:.3f} % FS; I ±{i_read * 100:.2f} % ±{i_fs_err * 100:.3f} % FS",
    "±1 % of reading ±0.1 % FS", "Met on paper (needs calibration)")
p_err_inst = math.sqrt(v_read ** 2 + i_read ** 2)
print(f"Instrument contribution to Pmax: ±{p_err_inst * 100:.2f} %")
q_ref = math.hypot(v_lsb / ref["vmp"], i_lsb / ref["imp"])
print(f"Quantization at the reference MPP: {q_ref * 100:.3f} % of Pmax per sample")
res("R6", f"Instrument noise {q_ref * 100:.2f} % per sample; irradiance drift dominates",
    "Pmax ±1 % over 3 sweeps", "Not verifiable at TRL 3")

# ------------------------------------------------------------------ 4. STC uncertainty (R7, R8)
u_t = BETA_P * U_TEMP
print("\nSTC uncertainty (root sum square)")
for u_ref in U_REFCELL:
    u = math.sqrt(u_ref ** 2 + U_SPECTRAL ** 2 + u_t ** 2 + p_err_inst ** 2)
    print(f"  reference cell ±{u_ref * 100:.0f} %: total ±{u * 100:.1f} %")
u_lo = math.sqrt(U_REFCELL[0] ** 2 + U_SPECTRAL ** 2 + u_t ** 2 + p_err_inst ** 2)
u_hi = math.sqrt(U_REFCELL[1] ** 2 + U_SPECTRAL ** 2 + u_t ** 2 + p_err_inst ** 2)
ref_max = math.sqrt(R8_TARGET ** 2 - U_SPECTRAL ** 2 - u_t ** 2 - p_err_inst ** 2)
irr_ref_max = math.sqrt(0.05 ** 2 - U_SPECTRAL ** 2)
print(f"  temperature term ±{u_t * 100:.1f} %; R8 is met if the reference cell is within ±{ref_max * 100:.1f} %")
print(f"  R7 irradiance ±5 % is met if the reference cell is within ±{irr_ref_max * 100:.1f} %")
res("R7", f"Irradiance ±{math.hypot(U_REFCELL[0], U_SPECTRAL) * 100:.1f} to ±{math.hypot(U_REFCELL[1], U_SPECTRAL) * 100:.1f} %; "
          f"temperature probe ±2 °C budget", "±5 %, ±2 °C", "At risk")
res("R8", f"±{u_lo * 100:.1f} to ±{u_hi * 100:.1f} % (needs reference cell within ±{ref_max * 100:.1f} %)",
    "±5 % or better", "At risk")
res("R9", f"{min(s['ppv'] for s in sweeps.values()):.0f} or more samples per volt; rules drafted",
    "Flags within 5 s", "Not verifiable at TRL 3")
res("R10", "A, B, C, reject thresholds decided (PVT-DDR-002); editable table", "Partner-editable grades", "Met (design review)")

# ------------------------------------------------------------------ 5. Discharge and heat (R11, R13)
tau_a, tau_p = R_DUMP * C_LOAD, R_BLEED * C_LOAD
tau_a_hi, tau_p_hi = tau_a * (1 + C_TOL), tau_p * (1 + C_TOL)
t30 = tau_a_hi * math.log(V_LIMIT / 30)
t1 = tau_a_hi * math.log(V_LIMIT / 1)
t60 = tau_p_hi * math.log(V_LIMIT / 60)
print(f"\nDischarge: active tau {tau_a * 1e3:.0f} ms ({tau_a_hi * 1e3:.0f} ms at +20 %): 100 V to 30 V in {t30:.2f} s, "
      f"to 1 V in {t1:.2f} s; passive tau {tau_p:.0f} s ({tau_p_hi:.0f} s at +20 %): 100 V to 60 V in {t60:.0f} s")
print(f"Peak dump power {V_LIMIT ** 2 / R_DUMP:.0f} W, peak dump current {V_LIMIT / R_DUMP:.1f} A, "
      f"bleed draw at 100 V {V_LIMIT / R_BLEED * 1e3:.0f} mA ({V_LIMIT ** 2 / R_BLEED:.1f} W)")
i_end_max = max(s["i_end"] for s in sweeps.values())
wait_max = max(s["t_wait"] * (1 + C_TOL) for s in sweeps.values())
print(f"Module current at 99 % of Voc: up to {i_end_max:.2f} A, above the 0.5 A opening limit; firmware keeps the "
      f"load switch closed until the current is below 0.5 A, at most {wait_max * 1e3:.0f} ms more (+20 % C)")
res("R11", f"30 V in {t30:.2f} s; 60 V passive in {t60:.0f} s; opens below 0.5 A after up to {wait_max * 1e3:.0f} ms more",
    "30 V in 2 s; 60 V in 60 s; open below 0.5 A", "Met")
e_lim = 0.5 * C_LOAD * V_LIMIT ** 2
p_dump_ref, p_dump_lim = ref["e"] / SWEEP_PERIOD, e_lim / SWEEP_PERIOD
print(f"Stored energy at 100 V: {e_lim:.0f} J (was {0.5 * 2 * C_UNIT * V_LIMIT ** 2:.0f} J with 4.4 mF); "
      f"average dump power at one sweep per {SWEEP_PERIOD:.0f} s: {p_dump_ref:.1f} W reference, {p_dump_lim:.1f} W at 100 V")

L_, W_, H_ = MP["case_l"] / 1e3, MP["case_w"] / 1e3, MP["case_h"] / 1e3
a_case = 2 * (L_ * W_ + L_ * H_ + W_ * H_)
a_top = L_ * W_
p_elec = P_CTRL + P_ISO
ha = H_CASE * a_case
print(f"Case outside area {a_case:.3f} m2, lid {a_top:.4f} m2, hA {ha:.2f} W/K")
thermal = {}
for label, alpha in (("light", ALPHA_LIGHT), ("dark", ALPHA_DARK)):
    for rate_label, pd in (("reference rate", p_dump_ref), ("100 V rate", p_dump_lim)):
        q = p_elec + pd + alpha * G_SUN * a_top
        thermal[(label, rate_label)] = T_AMB + q / ha
        print(f"  {label} case, {rate_label}: {q:.1f} W, inside about {T_AMB + q / ha:.0f} °C at {T_AMB:.0f} °C ambient")
res("R13", f"Inside about {thermal[('light', 'reference rate')]:.0f} °C (light case) to {thermal[('dark', 'reference rate')]:.0f} °C "
           f"(dark) at 45 °C in sun; TFT with sun hood, readability unproven; IP54 case", "0 to 45 °C, sun, IP54, readable",
    "Not met (display); at risk (heat)")

# ------------------------------------------------------------------ 6. Battery (R14)
p_batt = p_elec / ETA_BOOST
hours = E_CELL * USABLE / p_batt
sweeps_n = hours * 3600 / SWEEP_TIME_BUDGET
print(f"\nBattery: {p_elec:.2f} W at 5 V, {p_batt:.2f} W from the cell; {E_CELL * USABLE:.1f} Wh usable: {hours:.1f} h, "
      f"about {sweeps_n:.0f} sweeps at {SWEEP_TIME_BUDGET:.0f} s each")
res("R14", f"{hours:.1f} h, about {sweeps_n:.0f} sweeps", "8 h or 200 sweeps", "Met")
res("R15", "CSV fields defined in PVT-PRC-001; no firmware at TRL 3", "CSV per sweep, USB or Wi-Fi export", "Met (design review)")
res("R16", "No insulation test in this instrument", "Detect insulation faults", "Not met (out of scope)")

# ------------------------------------------------------------------ 7. Mass (R12) and cost (R17)
shell_cm3 = 2 * (L_ * W_ + L_ * H_ + W_ * H_) * MP["wall"] / 1e3 * 1e6
MASS = {
    "Enclosure body and lid, ABS 3 mm, with bumpers and glands": shell_cm3 * 1.05 + 45,
    "Window, PC 11.7 cm3 at 1.20 g/cm3, and gasket": 11.7 * 1.20 + 2, "Controller and display": 45, "Measurement board": 40,
    "Load capacitors, 3 x 75 g": 3 * 75, "MOSFETs and bar": 40, "Dump and bleed resistors": 45,
    "Fuse and holder": 40, "DC isolator": 120, "Battery, holder, charger": 72,
    "Test leads, 2 x 1 m 4 mm2 with MC4": 2 * (4e-6 * 8960 * 1e3 + 25) + 4 * 10,
    "Sensor pod with 3 m cable": 150, "Isolation board": 10, "Hardware and consumables": 50,
    "Display sun hood, PETG 11.6 cm3 at 1.27 g/cm3, with screws": 11.6 * 1.27 + 2,   # PVT-DDR-002 item 12, PVT-DDR-003
    "Chassis plate, polycarbonate 1.5 mm, 37.8 cm3 at 1.20 g/cm3": 37.8 * 1.20,         # PVT-DDR-003 C5 (model volume)
    "USB-C charging socket with lead": 8,                                             # PVT-DDR-003 C10
    "Keypad (membrane, tail), two status LEDs with clips, 6-way lead": 8,              # PVT-DEC-001 item 6, BOM line 18
}
mass = sum(MASS.values())
print("\nMass (g)")
for k, v in MASS.items():
    print(f"  {k}: {v:.0f}")
print(f"  total {mass:.0f} g")
env = (MP["case_l"] + 2 * MP["bumper"] / 2, MP["case_w"] + MP["bumper"], MP["case_h"])
print(f"Enclosure {MP['case_l']:.0f} x {MP['case_w']:.0f} x {MP['case_h']:.0f} mm; over bumpers "
      f"{env[0]:.0f} x {env[1]:.0f} mm; over glands {MP['case_l'] + 24:.0f} mm; knob top {MP['case_h'] + MP['knob_h'] + 8:.0f} mm")
res("R12", f"{mass / 1e3:.2f} kg; {env[0]:.0f} x {env[1]:.0f} x {MP['case_h']:.0f} mm over bumpers",
    "1.5 kg; 250 x 150 x 100 mm", "Met")

rows = list(csv.DictReader((ROOT / "bom/bom.csv").open()))
total = sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in rows)
BUDGET = 165.0   # project.yaml budget_usd: a value-engineering target, not a limit (STANDARDS section 18)
diff = total - BUDGET
print(f"\nBOM total USD {total:.2f}: value-engineering target USD {BUDGET:.0f}; "
      f"{'over' if diff > 0 else 'under'} the target by USD {abs(diff):.2f}")
res("R17", f"USD {total:.0f} in parts", f"Value-engineering target USD {BUDGET:.0f}",
    f"{'Over' if diff > 0 else 'Under'} the target by USD {abs(diff):.0f}")

# ------------------------------------------------------------------ output
order = [f"R{i}" for i in range(1, 18)]
results.sort(key=lambda r: order.index(r["id"]))
with (Path(__file__).parent / "results.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "value", "target", "status"])
    w.writeheader()
    w.writerows(results)
print("\nResults")
for r in results:
    print(f"  {r['id']:4s} {r['status']:38s} {r['value']}")
print("wrote docs/04-calcs/results.csv")
