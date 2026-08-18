"""Re-identify the `category` of every base problem against a refined 10-class
taxonomy, by TWO independent vendor models (consensus).

Replaces the legacy 12-class scheme (drops the incoherent `atmospheric_optics`
and `synoptic_meteorology`, folds optics into radiation, and lets every problem
be reassigned to its best physical home). Each problem is classified blindly by
gpt55-reasoning (primary) and opus48 (witness) against the same rubric; agreement
is the final label, disagreement is flagged for review.

Output: pipeline/reports/recategorize.json
    {id: {final, agree, gpt, opus, gpt_reason, opus_reason, old}}

    uv run python -m pipeline.recategorize --limit 8        # pilot
    uv run python -m pipeline.recategorize --workers 8      # full
"""

import os
import re
import json
import argparse
import threading
import concurrent.futures
from collections import Counter

from eval.models import load_config, build_model

# ── refined taxonomy: 10 categories, each with a crisp scope + disambiguation ──
TAXONOMY = {
    "atmospheric_dynamics":
        "Large-scale/synoptic air motion and the forces governing it: geostrophic/gradient/thermal "
        "wind, pressure-gradient & Coriolis, vorticity/divergence, atmospheric waves (Rossby, gravity), "
        "frontogenesis, circulation, momentum budgets, earth-geometry of flow.",
    "atmospheric_thermodynamics":
        "Heat- and moisture-state processes: dry/moist lapse rates, static stability & CAPE, adiabatic "
        "processes, potential temperature, hydrostatic balance, humidity/saturation/vapour pressure, "
        "thermodynamic phase changes, ideal-gas/equation-of-state of air.",
    "atmospheric_chemistry":
        "Chemical composition and GAS-PHASE reactions: photochemistry, reaction rates/lifetimes, ozone "
        "(Chapman), oxidation, gas solubility (Henry's law), acid deposition, chemical mixing-ratio "
        "budgets. (Aerosol PARTICLE physics goes to atmospheric_aerosols, not here.)",
    "atmospheric_aerosols":
        "The physics of aerosol particles / particulate matter: size distributions (lognormal, modes), "
        "number/mass/volume concentration, coagulation, condensational growth, nucleation, settling/dry "
        "deposition of particles, aerosol optical properties (extinction, scattering efficiency), "
        "PM and CCN as particles. (Their gas-phase chemistry goes to atmospheric_chemistry.)",
    "atmospheric_radiation":
        "The physics of radiation itself: blackbody/Planck/Stefan-Boltzmann emission, absorption & "
        "scattering (Rayleigh/Mie), optical depth/transmission, solar & terrestrial flux mechanics, and "
        "atmospheric OPTICS (rainbows, halos, refraction, scattering colour).",
    "cloud_physics":
        "Cloud microphysics and precipitation: droplet nucleation/growth, terminal/fall velocity, "
        "drop-size distributions, collision-coalescence, precipitation rate, latent heating from precip.",
    "boundary_layer":
        "Turbulent surface/boundary layer: turbulent (sensible/latent/momentum) fluxes, mixing & eddy "
        "diffusion, Monin-Obukhov/friction velocity, mixed-layer growth, surface energy balance.",
    "air_quality":
        "Air pollution meteorology: transport & dispersion of pollutants (Gaussian plume, stack/effluent "
        "& plume rise, dispersion coefficients), gaseous dry/wet deposition, box models for pollutant "
        "concentration, emission-rate & air-quality-standard calculations.",
    "climate_dynamics":
        "Energetics of the climate SYSTEM (not the radiation mechanics): planetary/global energy balance, "
        "equilibrium temperature, climate feedbacks & sensitivity/gain, insolation budgets, greenhouse "
        "forcing at system level, thermal-expansion sea-level rise.",
    "observation_and_modeling":
        "How the atmosphere is OBSERVED and MODELLED (methods/instruments, not a physical phenomenon): "
        "remote sensing — radar (reflectivity, Doppler, polarization, range/velocity ambiguity), satellite "
        "radiance/brightness temperature, lidar/limb sounding, microwave sensing — AND numerical/computational "
        "meteorology — finite-difference schemes, CFL/stability, grid spacing, data assimilation (fusing "
        "observations into models), NWP, forecast-verification statistics.",
}

CATS = list(TAXONOMY)

SYSTEM = ("You are an expert atmospheric scientist building a benchmark taxonomy. You assign each "
          "problem to the ONE category that best matches the PRIMARY physics it tests, judged by the "
          "given scope definitions, not by incidental sub-steps. Reply with ONLY the requested JSON.")

RULES = (
    "Decision rules:\n"
    "- Classify by the PRIMARY phenomenon being solved for, not a minor intermediate step.\n"
    "- radiation vs climate_dynamics: the mechanics of radiation (emission/absorption/scattering) -> "
    "atmospheric_radiation; the energy balance/feedback of the climate system -> climate_dynamics.\n"
    "- aerosol vs chemistry vs cloud: aerosol PARTICLE physics (size distribution, coagulation, number/mass, "
    "particle settling, aerosol optics) -> atmospheric_aerosols; gas-phase REACTIONS/lifetimes/solubility -> "
    "atmospheric_chemistry; droplet/ice growth, precipitation, CCN activation in clouds -> cloud_physics.\n"
    "- observation_and_modeling ONLY when the numerical scheme/stability/assimilation/verification or the "
    "instrument/retrieval IS the point; if a method merely computes a physical quantity, classify by the "
    "physical domain.\n"
    "- radar/satellite/lidar retrieval, numerical schemes, data assimilation, forecast verification -> observation_and_modeling.\n"
    "- You MUST pick exactly one category from the list (no new names)."
)


def build_prompt(p):
    cats = "\n".join(f"- {c}: {TAXONOMY[c]}" for c in CATS)
    kp = ", ".join(p.get("knowledge_points") or []) or "(none)"
    return (f"Assign this atmospheric-science problem to exactly one category.\n\n"
            f"## Categories\n{cats}\n\n{RULES}\n\n"
            f"## Problem\n{p['problem']}\n\n"
            f"## Topic hint: {p.get('topic','')}\n## Knowledge points: {kp}\n\n"
            f"Reply ONLY: {{\"category\":\"<one of the list>\",\"confidence\":\"high|medium|low\","
            f"\"second_choice\":\"<category or null>\",\"reason\":\"<=20 words\"}}")


def parse(t):
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def classify(model, p, retries=3):
    prompt = build_prompt(p)
    for _ in range(retries):
        try:
            out = parse(model.generate(prompt, SYSTEM).text)
        except Exception:
            continue
        if out and out.get("category") in TAXONOMY:
            return out
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="benchmark/base.json")
    ap.add_argument("--out", default="pipeline/reports/recategorize.json")
    ap.add_argument("--primary", default="gpt55-reasoning")
    ap.add_argument("--witness", default="opus48")
    ap.add_argument("--ids", nargs="+", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    problems = json.load(open(args.input))
    if args.ids:
        problems = [p for p in problems if p["id"] in set(args.ids)]
    if args.limit:
        problems = problems[: args.limit]

    out = json.load(open(args.out)) if os.path.exists(args.out) else {}
    todo = [p for p in problems if p["id"] not in out]
    print(f"problems: {len(problems)} | done: {len(out)} | todo: {len(todo)}")

    mp = build_model(load_config(args.primary))
    mw = build_model(load_config(args.witness))
    lock = threading.Lock()
    n = [0]

    def work(p):
        g = classify(mp, p)
        w = classify(mw, p)
        gc = g["category"] if g else None
        wc = w["category"] if w else None
        agree = gc is not None and gc == wc
        rec = {"old": p.get("category"), "gpt": gc, "opus": wc,
               "final": gc if agree else None, "agree": agree,
               "gpt_conf": (g or {}).get("confidence"), "opus_conf": (w or {}).get("confidence"),
               "gpt_reason": (g or {}).get("reason", ""), "opus_reason": (w or {}).get("reason", ""),
               "gpt_alt": (g or {}).get("second_choice"), "opus_alt": (w or {}).get("second_choice")}
        with lock:
            out[p["id"]] = rec
            n[0] += 1
            if n[0] % 25 == 0:
                json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
                ag = sum(1 for v in out.values() if v["agree"])
                print(f"  {n[0]}/{len(todo)} | agree {ag}/{len(out)}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))

    json.dump(out, open(args.out, "w"), indent=1, ensure_ascii=False)
    agree = sum(1 for v in out.values() if v["agree"])
    print(f"\nconsensus agree: {agree}/{len(out)} ({100*agree/len(out):.1f}%)")
    print("final dist (agreed only):", dict(Counter(v["final"] for v in out.values() if v["agree"])))
    print("disagreements:", [(i, v["gpt"], v["opus"]) for i, v in out.items() if not v["agree"]][:40])
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
