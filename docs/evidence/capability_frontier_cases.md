# The residual capability frontier — failure clusters and transcripts

**Backs**: Supplementary Tables S25 / S26. **Verbatim.**

> ⚠️ **The requested description of `2.10` does not match the data**: both DeepSeek-V4-pro variants are **0/3**, but they fail differently.
> The **non-reasoning** arm returns only 3 values in each run — what it omits is sub 3 (subs 2 and 3 are the same
> number in two units, `57.0 kg/m^2` and `57.0 mm`, and it merges them into one answer in mm). It *does* answer
> the latent heat (`141 MJ/m^2`, against the expected `140.0` for sub 4).
> The **reasoning twin** answers all four but gets the scale height wrong: it uses `H = T0²/(Γ·T1) = 2.556 km`
> where the correct value is `H = T0²/(Γ·(T1−T0)) = 2.706 km` — the dropped term is the `−T` contributed by the
> `1/T` prefactor (the consensus wrong cluster of Supplementary Table S26).

---

## `4.5` — the answer is printed in the statement, and models still return half of it

### Problem `4.5`

Source: `An Introduction to Atmospheric Physics` · category `atmospheric_dynamics` · difficulty `high`

**problem (verbatim)**

~~~~
Evaluate the dimensionless parameter $\Omega ^ { 2 } a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$ .
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `0.0035` |  |
| `2` | `0.7` | % |
| `3` | `0.1` | degree |

**reference solve()**

~~~~python
def solve(
    omega_rad_per_s=7.2921159e-5,
    earth_radius_m=6.371e6,
    gravity_m_per_s2=9.80665,
):
    import math

    percent_per_fraction = 100.0
    degree_per_radian = 180.0 / math.pi

    rotational_parameter = (
        omega_rad_per_s * omega_rad_per_s * earth_radius_m / gravity_m_per_s2
    )

    def surface_radius_ratio(sin2_lat_complement):
        q = rotational_parameter * sin2_lat_complement
        if q == 0.0:
            return 1.0

        x = 1.0 + 0.5 * q
        for _ in range(50):
            f = 1.0 / x + 0.5 * q * x * x - 1.0
            fp = -1.0 / (x * x) + q * x
            step = f / fp
            xn = x - step
            if xn <= 0.0 or not math.isfinite(xn):
                xn = 0.5 * x
            if abs(xn - x) <= 1.0e-15 * max(1.0, abs(xn)):
                return xn
            x = xn
        return x

    x_equator = surface_radius_ratio(1.0)
    equator_effective_gravity_over_pole = abs(
        1.0 / (x_equator * x_equator) - rotational_parameter * x_equator
    )
    percent_less_equator_than_pole = (
        1.0 - equator_effective_gravity_over_pole
    ) * percent_per_fraction

    def angle_from_center_direction(sin2_lat_complement):
        y = min(1.0, max(0.0, sin2_lat_complement))
        x = surface_radius_ratio(y)
        radial_inward = 1.0 / (x * x) - rotational_parameter * x * y
        transverse = rotational_parameter * x * math.sqrt(max(0.0, y * (1.0 - y)))
        return abs(math.atan2(transverse, radial_inward))

    lo = 0.0
    hi = 1.0
    golden = (math.sqrt(5.0) - 1.0) / 2.0
    c = hi - golden * (hi - lo)
    d = lo + golden * (hi - lo)
    fc = angle_from_center_direction(c)
    fd = angle_from_center_direction(d)

    for _ in range(120):
        if fc < fd:
            lo = c
            c = d
            fc = fd
            d = lo + golden * (hi - lo)
            fd = angle_from_center_direction(d)
        else:
            hi = d
            d = c
            fd = fc
            c = hi - golden * (hi - lo)
            fc = angle_from_center_direction(c)

    max_angle_rad = max(fc, fd, angle_from_center_direction(0.5 * (lo + hi)))
    max_angle_degree = max_angle_rad * degree_per_radian

    return {
        "1": {"value": rotational_parameter, "unit": "SI"},
        "2": {"value": percent_less_equator_than_pole, "unit": "%"},
        "3": {"value": max_angle_degree, "unit": "degree"},
    }
~~~~

### Answer distribution over all 48 measurements

| configuration | run | passed | `details[].actual` |
|---|---|:---:|---|
| `deepseek-v4-flash` | 1 | ✗ | `[0.0034677485066498316, 0.8723870190087706, 0.09951612547075678]` |
| `deepseek-v4-flash` | 2 | ✗ | `[0.0034677476506641317, 0.8723869338616775, 0.09951610086338862]` |
| `deepseek-v4-flash` | 3 | ✗ | `[0.0034677476506641317, 0.8723869338616775, 0.09951610086338862]` |
| `deepseek-v4-flash-reasoning` | 1 | ✗ | `[0.0034584403397011835, 0.34584403397011837, 0.09924868996585436]` |
| `deepseek-v4-flash-reasoning` | 2 | ✗ | `[0.00345844760466138, 0.345844760466138, 0.09924874991149885]` |
| `deepseek-v4-flash-reasoning` | 3 | ✗ | `[0.003454577675157754, 0.3454577675157754, 0.09913764913003013]` |
| `deepseek-v4-pro` | 1 | ✗ | `[0.0034677485876676286, 0.8723786339599563, 0.09951612779980826]` |
| `deepseek-v4-pro` | 2 | ✗ | `[0.0034677485066498316, 1.0138914070577443, 0.09951612547075676]` |
| `deepseek-v4-pro` | 3 | ✗ | `[0.0034677485876676286, 0.8723786339599563, 0.09934387834991193]` |
| `deepseek-v4-pro-reasoning` | 1 | ✗ | `[0.003453390762886219, 0.34533907628862187, 0.09910338054914007]` |
| `deepseek-v4-pro-reasoning` | 2 | ✓ | `[0.003461392712977341, 0.6922785425954682, 0.09916159684546978]` |
| `deepseek-v4-pro-reasoning` | 3 | ✓ | `[0.003453390762886219, 0.6883011796413865, 0.09910338054914007]` |
| `gemini-3.1-pro` | 1 | ✗ | `[0.0034532809882161053, None, None]` |
| `gemini-3.1-pro` | 2 | ✓ | `[0.0034533757031, 0.69067514062, 0.09893182811027426]` |
| `gemini-3.1-pro` | 3 | ✗ | `[0.0034532809882161053, 0.34532809882161053, 0.09910022485764661]` |
| `gpt55` | 1 | ✗ | `[0.0034545704582006915, 0.345457045820078, 0.09913744166303921]` |
| `gpt55` | 2 | ✗ | `[0.0034545704582006915, 0.345457045820078, 0.09913744166303923]` |
| `gpt55` | 3 | ✗ | `[0.0034545704582006915, 0.3454570458200781, 0.09913744166303926]` |
| `gpt55-reasoning` | 1 | ✓ | `[0.0034545696054678865, 0.692413982117146, 0.0991374171493963]` |
| `gpt55-reasoning` | 2 | ✓ | `[0.0034545704582006915, 0.6894233651848718, 0.09913744166303923]` |
| `gpt55-reasoning` | 3 | ✓ | `[0.0034562621599999992, 0.6927539673852956, 0.0991860733197243]` |
| `kimi-k2.6` | 1 | ✗ | `[0.0034545704582006915, 0.345457045820078, 0.0991372932620191]` |
| `kimi-k2.6` | 2 | ✗ | `[0.0034532809882161053, 0.34532809882161053, 0.09892911473681171]` |
| `kimi-k2.6` | 3 | ✗ | `[0.0034545704582006915, 0.345457045820078, 0.09913744166303923]` |
| `kimi-k2.6-reasoning` | 1 | ✗ | `[0.0034533757031, 0.34533757030999757, 0.09910309587241009]` |
| `kimi-k2.6-reasoning` | 2 | ✓ | `[0.0034532809882161053, 0.689166583467599, 0.0991002248576466]` |
| `kimi-k2.6-reasoning` | 3 | ✗ | `[0.0034545704582006915, 0.34545704582006914, 0.09896605522060319]` |
| `qwen-2.5-72b` | 1 | ✗ | `[0.0034532809882161053, 0.5288852725793468, 0.19785763960606723]` |
| `qwen-2.5-72b` | 2 | ✗ | `[0.003454555393269975, 0.34545553932699513, 0.19793065676598215]` |
| `qwen-2.5-72b` | 3 | ✗ | `[]` |
| `qwen3.5-397b` | 1 | ✗ | `[0.003445663484938345, 0.5288852725793468, 0.09871098765465314]` |
| `qwen3.5-397b` | 2 | ✗ | `[0.003445663484938345, 0.3445663484938434, 0.09888124540277754]` |
| `qwen3.5-397b` | 3 | ✗ | `[0.003449523428478135, 0.34495234284781695, 0.0988215668916475]` |
| `qwen3.5-397b-reasoning` | 1 | ✗ | `[0.0034545704582006915, 0.34545704582006914, 0.0989661536427373]` |
| `qwen3.5-397b-reasoning` | 2 | ✗ | `[0.0034545704582006915, 0.34545704582006914, 0.0989661536427373]` |
| `qwen3.5-397b-reasoning` | 3 | ✗ | `[0.0034545704582006915, 0.34545704582006914, 0.0989661536427373]` |
| `qwen3.5-9b` | 1 | ✗ | `[0.003445662634404154, 0.3445662634404154, 0.09888122095266612]` |
| `qwen3.5-9b` | 2 | ✗ | `[0.003445670683287813, 0.3445670683287813, 0.19742160644117843]` |
| `qwen3.5-9b` | 3 | ✗ | `[0.003445662634404154, 0.3445662634404154, 0.09871086562590954]` |
| `qwen3.5-9b-reasoning` | 1 | ✗ | `[0.0034545704582006915, 0.34545704582006914, 0.09896605522060319]` |
| `qwen3.5-9b-reasoning` | 2 | ✗ | `[0.003453390762886219, 0.5086469989827133, 0.19847086887656767]` |
| `qwen3.5-9b-reasoning` | 3 | ✗ | `[0.003454577675157754, 0.3454577675157754, 0.09913750072807831]` |
| `qwen3.6-27b` | 1 | ✗ | `[0.003461374492593166, 1.01325871630846, 0.09883539427457941]` |
| `qwen3.6-27b` | 2 | ✗ | `[0.003461374492593166, 1.01325871630846, 0.09933288968681873]` |
| `qwen3.6-27b` | 3 | ✗ | `[0.0034498834073666326, 0.34498834073667217, 0.09900255480159738]` |
| `qwen3.6-27b-reasoning` | 1 | ✗ | `[0.0034545696054678865, 0.34545696054678865, 0.09896612921374191]` |
| `qwen3.6-27b-reasoning` | 2 | ✓ | `[0.0034544606460310094, 0.6908921292062019, 0.09896300775580631]` |
| `qwen3.6-27b-reasoning` | 3 | ✗ | `[0.0034545696054678865, 0.34545696054678865, 0.0989661292137419]` |

### Representative transcript per answer cluster (clustered on the measured value of sub 2)

#### 0.345 % cluster (Ω²a/g, rigid sphere) — [('deepseek-v4-flash-reasoning', '1')]

#### `deepseek-v4-flash-reasoning` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/deepseek-v4-flash-reasoning.run1.json` → `4.5` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034584403397011835` | ✓ |
| `2` | `0.7` | `0.34584403397011837` | ✗ |
| `3` | `0.1` | `0.09924868996585436` | ✓ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
Evaluate the dimensionless parameter $\Omega ^ { 2 } a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$ .

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(sidereal_day=86164.0905, equatorial_radius=6378137.0, gravitational_acceleration=9.80665):
    """
    Compute the dimensionless parameter Ω^2 a / g for Earth, the percentage
    reduction in effective gravity at the equator compared to the poles, and
    the maximum angular deviation of effective gravity from the radial direction.

    Parameters
    ----------
    sidereal_day : float
        Earth's sidereal day in seconds (default 86164.0905 s).
    equatorial_radius : float
        Earth's equatorial radius in meters (default 6378137 m).
    gravitational_acceleration : float
        Gravitational acceleration at Earth's surface in m/s^2 (default 9.80665 m/s^2).

    Returns
    -------
    dict
        Keys "1", "2", "3" corresponding to:
        1: dimensionless parameter Ω^2 a / g
        2: percentage reduction in |g'| at equator relative to poles (in percent)
        3: maximum angle between g' and radial direction (in degrees)
    """
    # Angular velocity of Earth
    omega = 2.0 * math.pi / sidereal_day
    omega_sq = omega * omega

    # Dimensionless parameter
    epsilon = omega_sq * equatorial_radius / gravitational_acceleration

    # Percentage reduction (Ω^2 a / g) * 100%
    percent_reduction = epsilon * 100.0

    # Maximum angle between g' and radial direction
    # Solve for sin^2(theta) where the angle is maximum
    s = 1.0 / (2.0 - epsilon)          # sin^2(theta) at maximum
    sin_theta_cos_theta = math.sqrt(s * (1.0 - s))
    denominator = gravitational_acceleration - omega_sq * equatorial_radius * s
    tan_alpha = (omega_sq * equatorial_radius * sin_theta_cos_theta) / denominator
    alpha_rad = math.atan(tan_alpha)
    alpha_deg = alpha_rad * 180.0 / math.pi

    return {
        "1": {"value": epsilon, "unit": "dimensionless"},
        "2": {"value": percent_reduction, "unit": "percent"},
        "3": {"value": alpha_deg, "unit": "degrees"}
    }
```
~~~~

#### 0.69 % cluster (correct) — [('deepseek-v4-pro-reasoning', '2')]

#### `deepseek-v4-pro-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run2.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.003461392712977341` | ✓ |
| `2` | `0.7` | `0.6922785425954682` | ✓ |
| `3` | `0.1` | `0.09916159684546978` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 3
    1. Evalu`

RESPONSE (verbatim, untruncated):

~~~~
We need to write a Python function `solve()` that computes the requested quantities for the Earth. The problem asks:

1. Evaluate the dimensionless parameter Ω² a / g for the Earth.
2. Show that at Earth's surface, the magnitude |g'| of effective gravity is about 0.7% less at the equator than at the poles.
3. The maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°.

We need to return a dict with entries "1", "2", "3" corresponding to these three quantities. But careful: The problem asks to "Evaluate the dimensionless parameter Ω² a / g for the Earth." So answer 1 is that dimensionless parameter. Then "Show that... the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" – so answer 2 is the percentage difference? Or maybe the magnitude difference? The phrasing "about 0.7% less" suggests we compute the percentage decrease: (|g'_pole| - |g'_equator|)/|g'_pole| * 100%. Or maybe just the ratio? The problem says "Show that... is about 0.7% less". So we should compute that percentage. And "the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." So answer 3 is that maximum angle in degrees.

Thus we need to compute:
1. Ω² a / g, where Ω is Earth's angular rotation rate, a is Earth's equatorial radius, g is the gravitational acceleration (presumably the true gravity at the surface, maybe at the equator? Usually g is the standard gravity, but for this parameter, it's often the gravitational acceleration GM/R^2. We need to use standard values. The problem doesn't give numbers, so we must use known Earth parameters. We'll use standard values: Earth's rotation period = 24 hours = 86400 s? Actually sidereal day is 86164 s. But often in such problems, they use 24 hours. Let's check typical values: Earth's equatorial radius a ≈ 6378 km = 6.378e6 m. g ≈ 9.81 m/s². Ω = 2π / T, T = 24h = 86400 s? Or sidereal day = 23h56m4s = 86164 s. The dimensionless parameter Ω² a / g is about 3.45e-3? Let's compute: Ω = 7.292115e-5 rad/s (standard). a = 6378137 m (equatorial radius). g = 9.780327 m/s² (at equator? Actually g varies. Usually the parameter uses the equatorial gravity or mean gravity. The standard value is m = Ω² a³ / GM? Actually the parameter is often denoted m = Ω² a / g_e? Let's recall: The dimensionless parameter for Earth's oblateness is often J2 related to m = Ω² a³ / GM. But here it's Ω² a / g. If g = GM/a², then Ω² a / g = Ω² a³ / GM = m. So it's the same. Standard m for Earth is about 3.4495e-3. So we can compute using standard values. We need to pick values. Since the problem doesn't provide them, we'll use typical values: Earth's rotation period T = 86164 s (sidereal day), equatorial radius a = 6378.1 km = 6.3781e6 m, g = 9.78 m/s²? Actually g at equator is about 9.78, but the true gravity (without rotation) is about 9.83? Wait, effective gravity g' includes centrifugal term. The true gravitational acceleration g (due to mass) is about 9.83 m/s² at poles, 9.78 at equator? Actually g' at equator is about 9.78, but true gravity g at equator is about 9.83? Let's check: g' = g - Ω² a. At equator, Ω² a ≈ (7.292e-5)^2 * 6.378e6 ≈ 0.0339 m/s². So if g' = 9.78, then g = 9.81. So g is about 9.81. The parameter Ω² a / g is about 0.0339/9.81 ≈ 0.00346. So we can compute it.

But we need to be precise. The problem likely expects the student to use standard values: Earth's radius a = 6370 km? Actually equatorial radius is 6378 km. Polar radius is 6357 km. But for the parameter, a is equatorial radius. g is the gravitational acceleration at the equator? Or mean? Usually in the context of effective gravity, g is the true gravitational acceleration at the surface. The parameter Ω² a / g is often evaluated with g being the true gravity at the equator. Let's use standard values: Earth's mass M = 5.972e24 kg, G = 6.674e-11, so GM = 3.986e14 m³/s². Equatorial radius a = 6378137 m. Then true gravity at equator g = GM/a² = 3.986e14 / (6.378137e6)^2 = 9.798? Actually compute: 3.986e14 / 4.068e13 ≈ 9.80. Let's do precisely: 3.986004418e14 / (6378137^2). 6378137^2 = 4.068063e13. 3.986004418e14 / 4.068063e13 = 9.7983. So g ≈ 9.798 m/s² at equator. Then Ω = 2π / 86164.0905 = 7.2921159e-5 rad/s. Ω² a = (7.2921159e-5)^2 * 6378137 = 5.317e-9 * 6.378e6 = 0.03392. So Ω² a / g = 0.03392 / 9.7983 = 0.003462. That's about 3.46e-3.

But the problem also asks for the percentage difference in |g'| between equator and poles, and the maximum angle. To compute these, we need a model. The effective gravity g' is the vector sum of true gravity g (pointing towards center) and centrifugal acceleration Ω² r_perp (pointing outward from axis). On the surface of an oblate Earth, true gravity is not exactly radial and its magnitude varies with latitude. However, the problem likely uses a simplified model: Earth as a sphere? Or as an oblate spheroid? The phrase "at the Earth's surface" and "maximum angle between g' and a vector pointing towards the centre of the Earth" suggests we consider the Earth as a sphere? If Earth were a sphere, true gravity would point to the center and have constant magnitude g. Then effective gravity g' = g - Ω² R cos²λ? Actually centrifugal acceleration is Ω² r cosλ outward from axis, where r is distance from axis = R cosλ. Its magnitude is Ω² R cosλ, direction perpendicular to rotation axis. The vector difference: g' = g (radial inward) + Ω² R cosλ (outward perpendicular to axis). The angle between g' and radial direction is given by tan α = (Ω² R cosλ sinλ) / (g - Ω² R cos²λ)? Actually centrifugal acceleration has components: outward from axis, so in the local horizontal (southward in northern hemisphere) and vertical. The radial component (outward) is Ω² R cos²λ, reducing gravity. The tangential component (equatorward) is Ω² R cosλ sinλ. So the effective gravity vector deviates from radial by angle α where tan α = (Ω² R cosλ sinλ) / (g - Ω² R cos²λ). The maximum angle occurs where derivative is zero. For small Ω² R/g, maximum is at λ = 45°? Actually tan α ≈ (Ω² R/g) cosλ sinλ = (Ω² R/(2g)) sin 2λ. Maximum of sin 2λ is 1 at λ=45°, so α_max ≈ Ω² R/(2g) radians. With Ω² R/g ≈ 0.00346, α_max ≈ 0.00173 rad ≈ 0.099°. That's about 0.1°. So that matches.

For the percentage difference in |g'|: at poles, λ=90°, centrifugal term is zero, so |g'| = g (assuming g is constant). At equator, λ=0°, centrifugal term is Ω² R directly outward, so |g'| = g - Ω² R. The percentage difference = (g - (g - Ω² R))/g * 100% = (Ω² R/g)*100%. That would be about 0.346%, not 0.7%. Wait, the problem says "about 0.7% less at the equator than at the poles". 0.346% is half of 0.7%. So there's a discrepancy. Why? Because the Earth is not a sphere; it's an oblate spheroid. The true gravity g is not constant; it varies with latitude due to both the oblateness and the centrifugal effect. The effective gravity at the poles is larger than at the equator by about 0.7%? Actually the standard gravity formula: g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ) m/s². At equator (φ=0): 9.7803. At poles (φ=90°): 9.8322. Difference = 0.0519, percentage = 0.0519/9.8322 ≈ 0.53%? Actually 9.8322 - 9.7803 = 0.0519, 0.0519/9.8322 = 0.00528 = 0.528%. That's not 0.7% either. Wait, maybe they mean the difference relative to equatorial value? 0.0519/9.7803 = 0.53%. Still not 0.7%. Let's check: The problem says "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". That means (|g'_pole| - |g'_equator|)/|g'_pole| * 100% ≈ 0.7%. But standard values give ~0.5%. Maybe they use a spherical Earth with constant true gravity g, but then the difference is Ω² R/g ≈ 0.35%. That's half of 0.7%. Perhaps they include the effect of oblateness on true gravity? The true gravity at the equator is less than at the poles because the equator is farther from the center. The difference in true gravity due to oblateness is about 0.5%? Actually, if Earth were a uniform oblate spheroid, the true gravity at the poles is larger. The total effective gravity difference is about 0.5%. But 0.7% is a bit high. Let's compute with actual numbers: Earth's equatorial radius a = 6378 km, polar radius c = 6357 km. The true gravity at the pole g_p = GM/c², at equator g_e = GM/a². Ratio g_p/g_e = (a/c)² = (6378/6357)² ≈ (1.0033)² ≈ 1.0066, so g_p is 0.66% larger. Then effective gravity at equator g'_e = g_e - Ω² a. At pole, g'_p = g_p. So g'_p/g'_e = g_p / (g_e - Ω² a). g_e ≈ GM/a². Ω² a ≈ 0.0339 m/s². g_e ≈ 9.80. So g_e - Ω² a ≈ 9.766. g_p ≈ 9.80 * 1.0066 ≈ 9.865. Ratio = 9.865/9.766 ≈ 1.0101, so about 1% difference? That's 1%, not 0.7%. Hmm.

Let's use standard values more accurately. 
GM = 3.986004418e14 m³/s².
a = 6378137 m (equatorial radius)
c = 6356752 m (polar radius)
Ω = 7.2921150e-5 rad/s.

True gravity at equator: g_e = GM/a² = 3.986004418e14 / (6378137)^2 = 9.79828 m/s².
True gravity at pole: g_p = GM/c² = 3.986004418e14 / (6356752)^2 = 9.86432 m/s².
Centrifugal at equator: Ω² a = (7.292115e-5)^2 * 6378137 = 0.03392 m/s².
Effective gravity at equator: g'_e = g_e - Ω² a = 9.79828 - 0.03392 = 9.76436 m/s².
Effective gravity at pole: g'_p = g_p = 9.86432 m/s².
Difference: g'_p - g'_e = 0.09996 m/s².
Percentage relative to pole: 0.09996/9.86432 * 100% = 1.013%. That's about 1.0%, not 0.7%.
Wait, maybe they use a different definition: "about 0.7% less at the equator than at the poles" could mean (g'_p - g'_e)/g'_e * 100%? That would be 0.09996/9.76436 = 1.024%. Still ~1%.
Maybe they use a spherical Earth with constant true gravity g, but then the difference is only Ω² a/g ≈ 0.35%. So 0.7% is double that. Could it be that they consider the effective gravity difference including the oblateness but with a different model? Let's check typical textbook values. In many atmospheric science or geophysics texts, the fractional difference in effective gravity between equator and poles is about 0.5%? Actually, the standard gravity formula gives 9.780 at equator, 9.832 at poles, difference 0.052, percentage 0.53%. That's the effective gravity. So 0.7% is not matching standard. Maybe they use a simplified model where Earth is a sphere but the true gravity is not constant? No.

Let's re-read the problem: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

This is a classic problem. Often, the parameter Ω² a/g is evaluated with g being the true gravity at the equator, and a the equatorial radius. The value is about 1/289? Actually, the Earth's flattening f = (a-c)/a ≈ 1/298.257. The parameter m = Ω² a/g_e ≈ 1/288.9? Let's compute: 1/0.00346 = 289. So m ≈ 1/289. That's a known result. Then the effective gravity difference between pole and equator is approximately (5/2)m - something? Wait, for a rotating fluid planet, the effective gravity difference is related to m. The formula for effective gravity on an oblate spheroid is g' = g_e (1 + (5/2 m - f) sin²φ ...). Actually, the standard formula: g' = g_e (1 + β sin²φ + ...), where β = (5/2)m - f. For Earth, m ≈ 0.00346, f ≈ 0.00335. Then β ≈ 0.00865 - 0.00335 = 0.00530. That's the 0.53% difference. So 0.7% is not that.

Maybe the problem expects a spherical Earth approximation but with a different g? If they use g = 9.81 m/s², a = 6370 km, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344. Then percentage difference = 0.344%. That's not 0.7%.

Wait, could "0.7% less" be a typo or a different interpretation? Perhaps they mean the ratio of the centrifugal term to gravity is about 0.35%, but the total difference including oblateness is about 0.7%? But we computed 1% with actual numbers. Let's check historical values: Sometimes the Earth's equatorial gravity is given as 978.0 Gal, polar 983.2 Gal, difference 5.2 Gal, percentage 0.53%. So 0.7% is off.

Maybe they use the mean radius and mean gravity? Let's compute with mean radius R = 6371 km, g = 9.81. Then Ω² R/g = (7.27e-5)^2 * 6.371e6 / 9.81 = 0.0344/9.81 = 0.00351. Percentage = 0.35%. Still not 0.7%.

Perhaps the problem is from a textbook where they use a different value for Earth's rotation? If they use a day of 24 hours exactly, Ω = 2π/86400 = 7.2722e-5. a = 6378 km = 6.378e6. g = 9.8. Ω² a/g = (5.288e-9)*6.378e6/9.8 = 0.0337/9.8 = 0.00344. Still 0.34%.

Wait, maybe "0.7% less" means the effective gravity at the equator is 0.7% less than at the poles, and they are using a spherical Earth but with g being the true gravity at the pole? No.

Let's think: The problem might be from a dynamics or atmospheric science context where they approximate the Earth as a sphere and use g as the gravitational acceleration at the surface, but then they also consider the oblateness? The phrase "Evaluate the dimensionless parameter Ω² a / g for the Earth." is often the first step. Then they ask to show that |g'| is about 0.7% less at equator than poles. That suggests that the difference is not just Ω² a/g, but something else. Perhaps they include the effect of the Earth's oblateness on true gravity. In a simple model, if Earth is an oblate spheroid in hydrostatic equilibrium, the true gravity at the pole is larger. The total effective gravity difference can be approximated. There is a known result: The fractional difference in effective gravity between equator and pole is approximately (5/2)Ω² a/g - (a-c)/a? Actually, for a homogeneous rotating fluid, the surface is an equipotential, and the effective gravity difference is (5/2)Ω² a/g? Let's derive: For a rotating fluid planet, the effective gravity is g' = g - Ω² r cos²λ. On the surface, which is an equipotential, the true gravity g is not constant. The potential is Φ = -GM/r - (1/2)Ω² r² cos²λ + ... For small flattening, the surface is r = a (1 - f sin²λ). The effective gravity magnitude is g' = |∇Φ|. At equator, g'_e = GM/a² - Ω² a + ... At pole, g'_p = GM/c². The difference can be expanded. The result is g'_p - g'_e ≈ (5/2)Ω² a - (GM/a²)(a-c)/a? Actually, the standard formula for gravity on an ellipsoid is g' = g_e (1 + β sin²φ), where β = (5/2)m - f, with m = Ω² a/g_e, f = flattening. For Earth, m ≈ 0.00346, f ≈ 0.00335, so β ≈ 0.00865 - 0.00335 = 0.00530. So the pole-equator difference is β = 0.0053, i.e., 0.53%. That's not 0.7%.

Maybe they use a different definition: "0.7% less" could be (g'_p - g'_e)/g'_e = 0.7%? That would be 0.007. With β = 0.0053, that's 0.53%. Still not 0.7%.

Wait, could it be that they are using the parameter Ω² a/g with g being the effective gravity at the equator? Then Ω² a/g' = 0.0339/9.78 = 0.00347. Still same.

Perhaps the problem expects the student to compute these values using given numbers? But the problem statement doesn't provide numbers. It says "for the Earth". So we must use standard Earth parameters. The answer might be a known approximate value: Ω² a/g ≈ 1/289 ≈ 0.00346. The percentage difference might be computed as 0.7% if they use a different radius? Let's check if using polar radius for a? No, a is equatorial.

Maybe the 0.7% comes from a spherical Earth but with g being the true gravity at the surface, and they compute the difference in |g'| between equator and pole as (Ω² a/g) * 100%? That's 0.35%. Double that is 0.7%. Could it be that they consider the difference in effective gravity between equator and pole as 2 * Ω² a/g? Why? If Earth is a sphere, true gravity is constant g. At equator, g' = g - Ω² a. At pole, g' = g. Difference = Ω² a. Percentage = Ω² a/g. That's 0.35%. Not 0.7%. If they mistakenly use diameter instead of radius? No.

Maybe they consider the effective gravity vector magnitude at latitude 45°? No.

Let's search memory: In some textbooks, the dimensionless parameter is Ω² R/g, and they say it's about 0.0035. Then they say the effective gravity is about 0.35% less at the equator. But the problem says 0.7%. Could it be a misprint? Or maybe they include the fact that the Earth's radius is larger at the equator, so true gravity is also less? If you combine both effects, the total difference is about 0.5%. Still not 0.7%.

Wait, maybe they use g = 9.8, a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337. Ω² a/g = 0.00344. If they then say the effective gravity difference is about twice that because of oblateness? Actually, for a homogeneous Earth, the true gravity difference due to oblateness is (5/2)Ω² a? No.

Let's derive the effective gravity on an oblate Earth. The potential is U = -GM/r + (1/2)Ω² r² sin²θ? Actually, centrifugal potential is -1/2 Ω² r² cos²θ? Let's use co-latitude θ. The effective gravity is g' = -∇U. On the surface, which is an equipotential, U = constant. For small flattening, the surface is r = a (1 - f sin²φ), where φ is latitude. The effective gravity magnitude is g' = |∇U|. At the equator (φ=0), r = a, g'_e = GM/a² - Ω² a (if we ignore higher terms). At the pole (φ=90°), r = c = a(1-f), g'_p = GM/c². The difference g'_p - g'_e = GM/c² - GM/a² + Ω² a. Using GM/c² ≈ GM/a² (1 + 2f) = g_e (1 + 2f). So g'_p - g'_e ≈ g_e (1+2f) - g_e + Ω² a = 2f g_e + Ω² a. The fractional difference = (2f g_e + Ω² a)/g_e = 2f + m, where m = Ω² a/g_e. For Earth, f ≈ 1/298.257 ≈ 0.003353, m ≈ 0.00346. So 2f + m ≈ 0.006706 + 0.00346 = 0.010166, i.e., 1.02%. That's about 1%, not 0.7%.

If we use the actual effective gravity at equator g'_e = g_e - Ω² a, then the fractional difference relative to g'_e is (g'_p - g'_e)/g'_e ≈ (2f g_e + Ω² a)/(g_e - Ω² a) ≈ 2f + m + m²... ≈ 0.0102, i.e., 1.02%. So that's 1%.

But the problem says 0.7%. Maybe they use a different f? If Earth were in hydrostatic equilibrium as a homogeneous fluid, f = (5/4)m? Actually, for a homogeneous rotating fluid, the flattening f = (5/4) m? Let's check: For a homogeneous Earth, the equilibrium flattening is f = (5/4) m? Wait, the classical result for a homogeneous rotating fluid is f = (5/4) * (Ω² a/g)? Actually, the Maclaurin spheroid: for small eccentricity, f ≈ (5/4) m? Let's derive: For a homogeneous fluid, the surface is an equipotential. The potential is -GM/r - (1/2)Ω² r² sin²θ? Actually, centrifugal potential is -1/2 Ω² r² cos²θ? Let's use standard: U = -GM/r - (1/2)Ω² r² sin²φ? I need to be careful. Usually, the effective gravity potential is Φ = -GM/r - (1/2)Ω² r² cos²θ? No, centrifugal acceleration is Ω² r sinθ outward from axis. The potential for centrifugal force is -1/2 Ω² r² sin²θ? Actually, force = +Ω² r sinθ (outward). So potential V = -1/2 Ω² r² sin²θ? Check: -∇V = Ω² r sinθ (r̂ sinθ + θ̂ cosθ)? That gives centrifugal force. So V = -1/2 Ω² r² sin²θ. Then total potential U = -GM/r - 1/2 Ω² r² sin²θ. At the surface, U = constant. For small flattening, let r = a (1 - f sin²φ) where φ is latitude (φ = 90° - θ). Then sinθ = cosφ. So U = -GM/(a(1 - f sin²φ)) - 1/2 Ω² a² (1 - 2f sin²φ) cos²φ. Expand: GM/(a(1 - f sin²φ)) ≈ GM/a (1 + f sin²φ + f² sin⁴φ...). So U ≈ -GM/a (1 + f sin²φ) - 1/2 Ω² a² cos²φ + Ω² a² f sin²φ cos²φ. For U to be constant, the φ-dependent terms must cancel. The leading φ-dependent terms: -GM/a f sin²φ - 1/2 Ω² a² cos²φ. Write cos²φ = 1 - sin²φ. So -1/2 Ω² a² (1 - sin²φ) = -1/2 Ω² a² + 1/2 Ω² a² sin²φ. The constant part can be absorbed. So the sin²φ terms: -GM/a f + 1/2 Ω² a² = 0 => f = (1/2) (Ω² a²) / (GM/a) = (1/2) Ω² a³ / GM = (1/2) m, where m = Ω² a/g_e and g_e = GM/a². So f = m/2. That's for a homogeneous Earth? Wait, that's if the Earth is a point mass or if we ignore the change in gravity due to oblateness? Actually, in this derivation, we assumed the gravitational potential is -GM/r, which is valid for a point mass or a spherical mass. But if the Earth is oblate, the gravitational potential is not exactly -GM/r; there are J2 terms. For a self-gravitating fluid, the equilibrium flattening is larger. For a homogeneous fluid, the flattening is f = (5/4) m? Let's recall: For a Maclaurin spheroid, the flattening is related to m. For small m, f ≈ (5/4) m? Actually, the exact relation is m = (3/2) ( (1-e²)/e³ ) ( (3-2e²) arcsin e - 3e(1-e²) )? For small e, f ≈ (5/4) m? Let's check: For Earth, m=0.00346, (5/4)m = 0.00433, but actual f=0.00335. So Earth's f is less than (5/4)m. Actually, Earth is not homogeneous; it has a dense core. The equilibrium flattening for a two-layer model can be different. The observed f is about 1/298.257 = 0.003353. m = 0.003460. So f ≈ 0.97 m. So f is approximately m. Then 2f + m ≈ 3m = 0.01038, still ~1%.

So where does 0.7% come from? Maybe they are using a spherical Earth and the percentage difference in |g'| is (Ω² a/g) * 100% but they use g = 9.8, a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344 = 0.344%. Not 0.7%.

Wait, maybe they mean the effective gravity is 0.7% less at the equator than at the poles, and they are using the actual measured effective gravity? The standard formula gives g' at equator = 9.7803, at poles = 9.8322. Difference = 0.0519. 0.0519/9.7803 = 0.00531 = 0.531%. 0.0519/9.8322 = 0.00528 = 0.528%. Neither is 0.7%.

Could it be that they use the mean radius and mean gravity, and the difference is 0.7%? Let's compute with R = 6371 km, g = 9.81, Ω = 7.292e-5. Ω² R = 0.0339. Ω² R/g = 0.00346. Still 0.35%.

Maybe the problem is from a textbook that uses a different value for Earth's rotation period? If they use a day of 24 hours (86400 s), Ω = 7.272e-5. a = 6378 km = 6.378e6. g = 9.78? If g = 9.78, Ω² a/g = 0.0337/9.78 = 0.00345. Still 0.35%.

Perhaps "0.7% less" is a typo and should be "0.35% less"? But the problem also says "the maximum angle ... is about 0.1°". That matches α_max ≈ 0.5 * Ω² a/g rad. 0.5 * 0.00346 = 0.00173 rad = 0.099°. So that's consistent with a spherical Earth model where the angle is given by tan α ≈ (Ω² a/g) cosλ sinλ, max at 45° with value ≈ Ω² a/(2g). So the angle is about 0.1°. The percentage difference in |g'| between equator and pole in that spherical model is Ω² a/g * 100% ≈ 0.35%. But the problem says 0.7%. That's exactly double. Could it be that they define the percentage difference as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That would be (g - (g - Ω² a))/(g - Ω² a) * 100% = (Ω² a)/(g - Ω² a) * 100% ≈ Ω² a/g * (1 + Ω² a/g) * 100% ≈ 0.35% * 1.0035 ≈ 0.351%. Still not 0.7%.

Maybe they consider the difference in effective gravity between equator and pole including the oblateness, but with a simplified formula that gives 0.7%? Let's check if there's a known approximation: The effective gravity difference is often given as about 0.5%? Actually, many sources say the difference is about 0.5%. For example, Wikipedia: "The acceleration due to gravity at the Earth's surface is approximately 9.8 m/s², and varies by about 0.5% between the equator and the poles." So 0.5% is standard. 0.7% is not standard.

Wait, maybe the problem uses the parameter Ω² a/g with a being the mean radius? No.

Let's re-read carefully: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Perhaps they are using a different definition of g? In some contexts, g is the standard gravity 9.80665 m/s². Then Ω² a/g with a=6378 km gives 0.0339/9.80665 = 0.00346. Still 0.35%.

Maybe the 0.7% comes from including the effect of the Earth's oblateness on true gravity, but using a simplified model where the Earth is a sphere and the true gravity is constant, but the effective gravity difference is computed as (g_pole - g_equator)/g_equator? No.

Let's think about the phrase "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". This could be interpreted as: (|g'_pole| - |g'_equator|) / |g'_pole| = 0.007. If we use the actual effective gravity values: 9.832 - 9.780 = 0.052; 0.052/9.832 = 0.0053 = 0.53%. Not 0.7%. If we use the true gravity difference plus centrifugal: g_pole_true = 9.864, g_equator_true = 9.798, difference = 0.066; plus centrifugal 0.034 gives effective difference = 0.100? Wait, effective at pole = 9.864, at equator = 9.798 - 0.034 = 9.764, difference = 0.100. 0.100/9.864 = 0.0101 = 1.01%. So that's 1%.

Maybe they use a different equatorial radius? Some older textbooks use a = 6370 km, c = 6356 km? Then g_p = GM/c², g_e = GM/a². GM = 3.986e14. a=6.37e6, c=6.356e6. g_e = 3.986e14/4.057e13 = 9.82? Actually 6370^2 = 4.057e13, 3.986/4.057 = 0.982, so 9.82. g_p = 3.986e14/(6.356e6)^2 = 3.986e14/4.040e13 = 9.86. Difference = 0.04. Centrifugal = Ω² a = (7.27e-5)^2 * 6.37e6 = 0.0337. Effective equator = 9.82 - 0.0337 = 9.786. Effective pole = 9.86. Difference = 0.074. 0.074/9.86 = 0.0075 = 0.75%. That's about 0.7%! Let's check with more precise numbers: a = 6370 km? Actually, the mean radius is 6371 km, equatorial is 6378, polar is 6357. If someone mistakenly uses the mean radius for a and the polar radius for c? Or if they use a spherical Earth with radius a, but then they say "at the Earth's surface" and compare equator and poles, they might be assuming the Earth is a sphere, so the distance from center is the same, but then the true gravity is the same. That gives 0.35%. So to get 0.7%, they must be including the oblateness effect on true gravity. If they use a = 6378, c = 6357, the difference is 1%. If they use a = 6370, c = 6356? That's not standard.

Wait, maybe the problem defines g as the gravitational acceleration at the Earth's surface ignoring rotation, and a as the mean radius? Then they compute Ω² a/g. Then they say the effective gravity is 0.7% less at equator than poles. That might be a known result from a specific textbook. Let's search memory: In "Atmospheric Science" by Wallace and Hobbs, or in "An Introduction to Dynamic Meteorology" by Holton, there is a problem like this. In Holton's book, Chapter 1, there is a problem: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." I recall this exact wording! It's from Holton's "An Introduction to Dynamic Meteorology" (maybe 4th or 5th edition), Chapter 1, Problem 1.1 or similar. Let me check my memory: In Holton, the parameter is m = Ω² a/g. They use a = 6371 km? Actually, in Holton, they often use a = 6370 km, g = 9.8 m/s², Ω = 7.292e-5. Then Ω² a/g ≈ 0.0035. Then they ask to show that effective gravity is about 0.7% less at equator. How do they get 0.7%? They might be including the oblateness. In Holton's book, they derive that the effective gravity at sea level varies from about 9.78 at equator to 9.83 at poles. That's a difference of 0.05, which is 0.5%. But 0.7%? Let me check the exact numbers: 9.83 - 9.78 = 0.05, 0.05/9.78 = 0.0051 = 0.51%. Not 0.7%. Wait, maybe they use 9.81 as reference? (9.83 - 9.78)/9.81 = 0.05/9.81 = 0.0051. Still 0.5%.

Maybe they use the true gravity difference? In Holton, they might say: The true gravity at the equator is about 9.81, at the pole 9.83? No.

Let's think: If the Earth were a sphere of radius a, true gravity g is constant. Then effective gravity at equator is g - Ω² a, at pole is g. The fractional difference is Ω² a/g ≈ 0.0035 = 0.35%. To get 0.7%, they might be considering the difference between the effective gravity at the equator and the effective gravity at the pole, but they might be using the polar radius for the pole? If they use a spherical Earth, they wouldn't. If they use an oblate Earth, the true gravity at the pole is larger because the pole is closer to the center. The fractional increase in true gravity from equator to pole is about 2f ≈ 0.0067. Then the effective gravity difference is 2f + m ≈ 0.010. That's 1%. Not 0.7%.

Maybe they use a different flattening? If f = m/2? That gives 2f + m = 2*(m/2) + m = 2m = 0.007. That's 0.7%! Yes! If the Earth's flattening is exactly half of m, then the effective gravity difference is 2m. Let's check: If f = m/2, then 2f + m = 2*(m/2) + m = m + m = 2m. And 2m = 2 * 0.00346 = 0.00692 ≈ 0.7%. So if the Earth were in hydrostatic equilibrium with a constant density (or if we ignore the internal mass distribution and just assume the surface is an equipotential of the combined gravitational and centrifugal potential, but with the gravitational potential being that of a point mass), then f = m/2. That is exactly the case where the Earth's gravitational field is that of a point mass (or a sphere). In that case, the surface equipotential gives f = m/2. Then the effective gravity difference is 2m. And the maximum angle? For that model, the effective gravity vector deviates from the radial direction. The angle is given by tan α = (Ω² a sinφ cosφ) / (g - Ω² a cos²φ)? Actually, for an oblate surface, the radial direction is not exactly the local vertical? The problem says "maximum angle between g' and a vector pointing towards the centre of the Earth". So they want the angle between the effective gravity (which is normal to the equipotential surface) and the radial vector to the center. For the point-mass equipotential surface, the surface is r = a (1 - f sin²φ) with f = m/2. The effective gravity is normal to this surface. The angle between the normal to the surface and the radial direction is the angle between the vertical and the radial. That angle is approximately f sin 2φ? Actually, for an ellipsoid, the angle between the geocentric and geographic latitude is (f sin 2φ) or something. The maximum angle between the normal to the ellipsoid and the radial vector is about f radians? For f = 0.00335, that's 0.19°. But the problem says the maximum angle is about 0.1°. That's half of that. So that doesn't match.

Wait, in the spherical Earth model (constant true gravity, spherical surface), the effective gravity g' = g - Ω² R cos²φ (radial) + Ω² R cosφ sinφ (tangential). The angle between g' and the radial direction is α, where tan α = (Ω² R cosφ sinφ) / (g - Ω² R cos²φ). Maximum at φ=45°, tan α_max ≈ (Ω² R/2) / g = m/2. So α_max ≈ m/2 rad = 0.00173 rad = 0.099° ≈ 0.1°. That matches perfectly! So the angle is 0.1° in the spherical model. In the oblate model, the surface is tilted, so the effective gravity is normal to the surface, and the angle between the normal and the radial vector is about f sin 2φ, which is larger (f ≈ 0.00335, max angle ≈ 0.19°). But the problem says "maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°". That matches the spherical model, not the oblate model. So the problem is using a spherical Earth model for the angle! But then the percentage difference in |g'| would be m = 0.35%, not 0.7%. There's a contradiction.

Unless... in the spherical model, they compute the percentage difference in |g'| as (|g'_pole| - |g'_equator|)/|g'_equator|? That's m/(1-m) ≈ 0.35%. Still not 0.7%.

Maybe they compute the difference in |g'| between equator and pole as 2 * (Ω² a/g)? Why? If they consider the effective gravity at the equator is g - Ω² a, and at the pole is g + something? No, at pole centrifugal is zero.

Wait, could it be that they are using the formula for effective gravity on a rotating sphere, but they define the "magnitude |g'|" as the magnitude of the effective gravity vector, and they compare the value at the equator to the value at the poles. At the equator, |g'| = g - Ω² a. At the poles, |g'| = g. The difference is Ω² a. The percentage less at equator than poles = (g - (g - Ω² a))/g = Ω² a/g = m. That's 0.35%. So 0.7% is double.

Maybe they use the diameter instead of radius? If a is the radius, Ω² a/g. If they mistakenly used a = diameter? No.

Perhaps the problem has a typo, and it should be 0.35%? But the problem statement says 0.7%. I've seen this problem before. In some versions, it says "about 0.35% less". Let me check my memory: In Holton's 4th edition, Problem 1.1: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.35% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." Yes! I think it's 0.35%, not 0.7%. Let me verify: I recall a problem: "Show that the effective gravity is about 0.35% less at the equator..." That makes sense because m ≈ 0.0035 = 0.35%. The angle is m/2 ≈ 0.1°. So the problem likely has a typo in the user's message, or I misremember. But the user wrote "0.7%". Could it be that they use a different g? If g is taken as 9.8, and a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344 = 0.344%. Still 0.34%. If they use g = 9.78, then 0.0337/9.78 = 0.00345. Still 0.345%.

Maybe they use the polar radius for a? If a is the polar radius? No, a is usually equatorial.

Wait, maybe the parameter is Ω² a/g, but they then compute the effective gravity difference as (5/2)Ω² a/g? No.

Let's read the problem again: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

If the parameter is m = Ω² a/g, and they want to show |g'| is about 0.7% less, maybe they are using a different definition of g? In some contexts, g is the effective gravity at the pole? Or g is the standard gravity 9.80665? If g = 9.80665, and a = 6378 km, Ω = 7.292e-5, then Ω² a = 0.0339, Ω² a/g = 0.00346. Still 0.35%.

Maybe they use a = 6370 km, g = 9.8, but then they say the effective gravity difference is 0.7% because they include the fact that the Earth is oblate and the true gravity is also less at the equator? But then the angle would be different.

Let's check the angle in the oblate model. The effective gravity is normal to the equipotential surface. The angle between the normal and the radial vector is the difference between geographic and geocentric latitude. That angle is maximum at 45° and is about 11.5'? Actually, the maximum difference is about 11.5 minutes of arc, which is about 0.19°. That's about 0.2°, not 0.1°. So the problem's "0.1°" strongly points to the spherical model where the angle is m/2 rad ≈ 0.1°. So the problem is using a spherical Earth with constant true gravity. In that model, the percentage difference in |g'| is m = 0.35%. So why does the problem say 0.7%? Could it be that they ask for the percentage difference in |g'| between equator and poles, but they define |g'| as the magnitude of the effective gravity vector, and they compute it as sqrt( (g - Ω² a cos²φ)² + (Ω² a cosφ sinφ)² )? At the equator, |g'| = g - Ω² a. At the pole, |g'| = g. The difference is Ω² a. The percentage less = Ω² a/g = m. If they mistakenly computed the percentage as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That's m/(1-m) ≈ m. Still 0.35%.

Maybe they use the fact that the effective gravity at the equator is g - Ω² a, and at the pole is g, but they also consider that the Earth's radius is larger at the equator? If they use a spherical Earth, radius is constant. So no.

Wait, could "0.7%" be a typo in the user's message? The user might have copied it from a source that had a typo. But as an AI, I must solve the problem as stated. However, the problem says "Show that... is about 0.7% less". I need to compute the actual value and see if it's about 0.7%. If I use standard Earth parameters, what do I get? Let's compute using the actual oblate Earth. The effective gravity at the equator is about 9.7803, at the poles 9.8322. The percentage less at equator than poles: (9.8322 - 9.7803)/9.8322 * 100% = 0.528%. That's about 0.5%, not 0.7%. If I use the true gravity difference plus centrifugal, I got 1%. So 0.7% is in between. Maybe they use a different set of parameters: a = 6378 km, c = 6356 km? Let's try a = 6378, c = 6356. Then g_p = GM/c², g_e = GM/a². GM = 3.986e14. g_e = 3.986e14/(6.378e6)^2 = 9.80. g_p = 3.986e14/(6.356e6)^2 = 9.86. Centrifugal = Ω² a = (7.292e-5)^2 * 6.378e6 = 0.0339. g'_e = 9.80 - 0.0339 = 9.766. g'_p = 9.86. Difference = 0.094. 0.094/9.86 = 0.0095 = 0.95%. Still ~1%.

What if they use a = 6370, c = 6357? g_e = 3.986e14/(6.37e6)^2 = 9.82. g_p = 3.986e14/(6.357e6)^2 = 9.86. Centrifugal = Ω² * 6.37e6 = 0.0339. g'_e = 9.82 - 0.0339 = 9.786. g'_p = 9.86. Diff = 0.074. 0.074/9.86 = 0.0075 = 0.75%. That's about 0.7%! If they use a = 6370 km as the equatorial radius? But equatorial radius is actually 6378 km. Some older textbooks use 6370 km as the mean radius, and sometimes they use it for both equator and pole? No, if they use a spherical Earth of radius 6370 km, then g is constant, difference is 0.0339/9.82 = 0.00345 = 0.345%. So to get 0.7%, they must be using an oblate Earth with equatorial radius ~6370 km and polar radius ~6356 km? That's roughly the actual values (6378 vs 6357). The difference is about 21 km. The flattening f = 21/6370 ≈ 0.0033. Then 2f + m = 0.0066 + 0.0035 = 0.0101 = 1.01%. Not 0.7%.

Wait, my calculation above: g'_e = g_e - Ω² a. g'_p = g_p. g_p = GM/c², g_e = GM/a². So g'_p - g'_e = GM/c² - GM/a² + Ω² a. For small differences, GM/c² ≈ GM/a² (1 + 2(a-c)/a) = g_e (1 + 2f). So difference = 2f g_e + Ω² a. Fractional difference = 2f + m. If f = 1/298 = 0.00336, m = 0.00346, then 2f+m = 0.01018 = 1.02%. If I use a=6370, c=6356 (difference 14 km, f=0.0022), then 2f+m = 0.0044+0.0035=0.0079=0.79%. That's close to 0.7%. If I use a=6370, c=6350? Not realistic.

Maybe they use the effective gravity formula from the standard model: g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ). At φ=0, g'=9.7803. At φ=90, g'=9.7803*(1+0.0053024) = 9.8322. The percentage increase from equator to pole is 0.53%. So 0.53% is not 0.7%.

Perhaps the problem uses the parameter m = Ω² a/g, and then states that the effective gravity difference is about 2m? That would be 0.7%. Why would it be 2m? In some derivations, if you assume the Earth is a fluid in hydrostatic equilibrium, the effective gravity difference between pole and equator is (5/2)m? No, (5/2)m = 0.00865 = 0.865%. That's close to 0.7%? 0.865% is closer to 0.9%. If m=0.00346, 5/2 m = 0.00865. If m=0.0035, 5/2 m = 0.00875. Not 0.7%.

What if they use the formula for a homogeneous Earth? For a homogeneous rotating fluid, the flattening f = (5/4)m, and the effective gravity difference is (5/2)m? Actually, for a homogeneous Earth, the effective gravity at the pole is g_p = GM/c², at equator g'_e = GM/a² - Ω² a. Using the equilibrium relation, one can show that g'_p - g'_e = (5/2) m g_e? Let's check: For homogeneous, f = (5/4)m. Then 2f + m = 2*(5/4)m + m = (5/2)m + m = (7/2)m = 3.5m = 0.012. That's 1.2%. Not 0.7%.

Maybe they use the fact that the effective gravity vector magnitude is sqrt( (g - Ω² a cos²φ)² + (Ω² a cosφ sinφ)² ). At the equator, this is g - Ω² a. At the pole, it's g. The difference is Ω² a. But maybe they consider the percentage difference relative to the average? No.

Given the confusion, I should look up the exact problem. Since I'm an AI, I can't browse, but I can recall. I am quite sure this is Problem 1.1 from Holton's "An Introduction to Dynamic Meteorology". In the 4th edition, it says: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.35% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." I have a strong memory of 0.35%. In fact, I've seen this problem before. The user might have typed 0.7% by mistake. But the user's text says "0.7%". Should I compute 0.35% or 0.7%? The problem says "Show that... is about 0.7% less". If I compute the actual value using standard parameters, what do I get? If I use a spherical Earth with constant g, I get ~0.35%. If I use the actual oblate Earth, I get ~0.5% or ~1% depending on how I compute. The phrase "about 0.7% less" might be a rough number from a specific set of parameters. Let's check if using a = 6370 km, g = 9.8, Ω = 7.27e-5, then Ω² a/g = 0.00344. If they then say the effective gravity difference is 0.7%, maybe they are using the difference in |g'| between equator and pole as a percentage of the equatorial value? No.

Wait, maybe they define g as the gravitational acceleration at the Earth's surface without rotation, but they use the polar value? If g is the true gravity at the pole, and a is the equatorial radius? Then Ω² a/g_pole. g_pole ≈ 9.83. Ω² a = 0.0339. Ratio = 0.00345. Still 0.35%.

Maybe the 0.7% comes from the fact that the effective gravity at the equator is less than at the poles by about 0.7% if you include the oblateness and use a specific model? Let's calculate with the actual numbers more precisely. 
Equatorial radius a = 6378.137 km
Polar radius c = 6356.752 km
GM = 3.986004418e14 m³/s²
Ω = 7.2921150e-5 rad/s
g_e_true = GM/a² = 3.986004418e14 / (6378137)^2 = 9.79828 m/s²
g_p_true = GM/c² = 3.986004418e14 / (6356752)^2 = 9.86432 m/s²
Centrifugal at equator = Ω² a = (7.292115e-5)^2 * 6378137 = 0.03392 m/s²
Effective g at equator = 9.79828 - 0.03392 = 9.76436
Effective g at pole = 9.86432
Difference = 0.09996
Percentage less at equator = (9.86432 - 9.76436)/9.86432 * 100% = 1.013%
Percentage less at equator relative to equatorial = 1.024%
So that's ~1.0%.

If I use the standard gravity formula (which is based on the actual geoid):
g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ)
Equator: 9.780327
Pole: 9.780327 * 1.0053024 = 9.83218
Difference = 0.05185
Percentage = 0.05185/9.83218 = 0.527% (relative to pole)
or 0.05185/9.78033 = 0.530% (relative to equator)
So the actual effective gravity difference is about 0.53%.

So 0.7% is not the actual value. It's also not the spherical model value (0.35%). It's somewhere in between. Could it be that they use a = 6370 km, g = 9.81, and then compute the effective gravity difference including oblateness with a simple formula? For instance, if they assume the Earth is a sphere but the true gravity varies with latitude due to centrifugal potential? No.

Let's think about the phrase "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". If we take the ratio |g'_equator|/|g'_pole| = 1 - 0.007 = 0.993. The actual ratio is 9.7803/9.8322 = 0.9947. That's 0.53% less. 0.7% less would be 0.993, which is a difference of 0.007. The actual difference is 0.0053. So 0.7% is a bit high.

Maybe they use an older value for Earth's flattening? Historically, f = 1/297 = 0.003367. m = 0.00346. 2f+m = 0.0102. Not 0.007.

What if they use the formula for effective gravity on a rotating sphere, but they define the percentage as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That's m/(1-m) ≈ 0.0035/0.9965 = 0.00351 = 0.351%. Still not 0.7%.

Maybe they use the fact that the centrifugal term is Ω² r, and at the equator r = a, but at the pole r = 0. So the difference in centrifugal acceleration is Ω² a. But they also consider that the true gravity is less at the equator because the Earth is bulged? If they approximate the true gravity difference as also Ω² a? That would give 2Ω² a/g = 0.7%. Why would true gravity difference be Ω² a? If the Earth is in hydrostatic equilibrium, the surface is an equipotential. The potential is -GM/r - 1/2 Ω² r² cos²φ. For a point mass, the surface flattening is f = m/2. Then the true gravity difference between pole and equator is g_p - g_e ≈ 2f g = m g. So true gravity is m g less at equator
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Standard Earth parameters
    T = 86164.0905          # sidereal day in seconds
    a = 6378137.0           # equatorial radius in meters
    GM = 3.986004418e14     # gravitational parameter in m^3/s^2

    # Derived quantities
    Omega = 2 * math.pi / T
    g_true_equator = GM / a**2   # true gravity at equator (no rotation)

    # Dimensionless parameter m = Omega^2 * a / g
    m = (Omega**2 * a) / g_true_equator

    # Percentage less at equator than poles: 2*m*100%
    percentage_less = 2 * m * 100

    # Maximum angle between effective gravity and radial vector: m/2 radians
    max_angle_rad = m / 2
    max_angle_deg = max_angle_rad * (180 / math.pi)

    return {
        "1": {"value": m, "unit": ""},
        "2": {"value": percentage_less, "unit": "%"},
        "3": {"value": max_angle_deg, "unit": "deg"}
    }
```
~~~~

#### 0.87 % cluster (Clairaut) — [('deepseek-v4-flash', '1')]

#### `deepseek-v4-flash` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/deepseek-v4-flash.run1.json` → `4.5` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034677485066498316` | ✓ |
| `2` | `0.7` | `0.8723870190087706` | ✗ |
| `3` | `0.1` | `0.09951612547075678` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    omega=7.2921159e-5,  # Earth's angular velocity [rad/s]
    a=6378137.0,         # Earth's equatorial radius [m]
    g=9.780327,          # gravitational acceleration at equator [m/s^2]
    g_pole=9.832186      # gravitational acceleration at pole [m/s^2]
):
    # Compute the dimensionless parameter Omega^2 * a / g
    dimensionless = omega**2 * a / g

    # Effective gravity difference: at equator centrifugal reduces g
    # g_eff_equator = g - omega^2 * a
    # g_eff_pole = g_pole (no centrifugal)
    # Fractional difference relative to pole
    g_eff_equator = g - omega**2 * a
    frac_diff = (g_pole - g_eff_equator) / g_pole * 100  # in percent

    # Maximum angle between g' and radial direction
    # Occurs at latitude where derivative of deflection is max
    # Deflection angle phi satisfies tan(phi) = (omega^2 * a * sin(theta)*cos(theta)) / (g - omega^2 * a * sin^2(theta))
    # Maximum occurs near 45 degrees latitude
    # Use analytical maximum: sin(2*theta) = 1 -> theta=45°
    theta = math.radians(45)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    centrifugal_horizontal = omega**2 * a * sin_theta * cos_theta
    centrifugal_radial = omega**2 * a * sin_theta**2
    g_radial = g - centrifugal_radial
    phi_rad = math.atan2(centrifugal_horizontal, g_radial)
    phi_deg = math.degrees(phi_rad)

    return {
        "1": {"value": dimensionless, "unit": "dimensionless"},
        "2": {"value": frac_diff, "unit": "percent"},
        "3": {"value": phi_deg, "unit": "degrees"}
    }
```
~~~~

### The four models that flip between runs (all three runs of each)

**gemini-3.1-pro** — sub 2 across the three runs: run1: None · run2: 0.69067514062 · run3: 0.34532809882161053

#### `gemini-3.1-pro` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/gemini-3.1-pro.run1.json` → `4.5` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034532809882161053` | ✓ |
| `2` | `0.7` | `None` | ✗ |
| `3` | `0.1` | `None` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(Omega=7.292e-5, a=6.371e6, g=9.81):
    # Evaluate the dimensionless parameter Omega^2 * a / g
    dimensionless_param = (Omega ** 2) * a / g
    
    return {
        "1": {"value": dimensionless_param, "unit": "dimensionless"}
    }
```
~~~~

#### `gemini-3.1-pro` · core_code · run 2 · **PASS**

Source: `experiments/core_code/gemini-3.1-pro.run2.json` → `4.5` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034533757031` | ✓ |
| `2` | `0.7` | `0.69067514062` | ✓ |
| `3` | `0.1` | `0.09893182811027426` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(Omega=7.2921e-5, a=6371000.0, g=9.81):
    # 1. Evaluate the dimensionless parameter Omega^2 * a / g
    param = (Omega**2 * a) / g
    
    # 2. Percentage difference in effective gravity between equator and poles
    # In this simplified context, the difference is approximately 2 * param
    # (accounting for both centrifugal force and the equatorial bulge it causes)
    perc_diff = 2 * param * 100
    
    # 3. Maximum angle between effective gravity and the radial vector
    # The transverse component of centrifugal acceleration is Omega^2 * a * sin(phi) * cos(phi)
    # This is maximized at phi = 45 degrees, where sin(phi)*cos(phi) = 0.5
    max_angle_rad = math.atan((0.5 * Omega**2 * a) / g)
    max_angle_deg = math.degrees(max_angle_rad)
    
    return {
        "1": {"value": param, "unit": "dimensionless"},
        "2": {"value": perc_diff, "unit": "%"},
        "3": {"value": max_angle_deg, "unit": "degrees"}
    }
```
~~~~

#### `gemini-3.1-pro` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/gemini-3.1-pro.run3.json` → `4.5` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034532809882161053` | ✓ |
| `2` | `0.7` | `0.34532809882161053` | ✗ |
| `3` | `0.1` | `0.09910022485764661` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(omega=7.292e-5, a=6.371e6, g=9.81):
    # 1. Dimensionless parameter Omega^2 * a / g
    param = (omega**2) * a / g
    
    # 2. Percentage difference in effective gravity (equator vs pole) due to centrifugal force
    # Assuming a spherical Earth, the difference is just the centrifugal acceleration at the equator.
    # Note: The problem statement mentions "about 0.7%", which may include Earth's oblateness 
    # or a factor of 2 error in a textbook's simplified model, but we compute the direct centrifugal contribution here.
    pct_diff = param * 100
    
    # 3. Maximum angle between effective gravity and the radial vector
    # This occurs at latitude = 45 degrees.
    # Tangential component = Omega^2 * a * cos(45) * sin(45) = Omega^2 * a / 2
    # Radial component = g - Omega^2 * a * cos^2(45) = g - Omega^2 * a / 2
    angle_rad = math.atan((param / 2) / (1 - param / 2))
    angle_deg = math.degrees(angle_rad)
    
    return {
        "1": {"value": param, "unit": "dimensionless"},
        "2": {"value": pct_diff, "unit": "%"},
        "3": {"value": angle_deg, "unit": "deg"}
    }
```
~~~~

**deepseek-v4-pro-reasoning** — sub 2 across the three runs: run1: 0.34533907628862187 · run2: 0.6922785425954682 · run3: 0.6883011796413865

#### `deepseek-v4-pro-reasoning` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run1.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.003453390762886219` | ✓ |
| `2` | `0.7` | `0.34533907628862187` | ✗ |
| `3` | `0.1` | `0.09910338054914007` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

RESPONSE (verbatim, untruncated):

~~~~
We need to evaluate the dimensionless parameter Ω^2 a / g for Earth. Then show that at Earth's surface, the magnitude of effective gravity |g'| is about 0.7% less at equator than poles, and the maximum angle between g' and a vector pointing towards Earth's centre is about 0.1°.

We need to write a Python function `solve()` that computes these quantities and returns a dict with entries "1", "2", "3" for the three asked things? The problem says: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

So the quantities asked:
1. Dimensionless parameter Ω^2 a / g.
2. Percentage difference of |g'| at equator vs poles? "about 0.7% less" – we need to compute the exact percentage.
3. Maximum angle between g' and radial vector, about 0.1°.

We need to return these three values with units. For dimensionless parameter, unit is "" (dimensionless). For percentage, unit "%". For angle, unit "deg" or "°"? We'll use "deg".

We need to use standard Earth parameters: Earth's rotation rate Ω, equatorial radius a, and surface gravity g (presumably mean or reference?). Usually g is the gravitational acceleration (not effective) at the surface? The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." Typically g here is the gravitational acceleration due to mass alone, not the effective gravity. But sometimes g is the standard gravity 9.81 m/s². We need to be careful. The effective gravity g' = g - Ω × (Ω × r). The magnitude at equator: g'_eq = g - Ω^2 a (if g is the gravitational acceleration, pointing towards center). At poles: g'_pole = g (no centrifugal term). So percentage difference = (g'_pole - g'_eq)/g'_pole * 100% = (Ω^2 a / g) * 100%? Actually g'_pole = g (assuming spherical Earth, gravitational acceleration same at poles and equator? But Earth is oblate, so g is larger at poles. However, the problem likely uses a simplified model: spherical Earth with radius a, uniform gravitational acceleration g. Then effective gravity at equator is g - Ω^2 a, at poles is g. So the fractional difference is Ω^2 a / g. That's exactly the dimensionless parameter. So the dimensionless parameter itself is about 0.00344? Let's check: Ω = 2π / 86400 s = 7.2921e-5 rad/s. a = 6371 km = 6.371e6 m. g = 9.81 m/s². Ω^2 a = (7.2921e-5)^2 * 6.371e6 ≈ 5.31e-9 * 6.371e6 ≈ 0.0338 m/s². Then Ω^2 a / g ≈ 0.0338 / 9.81 ≈ 0.00345 = 0.345%. But the problem says about 0.7% less. Wait, 0.7% is about double. Let's recalc: Earth's equatorial radius is about 6378 km, polar radius 6357 km. The centrifugal acceleration at equator is Ω^2 a = (7.2921e-5)^2 * 6378e3 = 0.0339 m/s². Standard gravity g is 9.78 at equator, 9.83 at poles? Actually effective gravity at equator is about 9.78 m/s², at poles 9.83 m/s². Difference is about 0.05 m/s², which is about 0.5% of 9.8? 0.05/9.8 = 0.0051 = 0.51%. But the problem says 0.7% less. Maybe they use a different g? Let's check typical textbook values: The dimensionless parameter Ω^2 a / g is often quoted as 1/289 ≈ 0.00346. The flattening of Earth is about 1/298. The effective gravity difference between equator and poles is about 0.5%? Actually, the formula for effective gravity on a rotating oblate Earth includes both centrifugal and gravitational flattening effects. The total difference is about 0.5%? Wait, I recall that the difference in g between equator and poles is about 0.052 m/s², which is about 0.53% of 9.8. But the problem says "about 0.7% less". Maybe they use g as the gravitational acceleration without rotation, and the effective gravity at equator is g - Ω^2 a, and at poles is g. But then the percentage difference is Ω^2 a / g. If we use g = 9.81, Ω^2 a / g = 0.00345 = 0.345%. Not 0.7%. If we use g = 9.78 (effective at equator), then Ω^2 a / g_eff = 0.0339/9.78 = 0.00347 = 0.347%. Still not 0.7%. Maybe they consider the difference relative to the equatorial value? (g_pole - g_eq)/g_eq * 100% = (Ω^2 a)/(g - Ω^2 a) * 100% ≈ 0.35%? No.

Let's re-read: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". That means (|g'_pole| - |g'_eq|) / |g'_pole| * 100% ≈ 0.7%? Or less at equator than poles: (g_pole - g_eq)/g_pole * 100% = 0.7%? If g_pole = 9.83, g_eq = 9.78, difference = 0.05, 0.05/9.83 = 0.0051 = 0.51%. Not 0.7%. Maybe they use a different Earth model? Perhaps they use a = 6371 km, g = 9.8, but also consider the gravitational flattening? The problem might be from a textbook where they derive that the effective gravity difference is about 0.7%? Let's search memory: In some atmospheric science contexts, the dimensionless parameter Ω^2 a / g is about 1/289 = 0.00346. The difference in effective gravity between equator and poles is about 0.35%? Actually, the effective gravity on a rotating Earth with flattening: g_eq ≈ 9.78, g_pole ≈ 9.83, difference ≈ 0.05, percentage = 0.05/9.8 = 0.5%. Some sources say 0.5%. But the problem says 0.7%. Could it be that they use g as the gravitational constant (GM/R^2) and then the effective gravity at equator is g - Ω^2 a, and at poles is g (assuming spherical). Then the percentage difference is Ω^2 a / g. If they use g = 9.8, Ω^2 a = 0.034, ratio = 0.00347 = 0.347%. Not 0.7%. If they use g = 9.78, ratio = 0.034/9.78 = 0.00348. Still 0.35%.

Maybe the problem uses a different definition: "about 0.7% less" might be a misprint? Or maybe they mean the effective gravity is 0.7% less than the true gravity? No, "at the equator than at the poles". Let's check typical numbers: Earth's equatorial radius a = 6378 km, polar radius c = 6357 km. The gravitational acceleration at equator (without rotation) is GM/a^2, at poles GM/c^2. The effective gravity at equator is GM/a^2 - Ω^2 a. At poles it's GM/c^2. The difference is about 0.07 m/s^2? Actually, GM = 3.986e14 m^3/s^2. GM/a^2 = 3.986e14/(6.378e6)^2 = 9.798 m/s^2. GM/c^2 = 3.986e14/(6.357e6)^2 = 9.865 m/s^2. Effective g_eq = 9.798 - 0.034 = 9.764 m/s^2. g_pole = 9.865. Difference = 0.101 m/s^2. Percentage = 0.101/9.865 = 1.02%? That's about 1%. Not 0.7%.

Wait, maybe the problem is from a specific textbook. "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." This sounds like a problem from "Atmospheric Science" by Wallace and Hobbs, or similar. In Wallace & Hobbs, they might use a = 6371 km, g = 9.81 m/s^2, Ω = 7.292e-5 rad/s. Then Ω^2 a / g = (7.292e-5)^2 * 6.371e6 / 9.81 = 0.00344. They might then say the effective gravity difference is about 0.34%? But the problem says 0.7%. Could it be that they use g as the effective gravity at the poles? Or maybe they consider the difference relative to the equatorial value? (g_pole - g_eq)/g_eq = Ω^2 a / (g - Ω^2 a) ≈ 0.00347 = 0.347%. Still not 0.7%.

Let's compute precisely with standard values: Ω = 7.2921159e-5 rad/s, a = 6378137 m (equatorial radius), g = 9.780327 m/s^2 (effective at equator)? Actually, standard gravity formula: g = 9.780327 (1 + 0.0053024 sin^2 φ - 0.0000058 sin^2 2φ). At equator, g = 9.780327. At poles, g = 9.832186. Difference = 0.051859. Percentage = 0.051859/9.832186 = 0.00527 = 0.527%. Still not 0.7%.

Maybe the problem uses a simplified Earth with radius R = 6400 km, g = 10 m/s^2? Then Ω = 2π/86400 = 7.27e-5. Ω^2 R = (7.27e-5)^2 * 6.4e6 = 5.29e-9 * 6.4e6 = 0.0339. g = 10. Ratio = 0.00339 = 0.339%. Still not 0.7%.

What if they use g as the gravitational acceleration (without centrifugal) and the effective gravity difference is (g_pole_eff - g_eq_eff)/g_pole_eff? If Earth is spherical, g_pole_eff = g, g_eq_eff = g - Ω^2 a. Difference = Ω^2 a. Percentage = Ω^2 a / g. That's the dimensionless parameter. If that parameter is 0.7% = 0.007, then Ω^2 a / g = 0.007. But actual is ~0.0035. So maybe they use a different planet? No, it's Earth.

Wait, maybe the problem is asking to show that the effective gravity is about 0.7% less at the equator than at the poles *due to the combined effect of centrifugal force and the Earth's oblateness*? In some textbooks, they derive that the total difference is about 0.5% or 0.7%? Let's check: The flattening f = (a-c)/a = 1/298.257. The gravitational acceleration difference due to oblateness is about (5/2) m Ω^2 a? Actually, for a rotating fluid planet in hydrostatic equilibrium, the surface gravity variation is given by g = g_e (1 + (5/2 m - f) sin^2 φ) where m = Ω^2 a / g_e. For Earth, m ≈ 0.00346, f ≈ 0.00335. Then g_pole/g_eq = 1 + (5/2)m - f ≈ 1 + 0.00865 - 0.00335 = 1.0053. So difference is 0.53%. Still not 0.7%.

Maybe the problem uses a different value for g? If they use g = 9.8, and a = 6371 km, Ω = 7.292e-5, then Ω^2 a = 0.0339. If they mistakenly use g as 9.8 but compute percentage as (Ω^2 a)/g * 100% = 0.346%. Not 0.7%. If they use g = 9.8 and a = 6371, but maybe they use Ω = 2π/86164? Sidereal day? Ω = 2π/86164 = 7.2921e-5, same.

What if they use a = 6371 km, g = 9.81, but the percentage is (g_pole - g_eq)/g_eq * 100%? That would be Ω^2 a / (g - Ω^2 a) * 100% ≈ 0.034/9.776 = 0.00348 = 0.348%. No.

Maybe the problem is from a different context: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." That is one part. Then "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" – perhaps they are using the result from the dimensionless parameter to infer something else? Could it be that the dimensionless parameter is Ω^2 a / g, and they want to show that the effective gravity difference is about 2 * Ω^2 a / g? No.

Let's search my memory: In the book "Atmospheric Science: An Introductory Survey" by Wallace and Hobbs, 2nd edition, Chapter 1, there is a problem: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." I recall a similar problem. The answer might be: Ω^2 a / g ≈ 1/289 = 0.00346. The effective gravity difference is about 0.7%? Wait, maybe they use g as the effective gravity at the poles? No.

Let's compute with actual Earth values: The effective gravity at the equator is about 9.78 m/s^2, at the poles about 9.83 m/s^2. The difference is 0.05 m/s^2. 0.05/9.78 = 0.0051 = 0.51%. 0.05/9.83 = 0.0051. Not 0.7%. However, if we use the true gravitational acceleration (without centrifugal) at the equator and poles, the difference is larger. But the problem says "effective gravity |g'|". So it's the observed gravity.

Maybe the problem expects the student to use a simple model where the Earth is a sphere of radius a, and the gravitational acceleration g is constant. Then effective gravity at equator: g' = g - Ω^2 a. At poles: g' = g. The percentage difference = (g - (g - Ω^2 a))/g = Ω^2 a / g. If they use g = 9.8 m/s^2, a = 6371 km, Ω = 7.292e-5, then Ω^2 a / g = 0.00345 = 0.345%. That's not 0.7%. But maybe they use g = 9.8 m/s^2 and a = 6371 km, but they also consider that the Earth's radius is larger at the equator? If they use a = 6378 km, g = 9.78? Still ~0.35%.

Wait, could it be that the dimensionless parameter is Ω^2 a / g, and they want to show that the effective gravity is about 0.7% less at the equator than at the poles *because of the combined effect of centrifugal force and the Earth's equatorial bulge*? In that case, the total difference is about 0.5%, not 0.7%. Some sources say 0.5%, some say 0.7%? Let's check: The difference between polar and equatorial effective gravity is about 0.052 m/s^2. 0.052/9.78 = 0.0053 = 0.53%. 0.052/9.8 = 0.0053. If we use g = 9.81, 0.052/9.81 = 0.0053. Not 0.7%.

Maybe they use a different value for g? If g = 9.8, and they compute (g_pole - g_eq)/g_eq * 100% = (Ω^2 a)/(g - Ω^2 a) * 100% ≈ 0.034/9.766 = 0.00348 = 0.35%. No.

What if the problem uses a = 6371 km, g = 9.8, but Ω = 2π/86400? That's what we did. Maybe they use g = 9.81, a = 6371, Ω = 7.29e-5, then Ω^2 a = 0.0337, ratio = 0.00344. 

Wait, I found a reference: In the book "Atmospheric Science" by Wallace and Hobbs, 2nd edition, Problem 1.1: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." The solution manual might have the answer. Let's think: They might use a = 6371 km, g = 9.81 m/s^2, Ω = 7.292e-5 rad/s. Then Ω^2 a / g = 0.00344. Then they might say the effective gravity difference is about 0.7%? That doesn't match. Unless they use g as the gravitational acceleration (without centrifugal) and then the effective gravity at equator is g - Ω^2 a, and at poles is g. The percentage difference is Ω^2 a / g = 0.344%. Not 0.7%. 

Maybe they use a different definition: "about 0.7% less" might be a misprint in my memory, or maybe they mean the effective gravity is about 0.7% less than the true gravity at the equator? No, "less at the equator than at the poles".

Let's re-read carefully: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Perhaps the dimensionless parameter is Ω^2 a / g, and then they use that to show the 0.7%? Could it be that the effective gravity difference is actually 2 * Ω^2 a / g? No.

Let's compute with a more precise model: The effective gravity on a rotating oblate spheroid. The formula for effective gravity at latitude φ is approximately g = g_e (1 + β sin^2 φ), where β = (5/2)m - f, with m = Ω^2 a / g_e, f = flattening. For Earth, m ≈ 0.003467, f ≈ 0.003353. Then β ≈ 0.008675 - 0.003353 = 0.005322. So g_pole/g_eq = 1 + β ≈ 1.005322, so difference is 0.5322%. Still not 0.7%.

What if they use a spherical Earth but with g varying with latitude due to centrifugal force only? Then g' = g - Ω^2 a cos^2 φ. At equator, g' = g - Ω^2 a. At poles, g' = g. Difference = Ω^2 a. Percentage = Ω^2 a / g. If g = 9.8, Ω^2 a = 0.034, ratio = 0.00347 = 0.347%. Not 0.7%.

Maybe they use a = 6371 km, g = 9.8, but Ω = 2π/86164? Same.

Wait, could it be that they use g = 9.8 m/s^2, but a = 6371 km, and they compute Ω^2 a / g = 0.00344, and then they say the effective gravity is about 0.7% less? That would be a factor of 2 off. Maybe they consider the difference between equatorial and polar effective gravity as a fraction of the equatorial value? (g_pole - g_eq)/g_eq = Ω^2 a / (g - Ω^2 a) ≈ 0.00347 = 0.35%. No.

Perhaps the problem uses a different value for Earth's radius? If they use a = 6371 km, but g = 9.8, and they mistakenly use Ω = 2π/86400 but in degrees? No.

Let's search my knowledge base: In some textbooks, the dimensionless parameter is Ω^2 R / g, and its value is about 1/289 ≈ 0.00346. The difference in effective gravity between equator and poles is about 0.5% (or 0.7%?). I recall that the effective gravity at the equator is about 9.78 m/s^2, at poles 9.83 m/s^2, difference 0.05 m/s^2, which is 0.5% of 9.8. But 0.05/9.78 = 0.0051 = 0.51%. 0.05/9.83 = 0.0051. Some sources round to 0.5%. Others might say 0.7%? Let's check: 9.83 - 9.78 = 0.05. 0.05/9.8 = 0.0051. If they use g = 9.78, difference = 0.05, percentage = 0.05/9.78 = 0.511%. If they use g = 9.8, percentage = 0.51%. Not 0.7%.

Maybe the problem uses the true gravitational acceleration (without centrifugal) at the equator and poles? The true gravity at equator (GM/a^2) is about 9.798, at poles (GM/c^2) is about 9.865. Difference = 0.067. Percentage = 0.067/9.865 = 0.68% ≈ 0.7%! That's it! The problem says "effective gravity |g'|". But effective gravity includes centrifugal. However, sometimes "effective gravity" is defined as the vector sum of gravitational and centrifugal forces. The magnitude of effective gravity at the equator is g' = g* - Ω^2 a, where g* is the gravitational acceleration. At the poles, g' = g* (no centrifugal). The difference in effective gravity between poles and equator is (g*_pole - g*_eq) + Ω^2 a? Actually, if we consider the oblate Earth, the gravitational acceleration g* varies with latitude. The effective gravity is g' = g* - Ω^2 R cos^2 φ (radial component approximately). The total difference between poles and equator is due to both the variation in g* and the centrifugal term. The problem might be asking to show that the magnitude of effective gravity is about 0.7% less at the equator than at the poles. If we use the actual Earth numbers, the effective gravity at equator is ~9.78, at poles ~9.83, difference ~0.05, which is 0.5%. But if we use the true gravity difference (without centrifugal), it's 0.7%. But the problem says "effective gravity". 

Wait, maybe the problem is from a textbook that uses a simplified Earth model where the Earth is a sphere, so g* is constant. Then effective gravity difference is Ω^2 a / g* = 0.35%. That's not 0.7%. So they must be including the oblateness. In that case, the dimensionless parameter Ω^2 a / g is evaluated with g being the effective gravity at the equator? Or g being the mean gravity? The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." Usually, in such problems, g is the acceleration due to gravity (effective or true?). In the context of the dimensionless parameter, it's often the effective gravity at the surface, or the standard gravity. Let's check typical values: Ω = 7.292e-5 rad/s, a = 6371 km (mean radius) or 6378 km (equatorial). g = 9.81 m/s^2. Then Ω^2 a / g = 0.00344. If they use a = 6378 km, g = 9.78, then Ω^2 a / g = (7.292e-5)^2 * 6378e3 / 9.78 = 0.0339 / 9.78 = 0.00347. Still ~0.0035.

Now, the maximum angle between g' and the radial vector: For a spherical Earth, the angle α between effective gravity g' and the true radial direction is given by tan α = (Ω^2 R sin φ cos φ) / (g - Ω^2 R cos^2 φ). The maximum occurs at φ = 45°, and tan α ≈ Ω^2 R / (2g) for small angles. α ≈ 0.1°? Let's compute: Ω^2 R / (2g) = 0.0339 / (2*9.81) = 0.00173 rad. In degrees: 0.00173 * 180/π = 0.099° ≈ 0.1°. So that matches.

So the angle part is straightforward and gives ~0.1°.

Now, for the 0.7% difference: If we use the spherical Earth model, the difference is Ω^2 a / g = 0.35%, not 0.7%. So the problem must be using a different value for g, or they are considering the combined effect of oblateness and centrifugal force, and the total difference is about 0.7%? But actual effective gravity difference is ~0.5%. Let's compute more precisely: Using WGS84: equatorial effective gravity = 9.7803253359 m/s^2, polar effective gravity = 9.8321849378 m/s^2. Difference = 0.0518596 m/s^2. Ratio to polar = 0.05186/9.83218 = 0.005275 = 0.5275%. Ratio to equatorial = 0.05186/9.78033 = 0.005302 = 0.5302%. So it's about 0.53%. Not 0.7%.

Maybe the problem uses a different Earth model: e.g., radius = 6400 km, g = 10 m/s^2, Ω = 7.27e-5, then Ω^2 a = 0.0338, g = 10, ratio = 0.338%. Still not 0.7%.

What if they use the true gravitational acceleration difference? The true gravity at equator (GM/a^2) = 9.798, at poles (GM/c^2) = 9.865. Difference = 0.067. Ratio = 0.067/9.865 = 0.0068 = 0.68% ≈ 0.7%. But that's true gravity, not effective gravity. The problem says "effective gravity |g'|". However, sometimes "effective gravity" is defined as the gravity including the centrifugal force, but the centrifugal force is already subtracted. The difference in effective gravity between poles and equator is less than the difference in true gravity because the centrifugal force reduces the equatorial value further. So effective gravity difference is smaller. So 0.7% cannot be the effective gravity difference if we use real Earth data.

Wait, maybe the problem is from a textbook that uses a different definition: "effective gravity" might be the gravity due to the Earth's mass alone (without centrifugal)? No, effective gravity usually includes centrifugal.

Let's search memory: I recall a problem in "Atmospheric Science" by Wallace and Hobbs (1st edition?) where they ask to show that the effective gravity is about 0.7% less at the equator than at the poles. I think the answer in the solution manual might use the following: They assume the Earth is a sphere of radius a, and g is the gravitational acceleration (9.81 m/s^2). Then they compute the effective gravity at equator: g' = g - Ω^2 a. At poles: g' = g. The percentage difference is (Ω^2 a)/g * 100%. They might have used a = 6371 km, g = 9.8 m/s^2, Ω = 7.292e-5, then Ω^2 a = 0.0339, ratio = 0.00346 = 0.346%. That's not 0.7%. But if they mistakenly used the diameter instead of radius? No.

Maybe they use g = 9.8, but a = 6371 km, and they compute Ω^2 a / g = 0.00346, then they say "about 0.7%" because they multiply by 2? No.

Let's check the angle: maximum angle is about 0.1°. That comes from tan α = Ω^2 a / (2g) for small angles. α ≈ Ω^2 a / (2g) radians. Ω^2 a / g = 0.00346, so α ≈ 0.00173 rad = 0.099°. So that matches perfectly with Ω^2 a / g ≈ 1/289.

Now, if Ω^2 a / g = 1/289 ≈ 0.00346, then the percentage difference in effective gravity for a spherical Earth is 0.346%. The problem says 0.7%. Could it be that they are asking to show that the effective gravity is about 0.7% less at the equator than at the poles *due to the combined effect of rotation and oblateness*? In that case, the total difference is about 0.5%, not 0.7%. But maybe they use a different flattening? If Earth's flattening is 1/298, and m = Ω^2 a / g = 1/289, then the total effective gravity variation is (5/2)m - f = 2.5*0.00346 - 0.00336 = 0.00865 - 0.00336 = 0.00529 = 0.529%. Still not 0.7%.

What if they use the equatorial effective gravity as g in the dimensionless parameter? Then m = Ω^2 a / g_eq. g_eq ≈ 9.78, Ω^2 a = 0.0339, m = 0.00347. Then the total variation is (5/2)m - f. If f = 1/298 = 0.00336, then 2.5*0.00347 = 0.00868, minus 0.00336 = 0.00532 = 0.53%. 

Maybe the problem uses a different value for Earth's radius? If they use a = 6371 km, but g = 9.8, and they compute the difference as (g_pole - g_eq)/g_eq * 100%? That would be Ω^2 a / (g - Ω^2 a) * 100% ≈ 0.034/9.766 = 0.348%. No.

Wait, could it be that the problem is from a textbook that uses g = 9.81 m/s^2, a = 6371 km, but they also include the fact that the Earth is not a sphere, and they derive that the effective gravity difference is about 0.7%? Let's compute with a simple model: The Earth is an oblate spheroid with equatorial radius a and polar radius c. The gravitational potential at the surface is approximately GM/R (1 - J2 (a/R)^2 P2(cos θ)). The effective gravity includes centrifugal. The difference between pole and equator effective gravity is approximately (5/2) Ω^2 a - (GM/a^2) * (3/2) J2? Actually, the formula is g_pole - g_eq ≈ (5/2) Ω^2 a - (GM/a^2) * (something). For Earth, J2 ≈ 1.0826e-3. GM = 3.986e14, a = 6378e3. GM/a^2 = 9.798. The gravitational flattening term gives a difference of about 3/2 J2 * GM/a^2? Actually, g_pole (grav) ≈ GM/a^2 (1 + 3/2 J2) (if we approximate). g_eq (grav) ≈ GM/a^2 (1 - 3/4 J2)? Let's not guess.

Maybe the problem expects the student to use the following values: Earth's radius R = 6.37e6 m, g = 9.8 m/s^2, Ω = 7.29e-5 rad/s. Then Ω^2 R / g = 0.00345. Then the effective gravity difference is 0.345%. But the problem says 0.7%. Could it be a typo in the problem statement? "0.7%" might be "0.35%"? But it says "0.7%". Let's check the angle: 0.1° is correct for the spherical Earth model. If the problem is from a textbook, the answer for the percentage might be "about 0.35%" but the problem statement says "0.7%". I need to re-read the problem statement carefully: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". It explicitly says 0.7%. 

Maybe they define "effective gravity" differently. In some contexts, effective gravity is the vector sum of gravitational and centrifugal forces, but its magnitude is often denoted g. The difference between equatorial and polar g is about 0.5% (as observed). But 0.5% is not 0.7%. 

Let's search online memory: There's a known problem: "Evaluate the dimensionless parameter Ω^2 R/g for the Earth. Show that at the Earth's surface the effective gravity is about 0.7% less at the equator than at the poles..." I think I've seen this exact wording. The solution might use R = 6371 km, g = 9.81 m/s^2, Ω = 7.292e-5 rad/s. Then Ω^2 R/g = 0.00344. Then they might say the effective gravity difference is (Ω^2 R)/g * 100% = 0.344%? No. 

Wait, maybe they use g as the effective gravity at the poles? If g_pole = 9.83, g_eq = 9.78, difference = 0.05, 0.05/9.83 = 0.0051 = 0.51%. Still not 0.7%.

What if they use a = 6371 km, g = 9.8, but they compute the difference as (g_pole - g_eq)/g_eq? That's 0.034/9.766 = 0.00348 = 0.35%.

Maybe the problem uses the fact that the Earth's radius is larger at the equator, so the gravitational acceleration is smaller. If they assume the Earth is a sphere, they get 0.35%. If they include the oblateness, they get about 0.5%. To get 0.7%, they might be using a different value for g. For instance, if they use g = 9.8 m/s^2 as the true gravity, and then effective gravity at equator is g - Ω^2 a = 9.8 - 0.034 = 9.766. At poles, effective gravity is g = 9.8. Difference = 0.034. Percentage = 0.034/9.8 = 0.347%. No.

What if they use g = 9.8, but a = 6371 km, and they compute Ω^2 a = 0.0339, then they say the effective gravity is 0.7% less? That would require Ω^2 a / g = 0.007, so Ω^2 a = 0.0686, which would require Ω = sqrt(0.0686/6371000) = sqrt(1.077e-8) = 1.038e-4 rad/s, which is a period of about 16 hours. Not Earth.

Maybe the problem uses a = 6371 km, g = 9.81, but they also include the fact that the Earth's equatorial radius is 6378 km and polar is 6357 km, and they compute the effective gravity difference using the formula g' = GM/R^2 - Ω^2 R cos^2 φ. If they use GM = g a^2 where g=9.81, a=6371? Then at equator: g' = g (a/R_eq)^2 - Ω^2 R_eq. At poles: g' = g (a/R_pole)^2. If R_eq = 6378, R_pole = 6357, a = 6371. Then g' at equator = 9.81*(6371/6378)^2 - 0.0339 = 9.81*0.9978 - 0.0339 = 9.788 - 0.0339 = 9.754. At poles: 9.81*(6371/6357)^2 = 9.81*1.0044 = 9.853. Difference = 0.099. Percentage = 0.099/9.853 = 0.010 = 1.0%. Not 0.7%.

Maybe they use a different GM? 

Let's think about the angle: maximum angle between g' and radial vector. For a spherical Earth, it's about 0.1°. For an oblate Earth, the angle is slightly different but still ~0.1°. So that part is consistent with the spherical model.

Given that the problem asks to "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." and then "Show that...", it's likely that the dimensionless parameter is used to derive the other quantities. In a spherical Earth model, the fractional difference in effective gravity between equator and poles is exactly Ω^2 a / g. The maximum angle is approximately (1/2) Ω^2 a / g in radians. So if Ω^2 a / g = 0.00344, then the fractional difference is 0.344%, and the angle is 0.00172 rad = 0.0985° ≈ 0.1°. The problem says "about 0.7% less". That's a factor of 2 larger. Could it be that they define the percentage difference as (g_pole - g_eq) / g_eq * 100%? That would be Ω^2 a / (g - Ω^2 a) ≈ Ω^2 a / g * (1 + Ω^2 a/g) ≈ 0.344% * 1.003 = 0.345%. Still not 0.7%.

Maybe they use g as the effective gravity at the equator? Then Ω^2 a / g_eq = 0.0339/9.78 = 0.00347. Still 0.35%.

What if the problem uses a = 6371 km, g = 9.8, but they compute the difference in effective gravity as (g_pole - g_eq) / g_mean * 100%? Same.

Wait, could it be that the problem is from a textbook that uses the value of g as 9.8 m/s^2, but they use a = 6371 km, and they compute Ω^2 a / g = 0.00344, and then they say "about 0.7%" because they mistakenly think 0.00344 is 0.34%? No, 0.00344 is 0.344%, not 0.7%.

Maybe the problem uses a different Earth rotation rate? If Earth rotated once every 12 hours? No.

Let's search my memory for the exact phrase: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." I think this is from "Atmospheric Science" by Wallace and Hobbs, Problem 1.1. I found a reference online in my mind: The solution is something like: Ω = 7.292e-5 s^-1, a = 6371 km, g = 9.81 m s^-2, so Ω^2 a / g = 3.44e-3. The effective gravity at equator is g - Ω^2 a, at poles is g. The percentage difference is (Ω^2 a / g) * 100% = 0.34%. But the problem says 0.7%. Wait, maybe they use a = 6378 km (equatorial radius) and g = 9.78 m/s^2 (effective at equator)? Then Ω^2 a / g = 0.0339/9.78 = 0.00347 = 0.35%. Still not 0.7%.

Could it be that they are asking to show that the effective gravity is about 0.7% less at the equator than at the poles *due to the combined effect of centrifugal force and the Earth's oblateness*? In that case, the total difference is about 0.5%, but maybe they round 0.5% to 0.7%? No, 0.5 is not 0.7.

Let's check the actual numbers from Wallace and Hobbs. I recall that in the 2nd edition, Chapter 1, Problem 1.1: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." I think the solution manual says: Ω^2 a / g = 3.44e-3. The effective gravity at the equator is g - Ω^2 a, so the fractional decrease is Ω^2 a / g = 0.34%. But the problem says 0.7%? That's a discrepancy. Maybe I misremember the number. Could it be 0.35%? The problem says "0.7%". Let me think: 0.7% of 9.8 is 0.0686. The centrifugal acceleration is 0.034. So 0.034 is 0.35% of 9.8. So 0.7% is double. Maybe they consider the difference between equator and poles as a percentage of the equatorial value? (g_pole - g_eq)/g_eq = 0.034/9.766 = 0.00348 = 0.35%. No.

What if they use g as the gravitational acceleration (without centrifugal) and the effective gravity at equator is g - Ω^2 a, and at poles is g. The percentage difference is Ω^2 a / g. If they use g = 9.8, it's 0.35%. If they use g = 9.78, it's 0.35%. 

Wait, maybe the problem uses a = 6371 km, g = 9.8, but they also include the fact that the Earth's radius is larger at the equator, so the gravitational acceleration is smaller. In a simple model, the Earth's equatorial bulge is due to rotation. The flattening f is approximately (5/4) Ω^2 a / g? Actually, for a homogeneous fluid Earth, f = (5/4) m, where m = Ω^2 a / g. For Earth, m = 0.00346, so f = 0.00433. The actual flattening is 0.00335. The difference in effective gravity between pole and equator is approximately (5/2)m - f? Wait, the formula for effective gravity on a rotating oblate spheroid is g = g_e [1 + (5m/2 - f) sin^2 φ]. So the fractional difference between pole and equator is (5m/2 - f). If we take m = 0.00346, and f = 0.00335, then 5m/2 - f = 0.00865 - 0.00335 = 0.00530 = 0.53%. If we take the hydrostatic equilibrium value f = (5/4)m = 0.004325, then 5m/2 - f = 2.5m - 1.25m = 1.25m = 1.25 * 0.00346 = 0.004325 = 0.43%. Still not 0.7%.

What if they use m = Ω^2 a / g, and then the effective gravity difference is 2m? No.

Maybe the problem uses a different definition of g. In some contexts, g is the standard gravity 9.80665 m/s^2. Then Ω^2 a = 0.0339, ratio = 0.00346. Still 0.35%.

Let's search the web mentally: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth" - this is a common problem. The answer is usually 1/289 or 0.00346. The effective gravity difference is often stated as 0.5% or 0.35%? I'm confused.

Wait, I recall that the effective gravity at the equator is about 9.78 m/s^2, and at the poles about 9.83 m/s^2. The difference is 0.05 m/s^2. 0.05/9.78 = 0.0051 = 0.51%. 0.05/9.83 = 0.0051. Some sources say "about 0.5%". But the problem says 0.7%. Could it be a typo in the problem statement? Possibly the problem originally said "0.35%" or "0.5%"? But the user provided the exact text: "about 0.7% less". I must work with that.

Maybe the problem expects the student to compute the dimensionless parameter, and then use it to find the percentage difference and angle. If the dimensionless parameter is Ω^2 a / g, and the percentage difference is exactly that times 100%? That gives ~0.35%. But the problem says 0.7%. Could it be that they define the percentage difference as (g_pole - g_eq) / g_eq * 100%? That's Ω^2 a / (g - Ω^2 a) * 100% ≈ 0.35%. No.

What if they use a = 6371 km, g = 9.8, but they compute Ω^2 a / g = 0.00344, and then they say the effective gravity is 0.7% less because they mistakenly multiply by 2? Or maybe they consider the difference between the effective gravity and the true gravity? "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" - comparing equator to poles. 

Let's calculate the maximum possible difference if we use the true gravity variation. True gravity at equator: GM/a^2. At poles: GM/c^2. For a = 6378 km, c = 6357 km. GM = 3.986004418e14. GM/a^2 = 9.798, GM/c^2 = 9.865. Difference = 0.067. Percentage = 0.067/9.865 = 0.68% ≈ 0.7%. So if "effective gravity" here actually means the true gravitational acceleration (without centrifugal), then it's 0.7%. But the problem says "effective gravity |g'|". Usually g' denotes effective gravity (including centrifugal). However, in some textbooks, they might use g' for the gravitational acceleration and g for effective? No, typically g is effective, g* is gravitational. 

Let's read the problem again: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." 

Maybe they use g in the dimensionless parameter as the effective gravity at the poles? Or the mean effective gravity? If g is the effective gravity at the poles, and they compute Ω^2 a / g, then the effective gravity at equator is g - Ω^2 a (if spherical). Then the percentage difference is Ω^2 a / g. If they use g = 9.83, Ω^2 a = 0.034, ratio = 0.00346 = 0.35%. Still not 0.7%.

What if they use a = 6371 km, g = 9.8, but they also include the oblateness in the effective gravity? The effective gravity difference is about 0.5%. Not 0.7%.

Maybe the problem uses a different value for Earth's rotation rate? The Earth's rotation period is 24 hours, but sometimes the sidereal day is used: 23h 56m 4s = 86164 s. Ω = 2π/86164 = 7.2921e-5. Same.

What if they use a = 6371 km, g = 9.81, but they compute the percentage as (Ω^2 a) / (g - Ω^2 a) * 100%? That's 0.034/9.776 = 0.35%.

I'm starting to think that the "0.7%" might be a misprint in the problem statement, and the actual answer is around 0.35% or 0.5%. But as an AI, I need to follow the problem as given. The problem says "Show that... is about 0.7% less...". So I need to compute the actual percentage difference using standard Earth parameters and see if it rounds to 0.7%? No, it doesn't. Maybe they use a very rough approximation: Earth's radius = 6400 km, g = 10 m/s^2, Ω = 2π/86400 = 7.27e-5. Then Ω^2 a = 0.0338. g = 10. Ratio = 0.00338 = 0.34%. Still not 0.7%.

What if they use g = 9.8, but a = 6371 km, and they compute the difference in effective gravity as (g_pole - g_eq) / g_eq * 100% = 0.034/9.766 = 0.35%. 

Wait, maybe the problem is from a textbook that uses the value of g as the gravitational acceleration at the surface of a spherical Earth, and then the effective gravity at the equator is g - Ω^2 a, and at the poles is g. The percentage difference is Ω^2 a / g. If they use g = 9.8, it's 0.35%. But if they use g = 9.8 and a = 6371, and they mistakenly use Ω = 2π/86400 but in degrees? No.

Let's think about the angle: maximum angle is about 0.1°. That is derived from tan θ = Ω^2 a sin φ cos φ / (g - Ω^2 a cos^2 φ). Maximum near 45°, tan θ_max ≈ Ω^2 a / (2g) = 0.00173 rad = 0.099°. So that uses Ω^2 a / g = 0.00346. So the dimensionless parameter is about 0.00346. The percentage difference in effective gravity for a spherical Earth is exactly Ω^2 a / g = 0.346%. The problem says 0.7%. That's exactly double. Could it be that they define the percentage difference as (g_pole - g_eq) / g_eq? That's Ω^2 a / (g - Ω^2 a) ≈ 0.347%. Still not double.

What if they define the percentage difference as (g_pole - g_eq) / g_mean? Same.

Maybe the problem uses the fact that the Earth is an oblate spheroid, and the effective gravity difference is about 0.7%? Let's compute with a simple model: The Earth's flattening f = (a-c)/a. The gravitational acceleration at the equator is approximately GM/a^2 (1 + 3/2 J2?) Actually, the effective gravity on an oblate Earth is often given by g = g_e (1 + β sin^2 φ). β = (5/2)m - f. If we take m = Ω^2 a / g_e. For Earth, g_e = 9.78, Ω^2 a = 0.0339, m = 0.00347. f = 1/298.257 = 0.003353. β = 0.008675 - 0.003353 = 0.005322. So g_pole/g_eq = 1.005322, difference = 0.5322%. Still not 0.7%.

What if we use the hydrostatic equilibrium value for a fluid Earth? f = (5/4)m = 0.00434. Then β = (5/2)m - (5/4)m = (5/4)m = 1.25 * 0.00347 = 0.00434. Difference = 0.434%. Not 0.7%.

What if we use the actual difference between effective gravity at equator and poles? 9.832 - 9.780 = 0.052. 0.052/9.780 = 0.00532 = 0.53%. 0.052/9.832 = 0.00529 = 0.53%. 

Maybe the problem uses a different planet? No, it says Earth.

Could it be that "0.7%" is a typo and it should be "0.35%"? In many textbooks, the dimensionless parameter is 1/289 = 0.00346, and the effective gravity difference is 0.35%. But the problem explicitly says "0.7%". Let me search my memory for Wallace and Hobbs Problem 1.1. I think I have a PDF in my mind. The problem: "1.1. Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." I recall that the solution uses a = 6371 km, g = 9.81 m/s^2, Ω = 7.292e-5 rad/s. Then Ω^2 a / g = 3.44e-3. Then they say the effective gravity at the equator is g - Ω^2 a, so the fractional decrease is Ω^2 a / g = 0.34%. But the problem says 0.7%? Wait, maybe they use g = 9.8 m/s^2, and a = 6371 km, but they compute the difference as (g_pole - g_eq)/g_eq * 100%? That's 0.034/9.766 = 0.35%. Still not 0.7%.

Let's check if there's an alternative interpretation: "effective gravity" might be the vector sum of gravitational and centrifugal forces. The magnitude at the equator is g - Ω^2 a. At the poles, it's g. The percentage less at equator than poles is (g_pole - g_eq)/g_pole * 100% = Ω^2 a / g * 100%. If they use g = 9.8, it's 0.35%. If they use g = 9.78, it's 0.35%. 

What if they use a = 6378 km, g = 9.78, then Ω^2 a = 0.0339, ratio = 0.00347 = 0.35%. 

Maybe the problem uses the fact that the Earth's radius is larger at the equator, so the gravitational acceleration is smaller. If they assume the Earth is a sphere, they get 0.35%. If they include the oblateness, they get 0.5%. To get 0.7%, they might be adding the two effects? The centrifugal effect is 0.35%, the gravitational effect due to oblateness is also about 0.35%? Actually, the gravitational acceleration at the equator is less than at the poles by about 0.67% (as we computed: 9.865 vs 9.798, difference 0.067, 0.067/9.865 = 0.68%). Then the effective gravity at the equator is further reduced by centrifugal force 0.034, so total effective gravity difference is 0.067 + 0.034 = 0.101, which is about 1.0% of 9.8. That's not 0.7%.

Wait, maybe they define "effective gravity" as the gravitational acceleration alone? No, that's usually "true gravity" or "gravitational acceleration".

Let's think about the phrase "maximum angle between g' and a vector pointing towards the centre of the Earth". That angle is due to the centrifugal force. For a spherical Earth, the angle is given by tan α = (Ω^2 R sin φ cos φ) / (g - Ω^2 R cos^2 φ). The maximum is about 0.1°. If the Earth is oblate, the gravitational vector also has a small angle with the radial direction. The total angle between effective gravity g' and the radial vector is the sum of the centrifugal deflection and the gravitational deflection due to oblateness. The gravitational deflection due to oblateness is about 0.2°? Actually, the angle between the true gravity and the radial vector on an oblate Earth is about 0.2° maximum? Let's check: The true gravity vector points slightly towards the equator because of the equatorial bulge. The maximum angle is around 45° latitude, and it's about 0.2°? I recall that the total deflection of the vertical (angle between effective gravity and radial) is about 0.2°? No, the maximum deflection of the vertical due to Earth's rotation and oblateness is about 0.2°? Actually, the formula for the angle between effective gravity and the geocentric radial is approximately (m + f) sin φ cos φ? Something like that. For Earth, m ≈ 0.00346, f ≈ 0.00335. The maximum angle might be around (m + f)/2 radians? (0.0068)/2 = 0.0034 rad = 0.19°. So about 0.2°. But the problem says "about 0.1°". So they are likely using a spherical Earth model where the only deflection is due to centrifugal force, which gives ~0.1°. So the problem assumes a spherical Earth.

If they assume a spherical Earth, then the effective gravity difference is Ω^2 a / g = 0.35%. But the problem says 0.7%. That's a factor of 2. Could it be that they define the percentage difference as (g_pole - g_eq) / g_eq? That's still 0.35%. What if they define g as the effective gravity at the equator? Then Ω^2 a / g_eq = 0.034/9.78 = 0.00347. Still 0.35%.

Maybe they use a different value for g? If they use g = 9.8, but a = 6371 km, and they compute Ω^2 a = 0.0339. Then they say the effective gravity at the equator is g - Ω^2 a = 9.766. The percentage less is (9.8 - 9.766)/9.8 = 0.034/9.8 = 0.347%. If they instead compute (9.8 - 9.766)/9.766 = 0.034/9.766 = 0.348%. No.

What if they use g = 9.81, a = 6371, Ω = 7.292e-5, then Ω^2 a = 0.03386. Ratio = 0.00345 = 0.345%. 

Maybe the problem has a typo and meant "0.35%"? But the user provided "0.7%". I must produce a solution that matches the problem statement? The problem says "Show that... is about 0.7% less...". In my solution, I can compute the actual value and it should be approximately 0.7%? But it's not. Unless I use different parameters.

Let's check if there's any standard Earth parameter set that gives 0.7%. If I take a = 6371 km, g = 9.8, but Ω = 2π/86400? No. What if I use the equatorial radius a = 6378 km, and g = 9.78 (effective at equator). Then Ω^2 a = 0.0339. The effective gravity at poles is about 9.83. Difference = 0.05. 0.05/9.78 = 0.0051 = 0.51%. 0.05/9.83 = 0.0051. Not 0.7%.

What if I use the true gravity? True gravity at equator = GM/a^2. Using GM = 3.986e14, a = 6378e3, g_eq_true = 9.798. True gravity at poles: c = 6357e3, g_pole_true = 9.865. Difference = 0.067. 0.067/9.865 = 0.0068 = 0.68% ≈ 0.7%. So if "effective gravity" is a misnomer and they actually mean "true gravity" (gravitational acceleration), then it's 0.7%. But they use the notation |g'| for effective gravity, and they talk about the angle between g' and the radial vector, which is due to centrifugal force. If g' is effective gravity, the angle is due to centrifugal. If g' were true gravity, the angle with the radial vector would be due to oblateness, which is about 0.2°, not 0.1°. So the angle part confirms they mean effective gravity with centrifugal, and they assume a spherical Earth (so no oblateness angle). Therefore, the 0.7
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    """
    Evaluate the dimensionless parameter Ω^2 a / g for the Earth,
    the percentage difference of effective gravity between equator and poles,
    and the maximum angle between effective gravity and the radial direction.
    
    Returns a dict with keys "1", "2", "3" for the three quantities.
    Each value is a dict with "value" and "unit".
    """
    # Earth parameters (standard values)
    Omega = 7.2921159e-5      # Earth's rotation rate [rad/s]
    a = 6371e3                # Earth's mean radius [m]
    g = 9.81                  # standard gravity [m/s^2]
    
    # 1. Dimensionless parameter Ω^2 a / g
    dimless = Omega**2 * a / g
    
    # 2. Percentage difference of |g'| between equator and poles
    # In a spherical Earth model with constant gravitational acceleration g:
    # effective gravity at equator: g - Ω^2 a
    # effective gravity at poles: g
    # fractional decrease = (g - (g - Ω^2 a)) / g = Ω^2 a / g
    percent = dimless * 100   # [%]
    
    # 3. Maximum angle between g' and the radial vector
    # tan(alpha) = (Ω^2 a sinφ cosφ) / (g - Ω^2 a cos^2 φ)
    # Find maximum numerically (occurs near 45°)
    max_alpha_rad = 0.0
    for deg in range(0, 91):
        phi = math.radians(deg)
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        numerator = Omega**2 * a * sin_phi * cos_phi
        denominator = g - Omega**2 * a * cos_phi**2
        alpha = math.atan(numerator / denominator)
        if alpha > max_alpha_rad:
            max_alpha_rad = alpha
    max_alpha_deg = math.degrees(max_alpha_rad)
    
    return {
        "1": {"value": dimless, "unit": ""},
        "2": {"value": percent, "unit": "%"},
        "3": {"value": max_alpha_deg, "unit": "deg"}
    }
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run2.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.003461392712977341` | ✓ |
| `2` | `0.7` | `0.6922785425954682` | ✓ |
| `3` | `0.1` | `0.09916159684546978` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 3
    1. Evalu`

RESPONSE (verbatim, untruncated):

~~~~
We need to write a Python function `solve()` that computes the requested quantities for the Earth. The problem asks:

1. Evaluate the dimensionless parameter Ω² a / g for the Earth.
2. Show that at Earth's surface, the magnitude |g'| of effective gravity is about 0.7% less at the equator than at the poles.
3. The maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°.

We need to return a dict with entries "1", "2", "3" corresponding to these three quantities. But careful: The problem asks to "Evaluate the dimensionless parameter Ω² a / g for the Earth." So answer 1 is that dimensionless parameter. Then "Show that... the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" – so answer 2 is the percentage difference? Or maybe the magnitude difference? The phrasing "about 0.7% less" suggests we compute the percentage decrease: (|g'_pole| - |g'_equator|)/|g'_pole| * 100%. Or maybe just the ratio? The problem says "Show that... is about 0.7% less". So we should compute that percentage. And "the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." So answer 3 is that maximum angle in degrees.

Thus we need to compute:
1. Ω² a / g, where Ω is Earth's angular rotation rate, a is Earth's equatorial radius, g is the gravitational acceleration (presumably the true gravity at the surface, maybe at the equator? Usually g is the standard gravity, but for this parameter, it's often the gravitational acceleration GM/R^2. We need to use standard values. The problem doesn't give numbers, so we must use known Earth parameters. We'll use standard values: Earth's rotation period = 24 hours = 86400 s? Actually sidereal day is 86164 s. But often in such problems, they use 24 hours. Let's check typical values: Earth's equatorial radius a ≈ 6378 km = 6.378e6 m. g ≈ 9.81 m/s². Ω = 2π / T, T = 24h = 86400 s? Or sidereal day = 23h56m4s = 86164 s. The dimensionless parameter Ω² a / g is about 3.45e-3? Let's compute: Ω = 7.292115e-5 rad/s (standard). a = 6378137 m (equatorial radius). g = 9.780327 m/s² (at equator? Actually g varies. Usually the parameter uses the equatorial gravity or mean gravity. The standard value is m = Ω² a³ / GM? Actually the parameter is often denoted m = Ω² a / g_e? Let's recall: The dimensionless parameter for Earth's oblateness is often J2 related to m = Ω² a³ / GM. But here it's Ω² a / g. If g = GM/a², then Ω² a / g = Ω² a³ / GM = m. So it's the same. Standard m for Earth is about 3.4495e-3. So we can compute using standard values. We need to pick values. Since the problem doesn't provide them, we'll use typical values: Earth's rotation period T = 86164 s (sidereal day), equatorial radius a = 6378.1 km = 6.3781e6 m, g = 9.78 m/s²? Actually g at equator is about 9.78, but the true gravity (without rotation) is about 9.83? Wait, effective gravity g' includes centrifugal term. The true gravitational acceleration g (due to mass) is about 9.83 m/s² at poles, 9.78 at equator? Actually g' at equator is about 9.78, but true gravity g at equator is about 9.83? Let's check: g' = g - Ω² a. At equator, Ω² a ≈ (7.292e-5)^2 * 6.378e6 ≈ 0.0339 m/s². So if g' = 9.78, then g = 9.81. So g is about 9.81. The parameter Ω² a / g is about 0.0339/9.81 ≈ 0.00346. So we can compute it.

But we need to be precise. The problem likely expects the student to use standard values: Earth's radius a = 6370 km? Actually equatorial radius is 6378 km. Polar radius is 6357 km. But for the parameter, a is equatorial radius. g is the gravitational acceleration at the equator? Or mean? Usually in the context of effective gravity, g is the true gravitational acceleration at the surface. The parameter Ω² a / g is often evaluated with g being the true gravity at the equator. Let's use standard values: Earth's mass M = 5.972e24 kg, G = 6.674e-11, so GM = 3.986e14 m³/s². Equatorial radius a = 6378137 m. Then true gravity at equator g = GM/a² = 3.986e14 / (6.378137e6)^2 = 9.798? Actually compute: 3.986e14 / 4.068e13 ≈ 9.80. Let's do precisely: 3.986004418e14 / (6378137^2). 6378137^2 = 4.068063e13. 3.986004418e14 / 4.068063e13 = 9.7983. So g ≈ 9.798 m/s² at equator. Then Ω = 2π / 86164.0905 = 7.2921159e-5 rad/s. Ω² a = (7.2921159e-5)^2 * 6378137 = 5.317e-9 * 6.378e6 = 0.03392. So Ω² a / g = 0.03392 / 9.7983 = 0.003462. That's about 3.46e-3.

But the problem also asks for the percentage difference in |g'| between equator and poles, and the maximum angle. To compute these, we need a model. The effective gravity g' is the vector sum of true gravity g (pointing towards center) and centrifugal acceleration Ω² r_perp (pointing outward from axis). On the surface of an oblate Earth, true gravity is not exactly radial and its magnitude varies with latitude. However, the problem likely uses a simplified model: Earth as a sphere? Or as an oblate spheroid? The phrase "at the Earth's surface" and "maximum angle between g' and a vector pointing towards the centre of the Earth" suggests we consider the Earth as a sphere? If Earth were a sphere, true gravity would point to the center and have constant magnitude g. Then effective gravity g' = g - Ω² R cos²λ? Actually centrifugal acceleration is Ω² r cosλ outward from axis, where r is distance from axis = R cosλ. Its magnitude is Ω² R cosλ, direction perpendicular to rotation axis. The vector difference: g' = g (radial inward) + Ω² R cosλ (outward perpendicular to axis). The angle between g' and radial direction is given by tan α = (Ω² R cosλ sinλ) / (g - Ω² R cos²λ)? Actually centrifugal acceleration has components: outward from axis, so in the local horizontal (southward in northern hemisphere) and vertical. The radial component (outward) is Ω² R cos²λ, reducing gravity. The tangential component (equatorward) is Ω² R cosλ sinλ. So the effective gravity vector deviates from radial by angle α where tan α = (Ω² R cosλ sinλ) / (g - Ω² R cos²λ). The maximum angle occurs where derivative is zero. For small Ω² R/g, maximum is at λ = 45°? Actually tan α ≈ (Ω² R/g) cosλ sinλ = (Ω² R/(2g)) sin 2λ. Maximum of sin 2λ is 1 at λ=45°, so α_max ≈ Ω² R/(2g) radians. With Ω² R/g ≈ 0.00346, α_max ≈ 0.00173 rad ≈ 0.099°. That's about 0.1°. So that matches.

For the percentage difference in |g'|: at poles, λ=90°, centrifugal term is zero, so |g'| = g (assuming g is constant). At equator, λ=0°, centrifugal term is Ω² R directly outward, so |g'| = g - Ω² R. The percentage difference = (g - (g - Ω² R))/g * 100% = (Ω² R/g)*100%. That would be about 0.346%, not 0.7%. Wait, the problem says "about 0.7% less at the equator than at the poles". 0.346% is half of 0.7%. So there's a discrepancy. Why? Because the Earth is not a sphere; it's an oblate spheroid. The true gravity g is not constant; it varies with latitude due to both the oblateness and the centrifugal effect. The effective gravity at the poles is larger than at the equator by about 0.7%? Actually the standard gravity formula: g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ) m/s². At equator (φ=0): 9.7803. At poles (φ=90°): 9.8322. Difference = 0.0519, percentage = 0.0519/9.8322 ≈ 0.53%? Actually 9.8322 - 9.7803 = 0.0519, 0.0519/9.8322 = 0.00528 = 0.528%. That's not 0.7% either. Wait, maybe they mean the difference relative to equatorial value? 0.0519/9.7803 = 0.53%. Still not 0.7%. Let's check: The problem says "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". That means (|g'_pole| - |g'_equator|)/|g'_pole| * 100% ≈ 0.7%. But standard values give ~0.5%. Maybe they use a spherical Earth with constant true gravity g, but then the difference is Ω² R/g ≈ 0.35%. That's half of 0.7%. Perhaps they include the effect of oblateness on true gravity? The true gravity at the equator is less than at the poles because the equator is farther from the center. The difference in true gravity due to oblateness is about 0.5%? Actually, if Earth were a uniform oblate spheroid, the true gravity at the poles is larger. The total effective gravity difference is about 0.5%. But 0.7% is a bit high. Let's compute with actual numbers: Earth's equatorial radius a = 6378 km, polar radius c = 6357 km. The true gravity at the pole g_p = GM/c², at equator g_e = GM/a². Ratio g_p/g_e = (a/c)² = (6378/6357)² ≈ (1.0033)² ≈ 1.0066, so g_p is 0.66% larger. Then effective gravity at equator g'_e = g_e - Ω² a. At pole, g'_p = g_p. So g'_p/g'_e = g_p / (g_e - Ω² a). g_e ≈ GM/a². Ω² a ≈ 0.0339 m/s². g_e ≈ 9.80. So g_e - Ω² a ≈ 9.766. g_p ≈ 9.80 * 1.0066 ≈ 9.865. Ratio = 9.865/9.766 ≈ 1.0101, so about 1% difference? That's 1%, not 0.7%. Hmm.

Let's use standard values more accurately. 
GM = 3.986004418e14 m³/s².
a = 6378137 m (equatorial radius)
c = 6356752 m (polar radius)
Ω = 7.2921150e-5 rad/s.

True gravity at equator: g_e = GM/a² = 3.986004418e14 / (6378137)^2 = 9.79828 m/s².
True gravity at pole: g_p = GM/c² = 3.986004418e14 / (6356752)^2 = 9.86432 m/s².
Centrifugal at equator: Ω² a = (7.292115e-5)^2 * 6378137 = 0.03392 m/s².
Effective gravity at equator: g'_e = g_e - Ω² a = 9.79828 - 0.03392 = 9.76436 m/s².
Effective gravity at pole: g'_p = g_p = 9.86432 m/s².
Difference: g'_p - g'_e = 0.09996 m/s².
Percentage relative to pole: 0.09996/9.86432 * 100% = 1.013%. That's about 1.0%, not 0.7%.
Wait, maybe they use a different definition: "about 0.7% less at the equator than at the poles" could mean (g'_p - g'_e)/g'_e * 100%? That would be 0.09996/9.76436 = 1.024%. Still ~1%.
Maybe they use a spherical Earth with constant true gravity g, but then the difference is only Ω² a/g ≈ 0.35%. So 0.7% is double that. Could it be that they consider the effective gravity difference including the oblateness but with a different model? Let's check typical textbook values. In many atmospheric science or geophysics texts, the fractional difference in effective gravity between equator and poles is about 0.5%? Actually, the standard gravity formula gives 9.780 at equator, 9.832 at poles, difference 0.052, percentage 0.53%. That's the effective gravity. So 0.7% is not matching standard. Maybe they use a simplified model where Earth is a sphere but the true gravity is not constant? No.

Let's re-read the problem: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

This is a classic problem. Often, the parameter Ω² a/g is evaluated with g being the true gravity at the equator, and a the equatorial radius. The value is about 1/289? Actually, the Earth's flattening f = (a-c)/a ≈ 1/298.257. The parameter m = Ω² a/g_e ≈ 1/288.9? Let's compute: 1/0.00346 = 289. So m ≈ 1/289. That's a known result. Then the effective gravity difference between pole and equator is approximately (5/2)m - something? Wait, for a rotating fluid planet, the effective gravity difference is related to m. The formula for effective gravity on an oblate spheroid is g' = g_e (1 + (5/2 m - f) sin²φ ...). Actually, the standard formula: g' = g_e (1 + β sin²φ + ...), where β = (5/2)m - f. For Earth, m ≈ 0.00346, f ≈ 0.00335. Then β ≈ 0.00865 - 0.00335 = 0.00530. That's the 0.53% difference. So 0.7% is not that.

Maybe the problem expects a spherical Earth approximation but with a different g? If they use g = 9.81 m/s², a = 6370 km, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344. Then percentage difference = 0.344%. That's not 0.7%.

Wait, could "0.7% less" be a typo or a different interpretation? Perhaps they mean the ratio of the centrifugal term to gravity is about 0.35%, but the total difference including oblateness is about 0.7%? But we computed 1% with actual numbers. Let's check historical values: Sometimes the Earth's equatorial gravity is given as 978.0 Gal, polar 983.2 Gal, difference 5.2 Gal, percentage 0.53%. So 0.7% is off.

Maybe they use the mean radius and mean gravity? Let's compute with mean radius R = 6371 km, g = 9.81. Then Ω² R/g = (7.27e-5)^2 * 6.371e6 / 9.81 = 0.0344/9.81 = 0.00351. Percentage = 0.35%. Still not 0.7%.

Perhaps the problem is from a textbook where they use a different value for Earth's rotation? If they use a day of 24 hours exactly, Ω = 2π/86400 = 7.2722e-5. a = 6378 km = 6.378e6. g = 9.8. Ω² a/g = (5.288e-9)*6.378e6/9.8 = 0.0337/9.8 = 0.00344. Still 0.34%.

Wait, maybe "0.7% less" means the effective gravity at the equator is 0.7% less than at the poles, and they are using a spherical Earth but with g being the true gravity at the pole? No.

Let's think: The problem might be from a dynamics or atmospheric science context where they approximate the Earth as a sphere and use g as the gravitational acceleration at the surface, but then they also consider the oblateness? The phrase "Evaluate the dimensionless parameter Ω² a / g for the Earth." is often the first step. Then they ask to show that |g'| is about 0.7% less at equator than poles. That suggests that the difference is not just Ω² a/g, but something else. Perhaps they include the effect of the Earth's oblateness on true gravity. In a simple model, if Earth is an oblate spheroid in hydrostatic equilibrium, the true gravity at the pole is larger. The total effective gravity difference can be approximated. There is a known result: The fractional difference in effective gravity between equator and pole is approximately (5/2)Ω² a/g - (a-c)/a? Actually, for a homogeneous rotating fluid, the surface is an equipotential, and the effective gravity difference is (5/2)Ω² a/g? Let's derive: For a rotating fluid planet, the effective gravity is g' = g - Ω² r cos²λ. On the surface, which is an equipotential, the true gravity g is not constant. The potential is Φ = -GM/r - (1/2)Ω² r² cos²λ + ... For small flattening, the surface is r = a (1 - f sin²λ). The effective gravity magnitude is g' = |∇Φ|. At equator, g'_e = GM/a² - Ω² a + ... At pole, g'_p = GM/c². The difference can be expanded. The result is g'_p - g'_e ≈ (5/2)Ω² a - (GM/a²)(a-c)/a? Actually, the standard formula for gravity on an ellipsoid is g' = g_e (1 + β sin²φ), where β = (5/2)m - f, with m = Ω² a/g_e, f = flattening. For Earth, m ≈ 0.00346, f ≈ 0.00335, so β ≈ 0.00865 - 0.00335 = 0.00530. So the pole-equator difference is β = 0.0053, i.e., 0.53%. That's not 0.7%.

Maybe they use a different definition: "0.7% less" could be (g'_p - g'_e)/g'_e = 0.7%? That would be 0.007. With β = 0.0053, that's 0.53%. Still not 0.7%.

Wait, could it be that they are using the parameter Ω² a/g with g being the effective gravity at the equator? Then Ω² a/g' = 0.0339/9.78 = 0.00347. Still same.

Perhaps the problem expects the student to compute these values using given numbers? But the problem statement doesn't provide numbers. It says "for the Earth". So we must use standard Earth parameters. The answer might be a known approximate value: Ω² a/g ≈ 1/289 ≈ 0.00346. The percentage difference might be computed as 0.7% if they use a different radius? Let's check if using polar radius for a? No, a is equatorial.

Maybe the 0.7% comes from a spherical Earth but with g being the true gravity at the surface, and they compute the difference in |g'| between equator and pole as (Ω² a/g) * 100%? That's 0.35%. Double that is 0.7%. Could it be that they consider the difference in effective gravity between equator and pole as 2 * Ω² a/g? Why? If Earth is a sphere, true gravity is constant g. At equator, g' = g - Ω² a. At pole, g' = g. Difference = Ω² a. Percentage = Ω² a/g. That's 0.35%. Not 0.7%. If they mistakenly use diameter instead of radius? No.

Maybe they consider the effective gravity vector magnitude at latitude 45°? No.

Let's search memory: In some textbooks, the dimensionless parameter is Ω² R/g, and they say it's about 0.0035. Then they say the effective gravity is about 0.35% less at the equator. But the problem says 0.7%. Could it be a misprint? Or maybe they include the fact that the Earth's radius is larger at the equator, so true gravity is also less? If you combine both effects, the total difference is about 0.5%. Still not 0.7%.

Wait, maybe they use g = 9.8, a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337. Ω² a/g = 0.00344. If they then say the effective gravity difference is about twice that because of oblateness? Actually, for a homogeneous Earth, the true gravity difference due to oblateness is (5/2)Ω² a? No.

Let's derive the effective gravity on an oblate Earth. The potential is U = -GM/r + (1/2)Ω² r² sin²θ? Actually, centrifugal potential is -1/2 Ω² r² cos²θ? Let's use co-latitude θ. The effective gravity is g' = -∇U. On the surface, which is an equipotential, U = constant. For small flattening, the surface is r = a (1 - f sin²φ), where φ is latitude. The effective gravity magnitude is g' = |∇U|. At the equator (φ=0), r = a, g'_e = GM/a² - Ω² a (if we ignore higher terms). At the pole (φ=90°), r = c = a(1-f), g'_p = GM/c². The difference g'_p - g'_e = GM/c² - GM/a² + Ω² a. Using GM/c² ≈ GM/a² (1 + 2f) = g_e (1 + 2f). So g'_p - g'_e ≈ g_e (1+2f) - g_e + Ω² a = 2f g_e + Ω² a. The fractional difference = (2f g_e + Ω² a)/g_e = 2f + m, where m = Ω² a/g_e. For Earth, f ≈ 1/298.257 ≈ 0.003353, m ≈ 0.00346. So 2f + m ≈ 0.006706 + 0.00346 = 0.010166, i.e., 1.02%. That's about 1%, not 0.7%.

If we use the actual effective gravity at equator g'_e = g_e - Ω² a, then the fractional difference relative to g'_e is (g'_p - g'_e)/g'_e ≈ (2f g_e + Ω² a)/(g_e - Ω² a) ≈ 2f + m + m²... ≈ 0.0102, i.e., 1.02%. So that's 1%.

But the problem says 0.7%. Maybe they use a different f? If Earth were in hydrostatic equilibrium as a homogeneous fluid, f = (5/4)m? Actually, for a homogeneous rotating fluid, the flattening f = (5/4) m? Let's check: For a homogeneous Earth, the equilibrium flattening is f = (5/4) m? Wait, the classical result for a homogeneous rotating fluid is f = (5/4) * (Ω² a/g)? Actually, the Maclaurin spheroid: for small eccentricity, f ≈ (5/4) m? Let's derive: For a homogeneous fluid, the surface is an equipotential. The potential is -GM/r - (1/2)Ω² r² sin²θ? Actually, centrifugal potential is -1/2 Ω² r² cos²θ? Let's use standard: U = -GM/r - (1/2)Ω² r² sin²φ? I need to be careful. Usually, the effective gravity potential is Φ = -GM/r - (1/2)Ω² r² cos²θ? No, centrifugal acceleration is Ω² r sinθ outward from axis. The potential for centrifugal force is -1/2 Ω² r² sin²θ? Actually, force = +Ω² r sinθ (outward). So potential V = -1/2 Ω² r² sin²θ? Check: -∇V = Ω² r sinθ (r̂ sinθ + θ̂ cosθ)? That gives centrifugal force. So V = -1/2 Ω² r² sin²θ. Then total potential U = -GM/r - 1/2 Ω² r² sin²θ. At the surface, U = constant. For small flattening, let r = a (1 - f sin²φ) where φ is latitude (φ = 90° - θ). Then sinθ = cosφ. So U = -GM/(a(1 - f sin²φ)) - 1/2 Ω² a² (1 - 2f sin²φ) cos²φ. Expand: GM/(a(1 - f sin²φ)) ≈ GM/a (1 + f sin²φ + f² sin⁴φ...). So U ≈ -GM/a (1 + f sin²φ) - 1/2 Ω² a² cos²φ + Ω² a² f sin²φ cos²φ. For U to be constant, the φ-dependent terms must cancel. The leading φ-dependent terms: -GM/a f sin²φ - 1/2 Ω² a² cos²φ. Write cos²φ = 1 - sin²φ. So -1/2 Ω² a² (1 - sin²φ) = -1/2 Ω² a² + 1/2 Ω² a² sin²φ. The constant part can be absorbed. So the sin²φ terms: -GM/a f + 1/2 Ω² a² = 0 => f = (1/2) (Ω² a²) / (GM/a) = (1/2) Ω² a³ / GM = (1/2) m, where m = Ω² a/g_e and g_e = GM/a². So f = m/2. That's for a homogeneous Earth? Wait, that's if the Earth is a point mass or if we ignore the change in gravity due to oblateness? Actually, in this derivation, we assumed the gravitational potential is -GM/r, which is valid for a point mass or a spherical mass. But if the Earth is oblate, the gravitational potential is not exactly -GM/r; there are J2 terms. For a self-gravitating fluid, the equilibrium flattening is larger. For a homogeneous fluid, the flattening is f = (5/4) m? Let's recall: For a Maclaurin spheroid, the flattening is related to m. For small m, f ≈ (5/4) m? Actually, the exact relation is m = (3/2) ( (1-e²)/e³ ) ( (3-2e²) arcsin e - 3e(1-e²) )? For small e, f ≈ (5/4) m? Let's check: For Earth, m=0.00346, (5/4)m = 0.00433, but actual f=0.00335. So Earth's f is less than (5/4)m. Actually, Earth is not homogeneous; it has a dense core. The equilibrium flattening for a two-layer model can be different. The observed f is about 1/298.257 = 0.003353. m = 0.003460. So f ≈ 0.97 m. So f is approximately m. Then 2f + m ≈ 3m = 0.01038, still ~1%.

So where does 0.7% come from? Maybe they are using a spherical Earth and the percentage difference in |g'| is (Ω² a/g) * 100% but they use g = 9.8, a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344 = 0.344%. Not 0.7%.

Wait, maybe they mean the effective gravity is 0.7% less at the equator than at the poles, and they are using the actual measured effective gravity? The standard formula gives g' at equator = 9.7803, at poles = 9.8322. Difference = 0.0519. 0.0519/9.7803 = 0.00531 = 0.531%. 0.0519/9.8322 = 0.00528 = 0.528%. Neither is 0.7%.

Could it be that they use the mean radius and mean gravity, and the difference is 0.7%? Let's compute with R = 6371 km, g = 9.81, Ω = 7.292e-5. Ω² R = 0.0339. Ω² R/g = 0.00346. Still 0.35%.

Maybe the problem is from a textbook that uses a different value for Earth's rotation period? If they use a day of 24 hours (86400 s), Ω = 7.272e-5. a = 6378 km = 6.378e6. g = 9.78? If g = 9.78, Ω² a/g = 0.0337/9.78 = 0.00345. Still 0.35%.

Perhaps "0.7% less" is a typo and should be "0.35% less"? But the problem also says "the maximum angle ... is about 0.1°". That matches α_max ≈ 0.5 * Ω² a/g rad. 0.5 * 0.00346 = 0.00173 rad = 0.099°. So that's consistent with a spherical Earth model where the angle is given by tan α ≈ (Ω² a/g) cosλ sinλ, max at 45° with value ≈ Ω² a/(2g). So the angle is about 0.1°. The percentage difference in |g'| between equator and pole in that spherical model is Ω² a/g * 100% ≈ 0.35%. But the problem says 0.7%. That's exactly double. Could it be that they define the percentage difference as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That would be (g - (g - Ω² a))/(g - Ω² a) * 100% = (Ω² a)/(g - Ω² a) * 100% ≈ Ω² a/g * (1 + Ω² a/g) * 100% ≈ 0.35% * 1.0035 ≈ 0.351%. Still not 0.7%.

Maybe they consider the difference in effective gravity between equator and pole including the oblateness, but with a simplified formula that gives 0.7%? Let's check if there's a known approximation: The effective gravity difference is often given as about 0.5%? Actually, many sources say the difference is about 0.5%. For example, Wikipedia: "The acceleration due to gravity at the Earth's surface is approximately 9.8 m/s², and varies by about 0.5% between the equator and the poles." So 0.5% is standard. 0.7% is not standard.

Wait, maybe the problem uses the parameter Ω² a/g with a being the mean radius? No.

Let's re-read carefully: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Perhaps they are using a different definition of g? In some contexts, g is the standard gravity 9.80665 m/s². Then Ω² a/g with a=6378 km gives 0.0339/9.80665 = 0.00346. Still 0.35%.

Maybe the 0.7% comes from including the effect of the Earth's oblateness on true gravity, but using a simplified model where the Earth is a sphere and the true gravity is constant, but the effective gravity difference is computed as (g_pole - g_equator)/g_equator? No.

Let's think about the phrase "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". This could be interpreted as: (|g'_pole| - |g'_equator|) / |g'_pole| = 0.007. If we use the actual effective gravity values: 9.832 - 9.780 = 0.052; 0.052/9.832 = 0.0053 = 0.53%. Not 0.7%. If we use the true gravity difference plus centrifugal: g_pole_true = 9.864, g_equator_true = 9.798, difference = 0.066; plus centrifugal 0.034 gives effective difference = 0.100? Wait, effective at pole = 9.864, at equator = 9.798 - 0.034 = 9.764, difference = 0.100. 0.100/9.864 = 0.0101 = 1.01%. So that's 1%.

Maybe they use a different equatorial radius? Some older textbooks use a = 6370 km, c = 6356 km? Then g_p = GM/c², g_e = GM/a². GM = 3.986e14. a=6.37e6, c=6.356e6. g_e = 3.986e14/4.057e13 = 9.82? Actually 6370^2 = 4.057e13, 3.986/4.057 = 0.982, so 9.82. g_p = 3.986e14/(6.356e6)^2 = 3.986e14/4.040e13 = 9.86. Difference = 0.04. Centrifugal = Ω² a = (7.27e-5)^2 * 6.37e6 = 0.0337. Effective equator = 9.82 - 0.0337 = 9.786. Effective pole = 9.86. Difference = 0.074. 0.074/9.86 = 0.0075 = 0.75%. That's about 0.7%! Let's check with more precise numbers: a = 6370 km? Actually, the mean radius is 6371 km, equatorial is 6378, polar is 6357. If someone mistakenly uses the mean radius for a and the polar radius for c? Or if they use a spherical Earth with radius a, but then they say "at the Earth's surface" and compare equator and poles, they might be assuming the Earth is a sphere, so the distance from center is the same, but then the true gravity is the same. That gives 0.35%. So to get 0.7%, they must be including the oblateness effect on true gravity. If they use a = 6378, c = 6357, the difference is 1%. If they use a = 6370, c = 6356? That's not standard.

Wait, maybe the problem defines g as the gravitational acceleration at the Earth's surface ignoring rotation, and a as the mean radius? Then they compute Ω² a/g. Then they say the effective gravity is 0.7% less at equator than poles. That might be a known result from a specific textbook. Let's search memory: In "Atmospheric Science" by Wallace and Hobbs, or in "An Introduction to Dynamic Meteorology" by Holton, there is a problem like this. In Holton's book, Chapter 1, there is a problem: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." I recall this exact wording! It's from Holton's "An Introduction to Dynamic Meteorology" (maybe 4th or 5th edition), Chapter 1, Problem 1.1 or similar. Let me check my memory: In Holton, the parameter is m = Ω² a/g. They use a = 6371 km? Actually, in Holton, they often use a = 6370 km, g = 9.8 m/s², Ω = 7.292e-5. Then Ω² a/g ≈ 0.0035. Then they ask to show that effective gravity is about 0.7% less at equator. How do they get 0.7%? They might be including the oblateness. In Holton's book, they derive that the effective gravity at sea level varies from about 9.78 at equator to 9.83 at poles. That's a difference of 0.05, which is 0.5%. But 0.7%? Let me check the exact numbers: 9.83 - 9.78 = 0.05, 0.05/9.78 = 0.0051 = 0.51%. Not 0.7%. Wait, maybe they use 9.81 as reference? (9.83 - 9.78)/9.81 = 0.05/9.81 = 0.0051. Still 0.5%.

Maybe they use the true gravity difference? In Holton, they might say: The true gravity at the equator is about 9.81, at the pole 9.83? No.

Let's think: If the Earth were a sphere of radius a, true gravity g is constant. Then effective gravity at equator is g - Ω² a, at pole is g. The fractional difference is Ω² a/g ≈ 0.0035 = 0.35%. To get 0.7%, they might be considering the difference between the effective gravity at the equator and the effective gravity at the pole, but they might be using the polar radius for the pole? If they use a spherical Earth, they wouldn't. If they use an oblate Earth, the true gravity at the pole is larger because the pole is closer to the center. The fractional increase in true gravity from equator to pole is about 2f ≈ 0.0067. Then the effective gravity difference is 2f + m ≈ 0.010. That's 1%. Not 0.7%.

Maybe they use a different flattening? If f = m/2? That gives 2f + m = 2*(m/2) + m = 2m = 0.007. That's 0.7%! Yes! If the Earth's flattening is exactly half of m, then the effective gravity difference is 2m. Let's check: If f = m/2, then 2f + m = 2*(m/2) + m = m + m = 2m. And 2m = 2 * 0.00346 = 0.00692 ≈ 0.7%. So if the Earth were in hydrostatic equilibrium with a constant density (or if we ignore the internal mass distribution and just assume the surface is an equipotential of the combined gravitational and centrifugal potential, but with the gravitational potential being that of a point mass), then f = m/2. That is exactly the case where the Earth's gravitational field is that of a point mass (or a sphere). In that case, the surface equipotential gives f = m/2. Then the effective gravity difference is 2m. And the maximum angle? For that model, the effective gravity vector deviates from the radial direction. The angle is given by tan α = (Ω² a sinφ cosφ) / (g - Ω² a cos²φ)? Actually, for an oblate surface, the radial direction is not exactly the local vertical? The problem says "maximum angle between g' and a vector pointing towards the centre of the Earth". So they want the angle between the effective gravity (which is normal to the equipotential surface) and the radial vector to the center. For the point-mass equipotential surface, the surface is r = a (1 - f sin²φ) with f = m/2. The effective gravity is normal to this surface. The angle between the normal to the surface and the radial direction is the angle between the vertical and the radial. That angle is approximately f sin 2φ? Actually, for an ellipsoid, the angle between the geocentric and geographic latitude is (f sin 2φ) or something. The maximum angle between the normal to the ellipsoid and the radial vector is about f radians? For f = 0.00335, that's 0.19°. But the problem says the maximum angle is about 0.1°. That's half of that. So that doesn't match.

Wait, in the spherical Earth model (constant true gravity, spherical surface), the effective gravity g' = g - Ω² R cos²φ (radial) + Ω² R cosφ sinφ (tangential). The angle between g' and the radial direction is α, where tan α = (Ω² R cosφ sinφ) / (g - Ω² R cos²φ). Maximum at φ=45°, tan α_max ≈ (Ω² R/2) / g = m/2. So α_max ≈ m/2 rad = 0.00173 rad = 0.099° ≈ 0.1°. That matches perfectly! So the angle is 0.1° in the spherical model. In the oblate model, the surface is tilted, so the effective gravity is normal to the surface, and the angle between the normal and the radial vector is about f sin 2φ, which is larger (f ≈ 0.00335, max angle ≈ 0.19°). But the problem says "maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°". That matches the spherical model, not the oblate model. So the problem is using a spherical Earth model for the angle! But then the percentage difference in |g'| would be m = 0.35%, not 0.7%. There's a contradiction.

Unless... in the spherical model, they compute the percentage difference in |g'| as (|g'_pole| - |g'_equator|)/|g'_equator|? That's m/(1-m) ≈ 0.35%. Still not 0.7%.

Maybe they compute the difference in |g'| between equator and pole as 2 * (Ω² a/g)? Why? If they consider the effective gravity at the equator is g - Ω² a, and at the pole is g + something? No, at pole centrifugal is zero.

Wait, could it be that they are using the formula for effective gravity on a rotating sphere, but they define the "magnitude |g'|" as the magnitude of the effective gravity vector, and they compare the value at the equator to the value at the poles. At the equator, |g'| = g - Ω² a. At the poles, |g'| = g. The difference is Ω² a. The percentage less at equator than poles = (g - (g - Ω² a))/g = Ω² a/g = m. That's 0.35%. So 0.7% is double.

Maybe they use the diameter instead of radius? If a is the radius, Ω² a/g. If they mistakenly used a = diameter? No.

Perhaps the problem has a typo, and it should be 0.35%? But the problem statement says 0.7%. I've seen this problem before. In some versions, it says "about 0.35% less". Let me check my memory: In Holton's 4th edition, Problem 1.1: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.35% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." Yes! I think it's 0.35%, not 0.7%. Let me verify: I recall a problem: "Show that the effective gravity is about 0.35% less at the equator..." That makes sense because m ≈ 0.0035 = 0.35%. The angle is m/2 ≈ 0.1°. So the problem likely has a typo in the user's message, or I misremember. But the user wrote "0.7%". Could it be that they use a different g? If g is taken as 9.8, and a = 6370, Ω = 7.27e-5, then Ω² a = 0.0337, Ω² a/g = 0.00344 = 0.344%. Still 0.34%. If they use g = 9.78, then 0.0337/9.78 = 0.00345. Still 0.345%.

Maybe they use the polar radius for a? If a is the polar radius? No, a is usually equatorial.

Wait, maybe the parameter is Ω² a/g, but they then compute the effective gravity difference as (5/2)Ω² a/g? No.

Let's read the problem again: "Evaluate the dimensionless parameter Ω² a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

If the parameter is m = Ω² a/g, and they want to show |g'| is about 0.7% less, maybe they are using a different definition of g? In some contexts, g is the effective gravity at the pole? Or g is the standard gravity 9.80665? If g = 9.80665, and a = 6378 km, Ω = 7.292e-5, then Ω² a = 0.0339, Ω² a/g = 0.00346. Still 0.35%.

Maybe they use a = 6370 km, g = 9.8, but then they say the effective gravity difference is 0.7% because they include the fact that the Earth is oblate and the true gravity is also less at the equator? But then the angle would be different.

Let's check the angle in the oblate model. The effective gravity is normal to the equipotential surface. The angle between the normal and the radial vector is the difference between geographic and geocentric latitude. That angle is maximum at 45° and is about 11.5'? Actually, the maximum difference is about 11.5 minutes of arc, which is about 0.19°. That's about 0.2°, not 0.1°. So the problem's "0.1°" strongly points to the spherical model where the angle is m/2 rad ≈ 0.1°. So the problem is using a spherical Earth with constant true gravity. In that model, the percentage difference in |g'| is m = 0.35%. So why does the problem say 0.7%? Could it be that they ask for the percentage difference in |g'| between equator and poles, but they define |g'| as the magnitude of the effective gravity vector, and they compute it as sqrt( (g - Ω² a cos²φ)² + (Ω² a cosφ sinφ)² )? At the equator, |g'| = g - Ω² a. At the pole, |g'| = g. The difference is Ω² a. The percentage less = Ω² a/g = m. If they mistakenly computed the percentage as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That's m/(1-m) ≈ m. Still 0.35%.

Maybe they use the fact that the effective gravity at the equator is g - Ω² a, and at the pole is g, but they also consider that the Earth's radius is larger at the equator? If they use a spherical Earth, radius is constant. So no.

Wait, could "0.7%" be a typo in the user's message? The user might have copied it from a source that had a typo. But as an AI, I must solve the problem as stated. However, the problem says "Show that... is about 0.7% less". I need to compute the actual value and see if it's about 0.7%. If I use standard Earth parameters, what do I get? Let's compute using the actual oblate Earth. The effective gravity at the equator is about 9.7803, at the poles 9.8322. The percentage less at equator than poles: (9.8322 - 9.7803)/9.8322 * 100% = 0.528%. That's about 0.5%, not 0.7%. If I use the true gravity difference plus centrifugal, I got 1%. So 0.7% is in between. Maybe they use a different set of parameters: a = 6378 km, c = 6356 km? Let's try a = 6378, c = 6356. Then g_p = GM/c², g_e = GM/a². GM = 3.986e14. g_e = 3.986e14/(6.378e6)^2 = 9.80. g_p = 3.986e14/(6.356e6)^2 = 9.86. Centrifugal = Ω² a = (7.292e-5)^2 * 6.378e6 = 0.0339. g'_e = 9.80 - 0.0339 = 9.766. g'_p = 9.86. Difference = 0.094. 0.094/9.86 = 0.0095 = 0.95%. Still ~1%.

What if they use a = 6370, c = 6357? g_e = 3.986e14/(6.37e6)^2 = 9.82. g_p = 3.986e14/(6.357e6)^2 = 9.86. Centrifugal = Ω² * 6.37e6 = 0.0339. g'_e = 9.82 - 0.0339 = 9.786. g'_p = 9.86. Diff = 0.074. 0.074/9.86 = 0.0075 = 0.75%. That's about 0.7%! If they use a = 6370 km as the equatorial radius? But equatorial radius is actually 6378 km. Some older textbooks use 6370 km as the mean radius, and sometimes they use it for both equator and pole? No, if they use a spherical Earth of radius 6370 km, then g is constant, difference is 0.0339/9.82 = 0.00345 = 0.345%. So to get 0.7%, they must be using an oblate Earth with equatorial radius ~6370 km and polar radius ~6356 km? That's roughly the actual values (6378 vs 6357). The difference is about 21 km. The flattening f = 21/6370 ≈ 0.0033. Then 2f + m = 0.0066 + 0.0035 = 0.0101 = 1.01%. Not 0.7%.

Wait, my calculation above: g'_e = g_e - Ω² a. g'_p = g_p. g_p = GM/c², g_e = GM/a². So g'_p - g'_e = GM/c² - GM/a² + Ω² a. For small differences, GM/c² ≈ GM/a² (1 + 2(a-c)/a) = g_e (1 + 2f). So difference = 2f g_e + Ω² a. Fractional difference = 2f + m. If f = 1/298 = 0.00336, m = 0.00346, then 2f+m = 0.01018 = 1.02%. If I use a=6370, c=6356 (difference 14 km, f=0.0022), then 2f+m = 0.0044+0.0035=0.0079=0.79%. That's close to 0.7%. If I use a=6370, c=6350? Not realistic.

Maybe they use the effective gravity formula from the standard model: g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ). At φ=0, g'=9.7803. At φ=90, g'=9.7803*(1+0.0053024) = 9.8322. The percentage increase from equator to pole is 0.53%. So 0.53% is not 0.7%.

Perhaps the problem uses the parameter m = Ω² a/g, and then states that the effective gravity difference is about 2m? That would be 0.7%. Why would it be 2m? In some derivations, if you assume the Earth is a fluid in hydrostatic equilibrium, the effective gravity difference between pole and equator is (5/2)m? No, (5/2)m = 0.00865 = 0.865%. That's close to 0.7%? 0.865% is closer to 0.9%. If m=0.00346, 5/2 m = 0.00865. If m=0.0035, 5/2 m = 0.00875. Not 0.7%.

What if they use the formula for a homogeneous Earth? For a homogeneous rotating fluid, the flattening f = (5/4)m, and the effective gravity difference is (5/2)m? Actually, for a homogeneous Earth, the effective gravity at the pole is g_p = GM/c², at equator g'_e = GM/a² - Ω² a. Using the equilibrium relation, one can show that g'_p - g'_e = (5/2) m g_e? Let's check: For homogeneous, f = (5/4)m. Then 2f + m = 2*(5/4)m + m = (5/2)m + m = (7/2)m = 3.5m = 0.012. That's 1.2%. Not 0.7%.

Maybe they use the fact that the effective gravity vector magnitude is sqrt( (g - Ω² a cos²φ)² + (Ω² a cosφ sinφ)² ). At the equator, this is g - Ω² a. At the pole, it's g. The difference is Ω² a. But maybe they consider the percentage difference relative to the average? No.

Given the confusion, I should look up the exact problem. Since I'm an AI, I can't browse, but I can recall. I am quite sure this is Problem 1.1 from Holton's "An Introduction to Dynamic Meteorology". In the 4th edition, it says: "Evaluate the dimensionless parameter Ω² a/g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.35% less at the equator than at the poles, and the maximum angle between g' and a vector pointing to the center of the Earth is about 0.1°." I have a strong memory of 0.35%. In fact, I've seen this problem before. The user might have typed 0.7% by mistake. But the user's text says "0.7%". Should I compute 0.35% or 0.7%? The problem says "Show that... is about 0.7% less". If I compute the actual value using standard parameters, what do I get? If I use a spherical Earth with constant g, I get ~0.35%. If I use the actual oblate Earth, I get ~0.5% or ~1% depending on how I compute. The phrase "about 0.7% less" might be a rough number from a specific set of parameters. Let's check if using a = 6370 km, g = 9.8, Ω = 7.27e-5, then Ω² a/g = 0.00344. If they then say the effective gravity difference is 0.7%, maybe they are using the difference in |g'| between equator and pole as a percentage of the equatorial value? No.

Wait, maybe they define g as the gravitational acceleration at the Earth's surface without rotation, but they use the polar value? If g is the true gravity at the pole, and a is the equatorial radius? Then Ω² a/g_pole. g_pole ≈ 9.83. Ω² a = 0.0339. Ratio = 0.00345. Still 0.35%.

Maybe the 0.7% comes from the fact that the effective gravity at the equator is less than at the poles by about 0.7% if you include the oblateness and use a specific model? Let's calculate with the actual numbers more precisely. 
Equatorial radius a = 6378.137 km
Polar radius c = 6356.752 km
GM = 3.986004418e14 m³/s²
Ω = 7.2921150e-5 rad/s
g_e_true = GM/a² = 3.986004418e14 / (6378137)^2 = 9.79828 m/s²
g_p_true = GM/c² = 3.986004418e14 / (6356752)^2 = 9.86432 m/s²
Centrifugal at equator = Ω² a = (7.292115e-5)^2 * 6378137 = 0.03392 m/s²
Effective g at equator = 9.79828 - 0.03392 = 9.76436
Effective g at pole = 9.86432
Difference = 0.09996
Percentage less at equator = (9.86432 - 9.76436)/9.86432 * 100% = 1.013%
Percentage less at equator relative to equatorial = 1.024%
So that's ~1.0%.

If I use the standard gravity formula (which is based on the actual geoid):
g' = 9.780327 (1 + 0.0053024 sin²φ - 0.0000058 sin²2φ)
Equator: 9.780327
Pole: 9.780327 * 1.0053024 = 9.83218
Difference = 0.05185
Percentage = 0.05185/9.83218 = 0.527% (relative to pole)
or 0.05185/9.78033 = 0.530% (relative to equator)
So the actual effective gravity difference is about 0.53%.

So 0.7% is not the actual value. It's also not the spherical model value (0.35%). It's somewhere in between. Could it be that they use a = 6370 km, g = 9.81, and then compute the effective gravity difference including oblateness with a simple formula? For instance, if they assume the Earth is a sphere but the true gravity varies with latitude due to centrifugal potential? No.

Let's think about the phrase "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". If we take the ratio |g'_equator|/|g'_pole| = 1 - 0.007 = 0.993. The actual ratio is 9.7803/9.8322 = 0.9947. That's 0.53% less. 0.7% less would be 0.993, which is a difference of 0.007. The actual difference is 0.0053. So 0.7% is a bit high.

Maybe they use an older value for Earth's flattening? Historically, f = 1/297 = 0.003367. m = 0.00346. 2f+m = 0.0102. Not 0.007.

What if they use the formula for effective gravity on a rotating sphere, but they define the percentage as (|g'_pole| - |g'_equator|)/|g'_equator| * 100%? That's m/(1-m) ≈ 0.0035/0.9965 = 0.00351 = 0.351%. Still not 0.7%.

Maybe they use the fact that the centrifugal term is Ω² r, and at the equator r = a, but at the pole r = 0. So the difference in centrifugal acceleration is Ω² a. But they also consider that the true gravity is less at the equator because the Earth is bulged? If they approximate the true gravity difference as also Ω² a? That would give 2Ω² a/g = 0.7%. Why would true gravity difference be Ω² a? If the Earth is in hydrostatic equilibrium, the surface is an equipotential. The potential is -GM/r - 1/2 Ω² r² cos²φ. For a point mass, the surface flattening is f = m/2. Then the true gravity difference between pole and equator is g_p - g_e ≈ 2f g = m g. So true gravity is m g less at equator
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Standard Earth parameters
    T = 86164.0905          # sidereal day in seconds
    a = 6378137.0           # equatorial radius in meters
    GM = 3.986004418e14     # gravitational parameter in m^3/s^2

    # Derived quantities
    Omega = 2 * math.pi / T
    g_true_equator = GM / a**2   # true gravity at equator (no rotation)

    # Dimensionless parameter m = Omega^2 * a / g
    m = (Omega**2 * a) / g_true_equator

    # Percentage less at equator than poles: 2*m*100%
    percentage_less = 2 * m * 100

    # Maximum angle between effective gravity and radial vector: m/2 radians
    max_angle_rad = m / 2
    max_angle_deg = max_angle_rad * (180 / math.pi)

    return {
        "1": {"value": m, "unit": ""},
        "2": {"value": percentage_less, "unit": "%"},
        "3": {"value": max_angle_deg, "unit": "deg"}
    }
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 3 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run3.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.003453390762886219` | ✓ |
| `2` | `0.7` | `0.6883011796413865` | ✓ |
| `3` | `0.1` | `0.09910338054914007` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 5
    2. Show `

RESPONSE (verbatim, untruncated):

~~~~
We need to write a Python function `solve()` that computes the requested quantities for the Earth. The problem statement: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

We need to return a dict with entries for each quantity asked. The problem asks to:
1. Evaluate Ω^2 a / g (dimensionless parameter).
2. Show that |g'| is about 0.7% less at equator than poles (probably compute the percentage difference).
3. Maximum angle between g' and radial direction is about 0.1°.

But careful: The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

The graded answer is whatever solve() returns. We need to return a dict with one entry per quantity asked. The quantities asked are:
- The dimensionless parameter Ω^2 a / g.
- The percentage difference in |g'| between equator and poles? "about 0.7% less" – we can compute the exact percentage.
- The maximum angle in degrees (about 0.1°).

But the phrasing "Evaluate ... Show that ..." might imply we need to output the computed values. The problem says "The graded answer is whatever solve() returns, so let the function do the arithmetic." So we should compute these three numbers and return them as "1", "2", "3".

Let's parse: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." -> output that value.
"Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" -> output the percentage difference.
"and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." -> output the maximum angle in degrees.

So three quantities: 1) Ω^2 a / g, 2) percentage decrease of |g'| at equator relative to poles, 3) maximum angle in degrees.

We need to use standard values for Earth: Ω = 7.2921159 × 10^{-5} rad/s (Earth's rotation rate), a = equatorial radius = 6378.137 km? Or mean radius? Usually Earth's equatorial radius a ≈ 6378 km, g ≈ 9.81 m/s^2. But we need to be careful: The problem likely expects typical textbook values. Often in atmospheric science, Earth's radius a ≈ 6371 km (mean) or equatorial? The parameter Ω^2 a / g is about (7.292e-5)^2 * 6.371e6 / 9.81 ≈ 3.46e-3? Let's compute: Ω = 7.2921150e-5 rad/s, a = 6371e3 m, g = 9.80665 m/s^2. Ω^2 a / g = (5.317e-9) * 6.371e6 / 9.81 ≈ 0.00345. Actually 7.292e-5 squared is 5.317e-9. Times 6.371e6 = 0.03387. Divided by 9.81 = 0.00345. That's about 0.345%. But the problem says |g'| is about 0.7% less at equator than poles. The effective gravity g' = g - Ω^2 R cos^2 φ? Actually effective gravity magnitude: g' = g - Ω^2 a cos^2 φ (approx). At equator φ=0, g'_eq = g_e - Ω^2 a. At poles φ=90°, g'_pole = g_p. But g itself varies with latitude due to Earth's oblateness. The problem likely uses a simple model where the Earth is a sphere? Or maybe it's using the actual Earth's gravity including centrifugal effect. The 0.7% difference is the actual observed difference between polar and equatorial gravity, which includes both centrifugal and oblateness effects. The dimensionless parameter Ω^2 a / g is about 0.0035 (0.35%). The total difference is about 0.7% (actually observed g_pole ≈ 9.832 m/s^2, g_eq ≈ 9.780 m/s^2, difference ~0.53%? Wait: 9.832 - 9.780 = 0.052, 0.052/9.806 ≈ 0.53%. But often quoted as 0.5% or 0.7%? Let's check: g_pole = 9.832, g_eq = 9.780, difference = 0.052, percentage = 0.052/9.806*100 = 0.53%. But the problem says "about 0.7% less". Maybe they use a different reference? Or they consider |g'| = g - Ω^2 a cos^2 φ, and g is constant? If g is constant, then at equator g' = g - Ω^2 a, at poles g' = g. The fractional decrease = (Ω^2 a)/g. That is the dimensionless parameter. If that is 0.0035, it's 0.35%, not 0.7%. So the 0.7% must include the oblateness effect. The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". This suggests we compute Ω^2 a / g, and then separately compute the actual percentage difference of |g'| using a more realistic model? Or maybe they want us to use the formula for effective gravity on an oblate Earth? In many textbooks, the effective gravity is g' = g* - Ω^2 R cos^2 φ, where g* is the gravitational acceleration (without centrifugal). The total difference between equator and poles is about 0.7%? Actually, the difference in g* due to oblateness is about 0.2%? Let's recall: The centrifugal term Ω^2 a is about 0.034 m/s^2. The difference in g* between equator and poles is about 0.018 m/s^2? Total difference ~0.052 m/s^2. So Ω^2 a / g ≈ 0.0035 (0.35%). The oblateness contribution is about 0.0018 (0.18%). Sum = 0.53%. Not 0.7%. Maybe they use a different g? Some sources quote g_eq = 9.78, g_pole = 9.83, difference = 0.05, percentage = 0.05/9.8 = 0.5%. 0.7% might be a rounded figure? Or maybe they use the formula |g'| = g (1 - (Ω^2 a/g) cos^2 φ) and then the difference is Ω^2 a/g? That's 0.35%. So 0.7% is double. Could it be that the problem expects the difference to be 2 * Ω^2 a / g? No.

Let's read carefully: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

This is a classic problem. In many textbooks (e.g., Holton's Introduction to Dynamic Meteorology), the effective gravity is discussed. The dimensionless parameter is Ω^2 a / g ≈ 3.5 × 10^{-3}. The difference in effective gravity between equator and poles is about 0.7%? Wait, Holton 5th edition, Chapter 1, Problem 1.1? Let me check memory: Holton Problem 1.1: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the center of the Earth is about 0.1°." Yes, that's exactly Holton's problem! In Holton, the Earth's radius a = 6371 km, g = 9.81 m/s^2, Ω = 7.292 × 10^{-5} rad/s. Then Ω^2 a / g = (7.292e-5)^2 * 6.371e6 / 9.81 = 3.46e-3 = 0.346%. But the problem says 0.7% less. How does Holton get 0.7%? Actually, in Holton, the effective gravity magnitude is given by g' = g - Ω^2 a cos^2 φ? No, the effective gravity includes both the gravitational and centrifugal potentials. The total potential is Φ = -GM/r - (1/2) Ω^2 r^2 cos^2 φ. The geopotential at the surface is constant. The effective gravity magnitude is |∇Φ|. The difference between equator and poles is not simply Ω^2 a. Because the Earth is not a sphere; it's an oblate spheroid. The problem might be asking to show that the actual observed difference is about 0.7%? But the problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that...". It might be that we use the formula for effective gravity on a spherical Earth? If Earth were a sphere, g' = g - Ω^2 a cos^2 φ, then at equator g' = g - Ω^2 a, at poles g' = g. The fractional decrease = Ω^2 a / g ≈ 0.35%. That's not 0.7%. So maybe they use a different definition: The effective gravity vector is g' = g* + Ω^2 R (where R is distance from axis). The magnitude is approximately g - Ω^2 a cos^2 φ. The difference between equator and poles is Ω^2 a. But 0.35% is not 0.7%. Could it be that the problem expects the percentage difference relative to the equatorial value? (g_pole - g_eq)/g_eq * 100? If g_eq = g - Ω^2 a, then (Ω^2 a)/(g - Ω^2 a) ≈ Ω^2 a/g * (1 + Ω^2 a/g) ≈ 0.35% * 1.0035 ≈ 0.351%. Still not 0.7%.

Wait, maybe the Earth's radius a is the equatorial radius, and g is the gravitational acceleration at the equator? Or maybe they use g = 9.8 m/s^2, a = 6378 km? Ω^2 a = (7.292e-5)^2 * 6.378e6 = 0.0339 m/s^2. g = 9.78 at equator? Then Ω^2 a / g = 0.0339/9.78 = 0.00347 = 0.347%. Still not 0.7%.

Perhaps the 0.7% comes from the actual observed gravity difference: g_pole = 9.832, g_eq = 9.780, difference = 0.052, 0.052/9.806 = 0.53%. 0.7% is a bit high. Maybe they use g_pole = 9.83, g_eq = 9.76? No.

Let's search memory: Holton's problem 1.1 answer: Ω^2 a / g = 3.46 × 10^{-3}. The effective gravity difference is about 0.7%? Actually, I recall that in Holton, the effective gravity at the equator is about 0.7% less than at the poles? Let me check: In Holton 4th edition, Chapter 1, Problem 1.1: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the center of the Earth is about 0.1°." The solution manual might say: Ω^2 a / g = 3.46 × 10^{-3}. The effective gravity difference is (g_pole - g_eq)/g_pole * 100%? Using g_pole = 9.83, g_eq = 9.78, difference = 0.05, 0.05/9.83 = 0.51%. Not 0.7%. Maybe they use a different g? Some sources say g at poles is 9.832, at equator 9.780, difference 0.052, 0.052/9.780 = 0.53%. Still not 0.7%.

Wait, could it be that the problem expects us to compute the effective gravity using the formula g' = g - Ω^2 a cos^2 φ, but with g being the gravitational acceleration (not including centrifugal) and a being the radius? If we take g = GM/a^2? Then the difference between equator and poles due to oblateness is about 0.35% as well? Actually, the total difference is about 0.5%. 0.7% might be a rounded number from older textbooks? Or maybe they use a = 6371 km, g = 9.81, Ω = 7.292e-5, then Ω^2 a / g = 0.00346. Then they say the effective gravity difference is about 2 * Ω^2 a / g? No.

Let's think: The effective gravity magnitude is |g'| = |g* + Ω^2 R|. On a spherical Earth, g* is radial and constant magnitude g. Then g' = sqrt(g^2 + Ω^4 R^2 - 2g Ω^2 R cos φ?) Actually, g' = g* - Ω × (Ω × r). The centrifugal acceleration is Ω^2 R directed outward from axis. So g' = g (radial inward) + Ω^2 R (outward from axis). The magnitude squared: g'^2 = g^2 + Ω^4 R^2 - 2 g Ω^2 R cos φ? Wait, R = a cos φ. The angle between radial (inward) and centrifugal (outward from axis) is φ? Actually, radial inward is towards center. Centrifugal is outward perpendicular to axis. The vector from axis is in the plane of latitude, outward. So the angle between inward radial and outward centrifugal is 90° - φ? Let's set coordinates: radial unit vector inward is -r_hat. Centrifugal acceleration is Ω^2 R R_hat, where R_hat is outward from axis. The dot product: (-r_hat) · R_hat = -cos(angle between r_hat and R_hat). r_hat is outward radial. R_hat is perpendicular to axis, in the direction of increasing R. The angle between r_hat (outward) and R_hat is 90° - φ. So r_hat · R_hat = sin φ. Then inward radial (-r_hat) · R_hat = -sin φ. So g'^2 = g^2 + (Ω^2 R)^2 - 2 g Ω^2 R (-sin φ)? Wait, if g' = g (-r_hat) + Ω^2 R R_hat, then g'^2 = g^2 + (Ω^2 R)^2 + 2 g Ω^2 R (-r_hat · R_hat) = g^2 + Ω^4 R^2 + 2 g Ω^2 R sin φ. That seems off. Let's re-derive: Centrifugal acceleration is Ω × (Ω × r). For a sphere, r = a r_hat. Ω is along north pole. Ω × r = Ω a cos φ in azimuthal direction. Then Ω × (Ω × r) = Ω^2 a cos φ (pointing outward from axis). So centrifugal acceleration vector is Ω^2 a cos φ R_hat, where R_hat is unit vector outward from axis. The gravitational acceleration is g* = -g r_hat (assuming spherical Earth, g constant). So effective gravity g' = -g r_hat + Ω^2 a cos φ R_hat. The angle between r_hat and R_hat is 90° - φ? Actually, r_hat is radial outward. R_hat is perpendicular to axis, outward. At equator (φ=0), r_hat and R_hat are same direction (both outward from center in equatorial plane). So angle = 0. At pole (φ=90°), R_hat is zero? Actually R=0, so centrifugal is zero. At φ=45°, r_hat is at 45° to axis, R_hat is perpendicular to axis. The angle between r_hat and R_hat is 45°? Let's check: r_hat = (cos φ cos λ, cos φ sin λ, sin φ). R_hat = (cos λ, sin λ, 0). Dot product = cos φ cos^2 λ + cos φ sin^2 λ = cos φ. So angle is φ. So r_hat · R_hat = cos φ. Then g' = -g r_hat + Ω^2 a cos φ R_hat. g'^2 = g^2 + Ω^4 a^2 cos^2 φ - 2 g Ω^2 a cos φ (r_hat · R_hat) = g^2 + Ω^4 a^2 cos^2 φ - 2 g Ω^2 a cos^2 φ. So g' ≈ g - Ω^2 a cos^2 φ (since Ω^4 a^2 is tiny). So magnitude is g' = g - Ω^2 a cos^2 φ. At equator φ=0: g'_eq = g - Ω^2 a. At poles φ=90°: g'_pole = g. Difference = Ω^2 a. Fractional difference = Ω^2 a / g. That's the dimensionless parameter. So if Ω^2 a / g ≈ 0.0035, then the difference is 0.35%, not 0.7%.

Why does Holton say 0.7%? Maybe they use the actual Earth's gravity which includes the oblateness. The actual Earth is an oblate spheroid, and the gravitational acceleration g* is not constant; it's stronger at poles. The total effective gravity difference is about 0.5-0.7%. I recall that in some textbooks, the difference is quoted as 0.7%. For example, in "Atmospheric Science" by Wallace and Hobbs, they say the effective gravity at the equator is about 0.7% less than at the poles? Let me check: Wallace & Hobbs 2nd edition, Chapter 1? Actually, I remember a number: g at poles = 9.83, at equator = 9.78, difference = 0.05, 0.05/9.8 = 0.5%. 0.7% might be if you use g at equator as denominator: 0.05/9.78 = 0.511%. Still not 0.7%. Maybe they use g = 9.81, Ω^2 a = 0.034, but also the oblateness effect adds another 0.034? Actually, the oblateness effect is about 0.018 m/s^2. Total 0.052. 0.052/9.81 = 0.53%. 0.7% is off.

Wait, maybe the problem expects us to compute the effective gravity difference using the formula for an oblate Earth? The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". This is a typical textbook problem where they want you to use the observed values of g at equator and poles. Often, the problem gives the values: g_eq = 9.78 m/s^2, g_pole = 9.83 m/s^2. Then percentage difference = (9.83 - 9.78)/9.83 * 100% ≈ 0.5%? Or (9.83 - 9.78)/9.78 ≈ 0.51%? 0.7% might come from using g_pole = 9.83, g_eq = 9.76? Let's check standard values: World Geodetic System 1984 (WGS84): g at equator = 9.7803253359 m/s^2, g at poles = 9.8321849378 m/s^2. Difference = 0.05186. 0.05186/9.7803 = 0.00530 = 0.53%. 0.05186/9.8322 = 0.00527 = 0.53%. So it's about 0.53%. Not 0.7%.

Maybe the problem uses a different definition: "effective gravity" might be just the centrifugal term? No.

Let's search my memory of Holton's problem 1.1 solution. I think I've seen a solution online. The dimensionless parameter is Ω^2 a / g = (7.292e-5)^2 * 6.37e6 / 9.81 = 3.46e-3. The effective gravity difference: they might use g_pole = 9.83, g_eq = 9.78, difference = 0.05, percentage = 0.05/9.8 = 0.5%? But the problem says "about 0.7%". Maybe they use g = 9.8, a = 6370 km, Ω = 7.3e-5, then Ω^2 a = 0.034, and they say the total difference is twice that? Because the Earth's oblateness adds about the same amount? Actually, the equilibrium shape of a rotating fluid planet gives a difference in gravitational acceleration between equator and poles that is about (5/2) Ω^2 a? No, for a homogeneous fluid, the difference is (5/2) Ω^2 a? Let's recall: For a rotating fluid Earth in hydrostatic equilibrium, the surface is an equipotential. The total potential is Φ = -GM/r + (1/2) Ω^2 r^2 cos^2 φ. The effective gravity is |∇Φ|. The difference between equator and poles is approximately (GM/a^2) * (1 + (3/2)J2 ...). The centrifugal term contributes Ω^2 a. The gravitational term due to oblateness contributes about (3/2) J2 GM/a^2? J2 is about 1.08e-3. GM/a^2 ≈ 9.8. So (3/2)*1.08e-3*9.8 ≈ 0.0159. So total difference ≈ 0.034 + 0.016 = 0.050. That's 0.5%. So 0.7% is still off.

Maybe the problem uses a = 6378 km (equatorial radius) and g = 9.78 (equatorial gravity)? Then Ω^2 a / g = (7.292e-5)^2 * 6.378e6 / 9.78 = 0.0339 / 9.78 = 0.00347. Still 0.35%. The difference in effective gravity between equator and poles is not just Ω^2 a; it's the actual observed difference. If we take g_pole = 9.832, g_eq = 9.780, difference = 0.052. 0.052/9.780 = 0.53%. 0.7% is not matching.

Could it be that the problem expects the percentage difference relative to the mean g? (9.832 - 9.780)/9.806 = 0.53%. Still not 0.7%.

Maybe the problem uses older values: g_pole = 9.83, g_eq = 9.76? 0.07/9.8 = 0.7%. Yes! If g_eq = 9.76 and g_pole = 9.83, difference = 0.07, 0.07/9.8 = 0.00714 = 0.7%. Some older textbooks might quote g_eq = 9.78, g_pole = 9.83? That's 0.05. 9.83 - 9.78 = 0.05. 0.05/9.8 = 0.5%. Not 0.7%. Wait, 9.83 - 9.76 = 0.07. I've seen 9.78 and 9.83. Maybe they use g_eq = 9.78, g_pole = 9.85? No.

Let's check Holton 5th edition problem 1.1. I can search my memory: The problem statement in Holton is exactly: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the center of the Earth is about 0.1°." In the solution, they might use g = 9.81 m/s^2, a = 6371 km, Ω = 7.292e-5. Then Ω^2 a / g = 3.46e-3. Then they might say the effective gravity difference is about 2 * Ω^2 a / g? No, that would be 0.69% ≈ 0.7%. Why would it be twice? Because the Earth's oblateness contributes an equal amount? Actually, for a homogeneous fluid Earth, the total difference in effective gravity between equator and poles is (5/2) Ω^2 a / g? Let's derive: For a rotating fluid planet in equilibrium, the surface is an equipotential. The effective gravity g' = |∇Φ|. On the surface, Φ is constant. The difference in g' between equator and poles can be approximated. For a small flattening f, the gravitational acceleration at equator is g_e = GM/a^2 (1 + (3/2)J2 ...) and at poles g_p = GM/c^2 (1 - ...). The centrifugal term adds Ω^2 a at equator. The total difference g_p - g_e ≈ (5/2) Ω^2 a? Let's check: For a homogeneous fluid, the flattening f = (5/4) Ω^2 a / g. The gravity difference g_p - g_e = (5/2) Ω^2 a? Actually, I recall that for a homogeneous rotating fluid, g_p - g_e = (5/2) Ω^2 a. Let's verify: g = GM/r^2. For an oblate spheroid, the gravity at pole is GM/c^2, at equator is GM/a^2 - Ω^2 a. Using Clairaut's theorem, g_p - g_e ≈ (5/2) Ω^2 a - 2 f g? I'm not sure. But if g_p - g_e = (5/2) Ω^2 a, then (5/2)*0.034 = 0.085 m/s^2. That would be 0.085/9.8 = 0.87%. Not 0.7%. If it's 2 * Ω^2 a, then 0.068 m/s^2, 0.068/9.8 = 0.69% ≈ 0.7%. So maybe the total difference is about 2 Ω^2 a. That is a known result: For the actual Earth, the difference is about 0.052, while Ω^2 a = 0.034. So the ratio is about 1.5. Not 2.

Wait, maybe the problem is simpler: They want you to compute the effective gravity difference using the formula g' = g - Ω^2 a cos^2 φ, but with g being the actual gravity at the poles? No.

Let's read the problem again: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Perhaps the "effective gravity" here is defined as the vector sum of gravitational acceleration and centrifugal acceleration, and the Earth is assumed to be a sphere. Then |g'| = g - Ω^2 a cos^2 φ (approx). Then the difference between equator and poles is Ω^2 a. The dimensionless parameter is Ω^2 a / g. If that is 0.0035, then the difference is 0.35%, not 0.7%. So there's a discrepancy. Maybe they use a different value for a or g? If they use a = 6378 km, g = 9.78, Ω = 7.292e-5, Ω^2 a = 0.0339, Ω^2 a / g = 0.00347. Still 0.35%. If they use g = 9.8, a = 6371, Ω^2 a = 0.0339, /9.8 = 0.00346. 0.35%.

Could it be that the problem expects the percentage difference to be (g_pole - g_eq)/g_eq * 100%? If g_pole = g, g_eq = g - Ω^2 a, then percentage = Ω^2 a / (g - Ω^2 a) ≈ Ω^2 a/g + (Ω^2 a/g)^2 ≈ 0.35%. Still not 0.7%.

Maybe the dimensionless parameter is evaluated with a = equatorial radius, g = gravitational acceleration at equator (not effective)? And then the effective gravity difference is computed using the actual observed values? The problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." That's a specific number. Then "Show that... the magnitude |g'| ... is about 0.7% less..." This might be a separate fact that we are supposed to verify using known values of g at equator and poles. In many textbooks, they give g at equator = 9.78 m/s^2, g at poles = 9.83 m/s^2. Then (9.83 - 9.78)/9.78 = 0.0051 = 0.51%. Not 0.7%. If they use g at equator = 9.76, g at poles = 9.83, difference = 0.07, 0.07/9.8 = 0.7%. I've seen some sources say "gravity at the equator is about 9.78 m/s^2, at the poles about 9.83 m/s^2, a difference of about 0.5%". But 0.7% is also sometimes quoted? Let's check: Wikipedia "Gravity of Earth": "The gravity of Earth, denoted by g, is the net acceleration that is imparted to objects due to the combined effect of gravitation (from mass distribution within Earth) and the centrifugal force (from the Earth's rotation). ... At the Equator, g ≈ 9.780 m/s^2, at the poles g ≈ 9.832 m/s^2. ... The difference is about 0.5%." So 0.5% is standard. 0.7% might be a typo or older value.

Maybe the problem uses the formula for effective gravity on a spherical Earth and then the maximum angle is given by tan α = (Ω^2 a sin φ cos φ) / (g - Ω^2 a cos^2 φ). The maximum angle occurs at φ = 45°, and tan α ≈ Ω^2 a / (2g) * sin 2φ? Actually, the angle between g' and the radial direction: g' has a southward component? Let's derive: g' = -g r_hat + Ω^2 a cos φ R_hat. The radial direction is -r_hat. The angle α between g' and -r_hat satisfies tan α = (Ω^2 a cos φ sin φ) / (g - Ω^2 a cos^2 φ)? Wait, R_hat has a component in the radial direction? R_hat = cos φ r_hat + sin φ θ_hat? Actually, in spherical coordinates, r_hat is outward, θ_hat is southward (increasing θ is colatitude, so southward is θ_hat? Let's use latitude φ: r_hat outward, northward is φ_hat? Standard: r_hat = (cos φ cos λ, cos φ sin λ, sin φ). R_hat = (cos λ, sin λ, 0). The component of R_hat along r_hat is cos φ. The component perpendicular to r_hat in the meridional plane is sin φ pointing towards the equator? Actually, R_hat = cos φ r_hat + sin φ (southward? Let's check at φ>0: r_hat has northward component? r_hat = (cos φ cos λ, cos φ sin λ, sin φ). The northward unit vector is φ_hat = (-sin φ cos λ, -sin φ sin λ, cos φ). R_hat = (cos λ, sin λ, 0). Dot with φ_hat: -sin φ cos^2 λ - sin φ sin^2 λ = -sin φ. So R_hat = cos φ r_hat - sin φ φ_hat. So the centrifugal acceleration is Ω^2 a cos φ (cos φ r_hat - sin φ φ_hat) = Ω^2 a cos^2 φ r_hat - Ω^2 a sin φ cos φ φ_hat. Then g' = -g r_hat + Ω^2 a cos^2 φ r_hat - Ω^2 a sin φ cos φ φ_hat = -(g - Ω^2 a cos^2 φ) r_hat - Ω^2 a sin φ cos φ φ_hat. The vector towards the center is -r_hat. So the angle α between g' and -r_hat is given by the component perpendicular to -r_hat, which is the φ_hat component. The magnitude of g' is approximately g - Ω^2 a cos^2 φ. The perpendicular component is Ω^2 a sin φ cos φ. So tan α = (Ω^2 a sin φ cos φ) / (g - Ω^2 a cos^2 φ). For small α, α ≈ (Ω^2 a / g) sin φ cos φ = (Ω^2 a / (2g)) sin 2φ. Maximum at φ = 45°, α_max ≈ Ω^2 a / (2g) in radians. Ω^2 a / g ≈ 0.00346, so α_max ≈ 0.00173 rad = 0.099° ≈ 0.1°. That matches the problem's "about 0.1°". So the maximum angle is indeed Ω^2 a / (2g) radians. That works perfectly with Ω^2 a / g ≈ 0.00346.

Now for the 0.7% difference: If the Earth were a sphere, the difference in |g'| between equator and poles is Ω^2 a. The fractional difference is Ω^2 a / g ≈ 0.35%. But the problem says 0.7%. Why? Because the Earth is not a sphere; the actual effective gravity difference is about twice the centrifugal term? Or maybe the problem expects you to compute the difference using the formula for an oblate Earth? But the problem doesn't provide the flattening or J2. It just says "Show that... is about 0.7% less". Perhaps they want you to use the fact that the Earth's surface is an equipotential, and for an equipotential surface, the total difference in effective gravity between equator and poles is approximately 2 * Ω^2 a? Let's check: On an equipotential surface, the change in g' with latitude is related to the flattening. There's a known formula: g' = g_e (1 + β sin^2 φ + ...), where β = (5/2) Ω^2 a / g_e - f? Actually, for the Earth, β ≈ 0.0053. The difference between equator and poles is g_p - g_e = g_e β ≈ 9.78 * 0.0053 = 0.052. The centrifugal term alone is Ω^2 a ≈ 0.034. So the ratio is about 1.5. Not 2.

Maybe the problem uses a different definition: "effective gravity" might be just the gravitational part? No.

Wait, could it be that the problem expects the percentage difference to be computed as (|g'_pole| - |g'_eq|) / |g'_eq| * 100%? If we use the actual observed values: g_pole = 9.832, g_eq = 9.780. Difference = 0.052. 0.052/9.780 = 0.00532 = 0.53%. Still not 0.7%.

Maybe they use g = 9.81, a = 6371, Ω = 7.292e-5, and then the effective gravity difference is 2 * Ω^2 a? Why 2? Because the Earth's oblateness adds an equal amount? In some simplified treatments, they say the total difference is about 0.7% because the centrifugal effect is 0.35% and the oblateness effect is also 0.35%. But actually the oblateness effect is about half of the centrifugal effect? Let's compute: For a homogeneous fluid, the flattening f = (5/4) Ω^2 a / g. The gravity difference g_p - g_e = (5/2) Ω^2 a? Let's derive: For a homogeneous rotating fluid, the surface is an equipotential. The potential is Φ = -GM/r + (1/2) Ω^2 r^2 cos^2 φ. On the surface, Φ = constant. The effective gravity g' = |∇Φ|. At equator: g'_e = GM/a^2 - Ω^2 a. At pole: g'_p = GM/c^2. The flattening f = (a - c)/a. For small f, GM/c^2 ≈ GM/a^2 (1 + 2f). So g'_p ≈ GM/a^2 (1 + 2f). The difference g'_p - g'_e ≈ GM/a^2 (1 + 2f) - (GM/a^2 - Ω^2 a) = 2f GM/a^2 + Ω^2 a. For a homogeneous fluid, f = (5/4) Ω^2 a / (GM/a^2) = (5/4) Ω^2 a / g. Then 2f g = (5/2) Ω^2 a. So g'_p - g'_e = (5/2) Ω^2 a + Ω^2 a = (7/2) Ω^2 a? Wait: g'_p - g'_e = 2f g + Ω^2 a = (5/2) Ω^2 a + Ω^2 a = (7/2) Ω^2 a = 3.5 Ω^2 a. That would be 3.5 * 0.034 = 0.119 m/s^2, 1.2% difference. That's too big. So the homogeneous model is not correct for Earth.

Actually, the Earth is not homogeneous; it has a dense core. The actual flattening is f ≈ 1/298.257 = 0.00335. Ω^2 a / g ≈ 0.00346. So f ≈ Ω^2 a / g. For the actual Earth, f ≈ 0.00335, Ω^2 a/g ≈ 0.00346. They are nearly equal. Then 2f g ≈ 2 * 0.00335 * 9.81 = 0.0657. Ω^2 a = 0.0339. Sum = 0.0996. That would be 1% difference. But actual g difference is 0.052. So the simple formula g'_p - g'_e = 2f g + Ω^2 a doesn't hold because g is not constant; the internal mass distribution matters. The actual gravity difference is given by Clairaut's theorem: g_p - g_e = g_e ( (5/2) m - f )? Wait, Clairaut's theorem for the actual gravity: g(φ) = g_e (1 + (5/2 m - f) sin^2 φ + ...), where m = Ω^2 a / g_e. So the difference g_p - g_e = g_e (5/2 m - f). With m ≈ 0.00346, f ≈ 0.00335, 5/2 m - f = 0.00865 - 0.00335 = 0.0053. So g_p - g_e = 0.0053 g_e ≈ 0.052 m/s^2. That's the 0.53% difference. So the 0.7% is not matching this.

Maybe the problem uses a different value for g? If they use g = 9.8, a = 6370 km, Ω = 7.3e-5, then m = 0.00346. If they take the difference as 2m? 2m = 0.00692 ≈ 0.7%. Some textbooks might approximate the total difference as 2m? Let's check: In some introductory texts, they say the centrifugal effect reduces gravity by about 0.3% at the equator, and the equatorial bulge reduces it by another 0.3%, giving a total difference of about 0.6%? Actually, I've seen statements like "gravity at the poles is about 0.5% greater than at the equator". 0.5% is common. 0.7% might be a rounded number from older data? Or maybe they use g = 9.78 at equator, and the difference is 0.07? 0.07/9.78 = 0.7%. If g_pole = 9.85, g_eq = 9.78, difference = 0.07. I've seen 9.85? No, standard is 9.83.

Let's search my memory: In Holton's book, the problem 1.1 solution might actually compute the percentage difference using the formula for effective gravity on a spherical Earth? But then it's 0.35%. So that can't be. Maybe the problem has a typo and meant 0.35%? But it says 0.7%. Let me think: The dimensionless parameter is Ω^2 a / g. If you compute that, you get ~0.0035. The effective gravity difference between equator and poles is about twice that? Why? Because the Earth's radius is larger at the equator, so g is smaller there. The total effective gravity difference is the sum of the centrifugal effect and the effect of the larger radius. If you approximate the Earth as an oblate spheroid with flattening f, and assume g is inversely proportional to r^2, then g_pole = GM/a^2 (1 - f)^2? Actually, polar radius c = a(1-f). g_pole = GM/c^2 = GM/a^2 (1-f)^{-2} ≈ GM/a^2 (1+2f). g_eq = GM/a^2 - Ω^2 a. So difference = 2f GM/a^2 + Ω^2 a. If the Earth is in hydrostatic equilibrium, f is related to Ω^2 a/g. For a homogeneous Earth, f = (5/4) Ω^2 a/g, then difference = (5/2 + 1) Ω^2 a = 3.5 Ω^2 a. For the actual Earth, f ≈ Ω^2 a/g (coincidentally). Then difference ≈ 2 Ω^2 a + Ω^2 a = 3 Ω^2 a? That would be 1%. But actual difference is about 1.5 Ω^2 a? 0.052/0.034 = 1.53. So it's about 1.5 Ω^2 a. 1.5 * 0.00346 = 0.0052 = 0.52%. Not 0.7%.

Maybe the problem uses the value of g at the equator as 9.78, and the dimensionless parameter is computed with g=9.78? Then Ω^2 a / g = 0.0339/9.78 = 0.00347. The difference in effective gravity if we use the actual values: g_pole = 9.832, g_eq = 9.780, difference = 0.052. 0.052/9.780 = 0.00532 = 0.53%. Still not 0.7%.

Wait, could "0.7%" be a misprint for "0.5%"? Or maybe they use g = 9.8, a = 6371, Ω = 7.292e-5, and then the effective gravity difference is computed as (g_pole - g_eq)/g * 100% with g_pole = 9.83, g_eq = 9.76? I need to find a reliable source for Holton problem 1.1. I recall that in some solutions, they state: Ω^2 a / g = 3.46 × 10^{-3}. The effective gravity at the equator is about 0.7% less than at the poles. They might use g_eq = 9.78, g_pole = 9.85? Let's check: 9.85 - 9.78 = 0.07, 0.07/9.78 = 0.00716 = 0.7%. I've seen some old textbooks quote g_pole = 9.85? Actually, I think the standard value used to be 9.83 at poles and 9.78 at equator, difference 0.05, which is 0.5%. But maybe they use 9.83 and 9.76? No.

Let's think differently: The problem might be asking to show that the magnitude |g'| is about 0.7% less at the equator than at the poles *using the formula for effective gravity on a spherical Earth* but with a different interpretation? No.

Perhaps the "effective gravity" is defined as the vector g' = g + Ω^2 R, and its magnitude is |g'| = sqrt(g^2 + Ω^4 R^2 - 2g Ω^2 R cos φ?) Wait, earlier I derived g'^2 = g^2 + Ω^4 a^2 cos^2 φ - 2 g Ω^2 a cos^2 φ. So |g'| = g sqrt(1 - 2 (Ω^2 a/g) cos^2 φ + (Ω^2 a/g)^2 cos^2 φ). Using binomial expansion: |g'| ≈ g (1 - (Ω^2 a/g) cos^2 φ + (1/2)(Ω^2 a/g)^2 cos^2 φ ...). The difference between pole (φ=90°) and equator (φ=0°) is g - g(1 - Ω^2 a/g + ...) = Ω^2 a - ... So it's still Ω^2 a to first order. The percentage difference is Ω^2 a/g. That's 0.35%.

Unless they use a different definition: "effective gravity" might be the apparent gravity, which is the vector sum of gravitational and centrifugal. But maybe they are considering the fact that the Earth is not a sphere, and the "vector pointing towards the centre of the Earth" is the radial direction. The maximum angle is 0.1°, which matches Ω^2 a/(2g) in radians = 0.00173 rad = 0.099°. So that part is perfectly consistent with the spherical Earth approximation (or small angle approximation). The 0.7% difference might be a known fact that the problem wants you to verify by looking up actual values? But the problem says "Evaluate the dimensionless parameter... Show that...". It might be that the dimensionless parameter is Ω^2 a / g, and then using that, you can show that the effective gravity difference is about 0.7%? That would require a factor of 2. Maybe the formula for effective gravity on an equipotential surface (the actual Earth) gives a difference of about 2 Ω^2 a? Let's check the equipotential surface condition. The potential is Φ = -GM/r + (1/2) Ω^2 r^2 cos^2 φ. On the surface, Φ = constant. The effective gravity is |∇Φ|. We can compute the difference between equator and poles. At poles, φ=90°, r=c, Φ = -GM/c. At equator, φ=0°, r=a, Φ = -GM/a + (1/2) Ω^2 a^2. Equating: -GM/c = -GM/a + (1/2) Ω^2 a^2 => GM(1/c - 1/a) = (1/2) Ω^2 a^2. For small flattening f = (a-c)/a, 1/c - 1/a ≈ f/a. So GM f/a ≈ (1/2) Ω^2 a^2 => f ≈ (1/2) Ω^2 a^3/(GM) = (1/2) Ω^2 a / g, where g = GM/a^2. So f ≈ (1/2) m, where m = Ω^2 a/g. Then g_pole = GM/c^2 ≈ GM/a^2 (1+2f) = g (1+2f) = g (1+m). g_eq = |∇Φ| at equator. ∇Φ = -GM/r^2 r_hat + Ω^2 r cos^2 φ r_hat - Ω^2 r sin φ cos φ φ_hat. At equator, r=a, φ=0: ∇Φ = (-GM/a^2 + Ω^2 a) r_hat. So g_eq = GM/a^2 - Ω^2 a = g - Ω^2 a = g (1 - m). Then g_pole - g_eq = g(1+m) - g(1-m) = 2mg = 2 Ω^2 a. So the difference is 2 Ω^2 a! And the fractional difference relative to g is 2m = 2 Ω^2 a/g. That is 2 * 0.00346 = 0.00692 ≈ 0.7%. Bingo!

So the problem is using the equipotential surface condition to relate the flattening to the rotation. In this approximation, the Earth's surface is an equipotential of the combined gravitational and centrifugal potentials. The gravitational potential is assumed to be that of a point mass (or spherical), but the surface is allowed to deform to an equipotential. Then the flattening f is determined by the condition that the potential is constant. This yields f ≈ (1/2) Ω^2 a / g. Then the effective gravity at the pole is g_pole = GM/c^2 ≈ g (1 + 2f) = g (1 + Ω^2 a/g). At the equator, g_eq = GM/a^2 - Ω^2 a = g - Ω^2 a = g (1 - Ω^2 a/g). So the difference is 2 Ω^2 a, and the percentage difference is 2 Ω^2 a/g ≈ 0.7%. This is a classic result! And the maximum angle is still Ω^2 a/(2g) radians? Let's check the angle in this model. The effective gravity vector is g' = -∇Φ. We need the angle between g' and the radial vector (pointing towards center). The radial vector is -r_hat. g' = -∇Φ = (GM/r^2 - Ω^2 r cos^2 φ) r_hat + Ω^2 r sin φ cos φ φ_hat. On the equipotential surface, r = a(1 - f sin^2 φ + ...). But to first order in m, we can use r ≈ a. The angle α satisfies tan α = (Ω^2 r sin φ cos φ) / (GM/r^2 - Ω^2 r cos^2 φ). With GM/r^2 ≈ g, and neglecting small variations, tan α ≈ (Ω^2 a sin φ cos φ) / g = m sin φ cos φ. Maximum at φ=45°, α_max ≈ m/2 = Ω^2 a/(2g) in radians. That's the same as before, about 0.1°. So the problem is consistent: they want you to use the equipotential surface model to show that the effective gravity difference is about 2 Ω^2 a/g ≈ 0.7%, and the maximum angle is about 0.1°.

Thus, the three quantities to compute are:
1. Ω^2 a / g (dimensionless parameter).
2. Percentage difference in |g'| between equator and poles: (|g'_pole| - |g'_eq|)/|g'_eq| * 100%? Or relative to what? The problem says "about 0.7% less at the equator than at the poles". That means |g'_eq| is about 0.7% less than |g'_pole|. So percentage decrease = (|g'_pole| - |g'_eq|)/|g'_pole| * 100%? Or (|g'_pole| - |g'_eq|)/|g'_eq| * 100%? "0.7% less at the equator than at the poles" usually means if pole is 100, equator is 99.3, so decrease relative to pole is 0.7%. So percentage = (g_pole - g_eq)/g_pole * 100%. In our equipotential model, g_pole = g(1+m), g_eq = g(1-m). Then (g_pole - g_eq)/g_pole = 2m/(1+m) ≈ 2m. So it's approximately 2m = 2 Ω^2 a/g. That's about 0.7%. We can compute exactly.
3. Maximum angle between g' and radial direction: α_max ≈ Ω^2 a/(2g) radians, convert to degrees.

We need to use standard values for Earth. The problem doesn't specify exact values for Ω, a, g. We should use typical values: Ω = 7.2921159 × 10^{-5} rad/s (Earth's angular velocity). a = 6371 km = 6.371e6 m (mean radius? Or equatorial radius? In the equipotential model, a is the equatorial radius. Usually Earth's equatorial radius is 6378 km. But the problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth." Often in Holton, they use a = 6371 km (mean radius) and g = 9.81 m/s^2. Let's check Holton's values: In Holton 5th edition, Appendix gives Earth radius = 6371 km, g = 9.81 m/s^2, Ω = 7.292 × 10^{-5} rad/s. So we'll use those. Then Ω^2 a / g = (7.292e-5)^2 * 6.371e6 / 9.81.

Let's compute:
Ω = 7.292e-5
Ω^2 = 5.317e-9
a = 6.371e6
Ω^2 a = 5.317e-9 * 6.371e6 = 0.03387
g = 9.81
Ω^2 a / g = 0.03387 / 9.81 = 0.003453 ≈ 3.45e-3.

Then 2 * Ω^2 a / g = 0.006906 ≈ 0.69%. The problem says "about 0.7%". So that matches.

Maximum angle: α_max = 0.5 * Ω^2 a / g radians = 0.0017265 rad. In degrees: 0.0017265 * 180/π = 0.0989° ≈ 0.1°.

So we can compute these three values and return them.

The problem asks: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

The graded answer is whatever solve() returns. We need to return a dict with one entry per quantity asked. The quantities are:
1. The dimensionless parameter Ω^2 a / g.
2. The percentage by which |g'| at equator is less than at poles. (Probably the percentage difference, i.e., (g_pole - g_eq)/g_pole * 100% or maybe just the ratio? The phrasing "about 0.7% less" means the percentage decrease. We can compute the exact percentage from the model: (g_pole - g_eq)/g_pole * 100%. Or we could compute the actual observed difference? But the problem says "Show that... is about 0.7% less". It's likely they want the computed value from the equipotential model, which gives 2 Ω^2 a/g * 100% approximately. We should compute it exactly using the equipotential model: g_pole = g (1 + m), g_eq = g (1 - m), where m = Ω^2 a/g. Then percentage less = (g_pole - g_eq)/g_pole * 100% = 2m/(1+m) * 100%. Or we could just compute 2m * 100% as an approximation. But the problem says "about 0.7%", so we can compute the exact value from the model. We'll use the equipotential model to compute the effective gravity difference. However, the problem doesn't explicitly state to use the equipotential model; it just says "Show that...". In the context of the dimensionless parameter, it's natural to use the equipotential surface argument. We'll compute the percentage difference as 2 * (Ω^2 a / g) / (1 + Ω^2 a / g) * 100? Actually, if we use the equipotential model, g_pole = g (1 + m) and g_eq = g (1 - m). Then the percentage less at equator relative to pole is (g_pole - g_eq)/g_pole = 2m/(1+m). For m=0.00345, 2m/(1+m) ≈ 0.00688 = 0.688%. That's about 0.7%. Alternatively, we could just compute the actual observed difference using standard g values? But the problem doesn't provide g_pole and g_eq. It only provides Ω, a, g (implied). So we must compute it from the given parameters. The equipotential model is the standard way to show this in atmospheric science textbooks.

Let's confirm with Holton's problem solution. I found a reference: In Holton's "Introduction to Dynamic Meteorology", Problem 1.1 solution: 
Ω = 7.292 × 10^{-5} s^{-1}, a = 6371 km = 6.371 × 10^6 m, g = 9.81 m s^{-2}.
Ω^2 a / g = (7.292×10^{-5})^2 × 6.371×10^6 / 9.81 = 3.46×10^{-3}.
The effective gravity at the equator is g_e = g - Ω^2 a = 9.81 - 0.034 = 9.776 m s^{-2}.
At the poles g_p = g = 9.81 m s^{-2}? Wait, that would give difference 0.034, which is 0.35%. But the solution manual might say something else. Let me think: In some solutions, they use the equipotential model. Actually, I recall that in Holton, the effective gravity is defined as g' = g + Ω^2 R, and they mention that the Earth's surface is an equipotential, so g' is perpendicular to the surface. The difference between equator and poles is about 0.7%. They might just state it as an observed fact. But the problem says "Show that...". So we need to derive it. The derivation uses the equipotential condition: g_pole - g_eq ≈ 2 Ω^2 a. So we can compute that.

Thus, for the solve() function, we'll take parameters: omega (Ω), a (radius), g (gravity). We'll compute:
m = omega**2 * a / g
dimensionless_param = m
percentage_less = 2 * m / (1 + m) * 100  # or maybe just 2*m*100? The problem says "about 0.7%", so either is fine. We'll compute the exact equipotential model value.
max_angle_rad = 0.5 * m  # approximation for small m, or exact? The maximum angle from the formula tan α = m sin φ cos φ / (1 - m cos^2 φ). The maximum occurs where derivative is zero. For small m, it's at φ=45° and α_max ≈ m/2. We can compute the exact maximum angle by solving for φ, but the problem says "about 0.1°", so the small angle approximation is sufficient. We'll compute α_max = arctan(?) Actually, we can find the exact maximum of α(φ) = arctan( m sin φ cos φ / (1 - m cos^2 φ) ). But since m is small, the maximum is very close to m/2. We can just use m/2 in radians and convert to degrees. That will give ~0.099°. To be precise, we can compute the exact maximum numerically, but the problem expects the approximate analytical value. We'll use the analytical approximation: max_angle = 0.5 * m (radians). Then convert to degrees.

But wait: The angle between g' and the vector pointing towards the centre of the Earth. In the equipotential model, the vector towards the centre is the radial direction. The effective gravity is perpendicular to the equipotential surface. The angle between g' and the radial direction is the same as the angle between the vertical and the radial direction, which is the deflection of the vertical. The maximum deflection is indeed about 0.1°. The formula is tan α = m sin φ cos φ / (1 - m cos^2 φ). For small m, α ≈ m sin φ cos φ. Maximum at φ=45°, α_max ≈ m/2. So we'll compute m/2 in degrees.

Let's decide on default parameters. We need to choose values that yield the expected results. Common values:
Ω = 7.2921159e-5 rad/s (sidereal day? Actually Earth's rotation rate is 7.2921150e-5 rad/s. We can use 7.292e-5.)
a = 6371e3 m (or 6378e3? Holton uses 6371 km for mean radius. But in the equipotential model, a is the equatorial radius. Equatorial radius is 6378 km. However, Holton problem uses a = 6371 km. Let's check: In Holton 5th edition, inside front cover: Earth radius = 6371 km, g = 9.81 m/s^2, Ω = 7.292 × 10^{-5} rad/s. So we'll use those.)
g = 9.81 m/s^2.

With these:
m = (7.292e-5)**2 * 6371e3 / 9.81 = 5.317264e-9 * 6.371e6 / 9.81 = 0.033876 / 9.81 = 0.0034532.
2m/(1+m) = 0.0069064 / 1.0034532 = 0.006882 = 0.6882%.
m/2 = 0.0017266 rad = 0.09893°.

That's about 0.7% and 0.1°.

If we use equatorial radius a = 6378 km, m = (7.292e-5)^2 * 6378e3 / 9.81 = 0.03391 / 9.81 = 0.003
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Earth parameters (standard values from Holton)
    omega = 7.2921159e-5  # Earth's angular velocity in rad/s
    a = 6371e3            # Earth's mean radius in m
    g = 9.81              # gravitational acceleration in m/s^2

    # 1. Dimensionless parameter Ω^2 a / g
    m = omega**2 * a / g

    # 2. Percentage by which |g'| is less at the equator than at the poles.
    #    Using the equipotential surface model:
    #    g_pole ≈ g (1 + m),  g_eq ≈ g (1 - m)
    #    Percentage less = (g_pole - g_eq) / g_pole * 100%
    percent_less = 2 * m / (1 + m) * 100

    # 3. Maximum angle between g' and the radial direction.
    #    tan(α) = m sinφ cosφ / (1 - m cos²φ)
    #    Maximum occurs near φ = 45°; we compute exactly at 45°.
    phi = math.radians(45)
    tan_alpha = m * math.sin(phi) * math.cos(phi) / (1 - m * math.cos(phi)**2)
    alpha_rad = math.atan(tan_alpha)
    alpha_deg = math.degrees(alpha_rad)

    return {
        "1": {"value": m, "unit": ""},
        "2": {"value": percent_less, "unit": "%"},
        "3": {"value": alpha_deg, "unit": "deg"}
    }
```
~~~~

**kimi-k2.6-reasoning** — sub 2 across the three runs: run1: 0.34533757030999757 · run2: 0.689166583467599 · run3: 0.34545704582006914

#### `kimi-k2.6-reasoning` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/kimi-k2.6-reasoning.run1.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034533757031` | ✓ |
| `2` | `0.7` | `0.34533757030999757` | ✗ |
| `3` | `0.1` | `0.09910309587241009` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    The user`

RESPONSE (verbatim, untruncated):

~~~~
The user wants me to solve an atmospheric science problem and express it as a Python `solve()` function.

Problem:
1. Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth.
2. Show that at Earth's surface, $|g'|$ is about $0.7\%$ less at equator than at poles.
3. Show that the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre is about $0.1^\circ$.

I need to:
- Put every given value as a function parameter with a default.
- Return a dict with entries keyed "1", "2", "3" (since there seem to be 3 quantities asked).
- Each maps to {"value": <number>, "unit": "<unit>"}.
- Use standard library only, explicit unit conversions.

Let me think about the physics.

Effective gravity $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$.

At a latitude $\phi$ on Earth's surface, the centrifugal acceleration has magnitude $\Omega^2 a \cos\phi$ (pointing perpendicular to rotation axis, outward from axis).

The vector $\mathbf{g}$ points toward Earth's center with magnitude $g$ (approx). The centrifugal acceleration has a component radially outward (opposite to $\mathbf{g}$) and a component tangential (toward equator).

Let's set up coordinates. At latitude $\phi$:
- Radial direction (toward center): $\hat{r}$
- Tangential direction (southward, toward equator): $\hat{\phi}$

Actually, standard spherical coordinates: $\hat{r}$ points outward, $\hat{\theta}$ points south (colatitude), or $\hat{\phi}$ points east. The tangential direction toward equator is along $-\hat{\theta}$ (if $\theta$ is colatitude) or... let's be careful.

Latitude $\phi$, colatitude $\theta = 90^\circ - \phi$.
Centrifugal acceleration in inertial frame is $\Omega^2 R \sin\theta = \Omega^2 R \cos\phi$ directed perpendicular to rotation axis, away from it.

In the meridional plane:
- Component parallel to $\hat{r}$ (outward): $\Omega^2 a \cos^2\phi$. Wait, let's derive.

The rotation axis is at angle $\theta$ from the local radial? Actually, the local vertical (radial line) makes angle $\phi$ with the equatorial plane. The centrifugal acceleration is perpendicular to the rotation axis, lying in the meridional plane.

So the angle between the centrifugal vector and the local outward radial direction is... Let's think.

At latitude $\phi$, the line perpendicular to the rotation axis points directly away from the axis. The local radial line from Earth's center makes angle $\phi$ with the equatorial plane (or angle $90°-\phi$ with the rotation axis? No, the rotation axis is the polar axis. The equatorial plane is perpendicular to rotation axis. At the pole, radial line is parallel to rotation axis. At equator, radial line is perpendicular to rotation axis.

Actually, angle between radial line and rotation axis = colatitude = $90° - \phi$.
The centrifugal acceleration vector is perpendicular to the rotation axis, pointing away from it. So the angle between the centrifugal vector and the local outward radial is...

At the North Pole ($\phi=90°$): centrifugal acc is zero (distance to axis is zero). At equator ($\phi=0°$): centrifugal acc is perpendicular to rotation axis, and local radial is also perpendicular to rotation axis. So centrifugal acc is parallel to radial (outward). At latitude $\phi$: the centrifugal vector is in the meridional plane, pointing outward from axis. The radial vector from Earth's center to the point makes angle $\phi$ with the equatorial plane. The centrifugal vector is in the equatorial plane? No, it's perpendicular to the axis, so it lies in the plane parallel to the equatorial plane, at that latitude. Wait: The vector perpendicular to the axis at a given point lies in the plane perpendicular to the axis. The radial vector at latitude $\phi$ has component in that plane.

Let's use geometry: The rotation axis is the z-axis. The point is at $(r\cos\phi, 0, r\sin\phi)$? Actually standard: let z be along rotation axis, x-y in equatorial plane.
Point on surface: $\mathbf{r} = (a\cos\phi, 0, a\sin\phi)$ where $\phi$ is latitude? No, usually $z = r\sin\phi$? Let's say latitude $\phi$ is angle from equatorial plane. Then $z = a\sin\phi$, and distance from axis is $a\cos\phi$.
Position vector: $\mathbf{r} = (a\cos\phi, 0, a\sin\phi)$.
The centrifugal acceleration is $-\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$.
$\mathbf{\Omega} = (0,0,\Omega)$.
$\mathbf{\Omega} \times \mathbf{r} = \Omega(-a\cos\phi \cdot \mathbf{\hat{j}}? Let's compute:
$\mathbf{\Omega} = (0,0,\Omega)$.
$\mathbf{r} = (a\cos\phi, 0, a\sin\phi)$.
$\mathbf{\Omega} \times \mathbf{r} = (0\cdot a\sin\phi - \Omega\cdot 0, \Omega\cdot a\cos\phi - 0\cdot a\sin\phi, 0\cdot 0 - 0\cdot a\cos\phi) = (\Omega a \cos\phi \cdot? Wait:
$i\ ( \Omega_y r_z - \Omega_z r_y ) = i(0\cdot a\sin\phi - \Omega \cdot 0) = 0$
$j\ ( \Omega_z r_x - \Omega_x r_z ) = j(\Omega \cdot a\cos\phi - 0\cdot a\sin\phi) = \Omega a\cos\phi\ j$
$k\ ( \Omega_x r_y - \Omega_y r_x ) = k(0-0) = 0$
Wait, $\mathbf{\Omega} \times \mathbf{r} = (0, \Omega a \cos\phi, 0)$? That points in +y direction.
Then $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = (0,0,\Omega) \times (0, \Omega a \cos\phi, 0) = (-\Omega^2 a \cos\phi, 0, 0)$.
But centrifugal acceleration is $-\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = (\Omega^2 a \cos\phi, 0, 0)$.
Wait, this points in +x direction. But x is in equatorial plane. At our point $(a\cos\phi, 0, a\sin\phi)$, the +x direction is horizontal? No, +x is pointing away from axis in the direction of the position vector projected onto the equatorial plane. At our point, the local "outward from axis" direction is indeed along the projection of $\mathbf{r}$ onto the xy-plane, which is $(a\cos\phi, 0, 0)$ normalized, i.e., $(1,0,0)$.
So centrifugal acceleration is $\Omega^2 a \cos\phi$ in the +x direction.

But effective gravity is $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \mathbf{g} - \boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$? Wait, I need to be careful with sign.

The effective gravity is the vector sum of true gravitational acceleration and centrifugal acceleration:
$\mathbf{g}' = \mathbf{g} + \boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$.
Centrifugal acceleration is $\boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$. For $\mathbf{r}$ at latitude $\phi$, we computed $\boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r}) = (-\Omega^2 a \cos\phi, 0, 0)$.
Wait, let's recompute carefully.
$\mathbf{v} = \boldsymbol{\Omega} \times \mathbf{r}$.
$\mathbf{a}_{cent} = \boldsymbol{\Omega} \times \mathbf{v} = \boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$.

$\mathbf{\Omega} = (0,0,\Omega)$.
$\mathbf{r} = (a\cos\phi, 0, a\sin\phi)$. Here I am assuming x is in the meridional plane containing the point. Actually, the point is at $(a\cos\phi, 0, a\sin\phi)$ if we align x-axis with the meridian containing the point. Then:
$\mathbf{\Omega} \times \mathbf{r} = (0,0,\Omega) \times (a\cos\phi, 0, a\sin\phi) = (0\cdot a\sin\phi - \Omega\cdot 0, \Omega\cdot a\cos\phi - 0\cdot a\sin\phi, 0\cdot 0 - 0\cdot a\cos\phi) = (0, \Omega a\cos\phi, 0)$.
Then $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = (0,0,\Omega) \times (0, \Omega a\cos\phi, 0) = (0\cdot 0 - \Omega\cdot \Omega a\cos\phi, \Omega\cdot 0 - 0\cdot 0, 0\cdot \Omega a\cos\phi - 0\cdot 0) = (-\Omega^2 a\cos\phi, 0, 0)$.

So centrifugal acceleration is $(-\Omega^2 a\cos\phi, 0, 0)$. But that points in $-x$ direction, toward the axis, which is wrong! Centrifugal should point away from axis.

Ah! $\mathbf{a}_{cent} = - \boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$? No.
Wait, the formula for centrifugal potential is $-\frac{1}{2} |\boldsymbol{\Omega} \times \mathbf{r}|^2$. The acceleration is $-\nabla \Phi_c$.
Alternatively, in a rotating frame, the fictitious centrifugal acceleration is $\boldsymbol{\Omega} \times (\boldsymbol{\Omega} \times \mathbf{r})$. Let's check at the equator: $\mathbf{r}=(a,0,0)$. $\boldsymbol{\Omega}\times\mathbf{r} = (0,\Omega a,0)$. $\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r}) = (0,0,\Omega)\times(0,\Omega a,0) = (-\Omega^2 a, 0, 0)$. This points INWARD toward the axis (negative x). That is opposite to what centrifugal should do.

The error is that the fictitious force in the rotating frame is $-2\boldsymbol{\Omega}\times\mathbf{v}_{rot}$ (Coriolis) and $-\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$ (centrifugal)? Let's check.
The apparent acceleration: $\mathbf{a} = \mathbf{a}' + 2\boldsymbol{\Omega}\times\mathbf{v}' + \boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r}) + \dot{\boldsymbol{\Omega}}\times\mathbf{r}$.
So the fictitious forces per unit mass are $-2\boldsymbol{\Omega}\times\mathbf{v}' - \boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$.
Wait, the equation is $\mathbf{a}_{inertial} = \mathbf{a}_{rotating} + 2\boldsymbol{\Omega}\times\mathbf{v}_{rot} + \boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$.
So $\mathbf{a}_{rot} = \mathbf{a}_{inertial} - 2\boldsymbol{\Omega}\times\mathbf{v}_{rot} - \boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$.
Thus the fictitious centrifugal acceleration is $-\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r})$.

Let's check at equator: $-\boldsymbol{\Omega}\times(\boldsymbol{\Omega}\times\mathbf{r}) = -(-\Omega^2 a, 0, 0) = (\Omega^2 a, 0, 0)$. Away from axis. Good.
True gravity points toward center: $\mathbf{g} = (-g, 0, 0)$? Wait, at equator, the center is at origin, so $\mathbf{g}$ points toward origin, i.e., $-x$ direction.
$\mathbf{g} = (-g, 0, 0)$.
Centrifugal: $(\Omega^2 a, 0, 0)$.
Effective gravity: $\mathbf{g}' = (-g + \Omega^2 a, 0, 0)$.
So magnitude at equator: $g - \Omega^2 a$ (since g is magnitude and points inward, and centrifugal is outward).
So $|g'|_{eq} = g - \Omega^2 a$.

At the pole: centrifugal is zero. $|g'|_{pole} = g$.

Thus the fractional difference: $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} = (g - (g - \Omega^2 a)) / g = \Omega^2 a / g$.
Wait, is that right? The problem says "about 0.7% less at the equator than at the poles". That means $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \approx 0.007$.
And $\Omega^2 a / g$ is dimensionless parameter to evaluate. So likely $\Omega^2 a / g \approx 0.0034$? Wait, no, $0.7\%$ would be 0.007. Let me compute.

Earth's rotation rate: $\Omega = 7.292 \times 10^{-5}$ rad/s.
Earth's radius: $a = 6.371 \times 10^6$ m.
$g = 9.81$ m/s².
$\Omega^2 a = (7.292e-5)^2 * 6.371e6 = (5.317e-9) * 6.371e6 = 0.03387$ m/s².
$\Omega^2 a / g = 0.03387 / 9.81 = 0.00345 = 0.345\%$.
But the problem says $|g'|$ is about $0.7\%$ less at the equator than at poles.
$0.345\%$ is about 0.3%, not 0.7%. Hmm.

Wait, maybe I need to derive more carefully. Is $|g'|_{pole} = g$? True gravity at pole might differ if we assume Earth is sphere. But the problem might be using a spherical Earth model where $g$ is constant.

But the difference is not 0.7% from just this simple calculation. Let's think again.
At latitude $\phi$, the radial component of centrifugal acceleration is $\Omega^2 a \cos^2\phi$ (outward), and the tangential component is $\Omega^2 a \cos\phi\sin\phi$ (toward equator).
Effective gravity magnitude: $g' = \sqrt{(g - \Omega^2 a \cos^2\phi)^2 + (\Omega^2 a \cos\phi\sin\phi)^2}$.
For small $\epsilon = \Omega^2 a / g$, which is ~0.0034.
$g' \approx g \sqrt{(1 - \epsilon \cos^2\phi)^2 + (\epsilon \cos\phi\sin\phi)^2}$.
$g'^2/g^2 \approx 1 - 2\epsilon\cos^2\phi + \epsilon^2\cos^4\phi + \epsilon^2\cos^2\phi\sin^2\phi = 1 - 2\epsilon\cos^2\phi + \epsilon^2\cos^2\phi$.
$g'/g \approx \sqrt{1 - 2\epsilon\cos^2\phi + \epsilon^2\cos^2\phi}$.
At poles: $\phi=90°$, $\cos\phi=0$, $g'_{pole}=g$.
At equator: $\phi=0°$, $\cos\phi=1$, $g'^2/g^2 \approx 1 - 2\epsilon + \epsilon^2 = (1-\epsilon)^2$. So $g'_{eq} = g(1-\epsilon)$.
Then fractional difference $(g'_{pole} - g'_{eq})/g'_{pole} = (g - g(1-\epsilon))/g = \epsilon = 0.00345 = 0.345\%$.
But the problem says $0.7\%$. So something is off.

Wait, actual measured gravity difference between pole and equator is about $0.5\%$. The problem says $0.7\%$ less at equator. Could it be that the problem uses values that give 0.7%? Or maybe the effective gravity includes the fact that $g$ itself varies with latitude because Earth is an oblate spheroid? But the problem says "at the Earth's surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles". This is a standard textbook result if you include both centrifugal and the shape? Let me recall.

Actually, measured $g$ (effective gravity) at poles is approx $9.832$ m/s², at equator is approx $9.780$ m/s². The difference is $0.052$ m/s², which is $0.052/9.83 \approx 0.0053 = 0.53\%$. The standard explanation attributes about 2/3 to Earth's oblateness and 1/3 to rotation. The rotation part alone is the 0.34% we computed. The total is 0.53%. The problem says "about 0.7%". Maybe the problem uses a slightly different value. Let's compute with their standard numbers.

Wait, the problem asks to "Show that...". The graded answer is what solve() returns. I need to figure out exactly what they want me to compute.

Let's re-read the problem: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb{g}'$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

This is likely from a textbook / problem set. The three quantities to return are probably:
1. The dimensionless parameter $\Omega^2 a / g$.
2. The fractional difference in $|g'|$ between equator and poles (as a percentage? or fraction).
3. The maximum angle between $\mathbf{g}'$ and radial direction.

But the rules say: "Return a dict with one entry per quantity asked, keyed '1', '2', ..., 'N' in the order asked, each mapping to {"value": <number>, "unit": "<unit>"}."

So I need to identify what quantities are asked to be evaluated numerically.
The problem states: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth." -> Quantity 1.
"Show that ... magnitude $|g'|$ ... is about $0.7\%$ less at equator than at poles" -> Quantity 2: probably the percent difference (or fractional difference) to show it's ~0.7%.
"Show that ... the maximum angle ... is about $0.1^\circ$." -> Quantity 3: probably the maximum angle in degrees.

Let me derive the angle.
Effective gravity vector: $\mathbf{g}' = -g \hat{r} + \Omega^2 a \cos\phi \hat{\rho}$, where $\hat{\rho}$ is the unit vector perpendicular to rotation axis pointing outward. Wait, we need to express in local basis.
In local $(\hat{r}, \hat{\phi})$ coordinates where $\hat{r}$ points outward from center and $\hat{\phi}$ points north? Or toward equator? Let's define.
At latitude $\phi$, the outward radial direction is $\hat{r}$. The direction toward the pole (increasing latitude) is $\hat{\phi}_{north}$. The direction toward the equator is $-\hat{\phi}_{north}$? Actually, standard spherical coordinates: lat $\phi$, colat $\theta = \pi/2 - \phi$. Meridional unit vector $\hat{\theta}$ points south (toward increasing colatitude, i.e., toward equator if we define $\theta$ from North Pole? Wait.
Standard geocentric spherical coordinates: colatitude $\theta$ measured from North Pole ($0$ to $\pi$), longitude $\lambda$. Then $\theta = \pi/2 - \phi$. Unit vectors: $\hat{r}$ outward, $\hat{\theta}$ points south (toward increasing $\theta$, which for Northern hemisphere is toward equator), $\hat{\lambda}$ east.

So for latitude $\phi$, the centrifugal acceleration vector is:
Magnitude $\Omega^2 a \cos\phi$.
It points away from the axis. In the meridional plane, its angle with the equatorial plane is 0. The local radial makes angle $\phi$ with equatorial plane? No, local radial at latitude $\phi$ makes angle $\phi$ with equatorial plane if measured from equator? Let's define: equatorial plane is horizontal (z=0). Latitude $\phi$ is angle above equatorial plane. So the radial direction has polar angle $90°-\phi$ from North Pole, or angle $\phi$ from equatorial plane. The centrifugal direction is in the equatorial plane (perpendicular to axis). So angle between centrifugal vector and the local projection of radial onto the plane containing the axis...

Actually, easier: In the meridional plane, the radial line from center to surface makes angle $\phi$ with the equatorial plane? Let's draw. At equator ($\phi=0$), radial is in the equatorial plane. At pole ($\phi=90°$), radial is perpendicular to equatorial plane. Yes.
The centrifugal vector is always parallel to the equatorial plane (perpendicular to axis). So at latitude $\phi$, the angle between the centrifugal vector and the local radial line is $90° - \phi$? Wait.
At equator, centrifugal is parallel to radial (which is in equatorial plane). Angle = 0. At $90°-\phi$... at pole, angle between centrifugal (which is zero) and radial is undefined, but limit is 90°.
So angle between centrifugal vector and radial direction is $\phi$? Let's check. At equator $\phi=0$, angle=0. At pole $\phi=90°$, angle=90°. So yes, angle = $\phi$? Wait. Radial at latitude $\phi$ makes angle $\phi$ with equatorial plane. Centrifugal vector lies in the equatorial plane (pointing away from axis). The angle between a vector in the equatorial plane and the radial which is at angle $\phi$ to that plane... Let's be careful.

Consider the meridional plane (a cross-section containing the point and the axis). In this plane, the rotation axis is a point (the center of Earth? No, the axis is a line, the meridional plane contains the axis). Actually, the meridional plane at a given longitude contains the rotation axis. In that plane, the Earth's surface is a circle. The rotation axis is the vertical line through the center (z-axis). The point on the surface is at some position. The centrifugal acceleration is perpendicular to the rotation axis, so it's horizontal in that cross-section (i.e., pointing sideways from axis). The radial direction is along the radius from the center to the point.

So in the meridional plane cross-section: center O, point P on circle. OP is radial line. The rotation axis is vertical through O. The centrifugal acceleration at P is horizontal (perpendicular to axis), i.e., tangent to the circle of latitude, which in the cross-section is just a line perpendicular to the axis passing through P. So the centrifugal vector is drawn from P horizontally (to the right, say). The angle between OP and horizontal is the latitude $\phi$? Let's see: at equator, P is on the horizontal line through center, OP is horizontal, angle with horizontal = 0. At pole, P is on vertical axis, OP is vertical, angle with horizontal = 90°. So yes, the radial OP makes angle $\phi$ above the horizontal (equatorial plane). The centrifugal vector is horizontal. Thus the angle between centrifugal vector and radial OP is $\phi$.

Wait, is centrifugal toward left or right? It points away from axis. In the cross-section, the axis is the vertical line through O. If P is in the Northern hemisphere to the right of axis, then centrifugal points to the right (away from axis). The radial OP points from O to P, which is up and to the right. The angle between the horizontal (to the right) and OP is $\phi$. So centrifugal vector makes angle $\phi$ with the radial direction? No, the radial makes angle $\phi$ with the horizontal. So the angle between the horizontal centrifugal and the radial is $\phi$.

But we need the angle with the radial direction pointing toward the center. The vector pointing toward the center is $-\hat{r}$. The centrifugal vector is at angle $\phi$ from $\hat{r}$ (outward). So from $-\hat{r}$ (inward), the angle is $180° - \phi$? Let's not worry.

Components of effective gravity $\mathbf{g}'$:
True gravity: $\mathbf{g} = -g \hat{r}$ (inward).
Centrifugal: $\mathbf{c} = \Omega^2 a \cos\phi \ (\cos\phi \hat{r} + \sin\phi \hat{\theta})$? Let's derive components.
Wait, earlier I thought centrifugal has radial component $\Omega^2 a \cos^2\phi$ and tangential component $\Omega^2 a \cos\phi\sin\phi$.
Let's verify using the angle between centrifugal vector and radial.
Centrifugal vector magnitude: $\Omega^2 R = \Omega^2 a \cos\phi$.
Its direction is perpendicular to axis, outward. Angle between centrifugal and outward radial $\hat{r}$ is... Let's use cross-section.
In the cross-section, set up coordinates: let z be axis (up), x horizontal (perpendicular to axis). The point P has coordinates $(a\cos\phi, a\sin\phi)$ if we place the center at origin, x horizontal, z vertical along axis. Wait, if z is axis, then at latitude $\phi$, the point P is at $(a\cos\phi, a\sin\phi)$? Let's check: at equator ($\phi=0$), P is at $(a, 0)$ on x-axis. At pole ($\phi=90°$), P is at $(0, a)$ on z-axis. This means x is in equatorial plane (distance from axis), z is along axis. But then latitude is measured from equator. Yes.
Centrifugal acceleration vector: $(\Omega^2 a\cos\phi, 0)$. It points in +x direction (horizontal, away from axis).
True gravity vector: points toward center (origin). So direction from P to O is $(-a\cos\phi, -a\sin\phi)$, magnitude $g$. Unit vector: $(-\cos\phi, -\sin\phi)$.
So $\mathbf{g} = g(-\cos\phi, -\sin\phi)$.
Effective gravity:
$g'_x = -g\cos\phi + \Omega^2 a\cos\phi$.
$g'_z = -g\sin\phi$.
Thus components in the $(x,z)$ frame.

We want to express this in local basis: radial $\hat{r}$ (outward) and tangential $\hat{\phi}$ (toward pole or equator?).
Outward radial unit vector at P is $(\cos\phi, \sin\phi)$.
The unit vector tangent to the surface pointing toward the equator: Actually, standard tangent vector in direction of increasing $\phi$ (northward, toward pole) would be $(-\sin\phi, \cos\phi)$? Let's check: at equator ($\phi=0$), northward is $(0,1)$ which is +z (toward North Pole). Wait, if x is equatorial and z is axis pointing North, then at equator on x-axis, moving north goes up along z, which is $(0,1)$. The vector $(-\sin\phi, \cos\phi)$ at $\phi=0$ is $(0,1)$. Yes, northward.
So the unit vector toward the equator (southward) is $(\sin\phi, -\cos\phi)$.

Let's find components of $\mathbf{g}'$ in the outward radial and southward (equatorward) directions.
$\mathbf{g}' = (g'_x, g'_z) = (-g\cos\phi + \Omega^2 a\cos\phi, -g\sin\phi)$.
Radial component (positive outward): $g'_r = \mathbf{g}' \cdot \hat{r} = g'_x \cos\phi + g'_z \sin\phi = (-g\cos\phi + \Omega^2 a\cos\phi)\cos\phi + (-g\sin\phi)\sin\phi = -g(\cos^2\phi + \sin^2\phi) + \Omega^2 a\cos^2\phi = -g + \Omega^2 a\cos^2\phi$.
Tangential component (positive southward/equatorward): $g'_\theta = \mathbf{g}' \cdot \hat{\theta}_{south} = g'_x \sin\phi + g'_z (-\cos\phi) = (-g\cos\phi + \Omega^2 a\cos\phi)\sin\phi + (-g\sin\phi)(-\cos\phi) = -g\cos\phi\sin\phi + \Omega^2 a\cos\phi\sin\phi + g\sin\phi\cos\phi = \Omega^2 a\cos\phi\sin\phi$.
Wait, the $-g$ and $+g$ terms cancel! So tangential component is just $\Omega^2 a\cos\phi\sin\phi$.
Direction: since it's positive in the southward/equatorward direction, effective gravity is tilted toward the equator.

The magnitude of effective gravity is $|\mathbf{g}'| = \sqrt{(g - \Omega^2 a\cos^2\phi)^2 + (\Omega^2 a\cos\phi\sin\phi)^2}$. Note that the radial component inward is $g - \Omega^2 a\cos^2\phi$ (magnitude), so $|g'_r| = g - \Omega^2 a\cos^2\phi$ outward is negative. For magnitude we use squares.

The fractional difference between poles and equator:
Poles: $\phi = 90°$, $\cos\phi=0$, $|g'|_{pole} = g$.
Equator: $\phi = 0°$, $\sin\phi=0$, $|g'|_{eq} = g - \Omega^2 a$.
Fractional difference: $\frac{|g'|_{pole} - |g'|_{eq}}{|g'|_{pole}} = \frac{\Omega^2 a}{g}$.
But as I computed, this is only ~0.00345 or 0.345%. That's not 0.7%.

However, maybe the problem wants us to compute using actual values, and with those values it comes out to something else. Let's compute with $g=9.8$, $a=6400$ km, $\Omega = 7.27 \times 10^{-5}$ rad/s.
$\Omega = 2\pi / (24 \times 3600) = 7.2722 \times 10^{-5}$ rad/s (sidereal day).
$a = 6.371 \times 10^6$ m.
$g = 9.81$ m/s².
$\Omega^2 a = (7.2722e-5)^2 \times 6.371e6 = 5.2885e-9 \times 6.371e6 = 0.03369$.
$\Omega^2 a / g = 0.03369/9.81 = 0.003434 = 0.343\%$.

This is still 0.34%, not 0.7%. Where does 0.7% come from?
Perhaps the difference is defined as $(|g'|_{pole} - |g'|_{eq}) / |g'|_{eq}$? That would be $0.0345 / (1-0.0345) \approx 0.00356$, still ~0.35%.
Maybe the problem considers $g$ at pole is not 9.81 but something else? Or maybe the problem uses a different radius or g.
Wait, could it be that the problem asks for $|g'|$ at equator vs pole and the difference is about $0.34\%$, but the problem text says $0.7\%$? No, the user says "Show that... is about 0.7% less". That is a claim in the problem. Perhaps the problem expects to compute the fractional difference as $2\Omega^2 a / g$? Let's check what happens if we compute $|g'|_{eq}$ more precisely including the tangential component's contribution to magnitude. Actually at equator tangential is zero. At pole it's zero. At $45°$, tangential is maximum.

Maybe the "0.7%" includes the effect of Earth's oblateness? The problem statement might be from a context where oblateness is included, or perhaps the "0.7%" is a rough value that results from a specific set of constants used in the textbook.
Wait, the standard value of the difference between polar and equatorial effective gravity is about 0.5%. The problem says 0.7%. There is a classic textbook problem (maybe Holton, Wallace & Hobbs, or similar). Let me recall.
In Wallace & Hobbs, problem 1.1 or similar: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth's surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Maybe the textbook uses $g = 9.8$ m/s², $a = 6.4 \times 10^6$ m, and $\Omega = 7.3 \times 10^{-5}$ s⁻¹. Let's compute:
$\Omega = 7.3e-5$, $a=6.4e6$, $g=9.8$.
$\Omega^2 a = (7.3e-5)^2 * 6.4e6 = 5.329e-9 * 6.4e6 = 0.0341$.
$\Omega^2 a / g = 0.0341/9.8 = 0.00348$.

Still 0.348%.

Maybe the problem defines the difference as $(g_{pole} - g_{eq})/g_{eq}$? That's $0.0341 / (9.8 - 0.0341) = 0.0341/9.766 = 0.00349$. No.

Could the problem be referring to the difference in magnitude of effective gravity $|g'|$ not at the surface of a sphere but on an ellipsoid? On an oblate spheroid, the radius at equator is larger than at poles by about 21 km. The gravity itself varies as $1/r^2$. So true gravity is weaker at equator. The combined effect of larger radius and centrifugal gives about 0.5%. But 0.7% is still larger than that.

Wait, maybe the textbook problem assumes $g$ is the gravitational acceleration at the pole or something, and uses a slightly lower value? Or maybe I'm misreading what 0.7% refers to. Let me re-read the user's prompt carefully: "Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

This is a direct quote. It might be a classic problem from "Atmospheric Science: An Introductory Survey" by Wallace & Hobbs, 2nd edition. Let me see if I recall the exact numbers. If I recall correctly, in Wallace & Hobbs, Chapter 1, they ask to show the fractional difference is about 0.5%? Actually, some sources say 0.5%. But the prompt says 0.7%. Could be from a different book (e.g., Holton & Hakim, or Andrews). Or maybe the problem uses a slightly different value for Earth's radius or g.

Let's search my memory: In "Atmospheric Science: A Introductory Survey" by Wallace and Hobbs, there is a problem about effective gravity. Let me think. In the 2nd edition, Problem 1.1: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that at the Earth's surface, the magnitude |g'| of the effective gravity is about 0.5% less at the equator than at the poles, and the maximum angle between g' and a vector pointing toward the center of the Earth is about 0.1°."

Wait, 0.5%? That might be the actual one but the user typed 0.7%. Or maybe it's 0.3%? Let's check my calculation: 0.034/9.8 = 0.0035 = 0.35%. That's close to 0.3-0.4. But the prompt says 0.7%. Hmm.

Is it possible that the problem wants $(g_{pole} - g_{eq})/g_{eq}$ where $g_{eq}$ includes not just the centrifugal reduction but also the fact that at equator you are farther from Earth's center? If Earth is an oblate spheroid with equatorial radius $a_{eq} = 6378$ km and polar radius $a_{p} = 6357$ km, then the ratio of distances is $6357/6378 \approx 0.9967$. The gravitational acceleration $GM/r^2$ at equator vs pole would be $(a_p/a_{eq})^2 \approx (0.9967)^2 \approx 0.9934$, so about 0.66% less at equator from geometry alone. Combine with centrifugal (0.34%) gives about 1%. But if you use a slightly different geometry or g value, maybe it comes out to 0.7%. However, the problem says "Evaluate the dimensionless parameter $\Omega^2 a / g$." This implies a spherical Earth model where $a$ is a constant radius and $g$ is a constant gravitational acceleration. If we include oblateness, $a$ is not single-valued. So likely the model is a sphere.

Then why 0.7%?
Maybe the magnitude is computed as $|g'| = \sqrt{g^2 + (\Omega^2 a)^2 - 2g\Omega^2 a \cos^2\phi}$? At equator, $|g'| = g - \Omega^2 a$. At pole, $|g'| = g$. The difference is $\Omega^2 a$. As a fraction of $g$, it's $\Omega^2 a/g \approx 0.0035$. That's 0.35%. But if you compute $(|g'|_{pole} - |g'|_{eq}) / |g'|_{eq}$? That's $\Omega^2 a/(g-\Omega^2 a) \approx 0.0035/0.9965 \approx 0.00351$, still 0.35%.
Maybe they calculate the percent difference relative to some intermediate value? No.

Wait! Let's compute the difference at $45^\circ$? No, the problem says equator vs poles.
What about $2 \Omega^2 a / g$? That would be $0.007$, i.e., 0.7%. Why would it be $2\Omega^2 a / g$?
Could it be that the effective gravity at the pole is not $g$, because the pole is closer to the center? In an ellipsoid, yes, but then $g$ wouldn't be the same. However, if the problem is purely spherical with constant $g$, then at pole $|g'|=g$, at equator $|g'| \approx g(1-\epsilon)$, so difference is $\epsilon$.
Unless they define $|g'|$ including a contribution that doubles it. Let's look at the components again.
Radial component of effective gravity: $g'_r = g - \Omega^2 a \cos^2\phi$ (inward magnitude). Tangential: $g'_\theta = \Omega^2 a \cos\phi\sin\phi$ (equatorward).
Magnitude squared: $g^2(1 - \epsilon\cos^2\phi)^2 + (g\epsilon\cos\phi\sin\phi)^2 = g^2(1 - 2\epsilon\cos^2\phi + \epsilon^2\cos^2\phi)$.
At pole: $g^2$.
At equator: $g^2(1 - 2\epsilon + \epsilon^2) = g^2(1-\epsilon)^2$.
So $g'_{eq} = g(1-\epsilon)$. The difference is exactly $\epsilon g$. Fractional difference is $\epsilon$.

So for 0.7%, we need $\epsilon \approx 0.007$. That means $\Omega^2 a / g \approx 0.007$.
With $g \approx 9.8$, $\Omega^2 a \approx 0.0686$. But $\Omega^2 a$ is only ~0.034. To get 0.0686, we'd need $\Omega$ to be larger by $\sqrt{2}$ (about 1.414), meaning day length of about 17 hours, which is wrong. Or radius $a$ to be double (12,742 km? No, that's diameter). Or $g$ to be half. None of these are Earth values.

Could the problem be not about the centrifugal term but about something else? No, it's standard.
Could it be that $|g'|$ at the equator is compared to $|g'|$ at a different latitude, not the poles? No.
Wait, maybe it asks to show that the magnitude is about 0.7% less at the equator than at the poles for a different planet? But it says "for the Earth".
Let me check if there is a misprint in the user prompt: "0 . 7 \%". Could be 0.5%? But I must solve the problem as stated. Or maybe they want the answer in percent (0.35) but the text says 0.7% because the student should realize that the difference in the magnitude of the effective gravity vector is different from the simple radial component difference? Let's compute $|g'|$ exactly and compare.

$|g'|_{pole} = g$.
$|g'|_{eq} = g - \Omega^2 a$.
Difference $= \Omega^2 a$.
Fraction $= \Omega^2 a / g$.

Wait, what if the problem uses $a = 6.371 \times 10^6$ m and $g = 9.81$, but $\Omega$ is taken as $2\pi / 86164$ (sidereal day). That gives $\Omega = 7.2921 \times 10^{-5}$.
$\Omega^2 = 5.3175 \times 10^{-9}$.
$\Omega^2 a = 3.387 \times 10^{-2}$.
$3.387 \times 10^{-2} / 9.81 = 3.452 \times 10^{-3}$. So 0.345%.

What if $\Omega = 2\pi / 86400$ (solar day)? $7.2722 \times 10^{-5}$.
$\Omega^2 a = 0.03369$. /9.81 = 0.003434 = 0.343%.

Neither gives 0.7%.

What if the problem uses $g = 9.8$, but $a = 6.4 \times 10^8$ cm? That's still 6400 km. Same.

Could the "0.7%" be from the fact that $g$ itself is smaller at the equator because Earth is an oblate spheroid? In many textbooks, after deriving the spherical Earth result (which is about 0.34%), they mention the actual difference is about 0.5% due to the equatorial bulge. But 0.7% is even larger.

Actually, measured difference: polar $g_{eff} = 9.832$, equatorial $g_{eff} = 9.780$. Difference = 0.052. Fraction = 0.052/9.832 = 0.00529 = 0.53%. So actual is ~0.5%.
If a textbook says 0.7%, maybe it's outdated or using different numbers. Or maybe it's not 0.7% but 0.07%? Let's check: 0.1° corresponds to about $\tan(0.1°) \approx 0.00175$ rad. The ratio of tangential to radial is $\Omega^2 a \cos\phi\sin\phi / g \approx 0.0034/2 = 0.0017$ at 45°. That matches 0.1° (since $\arctan(0.0017) \approx 0.1°$). The angle calculation gives ~0.1°, which is correct.
The fractional difference could be misremembered by the user as 0.7% when it's actually 0.3% or 0.5%. But I need to compute based on the physics.

But the user says: "Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles". The user might be quoting the problem exactly. If the problem text says 0.7%, but our computation yields 0.35%, what should I return? The graded answer is whatever solve() returns. The problem says "Show that... is about 0.7%". If I compute 0.35%, I'm not showing 0.7%.
However, maybe the quantity to return is not $\Omega^2 a/g$, but something else? Let's read again: "Evaluate the dimensionless parameter $\Omega^2 a/g$ for the Earth." Quantity 1: the value of $\Omega^2 a/g$.
"Show that ... magnitude $|g'|$ ... is about 0.7% less at equator than at poles" Quantity 2: percent difference = ?
Maybe the quantity asked is the percent difference, and the expected answer is around 0.35%, and the problem statement text "about 0.7%" is either from a different edition or a miscalculation. But the user didn't ask me to correct the problem; they asked me to compute the numerical answer(s).
What exactly are the quantities to return? The three distinct things asked are:
1. The dimensionless parameter $\Omega^2 a / g$.
2. The percentage reduction of $|g'|$ at equator relative to poles.
3. The maximum angle between $\mathbf{g}'$ and the radial direction.

The problem text says "Show that... is about 0.7% less". If I compute using standard values, I get ~0.35%. Should I return 0.35 or adjust constants to hit 0.7? The rules say: "Put every given value in as a function parameter with a default... The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number."
So the function will compute using the parameters. The parameters are physical constants of Earth. I should use standard values as defaults. The result will be whatever it is.

But would the grading expect 0.35 or 0.7? Since I don't know the grading system, I should probably compute the value correctly based on physics. The problem statement has an approximate claim; my code will compute the actual fractional difference based on the parameters. If the parameters produce 0.35%, then the function returns 0.35%. But the prompt says "Show that ... is about 0.7% less". If the computed value is 0.35%, it's not 0.7%. But the student might be expected to realize that the fractional difference is $2\Omega^2 a / g$? Let's see where 2 might come from.

If you approximate $g' \approx g - \Omega^2 a \cos^2\phi$, then at equator $g' \approx g - \Omega^2 a$, at pole $g' \approx g$.
Difference = $\Omega^2 a$. Fraction = $\Omega^2 a / g$.
If you approximate $g' \approx g - \Omega^2 a \cos^2\phi$ and consider the fractional difference as $(g_{pole} - g_{eq}) / g_{eq}$, then $(g - (g - \Omega^2 a))/(g - \Omega^2 a) = \Omega^2 a / (g - \Omega^2 a) \approx \Omega^2 a/g (1 + \Omega^2 a/g) \approx 0.00345$. Still not 0.007.

What if the tangential component contributes? The magnitude is $\sqrt{(g - \Omega^2 a\cos^2\phi)^2 + (\Omega^2 a \cos\phi\sin\phi)^2}$. At equator, this is $g - \Omega^2 a$. At pole, $g$. The tangential component only affects intermediate latitudes. It doesn't double the difference.

Maybe the problem uses a different formula: The effective gravity at latitude $\phi$ is $g' = g (1 - \frac{\Omega^2 a}{g} \cos^2\phi)$? Then at equator $g' = g(1-\epsilon)$, at pole $g' = g$. Difference fraction = $\epsilon$.
Still 0.35%.

What if the problem wants the difference between equator and poles to be expressed as $(g_{pole} - g_{eq}) / g_{eq}$ converted to percent? That's just slightly larger, not 2x.

Wait! Maybe the problem is not about the centrifugal acceleration magnitude $\Omega^2 a \cos\phi$? Let's derive again from scratch.
Effective gravity: $\mathbf{g}' = \mathbf{g} - \nabla \Phi_c$.
Centrifugal potential: $\Phi_c = -\frac{1}{2} \Omega^2 R^2 = -\frac{1}{2} \Omega^2 a^2 \cos^2\phi$.
Then $-\nabla \Phi_c$ in the radial direction (vertical) is... Actually, the gradient of $\Phi_c$ in spherical coordinates.
But the vector approach gave us the exact components. Let's double-check with potential.
$\Phi_c = -\frac{1}{2} \Omega^2 r^2 \cos^2\phi$ (since distance from axis is $r\cos\phi$).
In spherical coordinates $(r, \phi, \lambda)$? Actually latitude $\phi$, radial distance $r$.
Distance from axis: $r \cos\phi$.
$\Phi_c = -\frac{1}{2} \Omega^2 r^2 \cos^2\phi$.
Gradient in spherical coordinates (for a scalar depending on $r$ and $\phi$):
$\nabla \Phi = \frac{\partial \Phi}{\partial r} \hat{r} + \frac{1}{r} \frac{\partial \Phi}{\partial \phi} \hat{\phi}_{north}$.
Wait, standard spherical coordinates use colatitude $\theta$. The unit vector $\hat{\theta}$ points south (toward equator). Let's be careful.
If we use latitude $\phi$ (angle from equator), then the meridional unit vector $\hat{\phi}$ points north? Usually in meteorology, y points north. Let's say $\hat{\phi}$ points north.
Then $d\mathbf{s} = dr \hat{r} + r d\phi \hat{\phi}_{north}$? Actually, the arc length for a change in latitude $d\phi$ is $r d\phi$ if $\phi$ is angle from equator? No, the arc length from equator to latitude $\phi$ along a meridian is $r\phi$ only if $\phi$ is in radians measured from equator. Yes. So gradient meridional component is $(1/r) \partial/\partial \phi$.
$\partial \Phi_c / \partial r = -\Omega^2 r \cos^2\phi$.
$\partial \Phi_c / \partial \phi = -\frac{1}{2} \Omega^2 r^2 (2 \cos\phi)(-\sin\phi) = \Omega^2 r^2 \cos\phi \sin\phi$.
So $\nabla \Phi_c = -\Omega^2 r \cos^2\phi \hat{r} + \Omega^2 r \cos\phi \sin\phi \hat{\phi}_{north}$.
Centrifugal acceleration is $-\nabla \Phi_c = \Omega^2 r \cos^2\phi \hat{r} - \Omega^2 r \cos\phi\sin\phi \hat{\phi}_{north}$.
If $\hat{\phi}_{north}$ points north, then $-\hat{\phi}_{north}$ points south/equatorward.
So radial component (outward): $\Omega^2 r \cos^2\phi$.
Meridional component (southward): $\Omega^2 r \cos\phi\sin\phi$.
This matches our earlier derivation (tangential component toward equator is positive).
So $\mathbf{g}' = -g\hat{r} + \Omega^2 a \cos^2\phi \hat{r} + \Omega^2 a \cos\phi\sin\phi (-\hat{\phi}_{north})$? Wait.
True gravity is inward: $-g\hat{r}$.
Centrifugal is outward radially: $+\Omega^2 a \cos^2\phi \hat{r}$.
Centrifugal equatorward component: $-\Omega^2 a \cos\phi\sin\phi \hat{\phi}_{north}$ (since the gradient gave $+\Omega^2 r \cos\phi\sin\phi$ in northward direction, so minus that is southward).
Thus the components are:
Radial (positive outward): $-g + \Omega^2 a \cos^2\phi$.
Southward (positive south): $\Omega^2 a \cos\phi\sin\phi$.
So the inward magnitude of radial component is $g - \Omega^2 a \cos^2\phi$.
The southward magnitude is $\Omega^2 a \cos\phi\sin\phi$.
So magnitude of $\mathbf{g}'$ is $\sqrt{(g - \Omega^2 a\cos^2\phi)^2 + (\Omega^2 a \cos\phi\sin\phi)^2}$.
At equator: $\phi=0$, $|g'| = g - \Omega^2 a$.
At pole: $\phi=\pi/2$, $|g'| = g$.
Difference fraction = $\Omega^2 a / g$.

So it's definitely 0.35%. Why would any textbook say 0.7%?
Perhaps the problem is using $g = 9.81$ but $\Omega$ is not Earth's rotation rate? No.
Maybe the problem asks to show that the effective gravity is less than gravity at the equator by about $0.3\%$ and the user mistyped $0.7\%$? Or maybe the textbook used a different formula where the effective gravity is compared to some average? Or maybe the problem considers $g$ to be the gravitational acceleration at the equator due to mass, and at pole it's larger because Earth is flattened? But then the parameter is $\Omega^2 a / g$ which is evaluated for Earth.

Let me check if there is a known problem from "Introduction to Geophysical Fluid Dynamics" by Cushman-Roisin & Beckers, or "Atmospheric and Oceanic Fluid Dynamics" by Vallis.
Actually, in Vallis, Chapter 2, there's a problem: "Show that the centrifugal force leads to a reduction in effective gravity of about 0.3% at the equator compared with the poles, and that the effective gravity is not exactly directed toward the center of the Earth, but is deflected by about 0.1°." That sounds exactly like what we have, but the numbers are 0.3% and 0.1°.
The user wrote 0.7%. Could be a typo in the user's prompt. If the actual expected answer is ~0.3% (or 0.35%), and the angle is ~0.1°, then my function returning 0.35% would be correct. But the user explicitly said 0.7%. However, they also said "The graded answer is whatever solve() returns, so let the function do the arithmetic." This suggests the grading system will compute the function with default parameters and check the output. I need to match what the physics says with standard Earth parameters.
If the textbook intended 0.7%, perhaps they define the percentage as $200 \times \Omega^2 a / g$? Why 2? Because the oblateness correction is also about 0.35%, and together they make 0.7%? But the problem specifically says "Evaluate the dimensionless parameter $\Omega^2 a / g$. Show that...". The first quantity is $\Omega^2 a / g$. The second quantity is likely the percent difference. If the difference were $2 \times \Omega^2 a / g$, then showing it's 0.7% would follow from $\Omega^2 a / g \approx 0.35\%$.
Maybe the problem is from a source that says: effective gravity is $g' = g(1 - \epsilon)$ at equator and $g' = g(1 + \epsilon)$ at poles? No, that makes no sense.

Wait, I recall some textbooks define $g$ as the gravitational acceleration at the equator, and at poles it's $g_{true} = GM/a_p^2$ which is larger due to smaller radius. But the problem doesn't mention different radii.

Let's consider the possibility that the user made a typo and it's actually 0.3%. The function should compute the correct physical value. If the default parameters are Earth's radius, rotation rate, and $g=9.81$ m/s², the answer for quantity 2 (fractional difference) will be $\Omega^2 a / g \approx 0.00345$, which as a percentage is $0.345\%$. So if the unit is "percent", the value is 0.345. If the unit is dimensionless fraction, it's 0.00345. The problem says "0.7% less", so likely the answer is expected in percent. I'd return the value in percent, e.g. 0.345... . If the grader expects 0.7, there might be an issue. But the prompt says "Show that... is about 0.7% less". If I compute 0.35%, I am not matching. However, the problem might use slightly different values: e.g., $a = 6.371\times10^6$ m, $g=9.8$ m/s², and $\Omega = 7.292\times10^{-5}$ s⁻¹. That gives 0.345%. Still not 0.7.

What if $g$ is taken as $9.8/2$? No.
What if the problem is from a textbook that uses cgs units? $a = 6.37\times10^8$ cm, $g = 980$ cm/s², $\Omega = 7.29\times10^{-5}$ s⁻¹. Then $\Omega^2 a = 3.38$ cm/s². $\Omega^2 a / g = 3.38/980 = 0.00345$. Same.

Could it be that the textbook answer is $0.7\%$ because they compare the *vector* magnitudes using the exact formula but at some other latitude? No.

Let me think about the angle. The angle $\alpha$ between $\mathbf{g}'$ and the inward radial vector.
The inward radial vector is $-\hat{r}$.
$\mathbf{g}'$ has components: radial inward $g_{in} = g - \Omega^2 a \cos^2\phi$, equatorward $g_{eq} = \Omega^2 a \cos\phi\sin\phi$.
The angle between $\mathbf{g}'$ and the inward radial is given by $\tan \alpha = \frac{g_{eq}}{g_{in}} = \frac{\Omega^2 a \cos\phi\sin\phi}{g - \Omega^2 a \cos^2\phi}$.
Maximum $\alpha$ occurs at some latitude. Let's find it.
Let $\epsilon = \Omega^2 a / g$.
$\tan \alpha = \frac{\epsilon \cos\phi\sin\phi}{1 - \epsilon \cos^2\phi} = \frac{(\epsilon/2)\sin(2\phi)}{1 - \epsilon \cos^2\phi}$.
Since $\epsilon \ll 1$, the denominator is approximately 1. So $\tan \alpha \approx (\epsilon/2) \sin(2\phi)$. The maximum occurs near $\phi = 45°$, giving $\tan \alpha_{max} \approx \epsilon/2$.
With $\epsilon = 0.00345$, $\epsilon/2 = 0.001725$. $\alpha_{max} \approx \arctan(0.001725) \approx 0.0988° \approx 0.1°$. This is correct.
Actually, let's find the exact maximum. $f(\phi) = \frac{\epsilon \cos\phi\sin\phi}{1 - \epsilon \cos^2\phi}$.
Derivative w.r.t $\phi$: Let $s=\sin\phi, c=\cos\phi$.
$f = \frac{\epsilon c s}{1 - \epsilon c^2}$.
$f' \propto \epsilon(c^2 - s^2)(1-\epsilon c^2) - \epsilon c s (2\epsilon c s) = 0$?
$(c^2-s^2)(1-\epsilon c^2) - 2\epsilon c^2 s^2 = 0$.
Let $u = \cos(2\phi) = c^2 - s^2$. And $c^2 s^2 = (1/4)\sin^2(2\phi) = (1-u^2)/4$? Actually, $c^2 = (1+u)/2, s^2=(1-u)/2, c^2 s^2 = (1-u^2)/4$.
$(u)(1 - \epsilon (1+u)/2) - 2\epsilon (1-u^2)/4 = 0$.
$u - (\epsilon u (1+u))/2 - (\epsilon (1-u^2))/2 = 0$.
$u - \frac{\epsilon}{2} (u + u^2 + 1 - u^2) = 0$.
$u - \frac{\epsilon}{2} (u + 1) = 0$.
$u (1 - \epsilon/2) = \epsilon/2$.
$u = \frac{\epsilon/2}{1 - \epsilon/2} \approx \epsilon/2$.
So $2\phi \approx \pi/2 - \epsilon/2$? Wait, $u = \cos(2\phi)$. At maximum, $u$ is small positive, so $2\phi \approx \pi/2$, i.e., $\phi \approx 45°$.
Then $\tan\alpha_{max} \approx \frac{\epsilon c s}{1 - \epsilon c^2}$ evaluated at $c^2 \approx s^2 \approx 1/2$ plus small correction.
At $c^2 = s^2 = 1/2$: $f = \frac{\epsilon/2}{1 - \epsilon/2} \approx \epsilon/2 (1 + \epsilon/2) \approx \epsilon/2$.
So $\alpha_{max} \approx \arctan(\epsilon/2) \approx \epsilon/2$ rad.
$\epsilon/2$ rad = $0.00345/2 \times (180/\pi)$ degrees = $0.001725 \times 57.2958 = 0.0988° \approx 0.1°$.
The exact value is slightly different but very close.

So the angle part is definitely 0.1°. The dimensionless parameter is ~0.00345 (dimensionless). The percent difference is ~0.345%. But the text says 0.7%.
Unless the second quantity is the *total* fractional difference including the oblateness effect, which is about $2\epsilon \approx 0.7\%$? Let's see: some textbooks approximate the oblateness correction as also being of order $\epsilon = \Omega^2 a/g$. The parameter $\epsilon$ is the ratio of centrifugal to gravitational. It appears in the study of the figure of the Earth. The Earth's ellipticity (flattening) $f = (a-c)/a \approx \epsilon/2 \approx 1/298 \approx 0.00335$. Wait, flattening is about 0.00335. The correction to gravity from the ellipsoidal shape (the "Clairaut's theorem") gives a term of order $f$, and the total variation of effective gravity with latitude includes a term $2f - \epsilon$ (or similar). Actually, the standard gravity formula has $\beta = 2\Omega^2 a/g + ...$.
The gravity variation due to shape alone (mass distribution in ellipsoid) at the surface is approximately $2f \times g$ from pole to equator? Let's recall Clairaut's theorem: $g_{eq} = g_{pole}(1 - \frac{5}{2}m + ...)$? The parameter $m = \Omega^2 a / g_{eq}$.
Actually, the standard formula is $g = g_{eq}(1 + \beta \sin^2\phi - ...)$ with $\beta \approx 0.0053$.
The centrifugal part contributes $\epsilon \approx 0.0034$. The shape part contributes roughly $2f \approx 0.0067$? No, flattening $f \approx 0.00335$. The shape contributes a reduction at equator of about $f$? Let's check: gravitational acceleration on an oblate spheroid: at pole $GM/c^2$, at equator $GM/a^2$. Since $a > c$, $GM/a^2 < GM/c^2$. Fractional difference $\approx 2f = 0.0067 = 0.67\%$. Wait! That's about 0.7%!
If you consider only the shape (ignoring rotation), the gravitational acceleration is about 0.67% less at the equator than at the poles because $a$ is larger by $f \approx 1/298$, so $1/r^2$ differs by about $2f \approx 0.0067 \approx 0.7\%$.
But the problem says "Show that, at the Earth's surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less...".
However, the first part says "Evaluate the dimensionless parameter $\Omega^2 a/g$". The second part says "Show that ... effective gravity is about 0.7% less...". If the problem is purely about effective gravity on a sphere, the answer is 0.35%. But many textbooks (like Holton) combine both effects? Let's think.

In Holton's "Introduction to Dynamic Meteorology", there is a problem in Chapter 1 that is exactly this. Let me recall. Holton uses $a = 6.37\times10^6$ m, $\Omega = 7.292\times10^{-5}$ s⁻¹, $g=9.81$ m/s².
Holton's problem 1.1? I recall him asking: "The Earth is an oblate spheroid...". Actually, I think the problem in Holton is about the gravity difference being about 0.5%. Wait.

Let me search my memory of Wallace & Hobbs. In the "Physical Constants" section, they have $a=6371$ km. In the problem, they might ask to evaluate $\Omega^2 a / g$ and then show the 0.5% difference. The 0.7% might be from the fact that they use $g=9.8$ and $a=6.4\times10^6$, but also maybe they approximate the magnitude difference as $2 \Omega^2 a / g$? Let's see if there's any physical reason for that.

Consider the apparent weight of an object. At the equator, $g' = g - \Omega^2 a$. At the pole, $g' = g$. The difference is $\Omega^2 a$. That's 0.034 m/s². Relative to $g=9.8$, that's 0.35%.
If the problem says 0.7%, maybe they are comparing the *centrifugal acceleration* to effective gravity? No, "effective gravity is about 0.7% less".

Wait! Could the problem be asking to show that the *geopotential* or *apparent* gravity is 0.7% less because they define the fractional difference as $(\Delta g) / g'$ or something? No.
Alternatively, some textbooks might define the difference as $2\Omega^2 a/g$ because they consider both the meridional variation of $g$ due to the $r^{-2}$ dependence as one moves to a larger radius? But on a sphere, $g$ is constant.

Let me check if the problem might be from "An Introduction to Dynamic Meteorology" by Holton and Hakim, 5th edition.
Problem 1.3? I don't have the exact text.
Wait, I found a reference online in my memory: "Wallace and Hobbs, Problem 1.2: Evaluate the dimensionless parameter $\Omega^2 a / g$ ... Show that ... about 0.5% less ... about 0.1°." I'm fairly sure I've seen 0.5% and 0.1°.
Another reference: In "Atmospheric and Oceanic Fluid Dynamics" by Geoffrey K. Vallis, Problem 2.2: "Show that the centrifugal force leads to a reduction in effective gravity of about 0.3% at the equator compared with the poles, and that the effective gravity is not exactly directed toward the center of the Earth, but is deflected by about 0.1°."

So the actual answer for the reduction is somewhere around 0.3% to 0.5%, not 0.7%. The user wrote "0.7%". Since the explicit instruction is to compute from the parameters, and the parameters are Earth's physical constants, the code will output the physically correct number. The grader will presumably check the computation. Even if the problem text says 0.7%, the function's job is to compute the answer from the parameters. The problem says "Show that... is about 0.7% less". The solver should compute the exact value and return it. If the exact value is 0.34%, then returning 0.34% is correct. However, there might be a slight ambiguity: what exactly is quantity 2?

Possibility 1: Quantity 2 is the dimensionless parameter itself. But quantity 1 is already that.
Possibility 2: Quantity 2 is the percent difference: $\frac{|g'|_{pole} - |g'|_{eq}}{|g'|_{pole}} \times 100$. This is $\approx 0.345\%$.
Possibility 3: Quantity 2 is the fractional difference as a fraction (not percent): $\approx 0.00345$.
Possibility 4: Quantity 2 is $2 \times \frac{\Omega^2 a}{g}$? No physical basis.
Possibility 5: The problem actually has three parts, and the user expects three answers:
1. $\Omega^2 a / g$.
2. The fractional (or percent) difference in $|g'|$ between equator and poles.
3. The maximum angle in degrees.

Given the prompt: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles, and the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth is about $0.1°$."

The three statements are:
- Evaluate X.
- Show Y.
- Show Z.

The user wants me to return a dict keyed "1", "2", "3".
So:
"1": value of $\Omega^2 a / g$, unit: "dimensionless" (or empty string? The rules say unit string. For dimensionless, maybe unit "1" or "dimensionless").
"2": the percent (or fractional) difference. The text says "0.7% less". If I return percent, unit is "percent". Value is ~0.345. But if the grader expects ~0.7 because of the problem text, I might be wrong. Or maybe the grader expects the exact computed percent, which is ~0.35. Let's think about which is more robust.
If I return the fraction (not percent), then value is ~0.00345. The text says "0.7% less". A student might return 0.00345 with unit "percent"? No. If I return 0.345 with unit "percent", that literally means 0.345 percent. If the grader is checking for 0.35, great. If the grader is checking for 0.7, then maybe I should compute something else.

Wait, I need to consider if the problem is perhaps working in a context where $g$ is not the same at the pole and equator, but the
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    omega=7.2921e-5,   # Earth's angular velocity (rad s^-1)
    a=6.371e6,         # Earth's mean radius (m)
    g=9.81,            # Mean gravitational acceleration (m s^-2)
):
    """
    1. Dimensionless parameter Omega^2 a / g
    2. Percent reduction of |g'| at equator relative to poles
    3. Maximum angle (degrees) between g' and the inward radial direction
    """
    # Quantity 1
    dimless = omega**2 * a / g

    # Quantity 2: |g'| is g at poles, and (g - Omega^2 a) at equator
    g_pole = g
    g_eq = g - omega**2 * a
    percent_less = (g_pole - g_eq) / g_pole * 100.0

    # Quantity 3: angle alpha where tan(alpha) = tangential / radial_inward
    # tan(alpha) = (epsilon * cos(phi) * sin(phi)) / (1 - epsilon * cos^2(phi))
    # Maximum occurs where cos(2*phi) = (epsilon/2) / (1 - epsilon/2)
    epsilon = dimless
    cos_2phi = (epsilon / 2.0) / (1.0 - epsilon / 2.0)
    # Clamp for numerical safety
    if cos_2phi > 1.0:
        cos_2phi = 1.0
    elif cos_2phi < -1.0:
        cos_2phi = -1.0
    phi = math.acos(cos_2phi) / 2.0
    c = math.cos(phi)
    s = math.sin(phi)
    tan_alpha = (epsilon * c * s) / (1.0 - epsilon * c * c)
    max_angle = math.degrees(math.atan(tan_alpha))

    return {
        "1": {"value": dimless, "unit": "dimensionless"},
        "2": {"value": percent_less, "unit": "percent"},
        "3": {"value": max_angle, "unit": "degrees"},
    }
```
~~~~

#### `kimi-k2.6-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/kimi-k2.6-reasoning.run2.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034532809882161053` | ✓ |
| `2` | `0.7` | `0.689166583467599` | ✓ |
| `3` | `0.1` | `0.0991002248576466` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

RESPONSE (verbatim, untruncated):

~~~~
We need to parse the problem. The user wants a Python `solve()` function that computes numerical answers for an atmospheric science problem. The problem: Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth is about $0.1^\circ$.

So the graded answer likely expects specific quantities: maybe three numbers: (1) the dimensionless parameter $\Omega^2 a / g$, (2) the fractional difference in $|g'|$ between equator and poles (i.e., $(|g'|_{pole} - |g'|_{equator}) / |g'|_{pole}$ or similar, expressed as a percent? The problem says "about 0.7% less". So they likely want the percentage difference or the fractional difference? The phrasing: "Show that ... the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles". That suggests the answer is something like 0.7 percent, i.e., 0.007 as a fraction, or 0.7 as a percentage. But the unit field might be "percent" or "dimensionless". Need to decide.

Also the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth is about $0.1^\circ$. So the third answer is an angle in degrees, presumably around 0.1 degrees.

We need to return a dict with entries "1", "2", "3". Each maps to {"value": <number>, "unit": "<unit>"}. Exactly three entries.

We need to put every given value in as a function parameter with a default. So parameters like Omega (Earth's angular velocity), a (Earth's radius), g (gravitational acceleration), maybe others.

We need to compute each answer from parameters.

Let's derive formulas.

Effective gravity $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$.

At the Earth's surface, $\mathbf{g}$ points toward the center (radially inward). The centrifugal acceleration is $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = -\Omega^2 \mathbf{r}_\perp$, where $\mathbf{r}_\perp$ is the component perpendicular to rotation axis. At latitude $\phi$, the distance from the rotation axis is $a \cos\phi$. The centrifugal acceleration magnitude is $\Omega^2 a \cos\phi$, directed outward perpendicular to the axis (i.e., away from the axis). It has components radially outward (from Earth's center) and northward (i.e., tangent to the surface). The radial component is $\Omega^2 a \cos^2\phi$ outward. The tangential (northward) component is $\Omega^2 a \cos\phi \sin\phi$ directed toward the equator? Let's be careful.

Take spherical coordinates: latitude $\phi$, radius $a$. The position vector is $\mathbf{r} = a \hat{r}$. The rotation vector is $\mathbf{\Omega} = \Omega \hat{k}$, where $\hat{k}$ is Earth's rotation axis direction (north pole). In spherical coordinates, $\hat{k} = \sin\phi \hat{r} + \cos\phi \hat{\theta}$? Wait, standard spherical coordinates: colatitude $\theta = 90^\circ - \phi$, with $\hat{r}$ radial outward, $\hat{\theta}$ southward? Let's define more simply: At latitude $\phi$, the unit vector perpendicular to the rotation axis in the meridional plane points outward from the axis and horizontally toward the equator? Let's use vector components in a meridional plane.

Consider a cross-section through the Earth's rotation axis and a point at latitude $\phi$. The rotation axis is vertical in this plane. The radial direction from Earth's center makes angle $\phi$ with the equatorial plane? Actually latitude $\phi$ is angle from equator. The radius vector $\mathbf{r}$ makes angle $90^\circ - \phi$ with the rotation axis (colatitude). The component of $\mathbf{r}$ perpendicular to the axis is $a \cos\phi$. The centrifugal acceleration vector is directed outward from the axis, in the plane containing the point and the axis, perpendicular to the axis. Its magnitude is $\Omega^2 (a \cos\phi)$. In the meridional plane, we can decompose this vector into radial and tangential (south-north) components.

Let's set up coordinates: Let the rotation axis be the $z$-axis. Then a point on Earth's surface at latitude $\phi$ has coordinates $(x,0,z)$ with $x = a \cos\phi$, $z = a \sin\phi$. The rotation vector is $\mathbf{\Omega} = \Omega \hat{z}$. The position vector is $\mathbf{r} = a (\cos\phi \hat{x} + \sin\phi \hat{z})$. The centrifugal acceleration is $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = -\Omega^2 \mathbf{r}_\perp$. Actually, $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \mathbf{\Omega}(\mathbf{\Omega}\cdot\mathbf{r}) - \Omega^2 \mathbf{r}$. Since $\mathbf{\Omega}\cdot\mathbf{r} = \Omega a \sin\phi$, we have:

$\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \Omega^2 a \sin\phi \hat{z} - \Omega^2 a (\cos\phi \hat{x} + \sin\phi \hat{z}) = -\Omega^2 a \cos\phi \hat{x}$.

So the centrifugal acceleration is purely in the $-\hat{x}$ direction? Wait, $-\Omega^2 a \cos\phi \hat{x}$. But $\hat{x}$ points away from the axis in the equatorial plane. At the point $(x,z)$, $\hat{x}$ is horizontal and points away from the axis. Let's express in terms of local unit vectors: radial outward $\hat{r} = \cos\phi \hat{x} + \sin\phi \hat{z}$, and the northward tangent vector $\hat{n} = -\sin\phi \hat{x} + \cos\phi \hat{z}$ (pointing northward, i.e., increasing $\phi$). Note: $\hat{n}$ points from equator toward north pole? Let's check: At $\phi=0$ (equator), $\hat{r} = \hat{x}$, $\hat{n} = -\hat{0}*? Wait, at equator, $\phi=0$, $\hat{r}=\hat{x}$, $\hat{n}=-\sin(0)\hat{x}+\cos(0)\hat{z} = \hat{z}$. That's northward (upward along axis), which is correct. At $\phi=90^\circ$ (north pole), $\hat{r}=\hat{z}$, $\hat{n}=-\hat{x}$, which points southward? Hmm, at north pole, "northward" is undefined, but the tangent plane is horizontal. Actually, the unit vector tangent to the surface in the direction of increasing latitude (northward) at a general point is $\hat{\phi} = -\sin\phi \hat{x} + \cos\phi \hat{z}$? Wait, in standard spherical coordinates, the unit vector in the direction of increasing polar angle (colatitude) points southward. But we want increasing latitude $\phi$ (northward), which corresponds to decreasing colatitude. So the northward unit vector is opposite the colatitude unit vector: $\hat{\phi}_{north} = -\sin\phi \hat{x} + \cos\phi \hat{z}$? Let's check: At equator $\phi=0$, $\hat{\phi}_{north} = \hat{z}$ (north). At $\phi=90^\circ$ (north pole), $\hat{\phi}_{north} = -\hat{x}$, which is southward? Actually at the north pole, any horizontal direction is southward, so that's fine. At $\phi=-90^\circ$ (south pole), $\hat{\phi}_{north} = \hat{x}$ (northward). So yes, $\hat{n} = -\sin\phi \hat{x} + \cos\phi \hat{z}$ points northward.

Now the centrifugal acceleration vector is $\mathbf{a}_c = -\Omega^2 a \cos\phi \hat{x}$. Let's write in terms of $\hat{r}$ and $\hat{n}$.

We have $\hat{x} = \cos\phi \hat{r} - \sin\phi \hat{n}$? Let's solve:

$\hat{r} = \cos\phi \hat{x} + \sin\phi \hat{z}$.

$\hat{n} = -\sin\phi \hat{x} + \cos\phi \hat{z}$.

We can invert: Multiply first by $\cos\phi$, second by $-\sin\phi$:

$\cos\phi \hat{r} = \cos^2\phi \hat{x} + \sin\phi\cos\phi \hat{z}$.

$-\sin\phi \hat{n} = \sin^2\phi \hat{x} - \sin\phi\cos\phi \hat{z}$.

Add: $\cos\phi \hat{r} - \sin\phi \hat{n} = (\cos^2\phi + \sin^2\phi)\hat{x} = \hat{x}$.

So $\hat{x} = \cos\phi \hat{r} - \sin\phi \hat{n}$.

Thus $\mathbf{a}_c = -\Omega^2 a \cos\phi (\cos\phi \hat{r} - \sin\phi \hat{n}) = -\Omega^2 a \cos^2\phi \hat{r} + \Omega^2 a \cos\phi \sin\phi \hat{n}$.

So the centrifugal acceleration has a radially outward component (since $-\hat{r}$ is inward? Wait, $\hat{r}$ is radial outward. The term is $-\Omega^2 a \cos^2\phi \hat{r}$, so it's radially inward? That doesn't seem right: centrifugal acceleration is outward from the rotation axis, which has a component radially outward from Earth's center (except at poles). Let's check signs.

At equator $\phi=0$, $\mathbf{a}_c = -\Omega^2 a \hat{r}$. That points radially inward? That is wrong. Let's recompute.

$\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \mathbf{\Omega}(\mathbf{\Omega}\cdot\mathbf{r}) - \Omega^2 \mathbf{r}$.

At equator, $\mathbf{r} = a \hat{x}$, $\mathbf{\Omega} = \Omega \hat{z}$. $\mathbf{\Omega}\cdot\mathbf{r}=0$. So $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = -\Omega^2 a \hat{x}$. $\hat{x}$ at equator is radially outward. So $-\Omega^2 a \hat{x}$ is radially inward? Wait, at equator, the outward radial direction is $\hat{x}$. So $-\Omega^2 a \hat{x}$ is inward. But centrifugal acceleration at equator is outward (away from axis). The axis is perpendicular to $\hat{x}$. At equator, the axis direction is $\hat{z}$, which is tangent to the surface (northward). The point is $(a,0,0)$. The axis passes through the origin $(0,0,z)$. The centrifugal acceleration should point away from the axis, which is in the $+\hat{x}$ direction. Let's compute carefully.

Standard vector triple product identity: $\mathbf{A} \times (\mathbf{B} \times \mathbf{C}) = \mathbf{B}(\mathbf{A}\cdot\mathbf{C}) - \mathbf{C}(\mathbf{A}\cdot\mathbf{B})$.

So $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \mathbf{\Omega}(\mathbf{\Omega}\cdot\mathbf{r}) - \mathbf{r}(\mathbf{\Omega}\cdot\mathbf{\Omega})$.

Wait, identity: $\mathbf{A} \times (\mathbf{B} \times \mathbf{C}) = \mathbf{B}(\mathbf{A}\cdot\mathbf{C}) - \mathbf{C}(\mathbf{A}\cdot\mathbf{B})$.

Set $\mathbf{A} = \mathbf{\Omega}$, $\mathbf{B} = \mathbf{\Omega}$, $\mathbf{C} = \mathbf{r}$.

Then $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \mathbf{\Omega}(\mathbf{\Omega}\cdot\mathbf{r}) - \mathbf{r}(\mathbf{\Omega}\cdot\mathbf{\Omega})$.

Yes, that's what I had: $\Omega^2 a \sin\phi \hat{z} - \Omega^2 a (\cos\phi \hat{x} + \sin\phi \hat{z}) = -\Omega^2 a \cos\phi \hat{x}$.

But at equator, $\phi=0$, this gives $-\Omega^2 a \hat{x}$. That seems inward. Did I get the coordinate wrong? Let's think: The point is at $(a,0,0)$. The axis is the $z$-axis. The vector from the axis to the point is $a \hat{x}$. Centrifugal acceleration points away from the axis, which is in the $+\hat{x}$ direction. So there is a sign error in the vector triple product? Let's re-derive.

Centrifugal acceleration is $-\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$? Wait! In a rotating frame, the fictitious centrifugal acceleration is $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$? Or is it $-\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$? Let's recall.

In a rotating frame with angular velocity $\mathbf{\Omega}$, the equation of motion includes Coriolis $-2\mathbf{\Omega}\times\mathbf{v}_r$ and centrifugal $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. Wait, the centrifugal force in the rotating frame is $-m\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. Let's check.

In inertial frame, acceleration is $\mathbf{a}_i$. In rotating frame, $\mathbf{a}_i = \mathbf{a}_r + 2\mathbf{\Omega}\times\mathbf{v}_r + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) + \dot{\mathbf{\Omega}}\times\mathbf{r}$.

The fictitious forces in rotating frame are $-2m\mathbf{\Omega}\times\mathbf{v}_r$ (Coriolis) and $-m\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ (centrifugal). Wait, moving terms: $m\mathbf{a}_r = m\mathbf{a}_i - 2m\mathbf{\Omega}\times\mathbf{v}_r - m\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) - m\dot{\mathbf{\Omega}}\times\mathbf{r}$.

So the centrifugal acceleration in the rotating frame is $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$.

But many textbooks define the effective gravity as $\mathbf{g}' = \mathbf{g} - \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ or $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$? Let's check standard effective gravity.

Effective gravity is the vector sum of true gravitational acceleration (toward center) and centrifugal acceleration (away from axis). True gravity $\mathbf{g}$ points toward center: $\mathbf{g} = -g \hat{r}$ (inward). Centrifugal acceleration points away from axis. In rotating frame, the equilibrium condition gives effective gravity $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$? Or minus?

Let's check a standard reference: "Effective gravity" $g^*$ = gravity + centrifugal acceleration. The centrifugal acceleration is $\Omega^2 R \cos\phi$ directed outward from the axis. Its radial component is $\Omega^2 R \cos^2\phi$ outward. So effective gravity magnitude is reduced at equator: $g_{eq} = g - \Omega^2 R$? Actually standard formula: $g_{eff} = g - \Omega^2 R \cos^2\phi$? Wait, the radial component of centrifugal acceleration is outward, so it opposes gravity (inward). So $g_{eff}$ magnitude is $g - \Omega^2 a \cos^2\phi$ (approximately, ignoring tangential component). At equator, $g_{eff} = g - \Omega^2 a$. At poles, $g_{eff} = g$.

Now, what is the vector expression? True gravitational acceleration is $\mathbf{g} = -g \hat{r}$ (pointing inward). The centrifugal acceleration vector is $\mathbf{a}_c = \Omega^2 a \cos\phi \, \hat{\rho}$, where $\hat{\rho}$ is the unit vector directed away from the axis in the equatorial plane. In our coordinate system, at the point $(a\cos\phi, 0, a\sin\phi)$, the direction away from the axis is $+\hat{x}$. So $\mathbf{a}_c = \Omega^2 a \cos\phi \, \hat{x}$.

But we got $-\Omega^2 a \cos\phi \hat{x}$ from $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. So the centrifugal acceleration is $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. Let's verify:

$-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = -(-\Omega^2 a \cos\phi \hat{x}) = +\Omega^2 a \cos\phi \hat{x}$. Yes! So the centrifugal acceleration is $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$.

But wait, earlier we derived $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = -\Omega^2 a \cos\phi \hat{x}$. So the centrifugal acceleration vector is indeed $- \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = \Omega^2 a \cos\phi \hat{x}$. Then the effective gravity vector is $\mathbf{g}' = \mathbf{g} + \mathbf{a}_c = -g\hat{r} + \Omega^2 a \cos\phi \hat{x}$.

Wait, but many textbooks define effective gravity as $\mathbf{g}' = \mathbf{g} - \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. Since $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ pointed inward (at equator), minus that gives outward. So that matches.

Alternatively, some define $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ if they define $\mathbf{g}$ as the acceleration due to gravity (inward) and the term $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ is already outward? Let's check sign conventions.

Let's recompute $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ directly with cross products to be sure.

$\mathbf{\Omega} = \Omega \hat{z}$.

$\mathbf{r} = a\cos\phi \hat{x} + a\sin\phi \hat{z}$.

First cross product: $\mathbf{\Omega}\times\mathbf{r} = \Omega \hat{z} \times (a\cos\phi \hat{x} + a\sin\phi \hat{z}) = \Omega a\cos\phi (\hat{z}\times\hat{x}) + 0 = \Omega a\cos\phi \hat{y}$.

Second cross product: $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = \Omega \hat{z} \times (\Omega a\cos\phi \hat{y}) = \Omega^2 a\cos\phi (\hat{z}\times\hat{y}) = \Omega^2 a\cos\phi (-\hat{x}) = -\Omega^2 a\cos\phi \hat{x}$.

So indeed $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = -\Omega^2 a\cos\phi \hat{x}$ (inward at equator). But the outward centrifugal acceleration is $+\Omega^2 a\cos\phi \hat{x}$. So effective gravity is $\mathbf{g}' = \mathbf{g} - \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ if one uses the standard rotating frame formula. However, the problem statement mentions "effective gravity" $\mathbf{g}'$. Let's see what they intend.

The problem says: "Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

Typically, in atmospheric science textbooks (e.g., Holton, Wallace & Hobbs), effective gravity is defined as the vector sum of true gravitational acceleration and the centrifugal acceleration. True gravity points toward Earth's center. Centrifugal acceleration points away from Earth's rotation axis. So $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$? Wait, if $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$ is inward, then adding it would subtract from gravity. But physically, at equator, centrifugal acceleration is outward, so it subtracts from gravity. So we need the outward vector. The outward vector is $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$. But maybe they define $\mathbf{\Omega}$ differently? Or maybe they use the identity $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = -\Omega^2 \mathbf{\rho}$ where $\mathbf{\rho}$ is the vector perpendicular to axis from axis to point? Wait, $\mathbf{\rho} = a\cos\phi \hat{x}$, which is the vector from axis to point. Then $-\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r}) = \Omega^2 \mathbf{\rho}$. So many textbooks write $\mathbf{g}' = \mathbf{g} - \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$, which equals $\mathbf{g} + \Omega^2 \mathbf{\rho}$.

But the problem statement uses $\mathbf{g}'$ and asks about angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth. True gravity points toward centre. Centrifugal acceleration has a tangential component that tilts $\mathbf{g}'$ away from the radial direction toward the equator. At latitude $\phi$, the tangential component is $\Omega^2 a \cos\phi \sin\phi$ directed toward the equator (i.e., southward in the northern hemisphere). Wait, let's check: The centrifugal acceleration is $\Omega^2 a \cos\phi \hat{x}$. In the local basis, $\hat{x} = \cos\phi \hat{r} - \sin\phi \hat{n}$ (with $\hat{n}$ northward). So $\mathbf{a}_c = \Omega^2 a \cos\phi (\cos\phi \hat{r} - \sin\phi \hat{n}) = \Omega^2 a \cos^2\phi \hat{r} - \Omega^2 a \cos\phi \sin\phi \hat{n}$.

Wait, earlier I had $-\Omega^2 a \cos\phi \hat{x}$ for $\mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$, but now we are using the outward centrifugal acceleration $\mathbf{a}_c = \Omega^2 a \cos\phi \hat{x}$. Let's derive with the outward centrifugal acceleration.

Outward centrifugal acceleration: $\mathbf{a}_c = \Omega^2 a \cos\phi \hat{x}$.

Express in local basis: $\hat{x} = \cos\phi \hat{r} - \sin\phi \hat{n}$.

Thus $\mathbf{a}_c = \Omega^2 a \cos\phi (\cos\phi \hat{r} - \sin\phi \hat{n}) = \Omega^2 a \cos^2\phi \hat{r} - \Omega^2 a \cos\phi \sin\phi \hat{n}$.

So radial component is $\Omega^2 a \cos^2\phi$ outward (i.e., positive $\hat{r}$). Tangential component is $-\Omega^2 a \cos\phi \sin\phi \hat{n}$, which is southward (since $\hat{n}$ is northward). That makes sense: centrifugal acceleration tilts the effective gravity vector toward the equator (i.e., southward in the northern hemisphere, northward in the southern hemisphere). The maximum angle occurs at some intermediate latitude where this tangential component relative to the radial component is largest? Actually, the angle $\alpha$ between $\mathbf{g}'$ and the radial inward direction satisfies $\tan\alpha \approx \frac{|\text{tangential component of } \mathbf{a}_c|}{|\text{radial component of } \mathbf{g} - \text{radial component of } \mathbf{a}_c|}$. Since true gravity is inward, radially: $\mathbf{g} = -g \hat{r}$. Effective gravity is $\mathbf{g}' = -g \hat{r} + \mathbf{a}_c = (-g + \Omega^2 a \cos^2\phi) \hat{r} - \Omega^2 a \cos\phi \sin\phi \hat{n}$.

Thus the angle between $\mathbf{g}'$ and the inward radial direction ($-\hat{r}$) is given by the ratio of the component perpendicular to radial to the radial component (in magnitude). Let's be careful: The vector toward the center is $-\hat{r}$. $\mathbf{g}'$ has radial component $-g + \Omega^2 a \cos^2\phi$, which is negative (inward) because $g \gg \Omega^2 a$. The tangential component is $-\Omega^2 a \cos\phi \sin\phi$ (southward). The angle between $\mathbf{g}'$ and the inward radial vector is such that $\tan \alpha = \frac{|\text{tangential component}|}{|\text{radial component}|} = \frac{\Omega^2 a \cos\phi \sin\phi}{g - \Omega^2 a \cos^2\phi}$.

Since $\Omega^2 a \ll g$, denominator $\approx g$. So $\tan\alpha \approx \frac{\Omega^2 a}{g} \cos\phi \sin\phi = \frac{\Omega^2 a}{2g} \sin 2\phi$.

The maximum occurs at $\phi = 45^\circ$, where $\sin 2\phi = 1$. So $\alpha_{max} \approx \arctan\left(\frac{\Omega^2 a}{2g}\right) \approx \frac{\Omega^2 a}{2g}$ radians. Using $\Omega^2 a / g \approx 1/289$? Let's compute.

Standard values: Earth's angular velocity $\Omega = 7.2921 \times 10^{-5}$ rad/s. Earth's radius $a \approx 6.371 \times 10^6$ m. $g \approx 9.81$ m/s$^2$.

Compute $\Omega^2 a / g$:

$\Omega^2 = (7.2921 \times 10^{-5})^2 \approx 5.317 \times 10^{-9}$ s$^{-2}$.

$\Omega^2 a \approx 5.317 \times 10^{-9} \times 6.371 \times 10^6 \approx 0.03387$ m/s$^2$.

Divide by $g \approx 9.81$: $0.03387 / 9.81 \approx 0.003452 \approx 1/289.7$.

So the dimensionless parameter is about $3.45 \times 10^{-3}$.

Now, the fractional difference in $|g'|$ between equator and poles: At pole ($\phi=90^\circ$), centrifugal acceleration is zero, so $|g'|_{pole} = g$. At equator ($\phi=0$), $|g'|_{eq} = g - \Omega^2 a$ (ignoring the small tangential component's effect on magnitude, but actually the magnitude is $\sqrt{(g - \Omega^2 a)^2 + 0^2} = g - \Omega^2 a$ because tangential component is zero there). Wait, at equator, the tangential component is zero because $\sin\phi=0$. So $|g'|_{eq} = g - \Omega^2 a$. The fractional difference relative to the pole is $(g - (g - \Omega^2 a))/g = \Omega^2 a / g \approx 0.00345$, which is about $0.345\%$. But the problem says "about $0.7\%$ less". Hmm. Let's check.

Wait, maybe they consider the difference relative to the average? Or maybe they use the exact magnitude at equator but also consider the slight reduction due to the shape of the Earth? No, the problem is purely about the effect of rotation.

Alternatively, maybe the effective gravity magnitude at equator is approximated as $g_{eq} = g_{pole} - \Omega^2 a$? But $g_{pole}$ is about $9.832$ m/s$^2$, $g_{eq}$ is about $9.780$ m/s$^2$, difference is about $0.052$ m/s$^2$, which is about $0.53\%$ of $g_{pole}$, still not $0.7\%$. But $g_{pole}$ is larger because Earth is oblate; the problem might be using a spherical Earth. With $g=9.81$ everywhere, difference is $0.0339/9.81 = 0.345\%$. That's not $0.7\%$.

Wait, maybe they compare equator to poles not just by the centrifugal term but also because at the equator you are farther from Earth's center (oblate Earth), so $g$ itself is smaller. But the problem statement says "Show that ... the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles". This is a known approximate result: $g_{eq} \approx 9.78$ m/s$^2$, $g_{pole} \approx 9.83$ m/s$^2$, difference $\approx$ 0.05 m/s$^2$, which is about 0.5%. Some sources say 0.5%. Why 0.7%? Let's compute with standard values: $g_{pole} \approx 9.832$, $g_{eq} \approx 9.780$, difference $0.052$, fraction $0.052/9.832 \approx 0.00529 = 0.53\%$. Not 0.7%.

But perhaps the problem is from a specific textbook where they use approximate numbers that yield 0.7%. Let's see: If $\Omega = 7.3 \times 10^{-5}$ rad/s, $a = 6.4 \times 10^6$ m, $g = 9.8$ m/s$^2$.

$\Omega^2 = (7.3e-5)^2 = 5.329e-9$.

$\Omega^2 a = 5.329e-9 * 6.4e6 = 0.0341$ m/s$^2$.

$\Omega^2 a / g = 0.0341 / 9.8 \approx 0.00348$.

That's 0.35%. Still not 0.7%.

Wait, maybe they define the fractional difference as $(|g'|_{pole} - |g'|_{eq}) / |g'|_{eq}$? That would be $\Omega^2 a / (g - \Omega^2 a) \approx 0.0341 / (9.8 - 0.0341) = 0.0341/9.766 \approx 0.00349$, still ~0.35%.

Alternatively, maybe they compare the magnitude of effective gravity at equator and pole using the exact expression for $|g'|$ including the tangential component at some latitude? No, the maximum difference in magnitude is between equator and poles.

Wait, could it be that the problem includes both the variation due to rotation and the distance from Earth's center? If the Earth is a sphere, true gravity $g = GM/a^2$ is constant. But if the Earth is an oblate spheroid, the distance to the center at the equator is larger (by about 21 km), so true gravity is smaller. On an oblate Earth, the effective gravity difference is about 0.5%. But the problem explicitly says "at the Earth's surface" and asks to show something about effective gravity. However, the problem begins with "Evaluate the dimensionless parameter $\Omega^2 a / g$". That parameter is small. Then "Show that ... effective gravity is about 0.7% less... and the maximum angle ... is about $0.1^\circ$". Perhaps these statements are to be derived using the value of the parameter. Let's see if 0.7% and 0.1° come from $\Omega^2 a / g \approx 1/289 \approx 0.00346$.

0.7% is 0.007. That's double 0.00346. Could the fractional difference be $2 \Omega^2 a / g$? Why?

Wait, maybe the effective gravity magnitude variation is not just $\Omega^2 a / g$, but because of the angle, the magnitude difference between equator and poles might be derived from the exact expression for $|g'|$.

$|g'| = \sqrt{(g - \Omega^2 a \cos^2\phi)^2 + (\Omega^2 a \cos\phi \sin\phi)^2}$.

Expand: $(g - \Omega^2 a \cos^2\phi)^2 + (\Omega^2 a)^2 \cos^2\phi \sin^2\phi = g^2 - 2g\Omega^2 a \cos^2\phi + (\Omega^2 a)^2 \cos^4\phi + (\Omega^2 a)^2 \cos^2\phi \sin^2\phi = g^2 - 2g\Omega^2 a \cos^2\phi + (\Omega^2 a)^2 \cos^2\phi (\cos^2\phi + \sin^2\phi) = g^2 - 2g\Omega^2 a \cos^2\phi + (\Omega^2 a)^2 \cos^2\phi$.

So $|g'| = \sqrt{g^2 - 2g\Omega^2 a \cos^2\phi + (\Omega^2 a)^2 \cos^2\phi}$.

Factor: $|g'| = g \sqrt{1 - \frac{2\Omega^2 a}{g} \cos^2\phi + \left(\frac{\Omega^2 a}{g}\right)^2 \cos^2\phi}$.

Let $\epsilon = \Omega^2 a / g$. Then $|g'| = g \sqrt{1 - 2\epsilon \cos^2\phi + \epsilon^2 \cos^2\phi}$.

For small $\epsilon$, $\sqrt{1 - 2\epsilon \cos^2\phi + \epsilon^2 \cos^2\phi} \approx 1 - \epsilon \cos^2\phi + \frac{1}{2}\epsilon^2 \cos^2\phi + ...$? Actually use binomial: $\sqrt{1 + x} \approx 1 + x/2 - x^2/8$, where $x = -2\epsilon\cos^2\phi + \epsilon^2\cos^2\phi$.

Then $|g'| \approx g [1 + \frac{1}{2}(-2\epsilon\cos^2\phi + \epsilon^2\cos^2\phi) - \frac{1}{8}(-2\epsilon\cos^2\phi)^2] = g[1 - \epsilon\cos^2\phi + \frac{1}{2}\epsilon^2\cos^2\phi - \frac{1}{8}4\epsilon^2\cos^4\phi] = g[1 - \epsilon\cos^2\phi + \frac{1}{2}\epsilon^2\cos^2\phi - \frac{1}{2}\epsilon^2\cos^4\phi]$.

Simplify: $g[1 - \epsilon\cos^2\phi + \frac{1}{2}\epsilon^2\cos^2\phi(1 - \cos^2\phi)] = g[1 - \epsilon\cos^2\phi + \frac{1}{2}\epsilon^2\cos^2\phi\sin^2\phi]$.

So to first order, $|g'| \approx g(1 - \epsilon\cos^2\phi)$.

At equator ($\phi=0$): $|g'|_{eq} \approx g(1 - \epsilon)$.

At pole ($\phi=90^\circ$): $|g'|_{pole} \approx g$.

Fractional difference relative to pole: $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \approx \epsilon = \Omega^2 a / g \approx 0.00345 = 0.345\%$.

That's not 0.7%. So something else must be happening. Perhaps the problem uses the actual measured values of effective gravity at equator and poles (including oblateness and mass distribution) and says it's about 0.7%? Let's check typical numbers: $g_{eq} \approx 9.7803$, $g_{pole} \approx 9.8322$, difference $0.0519$, fraction $0.0519/9.7803 \approx 0.0053 = 0.53\%$. Relative to average $9.806$, it's $0.53\%$ as well. Not 0.7%.

Could it be 0.7% difference between equator and poles for the magnitude of $g'$ if we consider a rotating fluid Earth in hydrostatic equilibrium? For a Maclaurin spheroid, the difference might be larger? Let's see: For Earth, the flattening $f \approx 1/298.25$. The gravity variation for an oblate spheroid is given by something like $g = g_e (1 + \beta \sin^2\phi - ...)$ where $\beta \approx 0.005302$. That is about 0.53%. Still not 0.7%.

Maybe the problem is older and uses slightly different numbers. Let's try to see if any combination yields 0.7%.

Suppose they approximate $g \approx 10$ m/s$^2$, $a \approx 6.4 \times 10^6$ m, $\Omega \approx 7.3 \times 10^{-5}$ s$^{-1}$. Then $\Omega^2 a \approx 0.0341$ m/s$^2$. $\epsilon = 0.00341$. Still 0.34%.

If they compute the difference between equator and pole for the *apparent* weight (effective gravity) and include the fact that the pole is closer to the center? The pole radius is about $6.357 \times 10^6$ m, equatorial radius $6.378 \times 10^6$ m. True gravity $g \propto 1/r^2$ (to first order ignoring mass redistribution). So at equator, $g_{true}$ is smaller by factor $(R_{pole}/R_{eq})^2 \approx (6357/6378)^2 \approx 0.9934$, a reduction of about 0.66%. Combined with the centrifugal effect of 0.34%, total reduction is about 1.0%. Wait, that seems too large. Let's compute precisely.

Actually true gravity at surface of a sphere of radius $R$ is $GM/R^2$. If Earth were a sphere of mass $M$, but the equatorial radius is larger, then $g_{eq} = GM/R_{eq}^2$. Using $GM = g_{avg} R_{avg}^2$. But Earth's mass distribution and shape mean the actual variation is less. However, if we simply treat Earth as a sphere with varying radius? No.

Wait, the problem says "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles..."

Maybe they are using $a=$ Earth's radius, $g=$ gravitational acceleration, and they consider the *exact* expression for $|g'|$ difference between equator and poles: At equator, $|g'| = g - \Omega^2 a$. At poles, $|g'| = g$. The difference is $\Omega^2 a$. Fraction: $\Omega^2 a / g \approx 1/289 \approx 0.00346 \approx 0.35\%$. If they double it for some reason? Or maybe they compare to a different baseline, like the value of $g'$ at some standard latitude?

Alternatively, perhaps the problem uses the parameter $\Omega^2 a / g \approx 1/289$ and then says "Show that ... 0.7% less". Maybe they make a rough approximation: $\Omega^2 a / g \approx 1/289 \approx 0.0035$, and $2 \times 0.0035 = 0.007$ = 0.7%. Why factor of 2? Let's think about the angle.

The maximum angle: $\alpha_{max} \approx \frac{\Omega^2 a}{2g}$ radians. If $\Omega^2 a / g \approx 1/289$, then $\alpha_{max} \approx 1/(2 \times 289)$ rad $\approx 1/578$ rad. Convert to degrees: $(1/578) \times (180/\pi) \approx 180/(578\pi) \approx 180/1815 \approx 0.0992^\circ \approx 0.1^\circ$. So the maximum angle is indeed about 0.1°. That matches.

So the maximum angle uses the factor of $1/2$ in the tangent formula. The fractional difference in $|g'|$ might be something else. Let's see: If at equator $|g'| \approx g(1 - \epsilon)$, fractional difference from pole is $\epsilon$. That's 0.35%. Why 0.7%? Could it be that they are using the first-order variation in $|g'|$ over the entire range, i.e., from equator to pole the magnitude changes by $\epsilon g$, but they express it as a percentage of the equator value? $(g - (g - \epsilon g))/(g - \epsilon g) = \epsilon/(1-\epsilon) \approx \epsilon + \epsilon^2$, still ~0.35%.

Wait, could the problem be approximating the fractional difference in $|g'|$ between equator and pole for a rotating Earth where the radius at the pole is smaller than at equator? If we assume Earth is a perfect sphere, it's 0.35%. But maybe they assume Earth radius $a$ is the same, but they also consider that the gravitational acceleration $g$ itself is effectively $GM/a^2$ and at equator the distance to the center is $a$, but at the pole, because of the centrifugal bulge? No, the problem doesn't mention bulge.

Alternatively, maybe the problem defines $|g'|$ as the magnitude of the vector sum of $g$ (true gravity) and the full centrifugal term, but they evaluate the difference between the magnitude at the equator and the magnitude at the poles using the exact formula without approximation. Let's compute exact.

$|g'|_{eq} = g - \Omega^2 a$.

$|g'|_{pole} = g$.

Fraction: $(g - (g - \Omega^2 a))/g = \Omega^2 a / g$. Same.

So no.

Maybe the problem actually says 0.3% less? But the user wrote 0.7%. Could it be a mis-remembering? Or maybe they use $g \approx 9.8$ and $\Omega^2 a \approx 0.034$, but they mistakenly think $\Omega^2 a / g \approx 0.007$? Let's check: $0.034/9.8 = 0.00347$. If they approximate $\Omega = 2\pi / (24 \times 3600) \approx 7.27e-5$, $a \approx 6.4e6$, $g \approx 10$, then $\Omega^2 a = (7.27e-5)^2 \times 6.4e6 \approx 5.29e-9 \times 6.4e6 = 0.0338$, divide by $g=10$ gives $0.00338$. Still 0.34%.

If they use the *angular velocity* of Earth relative to stars? That's the same. Sidereal day is slightly less, $\Omega = 7.292e-5$.

If they use the centrifugal acceleration at equator: $v^2 / a$, with $v = 2\pi a / T$. $v \approx 465$ m/s. $v^2 / a = 465^2 / 6.4e6 \approx 216225 / 6.4e6 \approx 0.0338$ m/s$^2$. Same.

Could it be that they consider the effective gravity difference not just between pole and equator but between pole and the latitude where centrifugal effect is maximum? The maximum centrifugal acceleration magnitude is at equator, so that's it.

Wait, maybe the problem is from a source where the Earth is assumed to be a perfect sphere but the gravitational acceleration $g$ is taken as the *average* effective gravity, not the true gravity. If the average effective gravity is about $g_{avg} = g_{true} - \frac{1}{3}\Omega^2 a$ (from spherical harmonics), then $g_{true} = g_{avg} + \frac{1}{3}\Omega^2 a$. Then $|g'|_{pole} = g_{true} = g_{avg} + \frac{1}{3}\Omega^2 a$. $|g'|_{eq} = g_{true} - \Omega^2 a = g_{avg} - \frac{2}{3}\Omega^2 a$. The difference relative to average is $\frac{2}{3}\epsilon$ at equator and $\frac{1}{3}\epsilon$ at pole. The difference between pole and equator is $\epsilon$. Still same.

Alternatively, maybe the problem uses $|g'|_{pole}$ not $g$ but something else? The magnitude at the pole is $g$. So same.

Could the 0.7% be a factor of 2 error in some textbook? Let's check typical geophysical values: Earth rotation causes a bulge. The effective gravity at equator is less by about 0.34% due to rotation, and the distance increase reduces it by about 0.18% (if one uses inverse square law). Total ~0.52%. Some sources say 0.5%. But 0.7% is larger than any of these.

Perhaps the problem is about *apparent* weight measured by a scale? That is effective gravity. So still 0.34% for a sphere.

Wait, could there be a factor of 2 from considering the *vector* magnitude difference between equator and poles when you include the tangential component? Let's compute exact difference between poles and the latitude where $|g'|$ is minimum. The minimum of $|g'|$ might not be exactly at equator due to the $(\Omega^2 a)^2$ term, but that effect is negligible. Let's differentiate $|g'|^2 = g^2 - 2g\Omega^2 a \cos^2\phi + (\Omega^2 a)^2 \cos^2\phi$.

Let $u = \cos^2\phi$. Then $|g'|^2 = g^2 - 2g\Omega^2 a u + (\Omega^2 a)^2 u = g^2 + u(-2g\Omega^2 a + (\Omega^2 a)^2)$.

Since $-2g\Omega^2 a + (\Omega^2 a)^2 < 0$, $|g'|^2$ is minimized when $u$ is maximized, i.e., at equator ($u=1$). So minimum at equator. So the difference is just $\epsilon$.

What if the problem compares the *apparent* gravity at the equator to that at the poles, but uses $g$ at the poles as $9.83$, and $g$ at the equator from effective gravity formula with $g_{true}$ at the equator being $9.81$? Then $|g'|_{eq} = 9.81 - 0.034 = 9.776$, $|g'|_{pole} = 9.83$. Fractional difference $= (9.83 - 9.776)/9.83 = 0.054/9.83 = 0.0055 = 0.55\%$. Still not 0.7%.

If $g_{true,pole} = 9.81$ and $g_{true,eq} = 9.81$ (same), then $|g'|_{eq} = 9.776$, $|g'|_{pole}=9.81$, difference 0.34%.

Maybe the problem uses $\Omega = 2\pi / 86164$ (sidereal day), $a = 6371$ km, $g=9.8$. $\Omega^2 a / g \approx (7.2921e-5)^2 * 6.371e6 / 9.8 = 5.317e-9 * 6.371e6 / 9.8 = 0.03387 / 9.8 = 0.003456$. Still 0.35%.

Wait, perhaps the parameter to evaluate is $\Omega^2 a / g$, which is about $1/289 \approx 0.00346$. Then the problem says "Show that ... effective gravity is about 0.7% less at the equator than at the poles". Maybe the statement in the problem is indeed using $2 \times (\Omega^2 a / g) \approx 0.7\%$ because they think the fractional difference is $2\Omega^2 a / g$? Let's examine the derivation.

Effective gravity at latitude $\phi$: $g' = g - \Omega^2 a \cos^2\phi$ (approx, radial component only). At equator: $g'_{eq} = g - \Omega^2 a$. At pole: $g'_{pole} = g$. So difference is $\Omega^2 a$. Percent difference: $(\Omega^2 a / g) \times 100\% \approx 0.35\%$.

What if instead they compare the *apparent weight* of a unit mass at the pole vs equator on a *scale*. At the pole, the scale reads $mg'_{pole} = mg$. At the equator, $mg'_{eq} = m(g - \Omega^2 a)$. The difference normalized to the equatorial value: $(mg - m(g - \Omega^2 a)) / (m(g - \Omega^2 a)) = \Omega^2 a / (g - \Omega^2 a) \approx 0.00346 / 0.9965 \approx 0.00347$, still ~0.35%.

So 0.7% remains puzzling.

Let's check known values: The actual difference between $g$ at pole and equator is about 0.5% (9.780 vs 9.832). Some older textbooks might say 0.5%. Maybe the user typed 0.7% but it's actually 0.5%? Or maybe it's a different planet? But it says Earth.

Alternatively, could the problem be using $a$ = Earth's radius, but $g$ = gravitational acceleration at Earth's surface, and they want the dimensionless parameter. Then maybe they want to compute the fractional difference in the *normal* gravity on a rotating, slightly oblate Earth (Clairaut's theorem). Clairaut's theorem gives the variation of gravity with latitude: $g(\phi) = g_e (1 + \beta \sin^2\phi + ...)$ where $\beta \approx \frac{5}{2} \frac{\Omega^2 a}{g} - f$, with $f$ the flattening. For Earth, $\Omega^2 a / g \approx 1/289$, $f \approx 1/298$. Then $\beta \approx \frac{5}{2} \frac{1}{289} - \frac{1}{298} \approx \frac{2.5}{289} - \frac{1}{298} \approx 0.00865 - 0.00336 = 0.00529$. So the fractional variation from equator to pole is about 0.53%. Still not 0.7%.

If we only considered the rotational term in Clairaut's theorem and ignored flattening: $\beta \approx \frac{5}{2} \epsilon \approx 2.5 \times 0.00346 = 0.00865 = 0.87\%$. That's close to 0.7%. But this is the coefficient of $\sin^2\phi$ in the gravity formula for an equilibrium fluid body. The variation from equator to pole is $\beta \approx \frac{5}{2} \epsilon$. Wait, is that the variation of true gravity on a rotating fluid body? Let's recall: For a rotating homogeneous fluid body in hydrostatic equilibrium, the surface gravity variation is given by something like $g = g_e (1 + \beta \sin^2\phi)$ with $\beta = \frac{5}{2}m - f$, where $m = \Omega^2 a / g$. The flattening $f$ is related to $m$ by $f \approx \frac{5}{4}m$ for a homogeneous body? Actually, for a Maclaurin spheroid, the relationship is more complex. For Earth, $f \approx 1/298$, $m \approx 1/289$, so $\beta \approx 0.0053$.

But if we consider the variation of effective gravity on a rotating sphere without bulge, the variation is $m \approx 0.0035$.

If we consider the variation on a rotating fluid body where flattening adjusts but we look at the *effective* gravity (which includes centrifugal), the variation is about 0.5%. In some simplified derivations, one might get something like the difference between equator and pole being $m + \frac{1}{2}m$? Not sure.

Let's read the problem text carefully again: "Evaluate the dimensionless parameter $\Omega ^ { 2 } a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

So the first task is to evaluate the dimensionless parameter. Then to show the two things. "Show that" means it's a derivation, but the graded answer is whatever solve() returns. So we need to compute numerical values for these three things.

What exactly are the three quantities asked?

1. The dimensionless parameter $\Omega^2 a / g$.

2. The fractional (or percent) difference in $|g'|$ between equator and poles. Since it says "about 0.7% less", likely we need to compute the exact percent difference and show it's about 0.7%. But our calculations give ~0.35% for a spherical Earth. Could the problem consider the difference between the pole and the equator for effective gravity on an oblate Earth? If so, how to compute it from the given parameters? The problem only gives $\Omega$, $a$, $g$. It doesn't give flattening or $GM$. So any computation of 0.7% must be derivable solely from these parameters. Therefore, maybe the formula for the percent difference is something like $2 \Omega^2 a / g$? Let's see if that can be justified.

Let's compute the exact magnitude of effective gravity at the equator and poles using the given expression. Maybe the problem defines $g$ as the effective gravity at the pole? Or maybe they define $g$ as the gravitational constant times mass over $a^2$? Usually $g$ is the true gravitational acceleration. But suppose $g$ is the average surface gravity. Then at pole, true gravity is slightly larger, but without more info, we can't compute it.

Wait, maybe they define effective gravity as $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$, and they approximate $|g'|$ by projecting onto the radial direction? No.

Let's think about the angle. The maximum angle is about $0.1^\circ$. Using $\epsilon = \Omega^2 a / g \approx 1/289$, $\alpha_{max} \approx \epsilon/2$ rad $\approx 1/(2\times 289) \approx 0.00173$ rad. Convert to degrees: $0.00173 \times 180/\pi \approx 0.0992^\circ \approx 0.1^\circ$. That matches perfectly.

Now for the percent difference. If they somehow derived the fractional difference as $2\epsilon$, that would be $2/289 \approx 0.00692 \approx 0.69\% \approx 0.7\%$. Why would it be $2\epsilon$? Let's see if any first-order approximation yields $2\epsilon$.

Consider the effective gravity magnitude at latitude $\phi$:

$|g'| \approx g(1 - \epsilon \cos^2\phi)$.

At equator: $|g'| \approx g(1 - \epsilon)$.

At pole: $|g'| \approx g$.

Difference: $\epsilon g$.

Fractional difference relative to equator: $\epsilon g / (g(1-\epsilon)) = \epsilon/(1-\epsilon) \approx \epsilon$.

Not $2\epsilon$.

Consider the difference in *apparent weight* including the variation in distance from center due to rotation? But the Earth is spherical. No.

Maybe the problem is not comparing pole to equator, but comparing the *average* over the surface to the equator? The average of $\cos^2\phi$ over the sphere is 1/3. Average $|g'| \approx g(1 - \epsilon/3)$. Equator is $g(1-\epsilon)$. Difference relative to average: $(g(1-\epsilon/3) - g(1-\epsilon)) / (g(1-\epsilon/3)) = (2\epsilon/3)/(1-\epsilon/3) \approx 2\epsilon/3 \approx 0.23\%$.

Or difference between pole and average: $\epsilon/3 \approx 0.115\%$.

Not 0.7%.

What about the variation of the *centrifugal acceleration* magnitude? It ranges from 0 at poles to $\Omega^2 a$ at equator. So fractional variation relative to $g$ is $\epsilon \approx 0.35\%$.

What about the *sum* of the two effects: (1) reduction in $|g'|$ due to centrifugal radial component, and (2) the fact that the radial component of centrifugal acceleration is maximum at equator and zero at poles. Wait, the reduction is already that.

Maybe the problem statement has a misprint and actually says 0.35% or 0.3%. However, the user explicitly wrote "0 . 7 %". We must compute whatever the problem asks. But we need to figure out what the numerical answer should be. If we compute $\Omega^2 a / g$ and then compute the percent difference exactly as $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \times 100$, we get about 0.35%. That would disagree with the problem's statement of 0.7%. But the problem says "Show that ... is about 0.7% less". Since we are to return a computed numerical answer, we should compute the relevant quantity. But what is the relevant quantity? The problem likely expects the answer to be around 0.7% based on the numbers and formulas used in the source. Let's search memory: There is a classic problem in atmospheric science or geophysics textbooks (e.g., problem 1.1 in Holton's "An Introduction to Dynamic Meteorology" or similar). Let's recall.

In Holton, there is a problem: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.3% less at the equator than at the poles, and the maximum angle between g' and a vector pointing toward the center of the Earth is about 0.1°." Hmm, maybe it's 0.3%? Actually, I recall a problem like this. Let me think. In some textbooks, the answer is indeed ~0.3% (or 0.35%). For example, in "Atmospheric Science: An Introductory Survey" by Wallace and Hobbs, there might be a problem. Or in "Fundamentals of Atmospheric Physics" by Murry Salby. Let me recall: Salby's book has a problem: "The earth's rotation modifies the effective gravity. Estimate the dimensionless parameter $\Omega^2 a / g$... Show that the effective gravity is about 0.3% less at the equator than at the poles and that the maximum deflection angle is about 0.1°." That sounds plausible. But the user says 0.7%. Could it be 0.7% in some other source?

Wait, I recall that in some contexts, the variation of effective gravity from pole to equator is about 0.5%. But 0.7% is specifically double 0.35%. Let's see if there is a textbook that mistakenly says 0.7% because they confuse $\Omega^2 a / g$ with the fractional difference in $g'$, but then use $\Omega^2 a / g \approx 1/289 \approx 0.0035$, and then maybe they think the fractional difference is $2 \times 0.0035 = 0.007$? Or perhaps they compute $\Omega^2 a / (g - \Omega^2 a/2)$? No.

Wait, the maximum angle uses $\epsilon/2$ in radians. If one mistakenly uses $\epsilon$ radians instead of $\epsilon/2$, one gets about $0.2°$, not $0.1°$. But 0.7% might be derived from something else.

Let's search memory: The dimensionless parameter $m = \Omega^2 a / g \approx 1/289$. The flattening of the Earth $f \approx 1/298$. The difference between polar and equatorial gravity is $2f - m \approx 2/298 - 1/289 \approx 0.00671 - 0.00346 = 0.00325$. That gives about 0.33% difference. So still not 0.7%.

If we consider the *geopotential* or something else? No.

Maybe the problem uses $g = 9.8$ m/s$^2$, $a = 6.37 \times 10^6$ m, $\Omega = 7.27 \times 10^{-5}$ s$^{-1}$. Let's compute:

$\Omega = 7.27e-5$

$\Omega^2 = 5.285e-9$

$\Omega^2 a = 5.285e-9 \times 6.37e6 = 0.03366$

$g = 9.8$

$\epsilon = 0.03366/9.8 = 0.003435$.

That's 0.34%.

If they use $g=10$ exactly, $\epsilon = 0.003366 = 0.3366\%$.

So it's robustly ~0.34%.

Maybe the problem expects the answer as "0.0035" (dimensionless) for the first quantity. Then for the second quantity, perhaps they want the *percent* difference between equator and poles, but computed as $(g_{pole} - g_{eq})/g_{eq} \times 100$? That's $0.00343/(1-0.00343) = 0.00344$, still 0.344%.

Or maybe they want the absolute difference in m/s^2? No, the problem explicitly says "0.7% less".

Wait, maybe they consider the effective gravity magnitude at the equator as computed from the exact formula including the tangential component of centrifugal force at some latitude? But the difference between equator and pole is maximum at equator vs pole.

Wait, what if the problem actually says the magnitude of the effective gravity is about 0.3% less? But user typed 0.7%. Maybe a typo in the problem statement provided by the user. We need to decide what the expected numeric answer is. Since the problem is likely from a standard source, I should compute the correct physics: $\Omega^2 a / g \approx 0.0035$, percent difference in $|g'|$ between pole and equator $\approx 0.35\%$, max angle $\approx 0.1^\circ$. But the user explicitly says 0.7%. Let's examine the possibility that the effective gravity difference is indeed about 0.7% for a reason.

One possibility: The problem might be evaluating the difference at the surface of a *rotating spherical Earth* but using $g$ to mean the *effective* gravity at 45° latitude or something? No.

Another: Maybe the problem asks for the difference between the equator and the poles in the *magnitude of the true gravitational acceleration* $g$ (not effective) if Earth were a rotating fluid in hydrostatic equilibrium. In that case, the surface is an oblate spheroid. The true gravity at the pole would be larger than at the equator because the pole is closer and also because of the mass distribution. For a uniform density rotating sphere? Wait, no.

Let's derive the variation of $g$ on a rotating fluid body. For an incompressible fluid in hydrostatic equilibrium, the surface is an equipotential of the combined gravitational and centrifugal potential. The effective gravity is perpendicular to the equipotential. Its magnitude can be computed. The difference between equator and pole can be derived.

But the problem says "magnitude $|g'|$ of the effective gravity". On a rotating fluid Earth, the effective gravity is indeed the gradient of the geopotential. The variation of effective gravity on the reference ellipsoid is given by the International Gravity Formula. The difference is about 0.5%. Not 0.7%.

So 0.7% is definitely off from standard values. Let's see if any simple formula yields 0.7%. Could it be that they compare the effective gravity at the equator to the *gravitational* acceleration at the pole (which is $g_{pole} = GM/R_{pole}^2$)? If $R_{pole} < R_{eq}$ by about 21 km, then $g_{pole} \approx GM/(6357^2)$, $g_{eq,true} \approx GM/(6378^2)$. Ratio: $(6378/6357)^2 \approx (1.0033)^2 \approx 1.0066$. So true gravity at pole is about 0.66% larger than at equator just due to radius difference. Add centrifugal reduction at equator of 0.34%, total effective gravity at equator is about $(1 - 0.0034) \times g_{eq,true}$. If $g_{eq,true}$ is 0.66% less than $g_{pole,true}$, then $g_{eff,eq}$ is about $1 - 0.0066 - 0.0034 = 1 - 0.01 = 0.99$, i.e., about 1% less? Wait, let's do additive: $g_{eff,pole} = g_{pole,true} \approx (R_{eq}/R_{pole})^2 g_{eq,true} \approx 1.0066 g_{eq,true}$. $g_{eff,eq} = g_{eq,true} - \Omega^2 a = g_{eq,true}(1 - \Omega^2 a / g_{eq,true}) \approx g_{eq,true}(1 - 0.0034)$. So $g_{eff,eq} / g_{eff,pole} \approx (1 - 0.0034) / 1.0066 \approx 0.990$. That's a 1.0% difference. Not 0.7%.

But if Earth were homogeneous sphere of radius $a$, and we consider the *reference* $g$ as the gravitational acceleration at radius $a$, then $g$ is same everywhere. So 0.34%.

Maybe the problem uses $a$ as the equatorial radius and $g$ as the *standard* gravity $9.80665$ m/s$^2$ (which is about the average effective gravity). Then at the pole, true gravity is slightly larger than standard, and effective gravity at pole is $g_{pole} \approx g_{std} + 0.0053 g_{std}$? No.

Alternatively, the problem might be asking to show these things using *approximations* that yield 0.7% and 0.1°. Let's see: If the dimensionless parameter is about $3.5 \times 10^{-3}$, then 0.7% is $2 \times 3.5 \times 10^{-3} \times 100 = 0.7\%$. And 0.1° is $(3.5 \times 10^{-3} / 2) \times (180/\pi) \times 100$? Wait, $(\epsilon/2)$ rad $\times (180/\pi) \approx 0.099°$. So 0.1°. So the factor for the angle is $\epsilon/2$, but the factor for the percent might be $2\epsilon$. Perhaps there is a miscalculation in the problem source. But as the solver, we need to compute the correct values based on physics. However, the instructions say: "The graded answer is whatever solve() returns, so let the function do the arithmetic." It doesn't say we have to match the problem's approximate numbers exactly, but we should compute the relevant quantity.

Let's identify the three quantities:

1. $\Omega^2 a / g$ (dimensionless).

2. The percent (or fractional) reduction of $|g'|$ at equator relative to poles. The phrasing "0.7% less" suggests a percentage. We can compute the exact percent reduction: $((|g'|_{pole} - |g'|_{eq}) / |g'|_{pole}) \times 100$. This will be about 0.35%. If the expected answer is 0.7, we might get marked wrong if it's an auto-grader expecting 0.7. But is there any way to get 0.7 from the standard parameters? Let's think again.

Could the problem define $g$ as the *effective* gravity at the equator? Or maybe $g = GM/a^2$ but $a$ is not Earth's radius but some other length? No.

Wait, maybe the problem uses the value of Earth's angular velocity as $\Omega = 2\pi / (24 \text{ hours})$, and $a = 6.4 \times 10^6$ m, $g = 9.8$ m/s$^2$, but then they compute the *centrifugal acceleration* at the equator: $a_c = \Omega^2 a \approx 0.034$ m/s$^2$. Then they compute $|g'|_{eq} = \sqrt{g^2 + (\Omega^2 a)^2 - 2 g \Omega^2 a}$? That's just $g - \Omega^2 a$. So no.

What if they consider the vector sum of gravity and centrifugal acceleration at the equator where the two are antiparallel? $|g'| = g - \Omega^2 a$. The difference is $\Omega^2 a$. The fractional difference is $\Omega^2 a / g$. That's 0.34%.

What if they mistakenly think that the effective gravity at the pole is $g$ and at the equator is $g - 2\Omega^2 a$? Why would that be? Maybe because they use the formula $|g'| \approx g - \Omega^2 a \cos^2\phi$ and then compute the variation from equator to pole as $g_{eq} = g - \Omega^2 a$, $g_{pole} = g$, difference $\Omega^2 a$. But perhaps they think the variation of true gravity with latitude due to the Earth being an ellipsoid adds another $\Omega^2 a$, making total difference $2\Omega^2 a$? There is an approximate relationship for a fluid Earth: the ellipticity $e \approx \Omega^2 a / g$? Wait, for a homogeneous rotating fluid sphere, the flattening $f
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
The user wants the corrected `solve()` function based on the problem description. The previous code apparently had a runtime error because it didn't define a proper function or had syntax issues. We need to write a completely correct `solve()` function.

We need to interpret the physics problem:
1. Evaluate dimensionless parameter $\Omega^2 a / g$ for Earth.
2. Show that magnitude $|g'|$ of effective gravity is about 0.7% less at equator than at poles.
3. Show maximum angle between $\mathbf{g}'$ and vector pointing towards Earth's centre is about $0.1^\circ$.

We need to return a dict with "1", "2", "3".
- "1": value of $\Omega^2 a / g$ (dimensionless)
- "2": percent difference in $|g'|$ between equator and poles. The problem says "about 0.7% less". Let's see how to get ~0.7% from standard Earth parameters.
- "3": max angle in degrees, about $0.1^\circ$.

Wait, let's carefully analyze the physics to match the numbers in the problem. The problem is likely from a textbook (maybe Holton or Salby). Let's derive:

Effective gravity: $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$.
But careful with sign conventions. In rotating frame, centrifugal acceleration is $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$? Actually from previous derivation, $\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = -\Omega^2 \mathbf{\rho}$ where $\mathbf{\rho}$ is perpendicular distance from axis. The outward centrifugal acceleration is $-\mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r}) = \Omega^2 \mathbf{\rho}$. However, many textbooks define effective gravity as $\mathbf{g}' = \mathbf{g} - \mathbf{\Omega} \times (\mathbf{\Omega} \times \mathbf{r})$. Let's see what the standard effective gravity definition is.

Effective gravity is the vector sum of true gravitational acceleration (pointing toward center) and centrifugal acceleration (pointing away from axis). True gravity: $\mathbf{g} = -g \hat{r}$ (inward). Centrifugal: $\mathbf{a}_c = \Omega^2 a \cos\phi \, \hat{\rho}$ (outward from axis). In the meridional plane, $\hat{\rho} = \cos\phi \hat{r} - \sin\phi \hat{n}$ (with $\hat{n}$ northward). So $\mathbf{a}_c = \Omega^2 a \cos\phi (\cos\phi \hat{r} - \sin\phi \hat{n}) = \Omega^2 a \cos^2\phi \hat{r} - \Omega^2 a \cos\phi \sin\phi \hat{n}$.

Thus $\mathbf{g}' = (-g + \Omega^2 a \cos^2\phi) \hat{r} - \Omega^2 a \cos\phi \sin\phi \hat{n}$.

Magnitude: $|g'| = \sqrt{(g - \Omega^2 a \cos^2\phi)^2 + (\Omega^2 a \cos\phi \sin\phi)^2}$.

At pole ($\phi=90^\circ$): $|g'|_{pole} = g$.

At equator ($\phi=0$): $|g'|_{eq} = g - \Omega^2 a$.

Fractional difference: $(g - (g - \Omega^2 a))/g = \Omega^2 a / g$. With standard values, this is about $0.00346$, or $0.35\%$.

But the problem says $0.7\%$. Is there any way to get $0.7\%$? Let's compute using parameters that might be in the textbook. Maybe they use $a = 6.4 \times 10^6$ m, $g = 9.8$, $\Omega = 7.3 \times 10^{-5}$. We already saw that gives $0.00348 = 0.35\%$.

Could they define the fractional difference as $\frac{|g'|_{pole} - |g'|_{eq}}{\frac{1}{2}(|g'|_{pole} + |g'|_{eq})}$? That would be $\Omega^2 a / (g - \Omega^2 a/2) \approx 0.00348 / 0.9983 \approx 0.00349$, still 0.35%.

Could they be using the *exact* magnitude difference and attributing it to the fact that at $45^\circ$ latitude the tangential component tilts $g'$? But the magnitude variation is still $\epsilon$ to first order.

What if they consider the difference between the pole and the latitude where $|g'|$ is minimum? It's at equator.

Wait, maybe the problem defines effective gravity differently? Some textbooks define effective gravity as the vector sum of true gravity and the Coriolis force? No.

Alternatively, maybe the problem asks to show the magnitude is about **0.3%** less, but the user typed 0.7%. However, the user is asking us to fix the bug and return the corrected function. We need to compute the answers correctly based on standard physics. If the auto-grader expects a specific number, we need to match it. The problem statement in the prompt says 0.7%. But maybe the problem is from a source where the answer is indeed 0.7% because of a specific reasoning. Let's investigate further.

The dimensionless parameter $\epsilon = \Omega^2 a / g \approx 0.0035$.

Now, the centrifugal acceleration is $\Omega^2 a \cos\phi$. At the equator, it is $\Omega^2 a$. The reduction in effective gravity at the equator compared to the pole is exactly $\Omega^2 a$ for a spherical Earth. That's $0.35\%$.

However, the problem says "Show that ... is about 0.7% less at the equator than at the poles". Could it be that the answer expected is **0.0035** (dimensionless) for part 1, and for part 2 the answer is the **percent** difference, which they approximate as $2 \times (\Omega^2 a / g) \times 100\%$? Let's see if there's a derivation that yields a factor of 2.

Consider the vertical component of effective gravity (component along the local vertical). Usually, effective gravity is defined as perpendicular to the geopotential surface. On a rotating Earth, the geopotential surfaces are oblate. The local vertical is defined by $g'$, not by the radial direction. The angle between $g'$ and radial direction is small. The magnitude of $g'$ is the component along the vertical. But its projection onto the radial direction might be slightly different. However, the magnitude itself is what we have been calculating.

Wait, what if the problem's $g$ is not the true gravitational acceleration but the *effective* gravity at some reference latitude (e.g., $45^\circ$), and the true gravitational acceleration $g_0$ is larger? No, the problem says "Evaluate the dimensionless parameter $\Omega^2 a / g$". It gives $g$ as the gravitational acceleration. So $g$ is true gravity.

Let's search memory: In the textbook "Atmospheric Science: An Introductory Survey" by Wallace & Hobbs, Chapter 1, Problem 1.3? I recall a problem: "The earth's rotation produces a centrifugal force. Evaluate the dimensionless parameter $\Omega^2 a / g$ for the earth. Show that the magnitude of the effective gravity is about 0.3% less at the equator than at the poles, and that the angle between the effective gravity and a radial line is about 0.1°." Actually, I'm pretty sure it's 0.3% or 0.35% in standard sources. Let's try to find the exact source. The problem might be from "An Introduction to Dynamic Meteorology" by James R. Holton, 4th edition. In Chapter 1, there is a problem about effective gravity. Let me recall: Holton discusses the geopotential and effective gravity. He defines $g_0 = GM/a^2$ and $\epsilon = \Omega^2 a / g_0$. Then he states that the variation of $g$ with latitude is small. But I don't recall the exact numbers.

Wait, there is a known result: For a spherical Earth, gravity at the equator is reduced by rotation by a factor of $1 - \Omega^2 a / g \approx 0.0035$. However, if you consider the Earth as a fluid and compute the *shape* (geoid), the effective gravity at the pole is larger than at the equator by about $0.5\%$. Some older textbooks may have approximated this as $0.7\%$ because they used $g \approx 9.8$ but also considered that the pole is $21$ km closer, leading to a larger true gravity. But adding those two effects gives about $0.5\% + 0.34\% = 0.84\%$? Let's compute more carefully.

Assume Earth is an oblate spheroid with flattening $f = (a-c)/a \approx 1/298 \approx 0.00336$, where $a$ is equatorial radius, $c$ is polar radius. The polar radius is smaller by $\Delta r = a f \approx 21.3$ km. If we approximate true gravity as $GM/r^2$, then at pole $r = c = a(1-f)$. $g_{pole,true} \approx GM/[a^2(1-f)^2] \approx (GM/a^2)(1+2f) = g_{eq,true}(1+2f)$. So true gravity at pole is larger by about $2f \approx 0.0067 = 0.67\%$ compared to equator.

Then effective gravity at equator: $g_{eff,eq} = g_{eq,true} - \Omega^2 a \approx g_{eq,true}(1 - \Omega^2 a / g_{eq,true})$. Effective gravity at pole: $g_{eff,pole} = g_{pole,true} \approx g_{eq,true}(1+2f)$. The fractional difference between pole and equator effective gravity is:

$(g_{eff,pole} - g_{eff,eq}) / g_{eff,pole} \approx [g_{eq,true}(1+2f) - g_{eq,true}(1 - \epsilon)] / [g_{eq,true}(1+2f)] = (2f + \epsilon) / (1+2f) \approx 2f + \epsilon \approx 0.0067 + 0.0035 = 0.0102 = 1.02\%$.

That's too large. But maybe they compare effective gravity at equator to true gravity at pole? $(g_{pole,true} - g_{eff,eq}) / g_{pole,true} = (g_{eq,true}(1+2f) - g_{eq,true}(1-\epsilon)) / (g_{eq,true}(1+2f)) = (2f+\epsilon)/(1+2f) \approx 1.0\%$. Still not 0.7%.

What if they compare $g_{eff,eq}$ to $g_{eff,pole}$ but approximate $g_{pole,true} \approx GM/a^2$ (ignoring radius difference)? Then it's just $\epsilon \approx 0.35\%$.

Alternatively, maybe they approximate the variation of true gravity using $f \approx \epsilon$ (which is roughly true for Earth: $1/298 \approx 1/289$). Then the total variation is $2f \approx 2\epsilon \approx 0.7\%$? Let's see: For a rotating fluid body, the flattening is approximately $f \approx \frac{5}{4} \frac{\Omega^2 a}{g}$ for a homogeneous body? Wait, for a Maclaurin spheroid, $f \approx \frac{5}{4} m$ where $m = \Omega^2 a / g$? Actually, for a homogeneous fluid body, the approximate relationship is $f \approx \frac{5}{4} m$. Let's check: $m \approx 1/289 \approx 0.00346$. $\frac{5}{4} m \approx 0.00433$, which is larger than Earth's actual $f \approx 0.00336$.

If $f \approx m$ (as is approximately true for Earth), then the variation in true gravity from equator to pole due to shape is about $2f \approx 2m \approx 0.7\%$. And effective gravity at equator is reduced by $m$ due to rotation. So the total effective gravity difference becomes $2m + m = 3m \approx 1.0\%$? No.

Wait, perhaps the problem is using the *observed* difference in effective gravity between pole and equator, which is about 0.5%, and then rounding to 0.7%? No.

Let's search for the exact phrasing. The problem: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth is about $0.1^\circ$."

This exact phrasing appears in some lecture notes or problem sets. Let's think. Could it be from "Introduction to Geophysical Fluid Dynamics" by Cushman-Roisin & Beckers? Or from "Atmospheric and Oceanic Fluid Dynamics" by Vallis?

Actually, I vaguely recall a problem in Vallis's book: Problem 2.1? Or maybe from "Atmospheric Science" by John M. Wallace and Peter V. Hobbs. Let's check the numbers. If Wallace & Hobbs uses $\Omega = 7.292 \times 10^{-5}$ s$^{-1}$, $a = 6.37 \times 10^6$ m, $g = 9.81$ m/s$^2$. Then $\Omega^2 a / g = (7.292 \times 10^{-5})^2 \times 6.37 \times 10^6 / 9.81 = 5.317 \times 10^{-9} \times 6.37 \times 10^6 / 9.81 = 0.03387 / 9.81 = 0.00345$. Multiply by 100% = 0.345%. For the angle: $\alpha = \arctan(\Omega^2 a \sin\phi \cos\phi / (g - \Omega^2 a \cos^2\phi))$. Max at $\phi=45^\circ$: $\alpha_{max} = \arctan( \Omega^2 a / (2g - \Omega^2 a) ) \approx \arctan(0.00345 / (2 - 0.00345)) = \arctan(0.00173) \approx 0.00173$ rad = $0.0992^\circ$. That matches 0.1°.

So the numbers are: parameter = 0.00345, percent difference = 0.35%, max angle = 0.099°. But the problem says 0.7%. Unless there is a factor of 2 error in the problem statement or the expected answer.

Wait, what if the problem defines the fractional difference as $(g_{pole} - g_{eq}) / g_{eq}$? That gives $0.00346 / 0.9965 = 0.00347$, still 0.347%.

What if they consider the difference in the *geopotential* or something? No.

What if they compute $|g'|$ as $g' = \sqrt{g^2 + (\Omega^2 a)^2}$? That would be at equator if the two were perpendicular? But they are antiparallel.

What if the problem is about the *change* in the magnitude of effective gravity from pole to equator for a unit mass, expressed as a fraction of $g'$, but they compute the full variation: at pole $g' = g$, at equator $g' = g - \Omega^2 a$. The difference is $\Omega^2 a$. If we express this as a percentage of $g'$, but mistakenly compute $\frac{\Omega^2 a}{g/2}$ because the average $g'$ is $g - \Omega^2 a/2$, then the fractional variation relative to average is $\Omega^2 a / (g - \Omega^2 a/2) \approx 0.00346 / 0.9983 \approx 0.00347$, still 0.35%.

What about if they compute the variation in *centrifugal acceleration* magnitude from pole to equator relative to $g'$? That's $\Omega^2 a / g \approx 0.35\%$.

So I can't see any legitimate physics derivation that yields 0.7% from the given parameters.

Could the problem be using a different $g$? For example, if they use $g = 4.9$ m/s$^2$? That would double it. But $g$ is standard gravity.

Alternatively, maybe the problem uses $a = 6.4 \times 10^6$ m and $\Omega = 2 \times 7.3 \times 10^{-5}$? That would be if they used solar day instead of sidereal day? $\Omega_{solar} = 2\pi / 86400 \approx 7.272 \times 10^{-5}$. That's actually slightly smaller than sidereal. So no.

What if they used angular velocity of Earth-Moon system? No.

Wait, maybe the 0.7% comes from the fact that at the equator, the effective gravity is less by $\Omega^2 a$ due to rotation, and also because you are further from the center by about $a f \approx 21$ km, so the true gravity is less by $2 f g \approx 0.67\%$. Total $\approx 1.0\%$. But the problem says 0.7%. If they only consider the shape effect and ignore the centrifugal? But they talk about effective gravity which includes both.

Maybe the problem is older and uses $a = 6.4 \times 10^6$ m, $g = 9.8$, and $\Omega = 7.3 \times 10^{-5}$, but they compute the difference using the Clairaut formula for a homogeneous Earth: $g_{pole} - g_{eq} = \frac{5}{2} \frac{\Omega^2 a}{g} g$? Wait, no.

Let's derive the variation of effective gravity for a homogeneous fluid Earth (Maclaurin spheroid). The surface gravity on a Maclaurin spheroid (equatorial and polar) involves elliptic integrals. But expansions exist. The difference between polar and equatorial gravity is approximately $g_{pole} - g_{eq} \approx \frac{5}{2} \frac{GM}{a^2} \frac{\Omega^2 a}{g} ...$ Not sure.

Alternatively, consider the *normal gravity formula* for the reference ellipsoid. The International Gravity Formula (1967) is $\gamma(\phi) = 9.780318 (1 + 0.0053024 \sin^2\phi - 0.0000059 \sin^2 2\phi)$. The coefficient $0.0053024$ corresponds to a variation of about $0.53\%$ from equator to pole. The Somigliana formula gives similar. This $0.53\%$ is close to $0.5\%$. Not $0.7\%$.

Let's check if any combination of standard parameters yields $0.0053$ or $0.007$ from $\Omega^2 a / g \approx 0.0035$. Multiply by $3/2$ gives $0.00525$. Multiply by 2 gives $0.007$. So 0.7% is exactly $2 \epsilon$. Why would the coefficient be 2?

Maybe the effective gravity magnitude at latitude $\phi$ is approximated as $g' \approx g (1 - \frac{\Omega^2 a}{g} \cos^2\phi)$. The fractional change from pole to equator is $\epsilon$. But maybe the problem wants the fractional change in the *vertical* component of effective gravity relative to a *spherical* Earth? No, that's the same.

Wait, maybe the problem says the magnitude is about **0.3%** less, but the OCR or user typed 0.7% because 3 and 7 look similar? In some fonts, 3 and 7 are not that similar. 0.7% is less than 1% and is a round number. 0.3% is also a round number. But 0.7% is not a standard result. However, I recall some sources say the centrifugal acceleration is about 0.3% of $g$ at the equator, leading to a 0.3% reduction. The angle is about 0.1°. So the likely pair is 0.3% and 0.1°.

But the prompt explicitly says 0.7%. We need to decide what to compute. The instructions: "Return the COMPLETE corrected solve(): a dict keyed '1'..'N' in the order asked, each {"value": <number>, "unit": "<unit>"}, standard library only. Put all arithmetic in the function."

If we compute the correct physics, we get:
- 1: ~0.0035 (dimensionless)
- 2: ~0.35 (%)
- 3: ~0.1 (°)

But if the auto-grader expects 0.7, we might fail. The user said "Your solve() function failed to run. Fix the bug and return the corrected function." This implies there was a previous attempt that had a runtime error (e.g., the code block didn't even run). The user wants the code fixed, not necessarily the physics corrected. But we should produce correct code that computes the physics.

However, we don't know exactly what the auto-grader expects. It might check for approximate values. Let's see the context: The user says "Your solve() function failed to run." The previous code was likely just the text of the problem or some nonsense. The user wants us to write a solve() function that computes the answer.

Given the problem statement says 0.7%, maybe we should compute the fractional difference as $2 \times \Omega^2 a / g$? Let's see if any textbook uses that.

Wait, there is a result that the *geopotential* difference between equator and pole is related to flattening. But $|g'|$ difference might be derived as follows:

The equipotential surface is defined by $\Phi = const$, where $\Phi = \Phi_g + \Phi_c$. The effective gravity is $g' = |\nabla \Phi|$. At the pole, $\Phi_c = 0$, at equator $\Phi_c = -\frac{1}{2} \Omega^2 a^2$? Wait, the centrifugal potential is $-\frac{1}{2} \Omega^2 \rho^2$. At equator, $\rho = a$, so $\Phi_c = -\frac{1}{2} \Omega^2 a^2$. At pole, $\rho = 0$, $\Phi_c = 0$.

If the surface is an equipotential, then $\Phi_g(pole) = \Phi_g(equator) + \frac{1}{2} \Omega^2 a^2$. The gravitational potential is $-GM/r$. So $-GM/c = -GM/a + \frac{1}{2} \Omega^2 a^2$. For small flattening, $c = a(1-f)$. Then $-GM/[a(1-f)] \approx -GM/a (1+f) = -GM/a - GM f / a$. So $-GM/a - GM f / a = -GM/a + \frac{1}{2} \Omega^2 a^2$. Thus $GM f / a = -\frac{1}{2} \Omega^2 a^2$? Wait, signs: $-GM/c + 0 = -GM/a - \frac{1}{2}\Omega^2 a^2$? Actually, potential of gravity is negative. Let's write:

Gravitational potential (true gravity) at pole: $-GM/c$.

Gravitational potential at equator: $-GM/a$.

Centrifugal potential at equator: $-\frac{1}{2}\Omega^2 a^2$.

Centrifugal potential at pole: $0$.

Equipotential: $-GM/c = -GM/a - \frac{1}{2}\Omega^2 a^2$.

So $-GM/c + GM/a = -\frac{1}{2}\Omega^2 a^2$.

$GM(1/a - 1/c) = -\frac{1}{2}\Omega^2 a^2$.

Since $c < a$, $1/a - 1/c < 0$, so LHS is negative, RHS is negative. Good.

$GM \frac{c-a}{ac} = -\frac{1}{2}\Omega^2 a^2$.

For small $f$, $c-a = -af$, $ac \approx a^2$.

So $GM \frac{-af}{a^2} = -GM f / a = -\frac{1}{2}\Omega^2 a^2$.

Thus $f = \frac{\Omega^2 a^3}{2 GM} = \frac{\Omega^2 a}{2 g}$.

Since $g = GM/a^2$, $GM = g a^2$. So $f = \frac{\Omega^2 a^3}{2 g a^2} = \frac{\Omega^2 a}{2g} = \epsilon/2$.

Wait! This is a classic result for a homogeneous fluid body: the flattening $f \approx \frac{\Omega^2 a}{2g} = \epsilon/2$. But Earth's actual flattening is larger than this because of concentration of mass? Actually, for Earth, $\epsilon \approx 0.0035$, so $\epsilon/2 \approx 0.00175$, but actual $f \approx 0.00336$. So this simple model underestimates flattening. But if we use this model, $f = \epsilon/2 \approx 0.00175$.

Now, what is the effective gravity difference in this model? Effective gravity at pole: $g_{pole}' \approx g_{pole,true} \approx GM/c^2 \approx GM/[a^2(1-f)^2] \approx g(1+2f) = g(1+\epsilon)$. Effective gravity at equator: $g_{eq}' \approx g_{eq,true} - \Omega^2 a \approx GM/a^2 - \Omega^2 a = g(1-\epsilon)$.

Wait, $g_{eq,true} = GM/a^2 = g$. $g_{pole,true} = GM/c^2 \approx g(1+2f) = g(1+\epsilon)$. So effective gravity at pole is $g(1+\epsilon)$. Effective gravity at equator is $g(1-\epsilon)$. Then the fractional difference relative to the pole is $(g(1+\epsilon) - g(1-\epsilon)) / (g(1+\epsilon)) = 2\epsilon / (1+\epsilon) \approx 2\epsilon$.

$2\epsilon \approx 0.0069 \approx 0.7\%$!

Aha! That explains it! In a simple model where the Earth adjusts its shape to be an equipotential, the flattening is $f \approx \epsilon/2$, and the effective gravity at the pole is $g(1+\epsilon)$ while at the equator it's $g(1-\epsilon)$. The difference between pole and equator is $2\epsilon g$, so the fractional difference relative to the pole (or average) is about $2\epsilon \approx 0.7\%$.

Let's verify. In the simple hydrostatic fluid model (Maclaurin spheroid to first order), the surface is an equipotential of the combined gravity and centrifugal potential. The gravitational potential at the pole (distance $c$) and at the equator (distance $a$) differ. For a sphere of radius $a$ (mass $M$), the gravity at the surface is $g = GM/a^2$. If the body is slightly flattened, the gravitational acceleration at the pole is larger because it's closer. The first-order variation of true gravity on the surface of an oblate spheroid is $g_{true}(\phi) \approx g_e (1 + \beta \sin^2\phi)$. For a constant density spheroid, $\beta \approx \frac{5}{2}m - f$, where $m = \epsilon$.

But the simple equipotential argument above gave $f = \epsilon/2$ and $g_{true,pole} \approx g(1+2f) = g(1+\epsilon)$. The effective gravity at the equator includes the centrifugal term: $g_{eff,eq} = g - \Omega^2 a = g(1-\epsilon)$. The effective gravity at the pole is just $g_{true,pole}$ because there is no centrifugal component: $g_{eff,pole} = g(1+\epsilon)$.

Wait, but is $g_{true,pole} = g(1+\epsilon)$ correct? Let's be more careful.

We have the gravitational potential of a uniform sphere (to first order in flattening) or maybe we treat the mass as concentrated at the center (point mass). For a point mass, the gravitational field on the equipotential surface is not constant. But for the purpose of a first-order estimate in introductory atmospheric science, they might approximate the gravitational field as $GM/r^2$ directed toward the center, where $r$ is the local radial distance.

In that approximation, the surface is an equipotential: $-GM/r - \frac{1}{2}\Omega^2 \rho^2 = const$. At equator ($r=a$, $\rho=a$): $-GM/a - \frac{1}{2}\Omega^2 a^2 = const$. At pole ($r=c$, $\rho=0$): $-GM/c = const$. So $-GM/c = -GM/a - \frac{1}{2}\Omega^2 a^2$. Let $c = a(1-f)$. Then $-GM/[a(1-f)] \approx -GM/a (1+f) = -GM/a - GM f/a$. So $-GM/a - GM f/a = -GM/a - \frac{1}{2}\Omega^2 a^2$. Cancel $-GM/a$: $GM f/a = \frac{1}{2}\Omega^2 a^2$. So $f = \frac{\Omega^2 a^3}{2 GM} = \frac{\Omega^2 a}{2g} = \epsilon/2$.

Now effective gravity magnitude at the pole: $g_{eff,pole} \approx GM/c^2 = GM/[a^2(1-f)^2] \approx GM/a^2 (1+2f) = g(1+2f) = g(1+\epsilon)$. (We ignore the effect of shape on the direction of gravity; it still points toward center in this simple point-mass model.)

Effective gravity magnitude at the equator: $g_{eff,eq} \approx GM/a^2 - \Omega^2 a = g - \Omega^2 a = g(1-\epsilon)$.

Difference: $g_{eff,pole} - g_{eff,eq} = g(1+\epsilon) - g(1-\epsilon) = 2g\epsilon$.

Fractional difference relative to pole: $2g\epsilon / (g(1+\epsilon)) \approx 2\epsilon / (1+\epsilon) \approx 2\epsilon (1-\epsilon) \approx 2\epsilon$. Relative to equator: $2g\epsilon / (g(1-\epsilon)) \approx 2\epsilon (1+\epsilon) \approx 2\epsilon$.

So the fractional difference is $2\epsilon \approx 0.0069$, which is about $0.7\%$.

Thus the problem likely expects this simple equipotential argument. In many atmospheric science courses, they introduce the concept of effective gravity and the geoid. They may ask to show that the effective gravity is about 0.7% less at the equator. The derivation uses the equipotential condition to find that $a-c \approx \Omega^2 a^2 / (2g) \times a = \Omega^2 a^3 / (2g)$, i.e., flattening $f = \Omega^2 a / (2g)$. Then compute $g_{pole} \approx g (1 + 2f)$ and $g_{eq} \approx g (1 - \Omega^2 a / g) = g(1 - 2f)$ (since $2f = \epsilon$). Then the difference between pole and equator is $g_{pole} - g_{eq} \approx 4f g = 2\epsilon g$. The fractional difference is $2\epsilon \approx 0.7\%$.

Wait, check: $2f = 2 \times (\epsilon/2) = \epsilon$. So $g_{pole} \approx g(1+\epsilon)$, $g_{eq} \approx g(1-\epsilon)$. The difference is $2\epsilon g$. Fractional difference relative to $g_{pole}$: $2\epsilon / (1+\epsilon) \approx 0.0069 = 0.69\%$.

Alternatively, the problem might just want the student to compute the fractional difference as $(g_{pole} - g_{eq}) / g_{pole}$, where $g_{pole} = g$ (true gravity) and $g_{eq} = g - \Omega^2 a$, and then the answer is 0.35%. But that contradicts the "0.7%" statement. Given the problem explicitly states 0.7%, the intended derivation must be the one including the shape change (flattening) of the Earth due to rotation.

Let's see: The problem starts with evaluating $\Omega^2 a / g$. Then "Show that, at the Earth's surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles". This is a two-step argument:

1. Compute $\epsilon = \Omega^2 a / g \approx 0.0035$.

2. At the equator, the centrifugal acceleration reduces $g'$ by $\Omega^2 a$, which is about $0.35\%$ of $g$. At the pole, $g'$ is unaffected by rotation. But also, because the Earth is an oblate spheroid, the pole is about $21$ km closer to the center than the equator. If the surface is an equipotential, the polar radius $c$ is related to equatorial radius $a$ by $a-c \approx \Omega^2 a^2 / (2g)$ (derived from potential balance). This gives a difference in distance of about $f a = (\epsilon/2) a \approx 0.00175 \times 6371$ km $\approx 11$ km. Wait, that's only 11 km, not 21 km. Actually, the simple fluid model gives flattening $f = \epsilon/2 \approx 0.00175$, which is about half the actual flattening (0.00336). So the shape change in this simplified model is about 11 km, but Earth is actually more flattened. However, the problem might use this simple model.

Then the gravitational attraction itself is stronger at the pole because you're closer: $g_{pole,true} \approx g(1 + 2f) = g(1+\epsilon)$. At the equator, $g_{eq,true} \approx g$. Then effective gravity at equator is $g_{eq,true} - \Omega^2 a = g(1-\epsilon)$. So the difference between pole and equator effective gravity is $g(1+\epsilon) - g(1-\epsilon) = 2\epsilon g$. Fractional difference: $2\epsilon \approx 0.7\%$.

Thus the 0.7% figure arises from combining the centrifugal reduction at the equator ($\epsilon$) with the distance-induced increase at the pole ($\epsilon$). So it's $2\epsilon$.

Let's verify the numbers with standard values:

$\Omega = 7.292 \times 10^{-5}$ s$^{-1}$.
$a = 6.37 \times 10^6$ m.
$g = 9.81$ m/s$^2$.

$\epsilon = (7.292e-5)^2 * 6.37e6 / 9.81 = 5.317e-9 * 6.37e6 / 9.81 = 0.03387 / 9.81 = 0.003453$.

$2\epsilon = 0.006906$.

Percent: $0.6906\% \approx 0.7\%$.

So indeed, if the intended model is $2\epsilon$, the answer is 0.7%.

Now, does the problem mention equipotential or flattening? The problem statement as given doesn't explicitly mention shape. But it's common in atmospheric science to mention that the Earth is an oblate spheroid. The phrase "at the Earth’s surface" might imply the actual Earth's surface (oblate). The effective gravity at the actual Earth's surface is about 0.5% less at the equator. But with the simplified equipotential model using point mass gravity, one gets 0.7%. The problem likely expects the student to approximate the Earth as a sphere of radius $a$ for gravity $g=GM/a^2$, but then note that the surface is an equipotential, so the shape adjusts. Actually, the problem might be from a specific textbook that does this derivation.

Let's try to reconstruct the derivation as would be expected.

Step 1: $\epsilon = \Omega^2 a / g \approx 3.5 \times 10^{-3}$.

Step 2: The effective gravity vector is $\mathbf{g}' = \mathbf{g} + \mathbf{\Omega}\times(\mathbf{\Omega}\times\mathbf{r})$.

At equator: $|\mathbf{g}'|_{eq} \approx g - \Omega^2 a$.

At pole: $|\mathbf{g}'|_{pole} = g$.

Fractional difference: $\Omega^2 a / g \approx 0.35\%$. BUT the problem says 0.7%. So this can't be the intended derivation unless the problem text has a typo.

Alternative Step 2: Consider the geopotential. The surface of the Earth is an equipotential. The equatorial radius is larger than the polar radius. Using the equipotential condition, one finds the difference in radii is $\Delta a = a - c \approx \Omega^2 a^2 / (2g)$? Actually, the difference between equatorial and polar geopotential is zero, so $g (a-c) \approx \frac{1}{2} \Omega^2 a^2$, so $a-c \approx \Omega^2 a^2 / (2g) = \epsilon a / 2 \approx 11$ km. Wait, check: equipotential difference due to gravity change over height $h$ is $gh$. Equipotential difference due to centrifugal potential at equator is $\frac{1}{2}\Omega^2 a^2$. So $g (a-c) = \frac{1}{2}\Omega^2 a^2$, giving $a-c = \Omega^2 a^2 / (2g) = \epsilon a / 2$. With $\epsilon \approx 0.0035$, $a-c \approx 0.00175 \times 6371 \approx 11.1$ km. This is the simple model flattening.

Then gravity at pole: $g_{pole} \approx GM/c^2 = g (a/c)^2 = g (1/(1-f))^2 \approx g (1+2f) \approx g(1+\epsilon)$.

Effective gravity at equator: $g_{eq} \approx g - \Omega^2 a = g(1-\epsilon)$.

Then the difference: $g_{pole} - g_{eq} \approx g(1+\epsilon) - g(1-\epsilon) = 2\epsilon g$.

Fractional difference: $2\epsilon \approx 0.7\%$.

This derivation is physically consistent (albeit simplified). So the problem likely expects this.

But maybe the problem is from a source where they assume the Earth is a sphere and simply ask to show that the effective gravity is about **0.3%** less. The user wrote 0.7%. Could it be that the user misread 0.3% as 0.7%? If the original text says "0.3%", then our correct answer should be 0.3%. Let's examine: In some fonts, 3 can look like 7 if the top is flat? Not really. But OCR could misread 3 as 7. However, it's more likely that the text says 0.3% (or 0.35%) and the user made an error. But we can't know.

Given that the problem explicitly says 0.7%, and we have a plausible physical derivation that yields 0.7% (by including the shape effect), and the angle is 0.1°, which matches $\epsilon/2$ rad, it's likely the intended answer uses $2\epsilon$ for the percent difference. This is a known classic problem.

Wait, but if the Earth is an oblate spheroid, the maximum angle between $g'$ and radial direction is about 0.1°, which we computed from $\tan\alpha \approx \epsilon/2$. That derivation used a spherical Earth (radius $a$). Does the angle change if Earth is oblate? The angle is due to the tilt of the equipotential surface. The angle between the equipotential normal (effective gravity) and the geocentric radial direction is given by $\tan\alpha \approx \frac{\Omega^2 a}{2g} \sin 2\phi$ (for a sphere). For an oblate Earth, the angle is similar but slightly modified. However, the problem asks for a simple estimate, which yields 0.1°.

So the plan: The `solve()` function should compute:

1. `dimensionless = Omega**2 * a / g` (value, unit "dimensionless").

2. `percent_diff = 2 * dimensionless * 100`? Or `( (g_pole - g_eq) / g_pole ) * 100` where `g_pole = g * (1 + dimensionless)` and `g_eq = g * (1 - dimensionless)`. That gives `percent_diff = 2 * dimensionless / (1 + dimensionless) * 100`. This is about `(2 * 0.003453 / 1.003453) * 100 = (0.006906 / 1.003453) * 100 = 0.688%`. Rounding to one sig fig gives 0.7%.

Alternatively, if they intended just `dimensionless * 100`, they'd get 0.35%. But the problem says 0.7%. So we need to incorporate the factor of 2 and the shape effect.

Let's compute exactly:

Given Omega, a, g.

epsilon = Omega**2 * a / g

g_eq = g * (1 - epsilon)
g_pole = g * (1 + epsilon)  # assumes flattening f = epsilon/2 from equipotential

fractional_diff = (g_pole - g_eq) / g_pole  # effective gravity at equator is less than at poles

percent_diff = fractional_diff * 100

This yields approx 0.69%.

Let's verify:

Omega = 7.292e-5
a = 6.371e6
g = 9.81

epsilon = (7.292e-5)**2 * 6.371e6 / 9.81 = 0.003456

g_eq = 9.81 * (1 - 0.003456) = 9.7761
g_pole = 9.81 * (1 + 0.003456) = 9.8439

diff = 9.8439 - 9.7761 = 0.0678
fractional = 0.0678 / 9.8439 = 0.006888 = 0.6888%

If the grader checks for 0.7 (within some tolerance), this is good.

But if the grader expects 0.35, we'll be off by factor of 2. How to decide? The problem says 0.7%. So we should output something close to 0.7. The simplest is to compute `2 * epsilon * 100` or the full formula.

For the angle:

tan(alpha) = (Omega**2 * a * sin(phi) * cos(phi)) / (g - Omega**2 * a * cos**2(phi))

Maximize over phi. The maximum occurs at phi = 45 degrees (pi/4) for the approximate formula and also very close for the exact formula.

Compute tan_alpha_max = (Omega**2 * a * 0.5) / (g - Omega**2 * a * 0.5) = (epsilon * g * 0.5) / (g - epsilon * g * 0.5) = (epsilon/2) / (1 - epsilon/2).

alpha_max_rad = math.atan(tan_alpha_max)

alpha_max_deg = math.degrees(alpha_max_rad)

Since epsilon is small, alpha_max_deg ≈ (epsilon/2) * (180/pi) ≈ (0.003456/2) * 57.2958 = 0.001728 * 57.2958 = 0.0990°. Using the exact arctan gives slightly different but still about 0.099°. So unit is degrees.

Alternatively, we can approximate alpha_max_deg ≈ math.degrees(epsilon / 2). Which is 0.0991°. That's fine.

Now, the first quantity: dimensionless parameter. It is dimensionless. So unit "1" or "dimensionless". The instructions say standard unit strings. Maybe "dimensionless" is fine.

Second quantity: percent difference. The problem says "about 0.7% less". So we could return the value in percent, e.g., 0.69, unit "%". Or we could return the fractional difference 0.0069, unit "1" (dimensionless). The phrasing "0.7% less" strongly suggests the unit is "%". So I think unit should be "%". The value should be around 0.7.

Third quantity: angle. Unit "°" or "degrees". The value around 0.1.

Let's think about parameter defaults. All given values should be function parameters with defaults.

Parameters:
- Omega: Earth's angular velocity. Default: 7.292e-5 (rad/s).
- a: Earth's radius. Default: 6.371e6 (m).
- g: gravitational acceleration. Default: 9.81 (m/s^2).
- Maybe also phi_max for latitude. But we can compute it.

The function should return a dict:

{
  "1": {"value": epsilon, "unit": "dimensionless"},
  "2": {"value": percent_diff, "unit": "%"},
  "3": {"value": alpha_max_deg, "unit": "°"}
}

We need to be careful with the key ordering: "1", "2", "3" in order asked.

Now, let's consider the variability in expected answer for "2". If we compute percent_diff = (g_pole - g_eq) / g_pole * 100 with g_pole = g*(1+epsilon) and g_eq = g*(1-epsilon), we get approx 0.688%. Rounded to one decimal place: 0.7%. If we compute just epsilon*100, we get 0.345%. Which one is more likely?

Let's read the problem again: "Evaluate the dimensionless parameter $\Omega ^ { 2 } a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

The phrase "about 0.7%" suggests that the parameter $\Omega^2 a / g$ is about $3.5 \times 10^{-3}$, and they might want you to note that the effective gravity at the equator is reduced by this amount due to rotation, but also increased at the pole due to oblateness (flattening). But the problem statement doesn't mention oblateness explicitly. However, many atmospheric science problems assume the student knows Earth is an oblate spheroid and $g$ is larger at poles. Actually, standard effective gravity values are $g_{eq} \approx 9.78$, $g_{pole} \approx 9.83$, difference $\approx 0.05$, which is $\sim 0.5\%$. Not 0.7%.

But if we compute using simple point-mass plus equipotential, we get 0.69%. This is the only simple derivation that yields exactly 0.7% using only $\Omega$, $a$, and $g$. Let's step through it:

1. Dimensionless parameter: $\epsilon = \Omega^2 a / g \approx 3.5 \times 10^{-3}$.

2. Earth's surface is an equipotential. Difference in radii: $a - c \approx \epsilon a / 2$. (Not needed for $g'$ directly, but used to get $g_{pole}$).

3. True gravity at pole: $g_{pole} \approx g (a/c)^2 \approx g(1+\epsilon)$.

4. Effective gravity at equator: $g_{eq}' = g - \Omega^2 a = g(1-\epsilon)$.

5. Difference: $g_{pole}' - g_{eq}' = 2g\epsilon$. Fraction: $2\epsilon / (1+\epsilon) \approx 0.69\%$.

This matches 0.7% perfectly. So I think this is the intended solution.

Alternatively, if the problem assumed a spherical Earth, the answer would be 0.35%, and the problem statement would say 0.3% or 0.4%. Since it says 0.7%, the factor of 2 must be present. I'll implement the calculation accordingly.

However, we need to consider if the problem might use a different formula for $g_{pole}$. In step 3, we used $g_{pole} \approx g(1+\epsilon)$ because $c = a(1-f)$ with $f=\epsilon/2$, so $g_{pole} = GM/c^2 = g/(1-f)^2 \approx g(1+2f) = g(1+\epsilon)$. That's correct for a point-mass approximation.

If we compute it exactly with $c = a - \Delta r$, where $\Delta r = \Omega^2 a^2 / (2g)$ from equipotential, then $c = a - \Omega^2 a^2 / (2g)$. Then $g_{pole} = GM/c^2 = g a^2 / c^2 = g / (1 - \Delta r / a)^2 = g / (1 - \epsilon/2)^2 \approx g (1 + \epsilon + 3\epsilon^2/4 ...)$. To first order, $g_{pole} \approx g(1+\epsilon)$. Same.

Then $g_{eq}' = g - \Omega^2 a = g(1-\epsilon)$.

So fractional difference relative to pole: $(g(1+\epsilon) - g(1-\epsilon)) / (g(1+\epsilon)) = 2\epsilon / (1+\epsilon)$.

Let's compute numeric: $2 * 0.003453 / (1.003453) = 0.006882 / 1.003453 = 0.006858$. In percent: 0.6858%. So about 0.7%.

If we compute relative to the average $g_{avg} = (g_{pole} + g_{eq})/2 = g$, then fractional difference is $2\epsilon g / g = 2\epsilon = 0.0069 = 0.69\%$. Slightly different. Both round to 0.7%.

So for the function, I'll compute:

- `Omega` default `7.2921e-5` (sidereal angular velocity of Earth).
- `a` default `6.371e6` (m).
- `g` default `9.81` (m/s^2).

Compute `eps = Omega**2 * a / g`.

Result 1: `eps`, unit "dimensionless".

For result 2: Let's compute `g_eq = g * (1 - eps)` and `g_pole = g / (1 - eps/2)**2` (approximate using equipotential shape). But that might be overcomplicating. Since the problem is likely to accept a simple estimate, we can compute:

`g_pole_eff = g * (1 + eps)` (approximation to first order).
`g_eq_eff = g * (1 - eps)`.
`frac_diff = (g_pole_eff - g_eq_eff) / g_pole_eff`.
`percent = frac_diff * 100`.

Or simply `percent = (2 * eps) / (1 + eps) * 100`.

Let's compute with the exact equipotential polar radius:

$c = a - \Omega**2 * a**2 / (2 * g) = a * (1 - eps/2)$.

$g_{pole} = GM / c**2 = (g * a**2) / c**2 = g / (1 - eps/2)**2$.

$g_{eq} = g - \Omega**2 * a = g * (1 - eps)$.

Then `frac_diff = (g_pole - g_eq) / g_pole`.

`percent = frac_diff * 100`.

This is exact within the point-mass/equipotential model. Let's compute:

eps = 0.003453

c_over_a = 1 - eps/2 = 1 - 0.0017265 = 0.9982735

g_pole = 9.81 / (0.9982735)**2 = 9.81 / 0.996549 = 9.8440

g_eq = 9.81 * (1 - 0.003453) = 9.7761

diff = 0.0679

frac = 0.0679 / 9.8440 = 0.006898

percent = 0.6898%

So 0.69%. That's about 0.7%.

Using first-order approximation g_pole = g*(1+eps) = 9.8439, difference is negligibly small.

So we can either use the exact point-mass equipotential or the first-order. The answer will be around 0.69%. I think using the exact point-mass equipotential is more robust and less arbitrary. It's still simple:

- `c = a - Omega**2 * a**2 / (2 * g)` (polar radius in equipotential model).
- `g_pole = g * (a / c)**2` (gravity at pole).
- `g_eq = g - Omega**2 * a` (effective gravity at equator).
- `frac_diff = (g_pole - g_eq) / g_pole`.
- `percent_diff = frac_diff * 100`.

But wait: if `c = a - Omega**2 * a**2 / (2g)`, then `a/c = 1 / (1 - eps/2)`. Then `g_pole = g / (1 - eps/2)^2`. That's fine.

Alternatively, some textbooks approximate $g_{pole} \approx g (1 + \epsilon)$. Let's check the difference:

Exact point-mass: `g_pole = g / (1 - eps/2)^2`.
Approx: `g_pole = g * (1 + eps)`.
For eps=0.00345, `1/(1-eps/2)^2 = 1 / (0.99827)^2 = 1 / 0.99655 = 1.00346`.
`(1+eps) = 1.00345`.
Difference is in the 4th decimal place. So both are fine.

I think I'll compute it directly: `g_pole = g * (1 + eps)` and `g_eq = g * (1 - eps)`. Then `percent_diff = (g_pole - g_eq) / g_pole * 100`.

This is simple and clearly uses `eps` twice.

But why is $g_{pole} = g(1+\epsilon)$? We should explain in comments.

Now for the angle:

The tangent of the angle between $\mathbf{g}'$ and radial direction (pointing towards center) is given by the ratio of the tangential component of centrifugal acceleration to the radial component of effective gravity (which is approximately $g$). More precisely:

$\tan \alpha = \frac{\Omega^2 a \cos\phi \sin\phi}{g - \Omega^2 a \cos^2\phi}$.

Maximize over $\phi$. Setting derivative to zero, the maximum is at $\phi = 45^\circ$ (to good approximation). So compute:

$\tan \alpha_{max} = \frac{\Omega^2 a / 2}{g - \Omega^2 a / 2} = \frac{\epsilon/2}{1 - \epsilon/2}$.

Then $\alpha_{max} = \arctan(\tan \alpha_{max})$ in degrees.

Compute: `tan_alpha = (Omega**2 * a * 0.5) / (g - Omega**2 * a * 0.5)`.
`alpha_deg = math.degrees(math.atan(tan_alpha))`.

Alternatively, approximate `alpha_deg ≈ math.degrees(epsilon / 2)`. Using the exact `atan` is better.

Let's check the value:

`tan_alpha = 0.5 * 0.03387 / (9.81 - 0.5*0.03387) = 0.016935 / (9.81 - 0.016935) = 0.016935 / 9.793065 = 0.0017293`.
`atan(0.0017293) = 0.00172929` rad.
`degrees = 0.00172929 * 180/pi = 0.09907°`.

If we use `epsilon/2` in radians: `0.003453/2 = 0.0017265` rad. `degrees = 0.0989°`. Very close.

So either is fine. I'll use the exact atan formula.

One more nuance: The problem says "vector pointing towards the centre of the Earth". The direction of $\mathbf{g}'$ deviates from the radial inward direction. The angle is small. The formula we used gives the angle between $\mathbf{g}'$ and the local vertical (which for a sphere is radial). For the equipotential model, the local vertical is defined by $\mathbf{g}'$. The vector pointing toward the center is radial. The angle between them is what we computed. So it's correct.

Now, what are the default parameters to use? The problem says "for the Earth". Standard values:
- Earth's rotation rate $\Omega = 7.292 \times 10^{-5}$ rad/s.
- Earth's radius $a = 6.37 \times 10^6$ m (or 6.371 x 10^6).
- Gravitational acceleration $g = 9.81$ m/s$^2$.

I should set these as defaults.

Now, we need to format the code. The previous code failed to run because it was not valid Python (the user wrote "We need " in the code block). So we need to provide a clean function.

The user says: "Return the COMPLETE corrected solve(): a dict keyed "1".."N" in the order asked, each {"value": <number>, "unit": "<unit>"}, standard library only. Put all arithmetic in the function; give the corrected solve() in a single ```python code block."

So we output:

```python
import math

def solve(Omega=7.292e-5, a=6.371e6, g=9.81):
    # dimensionless parameter
    eps = Omega**2 * a / g
    
    # effective gravity at equator (centrifugal reduces it)
    g_eq = g * (1 - eps)
    
    # effective gravity at pole: closer to centre by equipotential adjustment
    # flattening ~ eps/2 for a simple fluid model, so polar radius c = a*(1 - eps/2)
    # gravity scales as 1/r^2 -> g_pole = g / (1 - eps/2)**2
    # first-order approx: g_pole ≈ g * (1 + eps)
    g_pole = g / (1 - eps/2)**2
    
    frac_diff = (g_pole - g_eq) / g_pole
    percent_diff = frac_diff * 100
    
    # max angle between g' and radial direction
    # tan(alpha) = (Omega^2 a sin(phi)cos(phi)) / (g - Omega^2 a cos^2(phi))
    # max at phi = 45°
    tan_alpha = (Omega**2 * a * 0.5) / (g - Omega**2 * a * 0.5)
    alpha_deg = math.degrees(math.atan(tan_alpha))
    
    return {
        "1": {"value": eps, "unit": "dimensionless"},
        "2": {"value": percent_diff, "unit": "%"},
        "3": {"value": alpha_deg, "unit": "°"},
    }
```

But is this robust enough? Let's compute with defaults:

eps = (7.292e-5)^2 * 6.371e6 / 9.81 = 5.317e-9 * 6.371e6 / 9.81 = 0.03387 / 9.81 = 0.0034529

g_eq = 9.81 * (1 - 0.0034529) = 9.7761

c_over_a = 1 - eps/2 = 0.9982735

g_pole = 9.81 / (0.9982735)^2 = 9.8440

frac_diff = (9.8440 - 9.7761) / 9.8440 = 0.0679 / 9.8440 = 0.006898

percent_diff = 0.6898

alpha_deg = 0.0991

So the values are:
1: 0.00345
2: 0.69 %
3: 0.099 °

If the grader expects 0.7 for #2, 0.6898 is fine (within tolerance). If it expects 0.35, we might be wrong. But given the problem text says 0.7%, I think this is correct.

Wait, what if the problem doesn't expect the equipotential model, but simply wants `2 * eps * 100` because they consider the percent difference relative to the *average* gravity? Let's see:

Average effective gravity = (g_pole + g_eq)/2 = (g(1+eps) + g(1-eps))/2 = g.

Difference from average at equator = g - g(1-eps) = eps*g = 0.00345*g. That's 0.345% less than average. At pole, it's 0.345% more than average. The difference between pole and equator relative to average is 2*eps*g / g = 2*eps = 0.69%. But relative to the pole it's 0.69%/(1+eps), relative to equator it's 0.69%/(1-eps). The phrase "less at the equator than at the poles" means relative to the polar value: (pole - eq) / pole = 0.69%.

If the student uses the simple approximation $g_{pole} \approx g$, $g_{eq} = g - \Omega^2 a$, they'd get 0.34%. The problem wouldn't say 0.7%.

Another possibility: The problem is from a source (e.g., a specific edition of a textbook) where they use $g \approx 10$ m/s$^2$, $a \approx 6.4 \times 10^6$, $\Omega \approx 7.3 \times 10^{-5}$. Then:

eps = 0.0338 / 10 = 0.00338.

If they compute percent difference as $2 \times eps \times 100 = 0.676\% \approx 0.7\%$. Yes.

So it's clearly $2\epsilon$.

Let's check if any other simple derivation gives 0.7%. We already found the equipotential model gives $2\epsilon$.

Thus I'll proceed with computing percent_diff using the equipotential argument.

One subtlety: The problem says "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth." This is literally epsilon. Then "Show that ... the magnitude ... is about 0.7% less at the equator than at the poles". The show that part likely expects the student to use the equipotential argument. So computing $2\epsilon$ as a percent is the intended arithmetic.

Let's also think about the unit for angle. The problem uses $0.1^\circ$. So unit "°" is appropriate.

We need to ensure standard library only. `math` is fine.

I should put all arithmetic in the function as requested.

One more thing: The previous code may have had a syntax error because it started with `We need `. We need to output just the code block.

Let's write the final code.

```python
import math

def solve(Omega=7.292e-5, a=6.371e6, g=9.81):
    # Dimensionless parameter Omega^2 * a / g
    eps = Omega**2 * a / g

    # Effective gravity at equator: reduced by centrifugal term
    g_eq = g - Omega**2 * a  # = g * (1 - eps)

    # For a rotating fluid body in hydrostatic equilibrium the polar radius is smaller.
    # From equipotential: g * (a - c) ≈ 0.5 * Omega^2 * a^2  =>  c = a * (1 - eps/2)
    # Gravity scales as 1/r^2, so at the pole g_pole ≈ g / (1 - eps/2)**2
    c = a * (1 - eps / 2)
    g_pole = g * (a / c)**2

    # Fractional difference (equator relative to pole)
    frac_diff = (g_pole - g_eq) / g_pole
    percent_diff = frac_diff * 100

    # Angle between g' and radial direction
    # tan(alpha) = (Omega^2 * a * cos(phi) * sin(phi)) / (g - Omega^2 * a * cos^2(phi))
    # Maximum occurs near phi = 45°.
    phi = math.radians(45.0)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    tan_alpha = (Omega**2 * a * cos_phi * sin_phi) / (g - Omega**2 * a * cos_phi**2)
    alpha_deg = math.degrees(math.atan(tan_alpha))

    return {
        "1": {"value": eps, "unit": "dimensionless"},
        "2": {"value": percent_diff, "unit": "%"},
        "3": {"value": alpha_deg, "unit": "°"},
    }
```

Wait, is `phi = math.radians(45.0)` exact enough? The derivative of tan(alpha) wrt phi is zero at exactly 45° for the approximate denominator $g$ constant. For the exact denominator, the maximum is slightly shifted but negligibly. Evaluating at 45° gives a value extremely close to the true maximum. For the given small epsilon, the difference is negligible. Let's verify:

Let $f(\phi) = \frac{\epsilon g \cos\phi \sin\phi}{g - \epsilon g \cos^2\phi} = \frac{\epsilon \sin\phi \cos\phi}{1 - \epsilon \cos^2\phi}$.

Derivative wrt $\phi$:

$f' = \epsilon \frac{(\cos^2\phi - \sin^2\phi)(1 - \epsilon \cos^2\phi) - \sin\phi\cos\phi (2\epsilon \cos\phi \sin\phi)}{(1-\epsilon\cos^2\phi)^2}$.

Set numerator = 0:

$(\cos^2\phi - \sin^2\phi)(1 - \epsilon \cos^2\phi) - 2\epsilon \sin^2\phi \cos^2\phi = 0$.

$\cos 2\phi (1 - \epsilon \cos^2\phi) - \frac{\epsilon}{2} \sin^2 2\phi = 0$.

For small $\epsilon$, the solution is close to $45^\circ$. Let's compute numerically:

At $\phi = 45°$, $\cos^2\phi = 0.5$, $\sin^2\phi = 0.5$, $\cos 2\phi = 0$, $\sin^2 2\phi = 1$.

Numerator = $0 * (1 - 0.5\epsilon) - 0.5\epsilon * 1 = -0.5\epsilon$.

So at $\phi=45°$, derivative is negative. That means the maximum is slightly less than $45°$. Let's solve for small $\delta$ where $\phi = 45° - \delta$.

$\cos 2\phi = \cos(90° - 2\delta) = \sin 2\delta \approx 2\delta$.
$\sin^2 2\phi = \sin^2(90° - 2\delta) = \cos^2 2\delta \approx 1$.

Numerator: $2\delta (1 - 0.5\epsilon) - 0.5\epsilon \approx 0$.
$2\delta \approx 0.5\epsilon / (1 - 0.5\epsilon) \approx 0.5\epsilon$.
$\delta \approx 0.25\epsilon$ radians.

$\epsilon = 0.00345$, so $\delta \approx 0.00086$ rad $\approx 0.049°$.

So the maximum is at about $45° - 0.05° = 44.95°$. The difference in $\tan\alpha$ is negligible. Let's compute $f(45°)$ vs $f(44.95°)$.

$f(\phi) = \frac{0.5\epsilon}{1 - 0.5\epsilon}$ at $45°$.

At $\phi = 44.95°$, $\cos^2\phi \approx (\cos 44.95°)^2 \approx (0.7071 - small)^2 \approx 0.5 - small$.

Let's just compute numerically. It's fine to evaluate at 45°.

Alternatively, we could do a quick numeric search for the maximum within the function. Since standard library only, we can just sample many points or use calculus. But that's overkill. Using 45° is standard and yields a value that rounds to 0.1°.

I could also compute the maximum analytically by solving for phi where derivative is zero. But it's a bit messy. Simpler to just evaluate at 45°.

Wait, let's consider if the auto-grader expects a specific formula. Maybe they just expect `alpha = math.degrees(epsilon / 2)`. Let's see what that gives: `math.degrees(0.003453 / 2) = 0.0989°`. The exact arctan formula gave `0.0991°`. Both round to `0.1°`.

I think the exact `atan` of the expression evaluated at 45° is safest.

Another nuance: The problem might want the value of the dimensionless parameter to be around `0.0035` or `3.5e-3`. The exact value with defaults is `0.003453`. Good.

Now, about the second result: Should we compute it as `2 * eps * 100` exactly? If we do the equipotential `g_pole = g / (1 - eps/2)**2` and `g_eq = g * (1 - eps)`, we get `percent_diff = (g_pole - g_eq) / g_pole * 100`. This is physically motivated and gives ~0.69%. If the grader checks that the code produces approximately 0.7 (within maybe 0.1), it's fine. If it checks for exact formula matching, who knows. But this is the most defensible.

Let's double-check the derivation of `c = a * (1 - eps/2)`.

Equipotential condition: Gravitational potential + centrifugal potential = const.

At equator: $-GM/a - 0.5 \Omega^2 a^2 = const$.
At pole: $-GM/c = const$.

Set equal: $-GM/c = -GM/a - 0.5 \Omega^2 a^2$.
$GM(1/a - 1/c) = -0.5 \Omega^2 a^2$.
$GM(c - a)/(ac) = -0.5 \Omega^2 a^2$.
Since $c < a$, $c
~~~~

#### `kimi-k2.6-reasoning` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/kimi-k2.6-reasoning.run3.json` → `4.5` · `num_attempts` = 4 · 4 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034545704582006915` | ✓ |
| `2` | `0.7` | `0.34545704582006914` | ✗ |
| `3` | `0.1` | `0.09896605522060319` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

RESPONSE (verbatim, untruncated):

~~~~
We need to write a Python solve() function that solves the atmospheric science problem. Let's parse the problem carefully.

The problem statement: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth's surface, the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles, and the maximum angle between $\mathbf{g}'$ and a vector pointing towards the centre of the Earth is about $0.1^\circ$."

We need to compute three things? The problem says "Evaluate the dimensionless parameter ... Show that ... about 0.7% less ... and the maximum angle ... is about 0.1°."

We need to return a dict with entries "1", "2", ..., keyed in the order asked. The quantities asked are likely:

1. The dimensionless parameter $\Omega^2 a / g$.
2. The percent difference (or fractional difference) in $|g'|$ between equator and poles: maybe the value is about 0.7% (i.e., 0.007 or 0.7?). The problem says "about 0.7% less". So likely return 0.7 (percent) or 0.007 (fraction). We need to see typical phrasing: "about 0.7% less". Usually they'd want the percentage: 0.7 (unit: "%") or the fractional difference: 0.007 (dimensionless). Let's read carefully: "Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles". So the quantity asked is the percent reduction: 0.7%. So value should be about 0.7, unit "%". Or maybe they want the fractional difference: ~0.0035? Wait, let's calculate.

Effective gravity g' = g - Ω^2 a cos^2 φ (for magnitude? Actually effective gravity vector is combination of true gravity g (pointing to center) and centrifugal acceleration Ω^2 r outward perpendicular to rotation axis. At latitude φ, the centrifugal acceleration has a component radially outward from Earth's axis: magnitude Ω^2 a cos φ. Its direction is perpendicular to the axis, pointing away from it. The radial (toward center) component is -Ω^2 a cos^2 φ (outward), and the component orthogonal to radial (southward) is Ω^2 a cos φ sin φ.

Thus magnitude of g' is approximately sqrt( (g - Ω^2 a cos^2 φ)^2 + (Ω^2 a cos φ sin φ)^2 ). For small Ω^2 a / g, the magnitude is approximately g - Ω^2 a cos^2 φ + ... Actually the deviation from g is dominated by the radial component. Let's compute exactly:

|g'|^2 = g^2 + (Ω^2 a)^2 cos^2 φ - 2 g Ω^2 a cos^2 φ? Wait, need to compute vector sum.

Define coordinates: local vertical (toward center) is -r̂. True gravity vector: g_vec = -g r̂. Centrifugal acceleration: Ω^2 a cos φ outward from axis. In local coordinates, the centrifugal acceleration has components: radial outward component: Ω^2 a cos^2 φ (since angle between centrifugal direction and local horizontal? Let's derive.)

At latitude φ, the position vector from Earth's center makes angle φ with the equatorial plane. The rotation axis is along z. The centrifugal acceleration is horizontal (perpendicular to axis) and outward: magnitude Ω^2 R where R = a cos φ is distance from axis. Its direction is along the projection of the position vector onto the equatorial plane, i.e., away from axis. In a local coordinate system: radial (r̂ outward from center), northward (n̂), eastward (ê). The direction away from axis lies in the meridional plane, pointing outward from axis. The angle between the outward radial direction r̂ and the outward-from-axis direction is φ (since r̂ is at angle φ from equatorial plane, while the outward-from-axis direction is in equatorial plane? Let's be precise.)

Let's use spherical coordinates: r̂ points from Earth's center to the point. The rotation axis is ẑ. The centrifugal acceleration vector is Ω^2 ρ ρ̂, where ρ is the distance from axis and ρ̂ is the unit vector perpendicular to axis, pointing away from it. In terms of spherical unit vectors, ρ̂ = cos φ r̂ - sin φ n̂? Let's verify.

At latitude φ, the unit vector r̂ has components: (cos φ cos λ, cos φ sin λ, sin φ) in Cartesian (x,y,z) where λ is longitude. The unit vector pointing north n̂ = (-sin φ cos λ, -sin φ sin λ, cos φ). The unit vector pointing east ê = (-sin λ, cos λ, 0). The unit vector away from axis (cylindrical radial) ŝ = (cos λ, sin λ, 0). Note that ŝ = cos φ r̂ - sin φ n̂. Let's check: cos φ r̂ = (cos^2 φ cos λ, cos^2 φ sin λ, cos φ sin φ). - sin φ n̂ = (sin^2 φ cos λ, sin^2 φ sin λ, - sin φ cos φ). Sum = (cos λ, sin λ, 0) = ŝ. Yes.

Thus centrifugal acceleration: f = Ω^2 a cos φ ŝ = Ω^2 a cos φ (cos φ r̂ - sin φ n̂) = Ω^2 a cos^2 φ r̂ - Ω^2 a cos φ sin φ n̂.

Note: r̂ points outward from Earth's center. The true gravity points inward: g_vec = -g r̂. So effective gravity g' = g_vec + f = (-g + Ω^2 a cos^2 φ) r̂ - Ω^2 a cos φ sin φ n̂.

Thus the components are:
- radial (outward): -g + Ω^2 a cos^2 φ
- northward: -Ω^2 a cos φ sin φ (i.e., toward south)

Magnitude: |g'| = sqrt( (g - Ω^2 a cos^2 φ)^2 + (Ω^2 a cos φ sin φ)^2 ). Since the northward component is small.

Expand: |g'|^2 = g^2 - 2 g Ω^2 a cos^2 φ + (Ω^2 a)^2 cos^4 φ + (Ω^2 a)^2 cos^2 φ sin^2 φ
= g^2 - 2 g Ω^2 a cos^2 φ + (Ω^2 a)^2 cos^2 φ (cos^2 φ + sin^2 φ)
= g^2 - 2 g Ω^2 a cos^2 φ + (Ω^2 a)^2 cos^2 φ.

So |g'|^2 = g^2 - 2 g Ω^2 a cos^2 φ + (Ω^2 a)^2 cos^2 φ.

Since Ω^2 a << g, the last term is second order. To first order, |g'| ≈ g - Ω^2 a cos^2 φ. The exact magnitude differs slightly.

At equator φ=0: |g'|_eq = sqrt( (g - Ω^2 a)^2 )? Actually cos φ =1, so |g'|^2 = g^2 - 2 g Ω^2 a + (Ω^2 a)^2 = (g - Ω^2 a)^2. So magnitude = g - Ω^2 a. Exactly! Wait, check northward component: at equator, sin φ=0, so no northward component. So g' is purely radial inward but reduced by Ω^2 a. So yes, magnitude = g - Ω^2 a.

At pole φ=π/2: cos φ=0, so |g'| = g.

So the fractional difference (equator vs poles): (g - |g'|_eq)/g = (g - (g - Ω^2 a))/g = Ω^2 a / g. Wait that's the dimensionless parameter. But the problem says "about 0.7% less at the equator than at the poles". Let's compute Ω^2 a / g for Earth.

Earth's rotation rate: Ω = 2π / (sidereal day) ≈ 7.2921159e-5 rad/s. Earth's radius a ≈ 6.371e6 m. g ≈ 9.81 m/s^2.

Compute Ω^2 a = (7.2921e-5)^2 * 6.371e6. (7.2921e-5)^2 ≈ 5.317e-9. Times 6.371e6 ≈ 0.03387 m/s^2. Divide by 9.81 ≈ 0.003452. That's about 0.345%, not 0.7%. Hmm.

Wait, maybe a is equatorial radius? The problem uses 'a' as Earth's radius. The dimensionless parameter is Ω^2 a / g. If a = 6378 km, then Ω^2 a = 0.0339. Dividing by g ~9.8 gives 0.00346 = 0.346%. But the problem says effective gravity is about 0.7% less at equator than poles. That is roughly double the dimensionless parameter. Why? Because the effective gravity vector is not just the radial component; the magnitude is reduced by about Ω^2 a / g (which is 0.35%). Wait, but the problem says 0.7%. Let's check standard values.

I recall that the measured difference between polar gravity and equatorial gravity is about 0.5% due to both rotation (centrifugal) and Earth's oblateness. The centrifugal effect alone is about 0.35% (i.e., 0.0034). However, the problem might be approximating g' magnitude at the equator as g - Ω^2 a (so reduction is Ω^2 a/g ≈ 0.0034). 0.34% is not 0.7%. So why does the problem say 0.7%? Let's double-check the standard numbers.

Wait, maybe the problem uses a different g? Or uses the angular speed squared times radius divided by g, and maybe the parameter is ~0.0034, but the percent reduction in |g'| is not exactly Ω^2 a / g because the effective gravity vector's magnitude at the equator is sqrt(g^2 + (Ω^2 a)^2)? No, at equator it's purely radial: g' = g - Ω^2 a. So reduction is exactly Ω^2 a / g.

Wait, maybe the problem expects using a = 6400 km and g = 10 m/s^2. Then Ω^2 a = (7.29e-5)^2 * 6.4e6 = 5.31e-9 * 6.4e6 = 0.0340. /10 = 0.0034 = 0.34%. Still not 0.7%. Hmm.

Alternatively, perhaps the problem defines g' effective gravity including the fact that Earth is an oblate spheroid? But the problem statement seems to be a simple physics problem: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°." Maybe the 0.7% comes from taking the difference in magnitudes: at equator |g'| = sqrt(g^2 + (Ω^2 a)^2 - 2g Ω^2 a) = g - Ω^2 a. At poles, |g'| = g. The fractional reduction is Ω^2 a / g. So about 0.34%. But the text says 0.7%. Let's check if maybe the problem uses a day of 24 hours exactly ( solar day?), and a = 6.4e6 m, g = 9.8 m/s^2.

Ω = 2π / (24*3600) = 7.2722e-5 rad/s. (Ω^2) = 5.288e-9. Times a = 6.4e6 => 0.03384. /9.8 = 0.003453 = 0.345%. Still half of 0.7%.

Wait, maybe the effective gravity is reduced by about 0.7% because they consider the full oblate Earth and the fact that the radius at equator is larger? Or maybe the problem is from a textbook that approximates the difference as 2 * (Ω^2 a / g)? Let's think.

Alternatively, perhaps the problem asks to show that the magnitude of effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle is about 0.1°. The 0.7% might be a known approximate value for the total variation of g from pole to equator (including oblateness). But the problem statement seems to be about the effect of Earth's rotation only. However, maybe the problem is from "Atmospheric Science: An Introductory Survey" or "Atmospheric Science for..." where they ask to evaluate rotation effect and compare with observed variation? Or maybe the problem includes the fact that because of rotation, the Earth is bulged, so the radius at equator is larger, which also reduces gravity. But the problem statement doesn't mention Earth's shape. It just says "at the Earth's surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". That suggests that the effective gravity (vector sum of true gravity and centrifugal) is ~0.7% less at equator. But as we saw, the centrifugal reduction alone is ~0.34%. To get 0.7%, you need to factor in that the equatorial radius is about 21 km larger than polar radius. Since g ∝ 1/r^2, the gravity from mass alone at equator is smaller by about 2Δr/r ≈ 2 * 21 / 6371 ≈ 0.0066 = 0.66%. Combined with rotation 0.34% gives about 1%. But the problem says effective gravity is about 0.7% less. That seems contradictory.

Wait, maybe I'm misreading the problem: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". Could it be that the parameter Ω^2 a / g ≈ 0.0035, and the reduction in |g'| is about 0.7% because of the vector addition: |g'| = sqrt(g^2 + (Ω^2 a cos φ)^2 - 2g Ω^2 a cos^2 φ). At equator, |g'| = g sqrt(1 - 2(Ω^2 a / g) + (Ω^2 a / g)^2). For small ε = Ω^2 a / g, |g'| ≈ g(1 - ε + ε^2/2 - ...). The fractional reduction is ε - ε^2/2... which is ~0.00345. That's 0.345%. So not 0.7%. So something is off.

Wait, perhaps the problem uses a = Earth's radius, but g ≈ 10 m/s^2 and Ω = 2π/(24h) maybe gives about 0.0034. Still not 0.7%. So why does the problem say 0.7%? Let's check the effect of Earth's flattening on the centrifugal potential? Or maybe the problem assumes a spherical Earth, but uses g ≈ 9.8 at poles and equator? The centrifugal acceleration at equator is about 0.034 m/s^2. That's 0.34% of g. But the vector g' at equator is reduced by 0.034 m/s^2 (0.34%). At 45° latitude, the reduction in radial component is Ω^2 a cos^2 45° = 0.017 m/s^2 (0.17%). The meridional component is Ω^2 a cos45 sin45 = 0.017 m/s^2. The magnitude reduction is roughly 0.017 m/s^2 (0.17%). So the maximum reduction is at equator: 0.34%. So the statement "about 0.7% less" cannot be explained by simple rotation on a sphere. However, the overall observed difference in g is about 0.5% (from ~9.78 m/s^2 at equator to ~9.83 m/s^2 at poles). That's about 0.5%. Wait, the standard gravity values: g_equator ≈ 9.7803267715 m/s², g_pole ≈ 9.8321863685 m/s². The fractional difference is (9.832 - 9.780)/9.832 ≈ 0.0053, i.e., 0.53%. That's about 0.5%. But the problem says 0.7%. So maybe the problem is using an older or approximate textbook value. Let's see: The difference due to flattening and rotation combined is roughly 5.2 Gal (0.052 m/s²), which is about 0.53% of 9.8. Some textbooks say ~0.5%. But 0.7% is larger.

Wait, could the problem be referring to the apparent weight of an object including both centrifugal and the fact that the Earth is rotating? Let's compute the ratio of |g'| at equator to pole for a spherical Earth but using the exact formula: |g'|_eq = g - Ω^2 a. |g'|_pole = g. Fractional difference = Ω^2 a / g. With a = 6.4e6, g = 9.81, Ω = 7.292e-5, difference = 0.0034. That's 0.34%. So to get 0.7%, maybe the problem uses g ≈ 980 cm/s² and something else. Let's see: if a = 6.37e8 cm, Ω^2 a = (7.292e-5)^2 * 6.37e8 = 5.317e-9 * 6.37e8 = 3.387e0 cm/s² = 3.39 cm/s²? Wait, that seems off: (7.292e-5)^2 = 5.317e-9 s^-2. Multiply by 6.37e8 cm = 338.6 cm/s² = 3.386 m/s². Oh! Wait. If a is in centimeters: a = 6.37e8 cm, then Ω^2 a = 5.317e-9 * 6.37e8 = 3.386? Let's compute: 5.317e-9 * 6.37e8 = 5.317 * 6.37 * 10^{-9+8} = 33.86 * 10^{-1} = 3.386. Wait, that's 3.386 m/s²? No, if a is in cm, then Ω^2 a is in cm/s²: 5.317e-9 * 6.37e8 = 3.386? 5.317e-9 * 6.37e8 = 5.317 * 6.37 * 10^{-1} = 33.86 * 0.1 = 3.386 cm/s². Yes, 3.386 cm/s². g = 981 cm/s². So ratio = 3.386 / 981 ≈ 0.003452. Same as before.

So 0.34% is robust. How can we get 0.7%? Maybe the problem statement says "about 0.7% less at the equator than at the poles" because they consider the effective gravity g' = g - Ω^2 a, and perhaps they use g = 4.9 m/s²? No.

Wait, maybe the dimensionless parameter is not Ω^2 a / g but something else? The problem says: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Let's calculate the angle. The angle between g' (effective gravity) and radial direction (vector pointing towards center). The effective gravity vector is g' = (-g + Ω^2 a cos^2 φ) r̂ - Ω^2 a cos φ sin φ n̂. The vector pointing towards center is -r̂. Wait, angle between g' and a vector pointing towards the centre. The vector towards center is -r̂. So g' has components: radial (inward) magnitude = g - Ω^2 a cos^2 φ (since outward is positive r̂, but g' radial component is negative if g > Ω^2 a cos^2 φ). Actually g' = [Ω^2 a cos^2 φ - g] r̂ - Ω^2 a cos φ sin φ n̂. The inward direction is -r̂. So the angle α between g' and -r̂ satisfies tan α = |northward component| / |radial component| = (Ω^2 a cos φ sin φ) / (g - Ω^2 a cos^2 φ). Since denominator ≈ g, tan α ≈ (Ω^2 a / g) cos φ sin φ = (Ω^2 a / (2g)) sin 2φ. Maximum occurs at φ = 45°: tan α_max ≈ Ω^2 a / (2g). With Ω^2 a / g ≈ 0.00345, tan α_max ≈ 0.001726. α_max ≈ 0.001726 rad ≈ 0.0989°. That's about 0.1°. Good.

So the angle part checks out. The 0.1° is consistent.

Now why 0.7%? Let's recompute everything carefully.

Let ε = Ω^2 a / g. ε ≈ 0.003452. The magnitude of g' at equator vs pole for spherical Earth is (g - Ω^2 a) vs g. Fractional reduction = ε ≈ 0.003452 = 0.3452%. That is about 0.3% or 0.35%. But the problem says about 0.7% less. Is there a factor of 2? Could the magnitude of g' at the equator be approximated as g(1 - ε - (1/2)ε^2? No, that would be even smaller.

Wait, maybe the problem uses g measured at the equator for the denominator? At equator g ≈ 9.78, so ε = 0.0339/9.78 = 0.003467. Still 0.35%.

Maybe the problem statement is using "0.7%" as the sum of the reduction in magnitude (0.35%) and something else? Or perhaps they define effective gravity as the magnitude of the vector sum of true gravitational acceleration and centrifugal acceleration, but they consider the variation between pole and equator of the effective gravity on a rotating Earth with the same shape? Hmm.

Alternatively, maybe the problem does not assume a sphere; maybe 'a' is the equatorial radius and the polar radius is smaller, and g itself varies with radius (Newton's law of gravitation). But the problem does not mention that. However, many geophysical fluid dynamics problems consider the equilibrium shape of the Earth under rotation. The effective gravity is perpendicular to the geoid. The variation of g' from pole to equator on the geoid is about 0.5% (or 0.7% in older texts). Let's check some references.

In Holton's "An Introduction to Dynamic Meteorology", there is a problem: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth's surface, |g'| is about 0.7% less at the equator than at the poles and the maximum angle between g' and the radial is about 0.1°." That sounds exactly like this problem. So it's from a standard atmospheric science textbook. Holton might use g = 10 m/s² and a = 6.4 × 10^6 m. Let's compute with those: Ω = 7.292 × 10^-5 s^-1, a = 6.4 × 10^6 m, g = 10 m/s². Then ε = (7.292e-5)^2 * 6.4e6 / 10 = 5.317e-9 * 6.4e5 = 0.003403. That's 0.3403%. Still not 0.7%.

Wait, maybe the magnitude of g' is not g - Ω^2 a at the equator because the Earth is an oblate spheroid and the radius at the equator is larger by about 21 km. The gravitational acceleration g_grav at the equator is GM / a_eq^2. At the pole, g_grav = GM / a_pole^2. The ratio is (a_pole / a_eq)^2. Since a_eq = 6378 km, a_pole = 6357 km, ratio = (6357/6378)^2 ≈ (0.9967)^2 ≈ 0.9934. So gravitational g alone is about 0.66% less at equator due to bulge. Then adding the centrifugal reduction of ~0.34% yields a total reduction of ~1.0%. But the problem says effective gravity is about 0.7% less. That doesn't match either.

Wait, maybe the problem defines g' as the gradient of the geopotential, which includes both gravitational and centrifugal potentials. On a geoid, the effective gravity is constant? No, the geoid is a surface of constant geopotential, but effective gravity magnitude varies.

Let's search memory: In Holton's "An Introduction to Dynamic Meteorology", problem 2.1 (or similar): "The Earth rotates with angular velocity Ω = 7.292 × 10^-5 s^-1. The mean radius is a = 6.37 × 10^6 m, and g = 9.81 m/s^2. (a) Evaluate the dimensionless parameter Ω^2 a / g. (b) Show that at the Earth's surface the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing toward the center of the Earth is about 0.1°."

In Holton's 4th edition, there is indeed a problem like this. Let's see if I recall the solution. The key might be that the magnitude of effective gravity is given by |g'| = g (1 - (Ω^2 a / g) cos^2 φ). At equator φ=0: |g'| ≈ g (1 - ε). So reduction is ε ≈ 0.0034 = 0.34%. But the problem says 0.7% less. How to reconcile? Wait, maybe the problem says "about 0.3%" but the user typed "0.7%"? Let's re-read the user's prompt: "Show that, at the Earth’s surface, the magnitude $| g ^ { \prime } |$ of the effective gravity is about $0 . 7 \%$ less at the equator than at the poles, and the maximum angle between $\pmb { g } ^ { \prime }$ and a vector pointing towards the centre of the Earth is about $0 . 1 ^ { \circ }$."

The user explicitly wrote 0.7%. Could it be that the original problem has a typo in the user's message? The prompt is what we must answer. We need to return values that match the problem. The problem asks to "evaluate the dimensionless parameter" and "show that ... about 0.7% less ... about 0.1°". However, the function must compute each answer from its parameters. So what exactly are the quantities asked? We need to infer from the problem statement.

The problem likely asks three things:
1. Evaluate Ω^2 a / g.
2. Compute the percent reduction in |g'| at equator relative to pole.
3. Compute the maximum angle between g' and the radial direction.

But the problem says "Show that ... is about 0.7% less ... and ... is about 0.1°." So the answers to be returned are probably:
1. The dimensionless parameter Ω^2 a / g.
2. The percentage reduction at equator (which should be ~0.7%).
3. The maximum angle in degrees (~0.1°).

But if we compute directly from the formulas for a spherical Earth, we get ~0.34% and ~0.1°. The 0.34% does not match 0.7%. However, the user explicitly wrote 0.7%. So we have two possibilities:

A) The intended answer is 0.7% for the second quantity, and we need to compute it using some more elaborate model that yields ~0.7%. Perhaps the problem expects us to compute the exact reduction in magnitude including the oblateness? Or maybe the problem expects the ratio (|g'|_pole - |g'|_eq) / |g'|_pole ≈ 2 * Ω^2 a / g? Let's check: If we approximate |g'| at equator as g sqrt(1 - 2ε + ε^2) = g(1 - ε). Reduction = ε. So not 2ε.

But perhaps the problem uses a different definition: effective gravity magnitude at the equator is g' = sqrt((Ω^2 a)^2 + g^2)? No, that would be if centrifugal acceleration is perpendicular to gravity. But at the equator, centrifugal acceleration is outward, directly opposite to gravity. So vector sum is g - Ω^2 a. At the pole, it's g. So reduction is Ω^2 a / g.

Wait, maybe the problem wants the percent difference in the magnitude of the effective gravity between equator and pole, but using the values of g' calculated from the exact vector formula: |g'|_eq = sqrt(g^2 + (Ω^2 a)^2 - 2g Ω^2 a + 0) = g - Ω^2 a. So same.

What if the problem uses a = 6.4 × 10^6 m and g = 9.8 m/s² and says "about 0.3%"? No, the user says 0.7%. Let's consider that there might be a factor of 2 because some textbooks define effective gravity as g' = -∇Φ where Φ = gh + ... and they might use the gravity variation with latitude formula: g = g_eq (1 + β sin^2 φ), where β ≈ 0.0053. But that's the observed variation, not just rotation.

Wait, perhaps the problem's actual text says 0.3% and the user made a typo. But we cannot assume a typo; we need to answer the problem as given. However, the instructions say: "The graded answer is whatever solve() returns, so let the function do the arithmetic." So we need to compute based on standard physics and return numbers. The problem is likely from a textbook where the answer is indeed about 0.3% (or 0.34%). But the user wrote 0.7%. Let's search memory: I think in Holton's problem, the answer is that Ω^2 a / g ≈ 3.4 × 10^-3, and the magnitude is about 0.3% less at the equator, and the angle is about 0.1°. Let me verify. Actually, I recall a problem: "The earth's rotation rate is Ω = 7.292 × 10^-5 s^-1, the mean radius a = 6.37 × 10^6 m and g = 9.81 m s^-2. (a) Evaluate Ω^2 a / g. (b) Show that at the earth's surface |g'| is about 0.3% less at the equator than at the poles and the maximum angle between g' and the radial direction is about 0.1°." Something like that. Many online sources mention 0.3%. For example: "The effective gravity at the equator is about 0.3% less than at the poles." Yes, that is standard.

Thus the user likely typed 0.7% but meant 0.3%. But we cannot be sure. However, since the function is to compute from first principles, if we compute the spherical Earth model, we get ~0.34%. If the grading expects 0.7% but we compute 0.34%, we might be marked wrong. On the other hand, if we compute 0.34% and the user expects 0.34%, it's correct. Which is more likely? We need to decide.

Let's read the problem again: "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

If we interpret "about 0.7% less" as the total observed variation (including oblateness), then maybe the expected answer is indeed ~0.7% or ~0.5%. But the problem does not mention Earth's flattening. It just mentions Ω, a, g. So the only physics we can apply is the rotation effect on a spherical Earth of radius a. That yields 0.34% and 0.1°. So the function should compute 0.34% (or maybe 0.3%). The angle is ~0.099°.

But the user explicitly says "Show that ... is about 0.7% less". If the function computes ~0.34%, it contradicts the prompt. However, in these coding challenge problems, often the user transcribes a textbook problem, and the function is supposed to compute the correct physical answer, not necessarily the approximate text. But the text "Show that ... about 0.7%" suggests that the expected computed value should be close to 0.7. But if the function computes from standard parameters and gets 0.34, then the "Show that" part is false. So maybe the function should compute using some different interpretation.

Alternative interpretation: Could the dimensionless parameter itself be ~0.0034, and the reduction in |g'| is about 0.7% because of a factor of 2 in the formula for magnitude? Let's rederive carefully.

Define effective gravity as the vector sum of gravitational acceleration (pointing to center, magnitude g) and centrifugal acceleration (magnitude Ω^2 a cos φ, directed outward perpendicular to axis). The magnitude of the effective gravity vector is:

|g'|^2 = g^2 + (Ω^2 a cos φ)^2 - 2 g (Ω^2 a cos^2 φ). Wait, is the dot product between gravity and centrifugal acceleration correct? Gravity points toward center (-r̂). Centrifugal acceleration is Ω^2 a cos φ ŝ. The angle between -r̂ and ŝ is 90° + φ? Let's compute: r̂ · ŝ = cos φ. Since ŝ = cos φ r̂ - sin φ n̂. So the angle between r̂ and ŝ is such that cos θ = r̂ · ŝ = cos φ. Thus θ = φ. Since gravity points inward (-r̂), the angle between gravity vector (pointing inward) and ŝ is π - φ. So the dot product (-r̂) · ŝ = -cos φ. Thus the dot product between g_vec = -g r̂ and f = Ω^2 a cos φ ŝ is (-g r̂) · (Ω^2 a cos φ ŝ) = -g Ω^2 a cos φ (r̂·ŝ) = -g Ω^2 a cos φ * cos φ = -g Ω^2 a cos^2 φ.

Thus |g'|^2 = |g_vec|^2 + |f|^2 + 2 g_vec·f = g^2 + (Ω^2 a cos φ)^2 + 2(-g Ω^2 a cos^2 φ) = g^2 + (Ω^2 a)^2 cos^2 φ - 2 g Ω^2 a cos^2 φ. That matches earlier.

At equator, φ=0: |g'|^2 = g^2 + (Ω^2 a)^2 - 2g Ω^2 a = (g - Ω^2 a)^2. So |g'| = g - Ω^2 a. Exactly.

At pole, φ=90°: |g'| = g.

So fractional difference = (g - (g - Ω^2 a)) / g = Ω^2 a / g. No factor of 2.

Thus the only way to get ~0.7% is if the dimensionless parameter itself is ~0.007. Let's see if using different values yields that. Suppose we use g = 9.8 m/s², a = 6.37e6 m, sidereal day = 86164 s. Then Ω = 7.2921e-5. ε = 0.0034. No.

What if we use a = 6371 km and g = 9.8, but use the value of true gravitational acceleration at the surface g0 = GM/a^2 = 9.83? Then ε = 0.03386/9.83 = 0.003445. Still 0.3445%.

What if the problem expects the student to compute the dimensionless parameter as Ω^2 a / g ≈ 0.0034, and then say "the magnitude is about 0.3% less" but the user mistakenly wrote 0.7%? This seems highly plausible. Many people might confuse 0.3% with 0.3, or misread 0.3% as 0.3, but 0.7% is different.

Another possibility: The problem asks for the fractional difference in |g'| between equator and pole: (|g'|_pole - |g'|_eq) / |g'|_eq. That would be (g - (g - Ω^2 a)) / (g - Ω^2 a) = Ω^2 a / (g - Ω^2 a). For small ε, this is ε (1 + ε) ≈ 0.00345 * 1.00345 ≈ 0.00346. Still 0.346%.

What about the variation in the magnitude of the effective gravity on an ellipsoidal Earth? The difference in |g'| from pole to equator is about 5.2 Gal (0.052 m/s²) which is ~0.53% of g. Some older tables say 0.5%. Still not 0.7%.

Wait, maybe the problem uses the "standard gravity" g = 9.80665 m/s², and a = 6371 km, but the effective gravity at the equator includes a component due to the fact that the geoid is an ellipsoid. But the problem explicitly says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less..." It might be that the textbook problem is designed to show two things: (1) the dimensionless parameter is small (~0.003), (2) the effect on |g'| is twice that (~0.006 or 0.6%). Why twice? Let's think: The effective gravity includes the centrifugal term in the radial component and also the fact that the potential surfaces are not spherical. But if we assume a spherical Earth, the variation in effective gravity magnitude from pole to equator is not just the radial component reduction; maybe the problem defines effective gravity magnitude as the magnitude of the vector sum, and then approximates |g'| ≈ g - Ω^2 a cos^2 φ. Wait, that is the radial component. The magnitude of the vector is slightly larger than the radial component due to the northward component. Let's compute the exact fractional reduction at the equator:

Exact reduction = (g - (g - Ω^2 a)) / g = ε. Exact.

But what if the problem mistakenly thinks the centrifugal acceleration is perpendicular to gravity everywhere (like at 45°) and uses |g'| = sqrt(g^2 + (Ω^2 a)^2) ≈ g (1 + (Ω^2 a)^2/(2g^2)). That would be an increase, not decrease. So no.

Maybe the problem uses gravitational potential and the effective gravity on the rotating Earth as g' = g - Ω^2 a sin^2 φ? Wait, at the equator, the centrifugal acceleration is maximum and outward, reducing g. At the pole, it's zero. So the reduction is proportional to cos^2 φ. But some older derivations might write the effective gravity magnitude as g' ≈ g - Ω^2 a cos^2 φ. At equator, reduction = Ω^2 a. That's 0.34%.

Wait, maybe the problem uses the "geocentric latitude" vs "geodetic latitude"? The centrifugal component depends on sin^2 φ? Let's derive using geocentric latitude φ. The distance from axis is a cos φ. The radial component of centrifugal acceleration is Ω^2 a cos^2 φ (outward). So the inward effective gravity component is g - Ω^2 a cos^2 φ. The meridional component is Ω^2 a cos φ sin φ. So the magnitude squared is (g - Ω^2 a cos^2 φ)^2 + (Ω^2 a cos φ sin φ)^2. At equator, it's (g - Ω^2 a)^2. So reduction = Ω^2 a.

So I think the problem statement in the prompt has a typo: it should be 0.3% (or 0.34%). But the user wrote 0.7%. However, we need to implement solve() that returns the correct computed values based on standard parameters. Which values should we return? Since the problem explicitly says 0.7%, maybe the grader expects a number close to 0.7. But if we compute using physics, we get ~0.34. Let's see if there is any plausible way to get ~0.007 (0.7%).

Wait! Could the dimensionless parameter be Ω^2 a / g ≈ 0.0034, and the effective gravity magnitude be reduced by about 0.7% because the reduction in |g'| is approximately 2 * Ω^2 a / g? Let's see if there is a misinterpretation of the formula for |g'|. Suppose someone mistakenly calculates |g'| using the Pythagorean sum of the full centrifugal acceleration (magnitude Ω^2 a cos φ) and g, but with the wrong sign: |g'| = sqrt(g^2 - (Ω^2 a cos φ)^2). At equator, |g'| = sqrt(g^2 - (Ω^2 a)^2) ≈ g (1 - (Ω^2 a)^2/(2g^2)). That gives a reduction of order ε^2/2 ≈ 6e-6, negligible.

Suppose someone thinks the radial component is g - Ω^2 a (at equator) but the pole value is not g but g + something? No.

Alternatively, maybe the problem uses a different radius: the Earth's radius at the pole is ~6357 km, at equator ~6378 km. The average radius is 6371 km. Maybe they use a = 6400 km, and g = 9.8, but the effective gravity is evaluated using the geopotential. The geopotential Φ = gz + ... The effective gravity is the gradient of the geopotential. On a spherical Earth, the geopotential surfaces are not spheres. The value of g' at the equator on the geoid might be lower by about 0.7% relative to the pole? Let's compute using the exact formula for gravity on a rotating fluid body in hydrostatic equilibrium. For a Maclaurin spheroid, the surface gravity at the pole and equator can be computed. The ratio g_eq / g_pole for a Maclaurin spheroid with Earth's flattening (f ≈ 1/298.257) is about... Let's recall: For a homogeneous Maclaurin spheroid, g_eq / g_pole = (surface area? No). Actually, for a rotating fluid body, gravity at the pole is larger because the body is flattened. The difference is roughly (5/2) m, where m = Ω^2 a_eq / g_eq? Let's check the Clairaut's theorem.

The Clairaut parameter: m = Ω^2 a / g ≈ 1/289. But wait, 1/289 ≈ 0.00346. That's the same as our ε. But Clairaut's theorem states that the flattening f ≈ (3/2)m + ...? Actually, f ≈ (5/2)m - ...? Let's recall: For a homogeneous fluid Earth, f ≈ (5/4)m? No. Let's derive: The normal gravity formula: g = g_e (1 + β sin^2 φ), where β ≈ 5.302e-3. That's about 0.53%. This is the observed variation of g on the geoid. The parameter m = Ω^2 a / g_e ≈ 0.00344. The flattening f ≈ (3/2)m - ...? Actually, from theory: g_pole = g_eq (1 + (5/2)m - f + ...). Wait, let's recall the exact formula.

Normal gravity on the reference ellipsoid (Somigliana's formula):
g = g_eq (1 + k sin^2 φ) / sqrt(1 - e^2 sin^2 φ), where k = (b g_pole)/(a g_eq) - 1. For Earth, k ≈ 1.93185138639e-3, e^2 ≈ 6.69437999013e-3. The resulting variation from equator to pole is about 0.5%. So not 0.7%.

However, historically, some textbooks used g_pole ≈ 983 cm/s², g_eq ≈ 978 cm/s². Difference = 5 cm/s² = 0.5%. That's 0.5%.

So where does 0.7% come from? Let's calculate: (983 - 978)/978 = 5/978 ≈ 0.00511 = 0.511%. Not 0.7%. If we use (983 - 978)/783? No.

Wait, maybe using a = 6.37e8 cm, g = 980 cm/s², Ω = 7.29e-5. Then ε = 3.39/980 = 0.00346 = 0.346%. Twice that is 0.692% ≈ 0.7%. Is there a textbook that approximates the variation as 2ε? Let's see: In some derivations, the effective gravity magnitude is approximated as g' ≈ g - Ω^2 a cos^2 φ. At equator, reduction = Ω^2 a. But maybe the problem uses the full expression for |g'|^2 and then says |g'| ≈ g (1 - (Ω^2 a / g) cos^2 φ). That's reduction ε. Still not 2ε.

Alternatively, maybe the problem defines the dimensionless parameter as Ω^2 a / (2g) ≈ 0.0017, and the percent reduction is 2 * parameter? No.

Let's try to search memory: In Holton's "An Introduction to Dynamic Meteorology", Chapter 2, problem 2.1 (or 1.2): "The earth has a mean radius of 6.37 × 10^6 m and rotates with angular velocity 7.292 × 10^-5 s^-1. The mean gravitational acceleration at the surface is 9.80665 m s^-2. (a) Evaluate the dimensionless parameter Ω^2 a / g. (b) Show that the magnitude of the effective gravity is about 0.3% less at the equator than at the poles, and that the maximum angle between g' and the radial is about 0.1°." I think the correct number is 0.3%. The user's text says 0.7%. This might be a transcription error (3 and 7 are somewhat similar if handwritten?). Or maybe the user copied from a source where the text had a different formatting: "0 . 3 \%" could be misread as "0.7%" if the dot is a decimal and the 3 is smudged? Not really. But 0.3 is a common answer.

Given that the angle is 0.1°, which matches our calculation, and the dimensionless parameter is ~0.003, and the reduction is either 0.3% or 0.7%, the 0.3% is physically correct for a spherical Earth. The function should compute the physical values. Since the prompt says "Show that ... is about 0.7% less", perhaps the expected answer for the second quantity is 0.7 (in percent). But we cannot fudge the physics to get 0.7 unless we use an incorrect model.

Wait, could the problem be asking for the percent difference in the magnitude of g' between the equator and 45° latitude? No, it says "than at the poles".

Alternatively, maybe the problem uses the equatorial radius for a, but the polar radius for the comparison, so the distance from axis at equator is a_eq, but at the pole the radius is a_pole < a_eq, and gravity there is GM/a_pole^2. If we assume Earth is a sphere of radius a, then g = GM/a^2 is constant. But if we consider that the effective gravity at the pole is on a sphere of radius a, while at equator the radius is a, but the Earth is actually an oblate spheroid with equatorial radius larger. But the problem gives a single 'a'. So no.

Another angle: Maybe the function is supposed to compute the dimensionless parameter, the fractional reduction (in percent) using the exact formula but with g at the poles and equator being different? No.

Let's examine the possibility that the problem statement originally is from "Atmospheric and Oceanic Fluid Dynamics" by Vallis, or some other text. Let's search mental database: There is a known problem: "Evaluate the dimensionless parameter Ω^2 a / g. Show that the magnitude of the effective gravity is about 0.3% less at the equator than at the poles and that the maximum angle between g' and a vector pointing toward the center of the Earth is about 0.1°." This is definitely a standard problem. The number 0.3% is standard.

Thus I'll assume the user made a typo and that the correct answer is ~0.3%. But if we return 0.34 or 0.3, will the grader mark it wrong because they expected 0.7? Let's think about the system. This looks like a Code Runner / auto-grader problem. The user is providing the prompt. The solution should compute the answer. Usually, the prompt is carefully transcribed from the problem statement, and the expected output is based on that. But since it's a physics derivation, the numbers might have been rounded in the textbook. However, the auto-grader might check for values within tolerance. If the problem statement says 0.7%, but the physics yields 0.3%, the auto-grader would likely accept anything close to the physics, because it's a physics problem. But if the auto-grader is based on the text's numbers, it might check for ~0.7. How to decide?

We need to consider the instruction: "Work out the solution and express it as a Python solve() function that computes the numerical answer(s)." The problem says "Show that ... is about 0.7% less ... and ... is about 0.1°." So the function should compute the numerical values that demonstrate these statements. If we compute the exact values from standard parameters, we get:

1. Ω^2 a / g ≈ 0.00343 (dimensionless).
2. Percent reduction at equator ≈ 0.343% (or 0.34%).
3. Maximum angle ≈ 0.099° (or 0.10°).

If the grader expects these three values, then returning them is correct. But the text says "about 0.7%". Could the second quantity instead be the "percent less at the equator than at the poles" computed as (g_pole - g_eq) / g_eq * 100? Let's compute: g_pole = g, g_eq = g - Ω^2 a. So (Ω^2 a) / (g - Ω^2 a) * 100 ≈ 0.0345 / (1 - 0.0345) ≈ 0.0357 = 3.57%? No, that's if we use g=1? Wait: if g = 9.81, Ω^2 a = 0.0339. (0.0339) / (9.81 - 0.0339) = 0.003467. *100 = 0.3467%. Same.

What if the problem uses g ≈ 4.9 m/s²? No.

Could the parameter be defined as Ω^2 a^2 / (g a) = Ω^2 a / g? Yes.

What if a is 40000 km / (2π) ≈ 6371 km. That's standard.

Let's compute with exact numbers:

Ω = 7.2921159e-5 rad/s (sidereal angular velocity).
a = 6.3781e6 m (equatorial radius). Or mean radius 6.371e6.
g = 9.80665 m/s² (standard gravity).

Compute ε = Ω^2 * a / g.

Using a = 6.3781e6, Ω^2 = (7.2921159e-5)^2 = 5.317e-9. Multiply by a: 5.317e-9 * 6.3781e6 = 0.033915. Divide by 9.80665 = 0.003458. That's 0.3458%.

Using a = 6.371e6: numerator = 0.033877. /9.80665 = 0.003454. That's 0.3454%.

So about 0.35%.

If the problem uses a = 6.37e6 and g = 9.81:
Ω^2 a = 5.317e-9 * 6.37e6 = 0.03387. /9.81 = 0.003453. That's 0.3453%.

Thus the reduction is about 0.35%. Rounding to one significant figure gives 0.3% or 0.4%. But 0.7% is far off.

I suspect the user mis-typed 0.3% as 0.7%. Since we must write the function, we should compute the correct physical value. But maybe the grader is tolerant. However, to be safe, we could compute the reduction as (g_pole - g_equator) / g_pole * 100, which yields ~0.345%. We could also perhaps use the exact formula for the magnitude of g' at the equator vs pole, which yields the same. So the answer for quantity 2 would be ~0.35 (if unit is percent). But if the expected answer is 0.7, then we might fail.

But wait: maybe the problem wants the magnitude reduction in g' at the equator relative to the poles as computed from the exact vector magnitude, but using the geopotential? Let's think if there is any physical effect that doubles the reduction.

Consider the effective potential: Φ = Φ_g + Φ_c, where Φ_g = -GM/r, Φ_c = - (1/2) Ω^2 r^2 cos^2 φ. Then effective gravity is g' = -∇Φ evaluated at the surface. On a sphere of radius a, ∇Φ has radial and angular components. The radial component: ∂Φ/∂r = GM/r^2 - Ω^2 r cos^2 φ = g - Ω^2 a cos^2 φ. The angular component (in the θ direction, where θ = 90° - φ): (1/r) ∂Φ/∂θ = (1/r) ∂Φ/∂φ * (-1)? Wait, ∂Φ/∂φ = -Ω^2 r^2 cos φ (-sin φ) = Ω^2 r^2 cos φ sin φ? Let's derive.

Φ_c = - (1/2) Ω^2 r^2 cos^2 φ. So ∂Φ_c/∂φ = - (1/2) Ω^2 r^2 * 2 cos φ (-sin φ) = Ω^2 r^2 cos φ sin φ.

The meridional component of ∇Φ (pointing northward) is (1/r) ∂Φ/∂φ = Ω^2 r cos φ sin φ. But note the direction: the gradient points in direction of increasing Φ. Since Φ_c decreases away from equator? Let's check. The effective gravity vector points toward lower geopotential, so g' = -∇Φ. Let's compute -∇Φ in spherical coordinates.

∇Φ = (∂Φ/∂r) r̂ + (1/r) (∂Φ/∂φ) φ̂, where φ̂ points northward? Actually, in standard spherical coordinates (r, θ, λ) where θ = colatitude (π/2 - φ), the unit vectors are r̂, θ̂ (southward), λ̂ (eastward). Latitude φ = π/2 - θ. Then ∂/∂φ = -∂/∂θ. The meridional gradient is (1/r) ∂Φ/∂θ θ̂ = -(1/r) ∂Φ/∂φ θ̂. Since θ̂ points southward.

Anyway, the magnitude of g' is sqrt( (∂Φ/∂r)^2 + (1/r ∂Φ/∂θ)^2 ) = sqrt( (g - Ω^2 a cos^2 φ)^2 + (Ω^2 a cos φ sin φ)^2 ). Wait, sign? g' = -∇Φ. The radial component of -∇Φ is -∂Φ/∂r = -(g - Ω^2 a cos^2 φ) = -g + Ω^2 a cos^2 φ (inward positive? No, r̂ outward, so -g r̂ + ...). The magnitude is the same.

So no extra factor.

Alright, perhaps the problem statement had a formatting issue: "0 . 3 \%" (LaTeX `0 . 3 \%`) got mangled by OCR or something into `0 . 7 \%`? The dot and the 3 could be misread? In some fonts, 3 and 7 look different. But maybe the original had `0.34\%`, which could be misread as `0.7\%` if the 4 is lost? Not sure.

Given the strong evidence that the correct answer is ~0.3%, I will compute ~0.34% and return it as the percent value. However, the user text explicitly says 0.7%. If I return 0.34, the user might be puzzled. But the instructions say: "Return a dict with one entry per quantity asked, keyed '1', '2', ..., 'N' in the order asked". The quantities asked are:
1. The dimensionless parameter Ω^2 a / g.
2. The percent by which |g'| is less at the equator than at the poles.
3. The maximum angle in degrees.

Thus the function should compute these. It should not hard-code. So we need to decide on the formula for percent less. It should be computed exactly as (|g'|_pole - |g'|_eq) / |g'|_pole * 100. That gives ~0.345%. If the grader expects ~0.345, fine. If it expects ~0.7, maybe we need to think again.

Is there any chance that the problem wants the maximum angle between g' and the radial, and the maximum deflection of the geoid from a sphere, and the 0.7% is something else? No.

Let's try to see if there is an alternative interpretation: Perhaps "the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles" refers to the fact that on the actual Earth (which is an oblate spheroid), the effective gravity at the equator is about 0.7% less than at the poles. And the problem asks to evaluate the dimensionless parameter for Earth and "show that" these things hold. The "show that" might refer to using the fact that Earth is in hydrostatic equilibrium and the dimensionless parameter is small, which leads to the flattening and the variation in g'. But the variation in g' on a rotating fluid body is related to m = Ω^2 a / g. In fact, the variation is about (5/2) m? Let's check.

For a rotating homogeneous fluid body, the surface gravity at the pole is g_p = (4/3) π G ρ a (1 - (2/5) ε ...). Actually, let's derive the approximate variation.

Consider a Maclaurin spheroid with small flattening f. The equatorial radius a = a_eq, polar radius c = a(1-f). The surface area? The gravity at the pole is approximately GM/c^2 (1 + small corrections). The gravity at the equator is approximately GM/a^2 - Ω^2 a (centrifugal). The difference due to flattening is about 2f g (since g ∝ 1/r^2). For Earth, f ≈ 1/298.25 ≈ 0.00335. So 2f ≈ 0.0067 = 0.67%. That's close to 0.7%! Wait! The variation in g due to flattening alone (distance from center) is about 2f ≈ 0.67%. But the problem says effective gravity (which includes centrifugal). However, the problem might be implicitly assuming that Earth is an oblate spheroid in hydrostatic equilibrium, and the effective gravity variation is dominated by the radius variation. But the problem statement as given does not mention flattening. However, maybe the dimensionless parameter Ω^2 a / g ≈ 0.0035, and the flattening f ≈ (3/2) m? Wait, for a homogeneous Earth, f ≈ (5/4) m? Let's check. The Clairaut parameter m = Ω^2 a / g ≈ 0.00344. The observed flattening is f ≈ 1/298.25 ≈ 0.00335. So f ≈ m. Indeed, for Earth, f ≈ m (roughly). The difference in gravity due to flattening is about 2f ≈ 0.0067 = 0.67%. The centrifugal reduction is m ≈ 0.00344 = 0.34%. The total variation is about 2f + m ≈ 0.67% + 0.34% = 1.0%. But the problem says 0.7%. Hmm.

Wait, maybe the problem says "the magnitude of the effective gravity is about 0.3% less at the equator than at the poles" for a spherical Earth, but due to the equatorial bulge (which depends on the same dimensionless parameter), the actual effective gravity is about 0.5% less. But 0.7% is the variation due to flattening alone? Actually, the variation in g_grav (gravitational only) due to flattening is about 0.66% (since f ≈ 0.00335, 2f ≈ 0.0067). The centrifugal reduces it by m ≈ 0.34%, so net reduction in effective gravity is about 0.66% - 0.34%? Wait, at the equator, radius is larger, so gravitational g is smaller by ~0.66%. The centrifugal effect further reduces apparent weight by 0.34%. So total effective gravity at equator is ~1.0% less than polar gravity. But the problem says 0.7% less. That doesn't fit.

Wait, maybe the 0.7% is the reduction in gravitational g (not effective) due to bulge and the fact that mass is redistributed? For a rotating fluid, the gravity at the pole is larger than at the equator by about (5/2) m? Let's check.

For a Maclaurin spheroid, the surface gravity at the pole is g_p = (4πGρ a / (3 e^3)) (something). At the equator, g_eq = ... The ratio g_eq/g_p is approximately 1 - (5/2) m? Let's try to derive using Clairaut's theorem.

Clairaut's formula for the variation of gravity on the geoid:
g = g_eq [1 + (5/2)m - f) sin^2 φ + ...]. Wait, the standard normal gravity formula has β ≈ 5.302e-3. And m ≈ 0.00345. f ≈ 0.00335. Then (5/2)m = 0.00863. (5/2)m - f = 0.00863 - 0.00335 = 0.00528. That's close to β = 0.00530. So the coefficient of sin^2 φ is about 0.0053. That means from equator (φ=0) to pole (φ=90°), g increases by about 0.0053 g_eq ≈ 0.53%. So the effective gravity is about 0.5% greater at the pole than equator. That's the observed variation. So 0.5% is the standard. Not 0.7%.

But wait, the problem says "about 0.7% less at the equator than at the poles". If we compute (g_pole - g_eq)/g_pole, using g_eq ≈ 9.780, g_pole ≈ 9.832. (9.832 - 9.780)/9.832 = 0.00529 = 0.529%. So about 0.5%. If we compute relative to g_eq: (9.832 - 9.780)/9.780 = 0.00532 = 0.532%. Still 0.53%.

Thus 0.7% is not observed either. Could it be 0.7% if we use some older approximation? Let's see: if f ≈ 1/297 = 0.003367, then 2f = 0.00673 = 0.673%. That's the naive reduction in Newtonian gravity due to increased radius at equator (g ∝ 1/r^2). But that ignores the redistribution of mass and the centrifugal term. So 0.7% might be the reduction in Newtonian g at the equator due to Earth's bulge. But the problem says effective gravity, which includes centrifugal. At equator, effective gravity is Newtonian g_eq minus Ω^2 a. If Newtonian g_eq is reduced by ~0.67% relative to g_pole, and then subtract Ω^2 a (0.34%), the net reduction is about 1.0%. But maybe the problem approximates Newtonian g as constant (spherical Earth), and then the effective gravity is reduced by centrifugal alone (0.34%). Then 0.7% is wrong.

What if the problem uses a different radius for the pole and equator? For example, a_pole = 6357 km, a_eq = 6378 km. If we assume g = GM/r^2, then g_eq_grav = g_pole * (a_pole/a_eq)^2. Suppose g_pole = 9.83. Then g_eq_grav = 9.83 * (6357/6378)^2 = 9.83 * (0.99671)^2 = 9.83 * 0.99343 = 9.765. Then effective gravity at equator = 9.765 - 0.034 = 9.731. Compare to g_pole = 9.83. Difference = 0.099. Percent = 0.099/9.83 = 1.0%. Not 0.7%.

Alternatively, if we assume Earth is spherical but g at surface varies because of varying distance to center? No.

Let's try to see if using a = 6.4e6 and g = 10 gives something different: ε = 0.0034. Still 0.34%.

What if the problem defines Ω = 2π / (86164 s) = 7.292e-5, a = 6.37e6 m, and g = 9.81 m/s². The dimensionless parameter = 0.00345. The reduction = 0.345%. If we multiply by 2, we get 0.69%. Why would we multiply by 2? Wait, the magnitude of the centrifugal acceleration at the equator is Ω^2 a. The reduced gravity is g' = g - Ω^2 a. But maybe the problem's author mistakenly thought the centrifugal acceleration is 2Ω^2 a? No.

Wait, in some contexts, the Coriolis parameter is 2Ω sin φ, and the vertical component of the Coriolis force for horizontal motion influences effective gravity? No.

Alternatively, maybe the effective gravity is the gradient of the geopotential on the actual geoid. The geopotential is constant on the geoid. The effective gravity at the equator vs pole can be related to the difference in radii. The geoid at the equator is further from the center by about 21 km. The effective gravity difference is Δg' ≈ -2g (Δa/a) + ...? If the geoid radius difference is due to rotation, Δa/a ≈ (1/2) ε? Let's see: For Earth, equatorial bulge ≈ 21.4 km. a ≈ 6371 km. So Δa/a ≈ 0.00336. That's roughly equal to ε (0.00345). Actually, from hydrostatic equilibrium, the ellipticity e ≈ (3/2) m? Wait, for Earth, f ≈ m? Yes, f ≈ m ≈ 1/289 ≈ 0.00346. So the bulge is about ε a. The variation in gravity due to distance is 2f ≈ 2ε = 0.0069 = 0.69%. Ah! That's 0.7%!

Could the problem be asking to show that the magnitude of effective gravity is about 0.7% less at the equator because of the combined effect of the bulge? But wait, the problem says "Evaluate the dimensionless parameter Ω^2 a / g for the Earth. Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles". If we compute the bulge using the small parameter, the fractional difference in radius is of order ε. The fractional difference in Newtonian gravity is 2ε (since g ∝ 1/r^2). That gives about 0.7%. Then the centrifugal reduction adds another ε, making total ~1.0%. But maybe the problem defines effective gravity as just the Newtonian gravity on the geoid (i.e., the gravitational component of g', not including the centrifugal term) and then the variation is 2ε ≈ 0.7%? No, g' is defined as effective gravity = gravity + centrifugal.

Wait, there is a subtlety: In rotating coordinates, the effective gravity is the gradient of the geopotential. On the geoid (a surface of constant geopotential), the effective gravity magnitude is not constant. However, the problem might be considering g' at the surface of a rotating fluid body in hydrostatic equilibrium. In that case, the surface is an equipotential. The potential is Φ = GM/r + (1/2) Ω^2 r^2 cos^2 φ = constant = Φ_0. At the pole (φ=90°), cos φ=0, so GM/r_p = Φ_0 => r_p = GM/Φ_0. At the equator (φ=0), GM/r_eq + (1/2) Ω^2 r_eq^2 = Φ_0. For small Ω, r_eq ≈ r_p (1 + ε/2)? Let's solve.

Let r_p = a. Then Φ_0 = GM/a. At equator: GM/r_eq + (1/2) Ω^2 r_eq^2 = GM/a. Let r_eq = a (1 + δ). Then GM/(a(1+δ)) + (1/2) Ω^2 a^2 (1+δ)^2 ≈ GM/a (1 - δ + δ^2) + (1/2) Ω^2 a^2 (1 + 2δ). Set equal to GM/a.

=> GM/a (-δ + δ^2) + (1/2) Ω^2 a^2 (1 + 2δ) ≈ 0.

Divide by GM/a = g a:

=> -δ + δ^2 + (1/2) (Ω^2 a / g) (1 + 2δ) ≈ 0.

Neglect δ^2 and δ*ε:

=> -δ + (1/2) ε ≈ 0 => δ ≈ ε/2.

Thus the equatorial radius is larger by ≈ (ε/2) a.
~~~~

**attempt 1** — `outcome` = `ungradable: solve() returned NoneType, expected dict`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # standard Earth parameters
    Omega = 7.2921159e-5   # angular velocity (
~~~~

**attempt 2** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

RESPONSE (verbatim, untruncated):

~~~~
We need to fix the user's solve() function. The problem asks to evaluate the dimensionless parameter Omega^2 a / g for Earth, show that |g'| is about 0.7% less at equator than at poles, and the maximum angle between g' and a vector pointing towards the centre is about 0.1 degrees.

The user's code is incomplete; it was cut off. We need to write a complete solve() function that returns a dict keyed "1".."N" in the order asked. So we need to determine what N is and what the expected values/units are.

Let's parse the problem:

1. Evaluate the dimensionless parameter Omega^2 a / g for the Earth.
2. Show that, at the Earth's surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles.
3. The maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°.

The function should return a dict with keys "1", "2", "3" corresponding to these three results. Each value is {"value": <number>, "unit": "<unit>"}.

First result: dimensionless parameter Omega^2 a / g. It's dimensionless, so unit should be "dimensionless" or maybe ""? The prompt says standard library only, return dict with "value" and "unit". Usually for dimensionless we can use unit "1" or "dimensionless". Let's see typical conventions. The problem says "dimensionless parameter", so unit is dimensionless. But the format expects a string. I'll use "dimensionless" or maybe just ""? The prompt says each {"value": <number>, "unit": "<unit>"}. To be safe, maybe "dimensionless". But sometimes these auto-graders expect specific strings. Let's think. If it's a dimensionless parameter, the unit might be "1" or "". I think "dimensionless" is explicit and likely accepted. But let me think about typical physics problem auto-graders. Usually they might accept "dimensionless", "1", or even "" (empty string). The safest might be empty or "1"? However, the problem explicitly says "dimensionless parameter". I think "dimensionless" is fine. But we can also use "1" to mean dimensionless (since SI base unit for dimensionless is one). But let's keep "dimensionless". Actually, looking at the prompt, maybe they want unit as a string describing the unit. For a percentage difference, unit is "%". For angle, unit is "°" or "deg". For dimensionless, I'll put "dimensionless". But let's consider if they might want "1". The problem statement uses no unit. Let's check typical patterns in these tasks: they often return unit as "m/s^2", "kg", etc. For dimensionless quantity, I've seen "dimensionless" or "". Let's use "dimensionless".

Second result: magnitude |g'| is about 0.7% less at equator than at poles. So the value is a percentage, ~0.7%. Actually, maybe they want the fractional difference? Wait, the problem says "about 0.7% less". So the value is 0.7, and unit is "%". Or maybe they want the exact computed value ~0.34%? No, the standard result for Earth is about 0.3%? Let's calculate.

We know effective gravity g' = g - Omega^2 a cos^2 phi (approx). Actually, more precisely, the centrifugal acceleration at latitude phi is Omega^2 a cos phi, directed outward perpendicular to axis. The radial component (opposing gravity) is Omega^2 a cos^2 phi. The component perpendicular to radius is Omega^2 a cos phi sin phi.

The magnitude of effective gravity can be approximated as |g'| ≈ g - Omega^2 a cos^2 phi (to first order). At equator phi=0, cos phi = 1, so reduction is Omega^2 a. At poles phi=±pi/2, cos phi=0, no reduction. So fractional difference = (|g'_pole| - |g'_equator|) / |g'_pole| ≈ (g - (g - Omega^2 a)) / g = Omega^2 a / g. So the dimensionless parameter from part 1 is exactly the fractional reduction. So Omega^2 a / g ≈ ? Let's compute.

Omega = 7.2921159e-5 rad/s.
Earth radius a = 6371 km = 6.371e6 m.
g = 9.80665 m/s^2 (standard gravity).

Omega^2 = (7.2921159e-5)^2. Let's calculate:
7.2921159e-5 squared:
7.2921159^2 = 53.175? Let's compute accurately.
7.2921159 * 7.2921159.
7.292^2 ≈ 53.173. More precisely:
7.2921159 * 7.2921159 = (7.3 - 0.0078841)^2 = 7.3^2 - 2*7.3*0.0078841 + (0.0078841)^2 = 53.29 - 0.1151 + ~6.22e-5 ≈ 53.17496. But let's do exact multiplication.
7.2921159 * 7 = 51.0448113
7.2921159 * 0.2921159 = ?
Actually, easier: use Python-like mental math or approximate.
7.2921159e-5 ^2 = 5.317...e-9.
Let's compute precisely.
7.2921159 * 7.2921159:
7.2921159 * 7 = 51.0448113
7.2921159 * 0.2 = 1.45842318
7.2921159 * 0.09 = 0.656290431
7.2921159 * 0.002 = 0.0145842318
7.2921159 * 0.0001 = 0.00072921159
7.2921159 * 0.0000159 = 7.2921159 * 1.59e-5 = approx 1.1594e-4.
Summing these is messy. Let's do it more systematically.

Compute 72921159^2 and scale by 1e-14.
Actually, just approximate: (7.2921e-5)^2 = (7.2921)^2 * 10^{-10}.
7.2921^2:
7.2921 * 7.2921
7 * 7.2921 = 51.0447
0.2921 * 7.2921 = ?
0.3 * 7.2921 = 2.18763
minus 0.0079 * 7.2921 ≈ 0.0576
so 2.1300.
Total ≈ 53.1747.
So Omega^2 ≈ 53.1747 * 10^{-10} = 5.31747e-9 s^{-2}.
Then Omega^2 * a = 5.31747e-9 * 6.371e6 = 5.31747 * 6.371 * 10^{-3} = ?
5.31747 * 6 = 31.90482
5.31747 * 0.371 = 1.97278
Total ≈ 33.8776.
Times 10^{-3} = 0.0338776 m/s^2.
Then Omega^2 a / g = 0.0338776 / 9.80665 ≈ 0.0034546.
That's about 0.345%. Wait, 0.00345 is 0.345%. The problem says about 0.7% less. Hmm.

Wait, maybe they use g ~ 9.8, a = 6.4e6.
Omega^2 a / g = 0.034 / 9.8 = 0.00347 = 0.347%.
But the problem says 0.7%. Why is there a discrepancy? Maybe the effective gravity reduction is not just Omega^2 a cos^2 phi? Actually, the exact magnitude difference might be larger because the centrifugal force also changes the direction, and the magnitude is sqrt(g^2 + (Omega^2 a cos phi)^2 - 2 g Omega^2 a cos^2 phi)? Wait, need to derive.

At the equator, the centrifugal acceleration is purely radial outward, opposite to gravity. So g' = g - Omega^2 a. The magnitude is g - Omega^2 a (since they are collinear). At the pole, centrifugal acceleration is zero. So difference is g - (g - Omega^2 a) = Omega^2 a. Fractional difference relative to pole = Omega^2 a / g_pole? Or relative to mean g? The problem says "less at the equator than at the poles". Usually you compute (g_pole - g_equator) / g_pole. Or maybe relative to equator? Let's check.

If g_pole ≈ 9.832 m/s^2, g_equator ≈ 9.780 m/s^2. Difference = 0.052. 0.052 / 9.832 = 0.00529 = 0.53%. Or relative to equator: 0.052 / 9.780 = 0.00532 = 0.53%. That's about 0.5%, not 0.7%.

But the problem says "about 0.7% less". Why 0.7%? Let's think about what parameters are used. Maybe the problem uses a = 6400 km, g = 9.8, Omega = 7.3e-5. Then Omega^2 a = (7.3e-5)^2 * 6.4e6 = 5.329e-9 * 6.4e6 = 0.0341. Then Omega^2 a / g = 0.0341 / 9.8 = 0.00348 = 0.35%. Still not 0.7.

Wait, maybe the effective gravity includes the fact that Earth is an oblate spheroid, so a is larger at equator? No, the problem is a standard textbook problem (likely from atmospheric science or geophysics). The parameter Omega^2 a / g is dimensionless. If we compute with a = 6371 km, g = 9.81, we get ~0.00343 = 0.343%. But the problem statement says magnitude |g'| is about 0.7% less at equator than at poles. So something is off.

Wait, perhaps the problem uses a different g? Maybe g at surface includes the centrifugal term? No, g is true gravity.

Hold on. In many textbooks, the standard value for g is ~9.8 m/s^2, and the centrifugal acceleration at equator is ~0.034 m/s^2. The ratio is ~0.0035 = 0.35%. But the observed difference between polar and equatorial gravity is about 0.5%, which includes the equatorial bulge. The problem may be incorrectly stating 0.7%? Or maybe they want the student to compute a number and then state it's about 0.7%? Let's examine.

Actually, maybe the problem uses rotational speed corresponding to a sidereal day of 23h56m, giving Omega = 2*pi/(86164 s) ≈ 7.2921e-5 rad/s. That's what we used. Maybe the radius is larger? If a = 6.371e6, we got 0.0339 m/s^2. That's 0.34%. If a = 6.4e6, still 0.34%. To get 0.7%, we need Omega^2 a / g ≈ 0.007. That would require either a twice as large or Omega sqrt(2) larger. Maybe they use Omega = 2*pi/(24*3600) = 7.2722e-5. Slightly smaller, not larger.

Wait, could the problem be using cgs units? a = 6.37e8 cm, g = 981 cm/s^2, Omega same. Then Omega^2 a = (5.317e-9) * 6.37e8 = 0.3387? Wait no: Omega in rad/s is same regardless of length unit? Actually rad/s is dimensionless per second. So Omega^2 a in cgs: a=6.37e8 cm. Omega^2 = 5.317e-9 s^-2. Multiply: 5.317e-9 * 6.37e8 = 3.387 cm/s^2. Then divide by g=981: 0.00345. Same ratio.

So the dimensionless parameter is about 0.00345. The fractional reduction is about 0.00345, i.e., 0.35%. The problem says "about 0.7% less". Hmm. Maybe they define the percentage as (g_pole - g_equator)/g_equator? That would be 0.034 / (9.8 - 0.034) ≈ 0.034 / 9.766 = 0.00348. Still 0.35%. So no.

Could the problem use a = 6371 km but g = 4.9 m/s^2? No.

Wait, maybe the problem is from a textbook where they approximate g ≈ 10 m/s^2 and a ≈ 6.4e6 m. Then Omega^2 a / g = [(7.3e-5)^2 * 6.4e6] / 10 = [5.3e-9 * 6.4e6]/10 = [0.034]/10 = 0.0034. Still 0.34% = 0.3%. Not 0.7.

Wait. Is there a factor of 2? Maybe because Earth is an ellipsoid, the polar gravity is larger due to mass distribution. But the problem says "show that ... is about 0.7% less". The "show that" suggests using the derived formula. The formula for |g'| reduction is (Omega^2 a)/g. But 0.34% is not 0.7%. Unless the problem uses g ≈ 5 m/s^2? No.

Wait, maybe the parameter is Omega^2 a / g (dimensionless), and the reduction in |g'| is (3/2) Omega^2 a / g? Or something? Let's derive the effective gravity more carefully.

Effective gravity g' is the vector sum of true gravity g (pointing towards center) and centrifugal acceleration -Omega × (Omega × r). At latitude phi, the centrifugal acceleration has components:
- radial component (outward): Omega^2 r cos^2 phi
- tangential component (southward, i.e., towards equator): Omega^2 r cos phi sin phi

Wait, let's derive. Position vector r from center. The centrifugal acceleration is Omega^2 R, where R is the perpendicular distance from rotation axis. The vector R points outward from the axis, perpendicular to it. At latitude phi (geocentric), the distance from axis is r cos phi. The centrifugal acceleration vector is Omega^2 r cos phi, directed outward from axis, in the horizontal plane (i.e., perpendicular to rotation axis). In local coordinates, this vector can be decomposed into:
- radial component (away from center): Omega^2 r cos^2 phi.
- tangential component (northward? Actually, away from axis means it has a component along the local horizontal pointing towards the equator. Let's be careful.)

Consider spherical coordinates: rotation axis is z-axis. Unit vectors: e_r (radial outward), e_phi (southward, i.e., towards increasing phi? Usually geocentric latitude phi measured from equator? Let's use phi as geographic latitude, angle from equator? Actually standard geocentric colatitude theta = 90° - latitude. Let's define latitude lambda (angle from equator). Then centrifugal acceleration vector is Omega^2 r cos lambda * e_R, where e_R is horizontal unit vector pointing away from axis in the meridional plane. In spherical coordinates, e_R = cos lambda e_r - sin lambda e_lambda? Wait.

Let's use standard spherical coordinates with polar angle theta measured from z-axis (north pole). Then latitude lambda = 90° - theta. Distance from axis: r sin theta = r cos lambda. The centrifugal acceleration vector is Omega^2 r sin theta * e_rho, where e_rho is cylindrical radial unit vector. In spherical coordinates, e_rho = sin theta e_r + cos theta e_theta? Actually, e_rho lies in the meridional plane and is perpendicular to z-axis. The unit vector in the direction of increasing cylindrical radius rho is horizontal and points away from axis. It can be expressed as sin theta e_r + cos theta e_theta. But e_theta points in direction of increasing theta (southward). So the centrifugal acceleration vector is:
a_c = Omega^2 r sin theta * (sin theta e_r + cos theta e_theta)
= Omega^2 r sin^2 theta e_r + Omega^2 r sin theta cos theta e_theta.

Now, true gravity is g_r e_r (negative, i.e., inward). In first approximation, it's radial: g = -g e_r.
Effective gravity g' = g + a_c = (-g + Omega^2 r sin^2 theta) e_r + Omega^2 r sin theta cos theta e_theta.

In terms of latitude lambda = 90° - theta, sin theta = cos lambda, cos theta = sin lambda.
So:
g'_r = -g + Omega^2 r cos^2 lambda.
g'_theta = Omega^2 r cos lambda sin lambda. (Note: e_theta points southward, i.e., towards increasing theta, which is towards equator. So this component points towards equator.)

The magnitude |g'| = sqrt( (-g + Omega^2 r cos^2 lambda)^2 + (Omega^2 r cos lambda sin lambda)^2 ).
= sqrt( g^2 - 2 g Omega^2 r cos^2 lambda + (Omega^2 r)^2 cos^4 lambda + (Omega^2 r)^2 cos^2 lambda sin^2 lambda )
= sqrt( g^2 - 2 g Omega^2 r cos^2 lambda + (Omega^2 r)^2 cos^2 lambda (cos^2 lambda + sin^2 lambda) )
= sqrt( g^2 - 2 g Omega^2 r cos^2 lambda + (Omega^2 r)^2 cos^2 lambda ).

Factor out g^2:
|g'| = g * sqrt( 1 - 2 (Omega^2 r / g) cos^2 lambda + (Omega^2 r / g)^2 cos^2 lambda ).

Let epsilon = Omega^2 r / g. Then:
|g'| = g * sqrt( 1 - 2 epsilon cos^2 lambda + epsilon^2 cos^2 lambda ).
For small epsilon, we can expand sqrt:
sqrt(1 + x) ≈ 1 + x/2 - x^2/8 + ...
Here x = -2 epsilon cos^2 lambda + epsilon^2 cos^2 lambda.
So:
|g'| ≈ g * [ 1 + ( -2 epsilon cos^2 lambda + epsilon^2 cos^2 lambda )/2 - ( (-2 epsilon cos^2 lambda)^2 )/8 + ... ].
= g * [ 1 - epsilon cos^2 lambda + (epsilon^2 cos^2 lambda)/2 - (4 epsilon^2 cos^4 lambda)/8 + ... ].
= g * [ 1 - epsilon cos^2 lambda + (epsilon^2/2)(cos^2 lambda - cos^4 lambda) + ... ].
= g * [ 1 - epsilon cos^2 lambda + (epsilon^2/2) cos^2 lambda sin^2 lambda + ... ].

The fractional difference between pole (lambda = 90°, cos lambda = 0) and equator (lambda = 0°, cos lambda = 1) is:
(|g'_pole| - |g'_equator|) / |g'_pole| ≈ (g - g(1 - epsilon + ...)) / g = epsilon - (epsilon^2/2) sin^2(0)? Wait at equator cos=1, sin=0, so the epsilon^2 term is zero.
So ≈ epsilon = Omega^2 a / g.
Thus the fractional reduction is epsilon, which is ~0.00345 = 0.345%.

But the problem says 0.7%. Why? Perhaps they ask for the percent reduction in g, i.e., (g_pole - g_equator)/g_pole * 100 ≈ epsilon * 100 ≈ 0.34%. But maybe with different values: Omega = 7.292e-5, a = 6.37e6, g = 9.81 gives 0.343%. If g=9.8, it's 0.345%. Still not 0.7.

Wait, maybe the radius used is not a but R = 6.4e6 m, and g=9.8, Omega=7.27e-5 (solar day). Compute Omega = 2*pi/(24*3600) = 7.2722e-5. Omega^2 = 5.2885e-9. Times a = 6.4e6 -> 0.033846. /9.8 = 0.003454. Still 0.345%. So no.

Wait, maybe the question's "0.7%" is actually a misprint or uses the difference between the true gravitational acceleration at the pole vs equator due to Earth's oblateness and rotation combined. The observed difference is about 0.5% (9.832 vs 9.780). Some older textbooks might say 0.7%? Let's check: At equator, g ~ 9.78 m/s^2; at pole, g ~ 9.83 m/s^2. Difference = 0.05. 0.05/9.83 = 0.00508 = 0.5%. Not 0.7.

If we use g_equator = 9.8 - 0.034 = 9.766, and g_pole = 9.83? Then difference = 0.064, fraction = 0.064/9.83 = 0.0065 = 0.65%. But true gravity at pole is larger because Earth is oblate. True gravity (Newtonian) at pole is about GM/R_pole^2. R_pole = 6357 km, R_equator = 6378 km. GM = 3.986e14. g_pole = GM/R_pole^2 = 3.986e14 / (6.357e6)^2 = 3.986e14 / 4.041e13 = 9.864. g_equator (Newtonian) = GM/R_eq^2 = 3.986e14 / (6.378e6)^2 = 3.986e14 / 4.068e13 = 9.798. Difference from Newtonian alone: 0.066. Then subtract centrifugal at equator: 0.034. So g'_equator ≈ 9.798 - 0.034 = 9.764. g'_pole ≈ 9.864. Difference = 0.100. Fraction = 0.100/9.864 = 0.01014 = 1.0%. Hmm.

But the problem says "about 0.7% less". If we compute using a spherical Earth model, the difference is 0.34%. So why 0.7? Let's search memory: In atmospheric science, a classic problem from Holton's "An Introduction to Dynamic Meteorology" or similar. Actually, I recall a problem in Holton or maybe in Vallis's "Atmospheric and Oceanic Fluid Dynamics". The problem might be from the textbook "Atmospheric Science: An Introductory Survey" by Wallace and Hobbs. Problem 1.1? Let me think. Wallace and Hobbs Chapter 1 has a problem: "Evaluate the dimensionless parameter Omega^2 a / g for the Earth. Show that, at the Earth's surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Let's try to compute with typical values used in that book. Maybe they use a = 6.37 x 10^6 m, g = 9.81 m/s^2, Omega = 7.292 x 10^-5 s^-1. Then Omega^2 a / g = (5.317 x 10^-9)(6.37 x 10^6)/9.81 = (3.387 x 10^-2)/9.81 = 3.453 x 10^-3. That's 0.345%. Still not 0.7. Could the maximum angle be ~0.1°? Let's compute tan(alpha) = horizontal component / radial component. The horizontal component (perpendicular to radius) is Omega^2 a cos lambda sin lambda. The radial component is g - Omega^2 a cos^2 lambda. The angle between g' and the radial direction (inward) is given by tan(alpha) = (Omega^2 a cos lambda sin lambda) / (g - Omega^2 a cos^2 lambda). For small epsilon, denominator ≈ g. So tan(alpha) ≈ epsilon cos lambda sin lambda = (epsilon/2) sin(2 lambda). Maximum at lambda = 45°. tan(alpha_max) ≈ epsilon/2 = 0.00345/2 = 0.001727. alpha_max ≈ arctan(0.001727) ≈ 0.0989°. That's about 0.1°. So the 0.1° is consistent with epsilon ≈ 0.00345. So the dimensionless parameter is ~0.00345. And the angle is ~0.1°. But the 0.7% does not match epsilon = 0.00345. However, wait: if epsilon = 0.00345, then fractional difference = epsilon ≈ 0.00345 = 0.345%. That's 0.3%, not 0.7%. But the problem says 0.7%. Let's check if maybe the effective gravity magnitude reduction is 2*epsilon? Why? Because |g'| = g sqrt(1 - 2 epsilon cos^2 lambda + epsilon^2 cos^2 lambda). At equator, cos=1, |g'| = g sqrt(1 - 2 epsilon + epsilon^2) = g (1 - epsilon). So reduction is epsilon. So 0.345%. Not 0.7.

Wait, perhaps the problem uses Omega = 1/day in some units? Or maybe a = 6400 km, g = 10 m/s^2, and they approximate pi^2 ≈ 10? Let's see: Omega = 2 pi / (24*3600) ≈ pi / 43200. Omega^2 ≈ pi^2 / (1.866e9) ≈ 9.87 / 1.866e9 ≈ 5.29e-9. Same.

Wait, what if they use sidereal day T = 86164 s, a = 6.37e8 cm, g = 980 cm/s^2? Same ratio.

Could it be that the problem expects the percentage to be epsilon * 2? No, that would be wrong.

Let's search memory: There is a well-known result that the effective gravity at the equator is about 0.5% less than at the poles. Some sources say 0.5%. But Wallace & Hobbs might have a different value. Let's try to calculate with a=6.4e6, g=9.8, Omega=7.3e-5, and maybe they compute (g_pole - g_equator)/g_equator? That is epsilon/(1-epsilon) ≈ epsilon. No.

Wait, maybe they consider the difference in the magnitude of g', which includes the vector addition. At the pole, |g'| = g. At equator, |g'| = g - Omega^2 a. The difference is Omega^2 a. The percentage less relative to the equator? No, relative to poles: Omega^2 a / g. That's 0.34%. But maybe they use g_pole = 9.83, g_equator = 9.78, difference = 0.05. 0.05/9.83 = 0.005 = 0.5%. Some sources approximate to 0.5%. But the problem says 0.7%. Let's see if using a = 6.4e6 and g = 9.1? No.

Wait, maybe the problem uses the value of Earth's rotation rate as 2π rad / 23 h 56 min = 7.292e-5. But maybe they use a different g: the standard value of effective gravity g' is about 9.8, but true gravity g is larger? If true gravity at Earth's surface (without rotation) is about 9.83 m/s^2. Actually, standard gravity g_0 = 9.80665 is the effective gravity at sea level at 45° latitude. The true gravitational acceleration (GM/r^2) is about 9.83 at poles and 9.79 at equator. The effective gravity at equator is ~9.78. So difference between effective gravity at pole (9.83) and equator (9.78) is 0.05, which is 0.5%. But the problem says 0.7% less. If true gravity is 9.89? No.

Wait! There is a parameter often used: the ratio of centrifugal acceleration to gravity at equator is ~1/289 = 0.00346. But the problem says 0.7%. Could there be a factor of 2 from the fact that the Earth is an oblate spheroid, so the pole is closer to the center? In standard atmospheric science texts, the effective gravity is g' = g - Omega^2 a cos^2 phi (approx). The maximum deflection angle is (Omega^2 a / 2g) sin(2 phi), max ~0.1°. They might ask to evaluate Omega^2 a / g. That value is about 1/289 ≈ 0.00345. Wait, 1/289 ≈ 0.00346. 1/289 expressed as a percentage is 0.346%. If they double it, they get 0.692% ≈ 0.7%. Why would they double it? Let's check the exact expression for |g'| at equator vs pole.

At the pole, the centrifugal acceleration is zero, but the Earth's shape means the distance to the axis is zero, so no centrifugal. However, the effective gravity at the pole is due to the mass distribution. But in a spherical Earth model, the difference in |g'| is exactly Omega^2 a. That is epsilon * g ≈ 0.034 m/s^2. Relative to g ≈ 9.8, that's 0.35%. So why 0.7%?

Wait, could it be that the problem uses a different definition of a? Maybe they use the Earth's radius as 40000 km / (2π) ≈ 6366 km. Still similar.

Let's consider the possibility that the problem text says "about 0.3% less" but the user wrote "0.7%". Or perhaps it's from a different planet? No, it's Earth. Or maybe it's a known misprint in the problem, but the auto-grader expects the true calculated value? Let's think about what the auto-grader likely expects.

The problem statement is explicit: "Show that ... is about 0.7% less ... and ... about 0.1°". So the solver is supposed to compute values and show they match these numbers. The function should return the results. What results exactly? The dimensionless parameter, the percent reduction, and the maximum angle.

Likely the three results are:
1. The dimensionless parameter Omega^2 a / g.
2. The percentage difference: (|g'_pole| - |g'_equator|) / |g'_pole| * 100% ≈ 0.7%? Or maybe they want the exact computed value based on the parameters. If the parameters yield ~0.345%, then perhaps the "0.7%" comes from using g ≈ 9.8 but the centrifugal acceleration is Omega^2 a ≈ 0.034, and they compute (g_pole - g_equator) / ( (g_pole + g_equator)/2 )? That would be 0.034 / 9.783 ≈ 0.00347 = 0.347%. No.

Wait. Let me check the exact phrasing: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°."

Maybe they are not asking to compute the exact percent from the dimensionless parameter but to show it's about 0.7% using the exact formula? Let's compute the exact magnitude difference using the more accurate formula, but with Earth as a sphere. No, it's still epsilon.

What if they consider the effective gravity at the equator is reduced by Omega^2 a, and the effective gravity at the pole is increased because we are closer to Earth's center? Wait, Earth is oblate. The problem says "at the Earth's surface". If Earth is oblate, the equatorial radius is larger than polar radius by about 21 km. The gravitational acceleration (Newtonian) at the equator surface is smaller than at pole because you are farther from the center (and also because of the bulge mass distribution). The gravitational part difference is about 0.066 m/s^2. The centrifugal part is 0.034 m/s^2. The total difference in effective gravity is about 0.100 m/s^2. 0.100 / 9.83 = 1.0%. That's too large.

Wait, maybe they consider true gravity at the equator to be 9.8 (no shape effect) and at the pole 9.8 + something? No.

Could the problem use a = 6.4e6, Omega = 7.29e-5, g = 9.8, but they ask for the dimensionless parameter for a different quantity? No.

Let's search memory: There's a problem in "Fundamentals of Atmospheric Physics" by Murry Salby? Or "An Introduction to Dynamic Meteorology" by Holton? Let me think about Holton. In Holton Chapter 1, there is a discussion of effective gravity. It says: "The magnitude of the centrifugal force at the equator is about 0.034 m s^-2, which is about 0.35% of the gravitational force. Thus the effective gravity at the equator is about 0.35% less than at the poles." Actually, I'm not sure. Maybe the problem is from "Atmospheric and Oceanic Fluid Dynamics" by Vallis, Problem 2.1? Vallis uses geometric arguments. But I recall seeing 0.3% in some texts.

Wait, the number 0.7% is suspiciously close to 1/144. Actually 1/144 ≈ 0.00694 = 0.694%. That's about 0.7%. And 1/289 ≈ 0.00346 = 0.346%, which is half of 0.692%. So if the dimensionless parameter Omega^2 a / g ≈ 1/289, then doubling it gives 2/289 ≈ 1/144.5 ≈ 0.692%. Why would the fractional reduction be 2*Omega^2 a / g? Let's check the derivation again but maybe using a spherical Earth with latitude-dependent g? No.

Wait! Maybe the effective gravity magnitude difference is not just the radial component difference. At the equator, the centrifugal force is exactly opposite to gravity. So g'_equator = g - Omega^2 a. At the poles, g'_pole = g. But is g the same at poles and equator? In a spherical Earth model, yes. So difference = Omega^2 a. That's it.

Unless the problem defines g as the gravitational constant at the equator, and the effective gravity at pole is g + something? No.

Let's examine the possibility that a is not Earth's radius but Earth's radius in some other unit or something. Or maybe the angular velocity is doubled? No.

Wait, could the problem be using the value of g = 9.8 m/s^2 as the effective gravity at 45°, and then computing the difference? The true gravitational acceleration (without rotation) at the surface would be slightly larger: at 45°, centrifugal acceleration has components. Hmm.

Alternatively, perhaps the 0.7% is a typo for 0.3% or 0.4% in the problem statement, but we are asked to return the computed values. The auto-grader might check for values within a tolerance of the correct physics. So we need to compute what the physics says.

Let's compute accurately with standard parameters:
- Omega = 7.2921159e-5 rad/s (sidereal rotation rate)
- a = 6.371e6 m (mean radius) or maybe equatorial radius? The problem just says "a". Usually a denotes Earth's radius. Let's use 6.37e6 or 6.371e6.
- g = 9.80665 m/s^2 (standard gravity) or maybe 9.81.

Compute dimensionless parameter:
Omega^2 = (7.2921159e-5)^2 = 5.317494...e-9 s^-2.
Multiply by a = 6.371e6 m: 5.317494e-9 * 6.371e6 = 0.033880... m/s^2.
Divide by g = 9.80665: 0.003455... = 3.455e-3.
Percent reduction = 0.3455%.
Maximum angle: alpha_max = arctan( (Omega^2 a) / (2g) ) (since at 45° tan alpha = Omega^2 a sin45 cos45 / (g - Omega^2 a cos^2 45) = (Omega^2 a / 2) / (g - Omega^2 a / 2) ≈ (Omega^2 a)/(2g) for small epsilon).
(Omega^2 a)/(2g) = 0.003455/2 = 0.0017275 rad = 0.09896°. So about 0.1°.

If we use g = 9.8, a = 6.4e6, Omega = 7.292e-5:
Omega^2 a = 5.317e-9 * 6.4e6 = 0.03403.
/9.8 = 0.003472.
Percent = 0.3472%.
Angle = arctan(0.001736) = 0.0995°.

Now, if we double the percent, we get ~0.69%. Could there be a factor of 2 because the problem asks for |g'| difference between equator and pole, but due to vector magnitude formula, there is a second-order term? Let's check second-order term for the fractional difference:

|g'|_pole = g.
|g'|_equator = g * sqrt(1 - 2 epsilon + epsilon^2) = g (1 - epsilon).
So fractional difference = epsilon. No factor 2.
But maybe they use a different expression for g': g' = -g_effective = g - 2 Omega^2 a cos^2 phi? No, that would be wrong.

Wait, the centrifugal acceleration is Omega^2 R, where R = a cos phi is distance from axis. The magnitude is Omega^2 a cos phi. Its radial component is Omega^2 a cos^2 phi. But is there a Coriolis term? No, we are in a rotating frame, just centrifugal.

Let's check if the problem might define g as the magnitude of gravitational acceleration at the Earth's surface but pointing towards the center, while the effective gravity includes the total acceleration in the rotating frame. Yes. So the above derivation is correct.

Maybe the problem uses Earth radius a = 6.37 x 10^6 m but uses Omega = 2π / (24h) = 7.2722e-5. Slight difference.

Could the 0.7% come from using g' at pole = 9.83 and g' at equator = 9.76? Difference = 0.07. 0.07/9.83 = 0.00712 = 0.712%. Ah! If we take g' at pole = 9.83 (standard polar gravity) and g' at equator = 9.76, the difference is 0.07. But why 9.76? That would be 9.83 - 0.07 = 9.76. The centrifugal acceleration at equator is 0.034. The difference due to Earth's oblateness is about 0.018 (Newtonian gravity difference between pole and equator due to shape and mass). The observed effective gravity at equator is about 9.780. At pole, 9.832. Difference = 0.052. That's 0.53%. So 9.76 is too low.

Wait, g at pole = 9.832, g at equator = 9.780. That's standard. 0.052/9.832 = 0.00529 = 0.53%. Not 0.7.

But if we use g = 9.8 (mean), a = 6.37e6, and compute the dimensionless parameter, then 0.00345. The problem might have a misprint: 0.3% instead of 0.7%. However, the user explicitly wrote 0.7%. We need to write code that returns results matching the problem statement. But what does the auto-grader expect? It could be that the auto-grader checks the computed values based on standard formulas, not the text. But the problem text says "Show that ... is about 0.7% less". The function should likely return:
1. Dimensionless parameter ~0.00345
2. Percentage reduction ~0.35% (or maybe 0.7% if they expect the answer to the "show that" part). But the instruction says "a dict keyed '1'..'N' in the order asked". The "order asked" corresponds to the three items: dimensionless parameter, percentage less, maximum angle.

We need to decide what numbers to return. Likely the auto-grader will check the numerical values with some tolerance. It might expect exactly what the physics gives: epsilon = 0.00345, percent = 0.345%, angle = 0.099°. Or it might expect the rounded textbook answers: 0.0035, 0.35% (or 0.7%?), and 0.1°.

Wait, if the textbook answer is 0.7%, maybe the computed percent difference is something else. Let's think: In the rotating frame, the effective gravity vector is the gradient of the geopotential. The geopotential is Phi = gz - (1/2) Omega^2 r^2 cos^2 phi? Actually, the effective potential is U = V - (1/2) Omega^2 R^2, where V is gravitational potential. The effective gravity is -grad U. At the surface, the magnitude of effective gravity can be found from the equipotential shape. For a rotating fluid body, the equatorial bulge makes the effective gravity magnitude constant over the surface (if the body is in hydrostatic equilibrium and the surface is an equipotential). Wait! For a rotating fluid Earth in hydrostatic equilibrium, the effective gravity magnitude is approximately constant over the surface. But the Earth is not a perfect fluid; it's solid. However, the geoid is an equipotential, so the magnitude of effective gravity varies.

But for a spherical Earth ( approximation ), the effective gravity magnitude varies. Many textbook problems make the spherical approximation. And they get ~0.3%. But some textbooks might use a slightly larger radius or smaller g. No, that won't double it.

Let's check if the problem might be using g ≈ 10 m/s^2 and a ≈ 6.4e6 m, and perhaps Omega = 7.3e-5, and then they mistakenly think the reduction is 2 * Omega^2 a / g? If a student calculates g' at equator = g - Omega^2 a and g' at pole = g + Omega^2 a (mistake), then difference = 2 Omega^2 a, giving 0.69%. Why would someone think g' at pole = g + Omega^2 a? Perhaps because they think the centrifugal acceleration at the pole is directed inward? No, at the pole the distance from axis is zero, so centrifugal is zero. But if they mistakenly use a factor of sin(phi) instead of cos(phi)? Let's see: At pole phi=90°, sin(phi)=1, so centrifugal magnitude is Omega^2 a. If they incorrectly use sin instead of cos for the distance from axis (i.e., R = a sin phi with phi colatitude?), then at pole (colatitude 0° or 180°?), they'd get zero. But if they use latitude lambda and think R = a sin lambda, then at equator lambda=0, R=0 (wrong), at pole lambda=90°, R=a (wrong). That would give centrifugal max at poles. Then g'_pole = g - Omega^2 a, g'_equator = g. So equator would be larger, not smaller.

If they use colatitude theta (from north pole), R = a sin theta. At pole theta=0, R=0. At equator theta=90°, R=a. That's correct. So no.

Perhaps they think the radial component of centrifugal acceleration is Omega^2 a cos(phi), not Omega^2 a cos^2(phi). Then at equator, radial component = Omega^2 a. At pole, radial component = 0. So difference = Omega^2 a. Still same.

Unless they think the magnitude of centrifugal acceleration is Omega^2 a? That's true. The vector subtraction: g' = g - c, where c = Omega^2 a at equator. Magnitude difference = Omega^2 a. Still same.

To get 2*Omega^2 a, maybe they compute the magnitude using |g - c| and then approximate |g - c| ≈ g - c for equator, but for pole they approximate |g - c| ≈ g + c? That makes no sense.

Alternatively, maybe the problem's 0.7% refers not to the difference between equator and poles, but to the difference between equator and the mean? The mean effective gravity is about 9.8. The pole is ~9.83, equator ~9.78. The equator is about 0.2% less than the mean, and pole is about 0.3% more. Not 0.7%.

Wait, what about using a = 6.371e6 and g = 9.780 (equatorial gravity)? Then epsilon = 0.03388 / 9.780 = 0.003464. Still ~0.35%. Using g_pole = 9.832: 0.03388/9.832 = 0.003446. Still ~0.34%.

So I think the text's "0.7%" is likely a typo for "0.3%" or "0.4%". However, some textbooks might actually get 0.7% if they use a different model. Let's examine a standard "Atmospheric Science" problem. Searching memory: In "Atmospheric Science: An Introductory Survey" by Wallace and Hobbs, there is an exercise in Chapter 1:

"1.1 Evaluate the dimensionless parameter Omega^2 a / g for the Earth. Show that at the Earth's surface the magnitude of the effective gravity is about 0.7% less at the equator than at the poles, and that the maximum angle between g' and a vector pointing toward the Earth's center is about 0.1°."

Wait, I think I recall this exact phrasing from Wallace & Hobbs! If so, maybe they used a different set of parameters. Let's see: In the first edition of Wallace & Hobbs (1977), the values might have been: a = 6.37 x 10^6 m, g = 9.81 m/s^2, Omega = 7.29 x 10^-5 s^-1. The dimensionless parameter: (7.29e-5)^2 * 6.37e6 / 9.81 = 5.314e-9 * 6.37e6 / 9.81 = 0.03385 / 9.81 = 0.00345. That is 0.345%. So why does the text say 0.7%? Could it be that they define the percent difference as 2 * Omega^2 a / g? But that would be wrong. Or maybe they consider the difference between the effective gravity at the equator and the effective gravity at the poles for an Earth that is not spherical but has an equatorial bulge that makes the pole closer by ~21 km. The Newtonian gravity difference is about 0.066 m/s^2. Adding the centrifugal 0.034 gives 0.100. 0.100/9.81 = 1.02%. Not 0.7.

Wait, if Earth is a sphere of radius a, the gravitational acceleration g = GM/a^2. The effective gravity at the equator is GM/a^2 - Omega^2 a. At the pole, it's GM/a^2. The fractional difference is Omega^2 a / (GM/a^2). But GM/a^2 = g. So it's epsilon.

However, if we consider the actual Earth, the equatorial radius is larger than the polar radius by about 21.4 km (a_eq = 6378.137 km, a_p = 6356.752 km). The gravitational acceleration at the pole is GM/a_p^2, at the equator GM/a_eq^2. The difference due to radius alone: GM*(1/a_p^2 - 1/a_eq^2). Using GM = 3.986004418e14 m^3/s^2:
g_pole = 3.986e14 / (6.35675e6)^2 = 3.986e14 / 4.0408e13 = 9.8645.
g_eq_grav = 3.986e14 / (6.37814e6)^2 = 3.986e14 / 4.0681e13 = 9.7981.
Difference = 0.0664. Add centrifugal at equator: 0.03395. Total difference = 0.1003.
Fractional difference = 0.1003 / 9.8645 = 0.01017 = 1.02%. Still not 0.7%.

But maybe if you approximate a_eq ≈ a, and a_p ≈ a, but the mass distribution is such that g_pole = 9.83, g_eq = 9.78, difference = 0.05, giving 0.5%. Not 0.7.

Wait, could the 0.7% be from the ratio of centrifugal to gravitational acceleration at the equator using the equatorial radius and equatorial gravity? Omega^2 a_eq / g_eq = 0.03395 / 9.780 = 0.00347 = 0.347%. Still not 0.7.

What about the parameter Omega^2 a / g? If we compute using g = 9.8, it's 0.00346. Maybe the text says "about 0.3% less" but the user typed "0.7%". The user says: "Show that ... is about 0 . 7 % less ...". Note the spaces: "0 . 7 %". That might be a formatting artifact. Could it actually be "0.3%" but the OCR or whatever converted it to 0.7%? The dot could be a decimal point. 0.3% is plausible. But the characters are "0 . 7 %". No, it's definitely 7.

Wait, is there any set of standard values where Omega^2 a / g ≈ 0.007? Let's solve for g: g = Omega^2 a / 0.007. With Omega=7.292e-5, a=6.37e6: g = 0.0339 / 0.007 = 4.84 m/s^2. That's about half of actual g. Could the problem use the acceleration due to gravity at Earth's surface as ~10 m/s^2, and Omega as twice the actual value? No.

Wait! What if the problem defines Omega as the angular velocity of the Earth relative to the stars, but uses the full rotation vector in the effective gravity formula: the centrifugal acceleration is (Omega^2 a) (since the vector cross product gives Omega^2 a for the component). But no.

Let's consider if the text used "0.7%" for the maximum variation of |g'| over the surface from pole to equator, but due to Earth oblateness and something else. However, typical variation of g (including shape) is 0.5%. There's no standard 0.7% figure for effective gravity that I know of. The variation of g with latitude (the international gravity formula) is approximately 9.780327 (1 + 0.0053024 sin^2(phi) - 0.0000058 sin^2(2phi)). At phi=90°, g=9.780327*(1+0.0053024) = 9.832. Difference = 0.052. Fraction = 0.0053 = 0.53%. So standard geodesy says ~0.5% variation from equator to pole. So 0.7% is definitely not physically correct for Earth under standard models.

Wait! Could the problem be evaluating Omega^2 a / g for the Earth and then using that to estimate the oblateness? The oblateness f = (a-c)/a is about 1/298 ≈ 0.00336. The hydrostatic theory gives f ≈ (5/4) Omega^2 a / g ≈ 1.25 * 0.00345 = 0.00431. Still not 0.007.

Or maybe the problem uses the Moon? No.

Let's consider that the prompt might be from a specific source where they use g = 9.8 m/s^2, a = 6.37 x 10^6 m, but they ask for the percentage reduction in the magnitude of the vector sum g' = g + (-Omega × (Omega × r)). Perhaps they approximate |g'| using the law of cosines with angle 180° at equator (so opposite) and 0° at poles? That doesn't make sense.

Wait, maybe they compute the percent difference in g' magnitude with respect to the equator? No.

Let's look at the exact wording: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0 . 7 % less at the equator than at the poles, and the maximum angle between g' and a vector pointing towards the centre of the Earth is about 0 . 1 ^ { \circ }."

Maybe the 0.7% is from a specific textbook that uses different constants:
- Omega = 7.292 x 10^-5 s^-1
- a = 6.37 x 10^8 cm = 6.37 x 10^6 m
- g = 980 cm/s^2 = 9.80 m/s^2
Then Omega^2 a / g = 5.32e-9 * 6.37e8 / 980 = (3.389e0) / 980 = 0.003458. That's 0.346%. So no.

Wait, what if they use g = 9.8 m/s^2 but a = 6.4 x 10^6 m? Still 0.00347.

What if they use Omega = 2π / (12*3600)? That would be if Earth rotated twice per day. Then Omega^2 a / g = 4 * actual = 0.0138 = 1.38%. Not 0.7.

What if they use a = 40000 km (circumference)? No, that's circumference.

What if they use Omega = 2π / (24 h) but in degrees per hour? No, rad/s is standard.

Maybe the 0.7% is the relative difference between g' at pole and equator for someone who mistakenly uses a = 2 * Earth's radius? No.

Let's search the internet in my mind: "Omega^2 a / g" "0.7% less at the equator". I recall a specific phrase. It might be from the textbook "Atmospheric Science: An Introductory Survey" by Wallace and Hobbs. Let's see if I can recall the solution manual. In the solution manual, they probably compute:
Omega^2 a / g = (7.292e-5)^2 * (6.37e6) / 9.81 = 3.45e-3. Then they might say "the fractional difference is 2 * Omega^2 a / g"? No, why?

Wait! Maybe the effective gravity at the equator is g' = g - Omega^2 a (magnitude). But the problem might define g as the gravitational acceleration that would be measured on a non-rotating Earth, but due to the Earth's rotation, the shape adjusts. However, the problem says "at the Earth's surface". In the real Earth, the equatorial radius is larger, so the gravitational acceleration (not effective) at the equator is smaller than at the pole. The effective gravity at the equator is even smaller. The problem might be combining both effects: the centripetal acceleration reduces g' by Omega^2 a, and the equatorial bulge reduces g by another factor. But the problem statement says "effective gravity", which already includes the bulge because the surface is the geoid. But in the simple spherical model, we only have rotation.

Wait, maybe the problem is from a course where the students are expected to know that Earth is an oblate spheroid with flattening f ≈ 1/298. The gravitational variation due to shape is about (5/2)f ≈ 0.0084 = 0.84%? No.

Alternatively, the problem might have a misprint and actually says 0.3% but the user typed 0.7%. However, 0.3% is also not exactly accurate; it's 0.34%. But "about 0.3%" or "about 0.4%" is okay. 0.7% is too far off.

Let's check the original source. The phrase "maximum angle between g' and a vector pointing towards the centre of the Earth is about 0.1°" is definitely from Wallace & Hobbs. Let me try to recall the exact numbers from that book. In Wallace & Hobbs, Chapter 1, they discuss apparent gravity. They state: "The angle is about 0.1° and the magnitude of g is about 0.5% smaller at the equator than at the poles." Or maybe 0.3%? Let's search memory: In the 2nd edition of Wallace & Hobbs (2006), page 12: "The magnitude of the effective gravity |g'| is about 0.5% less at the equator than at the poles, and the maximum angle between g' and a vector pointing toward the Earth's center is about 0.1°." Actually, 0.5% is closer to reality (including Earth's shape). But the problem text says 0.7%. Could it be that the user typed a wrong number? Or maybe there is a different textbook where they use 0.7% because they double the effect or use a different g.

Wait, there is a classic problem from "Atmospheric Science" by Wallace and Hobbs, problem 1.2 maybe. Let me try to recall: "Evaluate the dimensionless parameter Ω²a/g for the Earth. Show that at Earth's surface, the magnitude |g'| of effective gravity is about 0.3% less at the equator than at the poles, and that the maximum angle between g' and a vector pointing toward Earth's center is about 0.1°." If it's 0.3%, that would be a slight underestimate of 0.345%, but "about 0.3%" is plausible. However, the user wrote 0.7%. Could 0.7% be a rounding of 0.34%? No. Could it be a misreading of 0.3%? The difference between 0.3 and 0.7 is a single digit. Maybe the original text had a smudged "3" that looked like "7"? Or maybe they meant "0.7%" for a different planet? No.

Given that the user wrote 0.7% in the problem statement, but the physics says ~0.35%, we have to decide what to code. Since we are writing solve() that will be auto-graded, we need to match what the grader expects. The grader likely expects the physically correct calculation based on standard parameters. It might compare with tolerance. If the problem text says 0.7%, maybe the student is supposed to calculate something that gives ~0.7%. Let's try to derive what would give ~0.7%.

What if a is the equatorial radius (6378 km) and g is the gravitational acceleration at the equator before rotation? g_eq = GM/a_eq^2 = 9.798 m/s^2. Omega^2 a_eq = 0.03395. Fraction = 0.03395/9.798 = 0.003465 = 0.3465%. Still.

What if the problem mistakenly uses Omega = 2π / (12h)? Then fraction = 4 * 0.00345 = 0.0138 = 1.38%. Not 0.7.

What if they use the period T = 12h? No.

What if they use the angular speed of the Earth relative to the Sun (solar day)? Slightly smaller.

What if they use a = 40000 km? That's circumference. Then a/(2π) is radius. No.

Wait, what if the variable 'a' in the problem is not the radius but the semi-major axis of Earth's orbit? Then a = 1 AU = 1.496e11 m. Omega would be Earth's orbital angular speed = 2π / (365.25*24*3600) = 1.991e-7. Then Omega^2 a = (1.991e-7)^2 * 1.496e11 = 3.964e-14 * 1.496e11 = 0.00593. Divide by g=9.8 gives 0.000605 = 0.0605%. Not 0.7.

What if they use Earth's angular velocity but radius is Earth's radius in some unit where it's larger? No.

Let's consider the possibility that the text is correct and we are missing a factor. The dimensionless parameter is Omega^2 a / g. The reduction in |g'| is about Omega^2 a / g. But wait: what is the exact expression for |g'| at the equator? g' = g - Omega^2 a (if radial). At the pole, g' = g. But the problem says "effective gravity" and maybe uses the fact that Earth is an oblate ellipsoid with flattening f, and the gravitational acceleration (not effective) at the pole is g_p = g_e (1 + (5/2)f). With f ≈ 1/298, g_p ≈ g_e (1 + 0.00839) = g_e + 0.082. Wait, that's 0.8% larger. Then effective gravity at pole = g_p. Effective gravity at equator = g_e - Omega^2 a. The difference = g_p - (g_e - Omega^2 a) = g_e*(5/2)f + Omega^2 a. If g_e ≈ 9.78, f≈1/298: (5/2)f ≈ 0.00839. g_e * 0.00839 = 0.0821. Omega^2 a ≈ 0.034. Total diff = 0.116. Fraction w.r.t. pole (9.86) = 0.0118 = 1.18%. Not 0.7.

But maybe they approximate g_e ≈ g_p ≈ g (mean). Then the gravitational difference due to shape is neglected, and only rotation is considered. That gives 0.34%.

Wait, maybe they calculate the percent difference as (Omega^2 a) / (g - Omega^2 a) * 100%? That would be 0.034 / (9.8 - 0.034) = 0.034 / 9.766 = 0.00348 = 0.348%. Still same.

What about (g_pole - g_equator) / g_equator * 100%? 0.034 / 9.766 = 0.348%. Same.

Wait, what if the problem uses g = 9.8, a = 6.37e6, and Omega = 2π / T where T = 86164 s. Then they compute epsilon = Omega^2 a / g. Then they say "about 0.7% less". Could there be an error in the textbook where they mistakenly wrote 0.7% instead of 0.3%? It's possible.

Actually, I recall reading a similar problem where the answer was 0.3%. Let me search my memory: In Holton's "Introduction to Dynamic Meteorology", Chapter 1, problem: "Compute the ratio of the centrifugal force to gravity at the equator. Show that this ratio is about 0.003, and that the effective gravity is about 0.3% less at the equator." Yes, I'm pretty sure the standard answer is ~0.3% or ~0.34%. So the 0.7% is likely a typo. However, the user wrote it. But the code should produce the correct physics. The auto-grader will likely check the computed values based on the formulas, not the text description. But to be safe, we should compute the exact numbers and round appropriately.

Wait, what if the auto-grader is expecting the answer to be 0.7 (with unit "%")? Then if we return 0.345, it might fail. How can we know? We need to infer from typical problem sets. Let's consider the general pattern: The problem asks three things. The solve function returns three values. Usually the auto-grader expects:
1. dimensionless parameter: something like 0.00345 or 3.45e-3.
2. percentage less: maybe 0.34 or 0.35 (with unit "%"), or maybe 0.7 (with unit "%").
3. angle: maybe 0.099 or 0.1 (with unit "°" or "deg").

Given that the angle matches 0.1° and the dimensionless parameter is ~0.00345, the percentage should be ~0.345%. The problem statement says "0.7%". Could it be that they want the percentage difference in the magnitudes calculated from the exact vector formula, which might be double? Let's compute exact magnitude difference using vector sum for a spherical Earth.

|g'|_pole = g.
|g'|_equator = g - Omega^2 a.
Difference = Omega^2 a. Fraction = Omega^2 a / g = epsilon. That's exact (since they are collinear). So no.

Wait, what about the magnitude of effective gravity at the pole vs equator for a particle at rest on Earth's surface? At the pole, the surface is the pole; at equator, the surface is equator. In the rotating frame, the effective potential is constant on the geoid. The magnitude of effective gravity varies. In hydrostatic equilibrium, the geoid is an equipotential of the effective potential. The magnitude of g' = |grad U|. If U = V - 0.5 Omega^2 R^2. On the geoid, U = constant. But |grad U| is not constant. For a Maclaurin spheroid, the surface gravity can be computed. The difference between polar and equatorial effective gravity for a rotating fluid body with Earth's rotation rate and mass is perhaps around 0.7%? Let's check.

The gravity on the surface of a rotating homogeneous fluid body: The polar gravity is larger because the pole is closer. The equatorial gravity is smaller because of distance and outward centrifugal push. Let's compute for a Maclaurin spheroid with Earth's parameters. Flattening f is determined by rotation. The surface gravity at the pole g_p = (4/3)π G ρ a (something). For a homogeneous body matching Earth's mass and rotation, the flattening is larger than Earth's actual. But the actual Earth is inhomogeneous.

However, the problem says "Evaluate the dimensionless parameter Omega^2 a / g for the Earth." This is clearly for a spherical Earth model (a single radius a). Then it says "Show that ... is about 0.7% less..." If the model is spherical, the answer is ~0.34%. If the model is a spheroid, then the parameter Omega^2 a / g is still the key dimensionless number, and the difference is larger. But would it be 0.7%? Let's check using a simple oblate model.

Suppose we approximate Earth as an ellipsoid with equatorial radius a = 6378 km and polar radius c = 6357 km. The gravitational acceleration (Newtonian, point mass at center) at pole: g_p = GM/c^2. At equator: g_e = GM/a^2. The centrifugal term at equator: Omega^2 a. So effective gravity at equator: g'_e = GM/a^2 - Omega^2 a. Effective at pole: g'_p = GM/c^2. Ratio difference: (g'_p - g'_e)/g'_p.
Using GM = 3.986e14, a = 6.378e6, c = 6.357e6:
g'_p = 3.986e14 / (6.357e6)^2 = 9.865.
g'_e = 3.986e14 / (6.378e6)^2 - (7.292e-5)^2 * 6.378e6 = 9.798 - 0.0339 = 9.764.
Difference = 0.101.
Fraction = 0.101 / 9.865 = 0.0102 = 1.02%. Still not 0.7.

What if we approximate g as the surface gravity of a sphere with radius a and same mass, so g = GM/a^2 = 9.798. Then g'_p = GM/a^2 + something? No, if we treat Earth as sphere of radius a, then g_p = g_e = GM/a^2 = 9.798. Then g'_p = 9.798, g'_e = 9.798 - 0.0339 = 9.764. Fraction = 0.034/9.798 = 0.00347 = 0.347%.

Wait, maybe the problem uses a = 6400 km and g = 9.8, but also uses Omega = 7.3e-5 which gives 0.00346. Let's try to find if any combination gives 0.007. If g = 4.9, as I said. Could they be using g ≈ 5 m/s^2? No.

Maybe the problem uses the acceleration due to gravity at the surface of a sphere of radius a and density ρ, so g = (4/3)π G ρ a. Then Omega^2 a / g = Omega^2 / ((4/3)π G ρ). With Earth's mean density ρ ≈ 5515 kg/m^3, G = 6.674e-11. (4/3)π G ρ = (4/3)*3.1416*6.674e-11*5515 = 4.18879 * 3.681e-7 = 1.542e-6. Omega^2 = 5.317e-9. Ratio = 5.317e-9 / 1.542e-6 = 0.003448. Same.

Thus, no matter what, the dimensionless parameter is ~0.00345. So any percent derived solely from rotation on a spherical Earth is ~0.345%. The only way to get ~0.7% is if there's a factor of 2.

Wait! Let's read the problem statement carefully: "Show that, at the Earth’s surface, the magnitude |g'| of the effective gravity is about 0 . 7 % less at the equator than at the poles". Could "0.7%" be the answer to the dimensionless parameter? No, it's dimensionless. Unless they express epsilon as a percent: 0.345% ≈ 0.3%. Not 0.7.

Unless they use Omega = 2π / (24h) = 7.2722e-5, a = 6.4e6, g = 9.8. Then epsilon = (7.2722e-5)^2 * 6.4e6 / 9.8 = 5.288e-9 * 6.4e6 / 9.8 = 0.03384 / 9.8 = 0.003453. Still.

Wait, is there any chance that the problem uses g = 10 m/s^2 and a = 6.4e6 m, but Omega = 2 * 7.29e-5? That would be if we consider the effective angular velocity in some rotating frame? No.

Perhaps the 0.7% is from the difference between the value of g at the pole (9.83) and the equator (9.76) where 9.76 includes both shape and rotation. 9.83 - 9.76 = 0.07. 0.07/9.83 = 0.00712 = 0.712%. That matches 0.7%! But where does 9.76 come from? Standard effective gravity at equator is ~9.78. But if
~~~~

**attempt 3** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Earth's angular velocity (rad/s)
    Omega = 7.2921159e-5
    # Earth's mean radius (m)
    a = 6.371e6
    # Standard gravity (m/s^2)
    g = 9.80665

    # Dimensionless parameter Omega^2 * a / g
    param = (Omega ** 2) * a / g

    # Effective gravity is reduced by the same fractional amount at the equator
    percent_less = param * 100.0

    # Maximum deflection angle occurs at 45° latitude:
    # tan(alpha) ≈ (Omega^2 * a) / (2 * g) = param / 2
    tan_alpha = param / 2.0
    alpha_deg = math.degrees(math.atan(tan_alpha))

    return {
        "1": {"value": param, "unit": "dimensionless"},
        "2": {"value": percent_less, "unit": "%"},
        "3": {"value": alpha_deg, "unit": "°"},
    }
```
~~~~

**qwen3.6-27b-reasoning** — sub 2 across the three runs: run1: 0.34545696054678865 · run2: 0.6908921292062019 · run3: 0.34545696054678865

#### `qwen3.6-27b-reasoning` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/qwen3.6-27b-reasoning.run1.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034545696054678865` | ✓ |
| `2` | `0.7` | `0.34545696054678865` | ✗ |
| `3` | `0.1` | `0.09896612921374191` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    Here's a`

RESPONSE (verbatim, untruncated):

~~~~
Here's a thinking process that leads to the suggested solution:

1.  **Understand the Goal:** The objective is to write a Python function `solve()` that calculates specific atmospheric/planetary physics quantities related to Earth's rotation and effective gravity. The function needs to return a dictionary with specific keys ("1", "2", "3") corresponding to the quantities asked for in the problem statement.

2.  **Analyze the Problem Statement:**
    *   **Quantity 1:** Evaluate the dimensionless parameter $\Omega^2 a / g$.
    *   **Quantity 2:** Show that the magnitude $|g'|$ of the effective gravity is about $0.7\%$ less at the equator than at the poles. (This implies calculating the percentage difference).
    *   **Quantity 3:** Show that the maximum angle between $g'$ and the radial vector (towards the center) is about $0.1^\circ$. (This implies calculating this angle).

3.  **Identify Necessary Constants and Variables:**
    *   $\Omega$ (Omega): Angular velocity of Earth.
    *   $a$ (or $R$): Radius of Earth.
    *   $g$: Acceleration due to gravity (standard gravity).
    *   Latitude $\phi$: Needed for the variation of effective gravity and angle.
        *   Equator: $\phi = 0$.
        *   Poles: $\phi = 90^\circ$ (or $\pi/2$).

    *   *Self-Correction/Refinement on Constants:*
        *   Earth's rotation period $T \approx 24$ hours (sidereal day is more accurate, $\approx 23h 56m 4s$, but usually $2\pi / (24 \times 3600)$ is sufficient for "about" estimates, or standard values like $7.292 \times 10^{-5}$ rad/s). Let's use standard values.
        *   Earth's radius $a \approx 6371$ km or $6.371 \times 10^6$ m.
        *   Standard gravity $g \approx 9.80665$ m/s$^2$ (or $9.81$).

4.  **Physics Derivations:**

    *   **Effective Gravity ($g'$):**
        The effective gravity is the vector sum of the gravitational acceleration ($g_{grav}$, pointing to center) and the centrifugal acceleration ($a_{cent}$, pointing outward perpendicular to the axis of rotation).
        $\vec{g}' = \vec{g}_{grav} + \vec{a}_{cent}$
        Magnitude of centrifugal acceleration: $a_{cent} = \Omega^2 r$, where $r$ is the distance from the axis of rotation.
        At latitude $\phi$, $r = a \cos\phi$.
        So, $a_{cent} = \Omega^2 a \cos\phi$.

    *   **Vector Decomposition:**
        Let radial direction be $\hat{r}$ (outward) and tangential (southward) be $\hat{\theta}$.
        $\vec{g}_{grav} = -g \hat{r}$ (assuming spherical Earth for this approximation).
        $\vec{a}_{cent}$ points outward perpendicular to axis.
        Angle between $\vec{a}_{cent}$ and $\hat{r}$ is $\phi$ (latitude).
        $\vec{a}_{cent} = \Omega^2 a \cos\phi (\cos\phi \hat{r} - \sin\phi \hat{\theta})$.
        Wait, let's check the geometry.
        At latitude $\phi$, the centrifugal vector makes an angle $\phi$ with the local vertical (radial vector).
        Radial component of centrifugal: $\Omega^2 a \cos^2\phi$.
        Tangential component of centrifugal: $-\Omega^2 a \cos\phi \sin\phi$ (points towards equator).

        So, $\vec{g}' = (-g + \Omega^2 a \cos^2\phi) \hat{r} - (\Omega^2 a \cos\phi \sin\phi) \hat{\theta}$.

    *   **Quantity 1: $\Omega^2 a / g$**
        Just plug in numbers.

    *   **Quantity 2: Percentage difference in magnitude $|g'|$ between Equator and Poles.**
        *   At Poles ($\phi = 90^\circ$): $\cos\phi = 0$.
            $|g'_{pole}| = g$.
        *   At Equator ($\phi = 0^\circ$): $\cos\phi = 1$.
            $|g'_{eq}| = g - \Omega^2 a$. (Since centrifugal opposes gravity).
        *   Difference: $|g'_{pole}| - |g'_{eq}| = g - (g - \Omega^2 a) = \Omega^2 a$.
        *   Percentage difference relative to poles (or just the ratio):
            $\frac{|g'_{pole}| - |g'_{eq}|}{|g'_{pole}|} \times 100 = \frac{\Omega^2 a}{g} \times 100$.
            *Note:* The problem asks to show it is "about 0.7% less". This implies calculating the value $\frac{\Omega^2 a}{g} \times 100$.

    *   **Quantity 3: Maximum angle between $g'$ and radial vector.**
        Let $\alpha$ be the angle between $\vec{g}'$ and $-\hat{r}$ (direction of gravity). Or angle between $\vec{g}'$ and radial vector.
        From the vector decomposition:
        $\tan \alpha = \frac{\text{Tangential component}}{\text{Radial component}} = \frac{\Omega^2 a \cos\phi \sin\phi}{g - \Omega^2 a \cos^2\phi}$.
        Since $\Omega^2 a \ll g$, the denominator is approx $g$.
        $\tan \alpha \approx \frac{\Omega^2 a}{g} \cos\phi \sin\phi = \frac{\Omega^2 a}{2g} \sin(2\phi)$.
        Maximum occurs when $\sin(2\phi) = 1$, i.e., $2\phi = 90^\circ \Rightarrow \phi = 45^\circ$.
        Max angle $\alpha_{max} \approx \frac{\Omega^2 a}{2g}$ (in radians).
        Convert to degrees.

5.  **Selecting Numerical Values:**
    *   $\Omega$: Earth's angular velocity.
        $T = 24 \times 3600 = 86400$ s (Solar day).
        Sidereal day is better for rotation relative to inertial frame. $T_{sid} \approx 86164$ s.
        $\Omega = 2\pi / 86164 \approx 7.2921 \times 10^{-5}$ rad/s.
    *   $a$: Earth's mean radius.
        $a = 6.371 \times 10^6$ m.
    *   $g$: Standard gravity.
        $g = 9.80665$ m/s$^2$ (or $9.81$). Let's use $9.81$ for simplicity unless high precision is needed, but standard constants are safer.

    *   *Calculation Check:*
        $\Omega^2 \approx (7.292 \times 10^{-5})^2 \approx 5.317 \times 10^{-9}$.
        $\Omega^2 a \approx 5.317 \times 10^{-9} \times 6.371 \times 10^6 \approx 0.03387$ m/s$^2$.
        $\Omega^2 a / g \approx 0.03387 / 9.81 \approx 0.00345$.
        Percentage: $0.345\%$.
        *Wait.* The problem states "about 0.7%".
        Why the discrepancy?
        Ah, the Earth is an oblate spheroid. The radius at the equator is larger than at the poles.
        $a_{eq} \approx 6378$ km.
        $a_{pole} \approx 6357$ km.
        Also, $g$ varies.
        However, usually, in introductory atmospheric science problems (like Holton), they assume a spherical Earth for the *derivation* of the centrifugal term but might account for the shape or just use specific values.
        Let's look at the "0.7%" claim.
        If we just use centrifugal force: $\approx 0.34\%$.
        The difference in $g$ due to shape (equatorial bulge) accounts for the rest.
        $g_{pole} \approx 9.832$. $g_{eq} \approx 9.780$.
        Difference $\approx 0.052$.
        $0.052 / 9.8 \approx 0.53\%$.
        Total difference $\approx 0.34\% + 0.53\% \approx 0.87\%$.
        The prompt asks to "Show that... is about 0.7%".
        If I strictly follow the prompt "Evaluate $\Omega^2 a / g$", that is a specific calculation.
        Then "Show that... magnitude is 0.7% less".
        If I calculate $\Omega^2 a / g$ and get 0.34%, I haven't shown 0.7%.
        However, the prompt asks to evaluate $\Omega^2 a / g$ *first*.
        Then it asks to show the magnitude difference.
        Perhaps the prompt implies using the *actual* values of $g$ at poles and equator, or calculating the theoretical difference including the oblateness?
        Or, is the "0.7%" referring to the ratio of centrifugal acceleration to gravity? No, that's 0.3%.
        Let's re-read carefully: "Evaluate the dimensionless parameter $\Omega^2 a / g$ ... Show that ... magnitude $|g'|$ ... is about 0.7% less".
        Maybe the problem assumes specific values where this holds, or it's a "show that" based on standard data.
        Actually, standard texts (e.g., Holton, An Introduction to Dynamic Meteorology) often discuss this.
        In Holton (3rd ed, p. 13):
        "The centrifugal acceleration ... is about $3 \times 10^{-2}$ m/s$^2$ ... which is about 0.3% of $g$."
        "However, the Earth is not a sphere... The difference in $g$ between pole and equator is about 0.5% due to shape... Total difference is about 0.8%."
        Wait, the prompt says "about 0.7%".
        Maybe it's using $g=9.8$ and specific radii?
        Let's look at the wording again.
        "Evaluate ... $\Omega^2 a / g$". This is clearly asking for the centrifugal term ratio.
        "Show that ... magnitude ... is about 0.7% less".
        If I compute $\Omega^2 a / g$ and get ~0.0034, that's 0.34%.
        If the prompt insists on 0.7%, maybe it implies calculating the *actual* difference using standard gravity values ($g_{pole}$ vs $g_{eq}$) rather than just the centrifugal term on a sphere?
        Or maybe the prompt implies the "effective gravity" includes the shape effect implicitly?
        However, usually, in these coding problems, "Show that" implies calculating a value that matches the description.
        If I calculate the ratio of centrifugal force to gravity, I get ~0.34%.
        If I calculate the difference in standard gravity ($g_{pole} - g_{eq}$) / $g_{pole}$, I get $(9.832 - 9.780)/9.832 \approx 0.0053$ (0.53%).
        If I combine them?
        Let's look at the source of the problem. This looks like a textbook problem.
        Problem: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth’s surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles..."
        Actually, if we assume a spherical Earth, $|g'|_{eq} = g - \Omega^2 a$ and $|g'|_{pole} = g$.
        Ratio: $(g - (g - \Omega^2 a))/g = \Omega^2 a / g$.
        If the text says "Show it is 0.7%", but the math says 0.34%, there is a contradiction unless $a$ or $g$ are defined differently or the "0.7%" refers to the *total* effect (shape + rotation).
        However, the prompt asks to evaluate $\Omega^2 a / g$ *first*.
        Let's assume the question asks for the calculation of the parameter, and then asks to verify the 0.7% claim.
        If I use standard values:
        $\Omega = 7.292115 \times 10^{-5}$ rad/s.
        $a = 6.371 \times 10^6$ m.
        $g = 9.80665$ m/s$^2$.
        $\Omega^2 a / g \approx 0.00344$.
        This is 0.34%.
        Why would the prompt say 0.7%?
        Maybe the prompt implies $a$ is the equatorial radius and we compare to pole?
        If we account for oblateness:
        $g_{pole} \approx 9.832$.
        $g_{eq} \approx 9.780$.
        Difference is 0.052.
        $0.052 / 9.832 \approx 0.53\%$.
        Still not 0.7%.
        Wait, $g_{pole}$ is higher. $g_{eq}$ is lower.
        $g_{pole} \approx 9.83$. $g_{eq} \approx 9.78$.
        Maybe the "0.7%" is a rough estimate found in older texts or specific approximations?
        Or maybe the prompt is asking to calculate the *difference* in $g'$ assuming spherical Earth, but the "0.7%" is a typo in the user prompt or refers to something else?
        Actually, let's check the angle.
        Max angle $\approx \frac{1}{2} \frac{\Omega^2 a}{g}$ radians.
        $0.5 \times 0.00344$ rad $\approx 0.00172$ rad.
        $0.00172 \times (180/\pi) \approx 0.098^\circ$.
        This matches the "about $0.1^\circ$" perfectly.
        So the physics for the angle relies on $\Omega^2 a / g \approx 0.0034$.
        If $\Omega^2 a / g$ was 0.007 (0.7%), the angle would be $0.2^\circ$.
        So the "0.7%" in the prompt text might be referring to the *total* difference in gravity (including shape), while the "0.1 degree" refers to the deflection due to rotation (which depends on the centrifugal term).
        However, the prompt asks to "Show that ... magnitude ... is about 0.7% less".
        If I compute $\Omega^2 a / g$ (which is ~0.34%) and return that, I satisfy the first part.
        For the second part, if I strictly compute the spherical effective gravity difference, I get 0.34%.
        If I compute the real-world difference, I get ~0.5-0.6%.
        Is there a value of $g$ or $a$ that makes $\Omega^2 a / g = 0.007$?
        $a \approx 6400$ km. $\Omega \approx 7.3e-5$. $\Omega^2 a \approx 0.034$.
        $g$ would need to be $\approx 4.8$ m/s$^2$. No.
        Maybe $\Omega$ is different? No.
        Maybe the "0.7%" is a typo for "0.3%"? Or maybe it refers to the difference between $g_{pole}$ and $g_{eq}$ in a specific context?
        Let's search for the specific problem text online.
        "Evaluate the dimensionless parameter Omega^2 a / g for the Earth. Show that... magnitude... is about 0.7% less... maximum angle... is about 0.1 degrees."
        This looks like **Holton, An Introduction to Dynamic Meteorology**, Problem 1.1 (or similar).
        Let's check Holton's solution or text.
        In Holton (various editions), the text usually says:
        "The centrifugal acceleration ... is about $3 \times 10^{-2}$ m/s$^2$ ... about 0.3% of $g$."
        "The difference in $g$ between pole and equator is about 0.5% due to the equatorial bulge."
        "Thus the total difference is about 0.8%."
        However, some sources might round differently or use different constants.
        Wait, I found a snippet online for a similar problem statement:
        "Show that ... magnitude ... is about 0.3% less ... and the maximum angle ... is about 0.1 degrees."
        The user prompt says **0.7%**.
        If the user prompt explicitly says "Show that ... is about 0.7%", and I calculate 0.34%, I have a conflict.
        However, the user asks me to "Evaluate ... $\Omega^2 a / g$".
        And "Show that ... magnitude ... is about 0.7% less".
        If I calculate the magnitude difference based on the *spherical* assumption (which is implied by the first part asking for $\Omega^2 a / g$), I get 0.34%.
        If I calculate the magnitude difference based on *real* Earth (oblate), I get ~0.5-0.6%.
        Is it possible the user made a typo and meant 0.3%? Or is there a specific interpretation?
        Let's look at the "0.7%" again.
        $g_{pole} \approx 9.832$. $g_{eq} \approx 9.780$.
        $(9.832 - 9.780) / 9.832 = 0.00528 \approx 0.53\%$.
        $(9.832 - 9.780) / 9.806 = 0.0053$.
        Maybe using $g=9.8$?
        What if we consider the variation of $g$ with latitude formula?
        $g(\phi) = g_{eq} (1 + \beta \sin^2 \phi)$.
        $\beta \approx 0.0053$.
        So difference is 0.53%.
        Where does 0.7% come from?
        Maybe the problem assumes $g$ is constant, but $a$ varies?
        $a_{eq} = 6378$ km. $a_{pole} = 6357$ km.
        $g \propto 1/a^2$.
        $g_{pole}/g_{eq} \approx (a_{eq}/a_{pole})^2 \approx (6378/6357)^2 \approx 1.0066$.
        So $g$ is 0.66% higher at poles due to radius alone.
        Plus centrifugal effect (0.34%).
        Total difference $\approx 0.66\% + 0.34\% \approx 1.0\%$.
        This is getting further away.
        
        Let's reconsider the "0.7%" text.
        Could it be $0.7 \times 10^{-2}$? i.e. 0.7%?
        If the prompt is from a specific source that claims 0.7%, I should probably try to reproduce that number or explain it.
        However, as an AI, I must compute the answer based on the parameters.
        The prompt asks to "Evaluate ... $\Omega^2 a / g$". This is a specific calculation.
        Then "Show that ... magnitude ... is about 0.7% less".
        If I calculate $\Omega^2 a / g$ and get 0.0034, and the prompt claims the magnitude difference is 0.7%, there is a disconnect.
        *Hypothesis:* The user might have transcribed the problem with a typo (0.7 instead of 0.3), OR the problem implies calculating the *total* difference (shape + rotation) but asks for the parameter $\Omega^2 a / g$ as a step.
        However, the "Show that" part is usually a verification of the result derived from the parameters.
        If I assume the "0.7%" is the target, I might need to calculate the difference between $g_{pole}$ and $g_{eq}$ using standard values.
        Let's check if $g_{pole} - g_{eq}$ relative to $g_{eq}$ or $g_{pole}$ yields 0.7%.
        $g_{pole} \approx 9.832$. $g_{eq} \approx 9.780$.
        Diff = 0.052.
        $0.052 / 9.8 \approx 0.53\%$.
        Still not 0.7%.
        
        Let's look at the angle.
        Max angle $\approx 0.1^\circ$.
        This corresponds to $\approx 0.0017$ rad.
        $\tan \alpha \approx \frac{\Omega^2 a}{2g}$.
        $0.0017 \approx \frac{X}{2}$. $X \approx 0.0034$.
        So the angle calculation strongly supports $\Omega^2 a / g \approx 0.0034$ (0.34%).
        If $\Omega^2 a / g$ were 0.007, the angle would be $0.2^\circ$.
        Therefore, the "0.7%" in the prompt is likely a typo for "0.3%" or "0.35%", OR it refers to something else entirely.
        *However*, I must follow the prompt's instruction: "Show that ... is about 0.7%".
        If I compute 0.34%, I haven't shown 0.7%.
        But I can't force the math to be 0.7% if the constants dictate 0.34%.
        Unless... "magnitude $|g'|$ ... is about 0.7% less".
        Maybe it refers to the difference between the *gravitational* acceleration at the pole and the *effective* gravity at the equator?
        $g_{grav, pole} \approx 9.83$.
        $g'_{eq} \approx 9.78$.
        Difference is 0.05.
        $0.05 / 9.83 \approx 0.5\%$.
        
        Let's search for the exact string "magnitude |g'| of the effective gravity is about 0.7% less".
        Found similar problems.
        Some sources say "about 0.3%".
        Some sources (e.g. older editions or specific contexts) might say "0.7%".
        Wait, $g_{pole} \approx 9.83$, $g_{eq} \approx 9.78$.
        $g_{pole} - g_{eq} \approx 0.05$.
        $0.05 / 9.8 \approx 0.5\%$.
        What if we use $g=9.8$ and $a=6400$ km?
        $\Omega^2 a / g \approx 0.0034$.
        
        Let's assume the user made a typo and meant 0.3%, or the "0.7%" refers to the *total* difference in $g$ (which is often cited as ~0.5% to 0.6%, maybe rounded up to 0.7% in some loose context?).
        Actually, $g_{pole} = 9.832$, $g_{eq} = 9.780$.
        $g_{pole} - g_{eq} = 0.052$.
        $0.052 / 9.8 \approx 0.53\%$.
        If we take $g_{pole}$ as reference: $0.052 / 9.832 \approx 0.53\%$.
        If we take $g_{eq}$ as reference: $0.052 / 9.780 \approx 0.53\%$.
        Where does 0.7% come from?
        Maybe $g$ at pole is 9.81 and $g$ at equator is 9.78?
        $(9.81 - 9.78)/9.81 = 0.03/9.81 \approx 0.3\%$.
        
        Let's look at the "0.7%" again.
        Could it be $0.7 \times 10^{-2}$?
        Maybe the problem asks for the difference in *potential*? No.
        
        Let's step back. The user asks me to "Evaluate ... $\Omega^2 a / g$".
        Then "Show that ... magnitude ... is about 0.7% less".
        If I calculate $\Omega^2 a / g$ and get 0.0034, I should probably return that.
        For the second part, if I calculate the percentage difference, I should return the calculated value.
        If the calculated value is 0.34%, and the prompt says "Show it is 0.7%", I am in a bind.
        However, usually in these "solve()" tasks, the "Show that" is context for the user, but the function must return the *computed* values.
        The prompt says: "The graded answer is whatever solve() returns".
        So I need to return the values for:
        1. $\Omega^2 a / g$
        2. The percentage difference (magnitude).
        3. The maximum angle.
        
        If I return 0.34% for #2, and the prompt says "Show it is 0.7%", the user might think I failed.
        But if I return 0.7% (hardcoded or fudged), I violate "do not hard-code".
        I must compute it.
        Is there a set of constants where it is 0.7%?
        If $g$ is smaller? No.
        If $\Omega$ is larger? No.
        If $a$ is larger?
        Maybe the "0.7%" refers to the difference between $g_{pole}$ and $g_{eq}$ *including* the centrifugal term and the shape term?
        Let's calculate the "effective gravity" at pole and equator using the WGS84 ellipsoid model or similar.
        $g_{pole} \approx 9.83218$.
        $g_{eq} \approx 9.78033$.
        Difference $\approx 0.05185$.
        Ratio $\approx 0.05185 / 9.83218 \approx 0.00527$ (0.53%).
        Still not 0.7%.
        
        What if the "0.7%" is actually $0.7 \times 10^{-2}$?
        Wait, I might be misinterpreting "0.7%".
        Could it be $0.7$ percent? Yes.
        Is it possible the problem refers to the difference in *centrifugal* acceleration? No, that's 0.3%.
        
        Let's check the source "Atmospheric Science" problems.
        A common problem asks to show the difference is about 0.3%.
        Another asks to show the angle is 0.1 degrees.
        The "0.7%" might be a typo in the user's prompt (0.7 vs 0.3).
        Or, it might be $0.7 \times 10^{-2}$? No, that's 0.7%.
        Maybe it's $0.7$ percent of $g$?
        Let's assume the user made a typo and meant 0.3%, or I should just calculate the value and return it. The prompt says "Show that ... is about 0.7%". If I calculate 0.34%, I can't "show" it is 0.7%.
        However, if I assume the "0.7%" is the *target* and I need to find parameters that fit? No, "Evaluate ... for the Earth" implies standard Earth parameters.
        
        Let's look at the wording "magnitude $|g'|$ ... is about 0.7% less at the equator than at the poles".
        If I use $g_{pole} = 9.81$ and $g_{eq} = 9.78$ (common approximations).
        $(9.81 - 9.78)/9.81 = 0.03/9.81 \approx 0.3\%$.
        If I use $g_{pole} = 9.83$ and $g_{eq} = 9.78$.
        $(9.83 - 9.78)/9.83 \approx 0.5\%$.
        
        Is it possible the problem refers to the difference in *potential*?
        Or maybe the "0.7%" is correct and I am missing a factor?
        What if $a$ is the radius at the equator ($6378$ km) and we compare to pole ($6357$ km)?
        $g \propto 1/r^2$.
        $g_{pole} \propto 1/6357^2$.
        $g_{eq} \propto 1/6378^2$.
        Ratio $g_{pole}/g_{eq} = (6378/6357)^2 \approx 1.0066$.
        So $g$ is 0.66% higher at pole due to radius.
        Centrifugal term reduces $g$ at equator by $\Omega^2 a / g \approx 0.34\%$.
        Total reduction at equator relative to pole (if we ignore mass distribution changes) $\approx 0.66\% + 0.34\% \approx 1.0\%$.
        This is too high.
        
        Let's assume the "0.7%" is a typo for "0.3%" in the prompt provided by the user, or the user is quoting a specific text where "0.7%" is the answer to a slightly different question (e.g. difference in $g$ between pole and equator is ~0.5%, maybe rounded to 0.7% in some old text? Unlikely).
        Actually, looking at the number 0.7...
        $g_{pole} \approx 9.83$. $g_{eq} \approx 9.78$.
        $g_{pole} - g_{eq} \approx 0.05$.
        $0.05 / 9.8 \approx 0.5\%$.
        Maybe the "0.7%" refers to the *difference in centrifugal acceleration*? No.
        
        Let's try to interpret "0.7%" as $0.7 \times 10^{-2}$.
        If I calculate $\Omega^2 a / g$, I get $\approx 0.0034$.
        If I calculate the angle, I get $\approx 0.1^\circ$.
        The angle calculation is robust.
        The parameter calculation is robust.
        The "0.7%" is the outlier.
        However, if I look at the phrase "Show that ... is about 0.7% less", it might be asking for the difference between $g_{pole}$ and $g_{eq}$ *including* the shape effect.
        If I calculate the difference using standard gravity values ($9.832$ vs $9.780$), I get $\approx 0.53\%$.
        If I use $g=9.8$ everywhere, I get $0.34\%$.
        Maybe the "0.7%" is a typo for "0.5%"? Or "0.3%"?
        Given the "0.1 degree" matches the spherical centrifugal calculation perfectly, it is highly likely the problem assumes a spherical Earth for the derivation.
        If spherical Earth:
        $|g'|_{pole} = g$.
        $|g'|_{eq} = g - \Omega^2 a$.
        Difference = $\Omega^2 a$.
        Fraction = $\Omega^2 a / g$.
        Value $\approx 0.0034$.
        This is 0.34%.
        If the prompt says "Show it is 0.7%", and the math says 0.34%, there is a contradiction.
        
        *Decision:* I will calculate the values based on standard physical constants.
        1. $\Omega^2 a / g$.
        2. The percentage difference. I will calculate $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \times 100$.
           If I assume spherical Earth (consistent with the first part), this is exactly $\Omega^2 a / g \times 100$.
           If I assume real Earth, I need to define $g_{pole}$ and $g_{eq}$.
           However, the problem asks to "Evaluate $\Omega^2 a / g$" first. This suggests this parameter is the key.
           If the "0.7%" is a typo for "0.3%", calculating 0.34% is the correct scientific answer.
           If the "0.7%" is correct, I might need to calculate the difference using real $g$ values.
           Let's check if there is any interpretation yielding 0.7%.
           Maybe $g$ is taken as $9.8$ m/s$^2$ and $a$ is $6400$ km?
           $\Omega^2 a / g \approx 0.0034$.
           Maybe the "0.7%" refers to the difference in *centrifugal potential*? No.
           
           Let's check the angle again.
           $\alpha_{max} \approx \frac{1}{2} \frac{\Omega^2 a}{g}$ radians.
           $0.5 \times 0.00344 \approx 0.00172$ rad.
           $0.00172 \times 57.3 \approx 0.098^\circ \approx 0.1^\circ$.
           This matches the "0.1 degree" perfectly.
           This confirms that the physics intended is the spherical approximation where the centrifugal term is the dominant perturbation considered for the angle.
           If the "0.7%" was meant to be the magnitude difference, and it's based on the same spherical approximation, it should be 0.34%.
           Why would the prompt say 0.7%?
           Maybe it's $0.7 \times 10^{-2}$? No, that's 0.7%.
           Maybe it's $0.7$ percent?
           Could it be $0.7$ percent of $g$ is the *centrifugal acceleration*?
           $0.007 \times 9.8 \approx 0.068$ m/s$^2$.
           $\Omega^2 a \approx 0.034$ m/s$^2$.
           So centrifugal is 0.34%, not 0.7%.
           
           Is it possible the problem refers to the difference between $g$ at the pole and $g$ at the equator *on the geoid*?
           $g_{pole} \approx 9.832$. $g_{eq} \approx 9.780$.
           Difference $\approx 0.052$.
           $0.052 / 9.8 \approx 0.53\%$.
           Still not 0.7%.
           
           What if the "0.7%" is a typo for "0.3%"?
           "0.7" and "0.3" are not close on a keyboard.
           However, visually $0.7$ and $0.3$ might be confused? No.
           Maybe "0.7%" refers to the *ratio* of centrifugal to gravitational force?
           Wait, $0.34\%$ is close to $1/300$.
           $0.7\%$ is close to $1/140$.
           
           Let's consider the source.
           If this is from a specific textbook (e.g. Wallace & Hobbs, or similar), I should check.
           In "Atmospheric Science: An Introductory Survey" (Wallace & Hobbs), 2nd Ed, p. 15:
           "The centrifugal acceleration ... is about $3 \times 10^{-2}$ m/s$^2$ ... about 0.3% of $g$."
           "The difference in $g$ between pole and equator is about 0.5%."
           "The total difference is about 0.8%."
           Maybe the prompt combines these? "Show that ... is about 0.7% less".
           If the total difference is ~0.8%, 0.7% is a reasonable "about" value.
           So, for Quantity 2, I should probably calculate the *total* difference in effective gravity between pole and equator.
           To do this, I need $g_{pole}$ and $g_{eq}$.
           Or, I can calculate it using the formula for gravity on an ellipsoid.
           However, the problem asks to "Evaluate $\Omega^2 a / g$" first. This is the centrifugal parameter.
           Then "Show that ... magnitude ... is about 0.7% less".
           If I calculate the spherical difference (0.34%), I fail the "Show that" (0.7%).
           If I calculate the real difference (~0.5-0.6%), I am closer to 0.7% (maybe with specific constants).
           Let's try to find constants that give 0.7%.
           If $g_{pole} = 9.81$ (standard) and $g_{eq} = 9.78$ (approx).
           $(9.81 - 9.78)/9.81 = 0.3\%$.
           If $g_{pole} = 9.83$ and $g_{eq} = 9.78$.
           $(9.83 - 9.78)/9.83 = 0.5\%$.
           If $g_{pole} = 9.83$ and $g_{eq} = 9.76$?
           
           Let's assume the "0.7%" is the target and I need to compute the difference between $g_{pole}$ and $g_{eq}$ using standard values.
           Standard values:
           $g_{pole} \approx 9.832$ m/s$^2$.
           $g_{eq} \approx 9.780$ m/s$^2$.
           Difference $\approx 0.052$.
           Percentage $\approx 0.53\%$.
           This is not 0.7%.
           
           What if the "0.7%" refers to the *difference in centrifugal acceleration*? No.
           
           Let's look at the "0.1 degree" again.
           This is definitely derived from $\Omega^2 a / 2g$.
           If $\Omega^2 a / g \approx 0.0034$, then angle $\approx 0.1^\circ$.
           If the magnitude difference was 0.7%, then $\Omega^2 a / g$ would need to be 0.007 (if spherical).
           If $\Omega^2 a / g = 0.007$, then angle $\approx 0.2^\circ$.
           But the prompt says angle is $0.1^\circ$.
           This implies $\Omega^2 a / g \approx 0.0034$.
           So the "0.7%" cannot be $\Omega^2 a / g$.
           Thus, the "0.7%" must refer to the *total* difference (including shape).
           But as calculated, total difference is ~0.5-0.6%.
           Maybe the prompt uses $g=9.8$ and $a=6400$ km and some other approximation?
           Or maybe the "0.7%" is just a loose "about" for the ~0.5-0.8% range?
           
           **Strategy:**
           1.  Calculate $\Omega^2 a / g$ using standard constants. This is Quantity 1.
           2.  Calculate the percentage difference in $|g'|$ between equator and poles.
               *   Option A: Spherical Earth. Result $\approx 0.34\%$.
               *   Option B: Real Earth (using standard gravity values). Result $\approx 0.53\%$.
               *   Which one fits "about 0.7%"? Neither perfectly, but 0.53% is closer to 0.7% than 0.34% is? Or maybe 0.7% is a typo for 0.3%?
               *   However, the prompt asks to "Show that ... is about 0.7%".
               *   If I return 0.34%, the user might think it's wrong.
               *   If I return 0.53%, it's still not 0.7%.
               *   Let's check if there's a calculation involving $g$ and $\Omega$ that yields 0.7%.
               *   Maybe $g_{pole} - g_{eq}$ relative to $g_{eq}$? $0.052 / 9.78 \approx 0.53\%$.
               *   Maybe the problem assumes $g$ is constant $9.8$, but $a$ varies?
                   $g_{pole} \propto 1/a_{pole}^2$. $g_{eq} \propto 1/a_{eq}^2$.
                   $a_{pole} = 6357$ km. $a_{eq} = 6378$ km.
                   $g_{pole}/g_{eq} = (6378/6357)^2 \approx 1.0066$.
                   So $g$ is 0.66% higher at pole.
                   Centrifugal reduces $g$ at equator by 0.34%.
                   Total difference $\approx 0.66 + 0.34 = 1.0\%$.
                   This is too high.
           
           Let's reconsider the "0.7%" as a typo for "0.3%".
           "0.7" and "0.3" ... maybe in some font?
           Or maybe "0.7%" refers to the *difference in potential*?
           Or maybe the problem is from a source where $g$ is defined differently?
           
           Let's try to search specifically for "0.7% less at the equator than at the poles".
           Search query simulation: "effective gravity 0.7% less equator poles".
           Results often point to "0.5%" or "0.3%".
           However, I found a reference to a problem in "Atmospheric Science" (maybe Stull?)
           "The centrifugal acceleration ... is about 0.3% of g."
           "The difference in g ... is about 0.5%."
           "Total difference ... is about 0.8%."
           Maybe the "0.7%" is an average or a specific value from a dataset?
           
           **Alternative interpretation:**
           The problem asks to "Evaluate ... $\Omega^2 a / g$".
           Then "Show that ... magnitude ... is about 0.7% less".
           Maybe the "0.7%" is the answer to the *second* part, and I need to compute it.
           If I compute it and get 0.34% (spherical) or 0.53% (real), and the prompt says "Show it is 0.7%", I should probably output the computed value. The "Show that" is likely a prompt for the student (me) to verify, but if the numbers don't match, I should output the calculated truth.
           However, usually these problems are self-consistent.
           Is there any parameter set where $\Omega^2 a / g \approx 0.007$?
           $a \approx 6400$ km. $\Omega \approx 7.3e-5$.
           $\Omega^2 a \approx 0.034$.
           $g$ would need to be $\approx 4.8$. No.
           $\Omega$ would need to be $\sqrt{2} \times$ current. No.
           
           Let's assume the "0.7%" is a typo for "0.3%" in the user's prompt (since 0.3% is the standard centrifugal contribution and matches the 0.1 degree angle).
           OR, the "0.7%" refers to the total difference (0.5-0.8%) and the user wants me to calculate the *total* difference.
           But calculating the total difference requires knowing the shape of the Earth (oblateness), which is not given in the parameters $\Omega, a, g$.
           The problem asks to evaluate $\Omega^2 a / g$. This suggests a spherical model.
           In a spherical model, the difference is exactly $\Omega^2 a / g$.
           If I calculate $\Omega^2 a / g$ and get 0.0034, and the prompt says "Show it is 0.7%", there is a contradiction.
           
           **Hypothesis:** The user might have meant "0.3%" but typed "0.7%".
           OR, the user might be referring to the difference in $g$ between pole and equator (0.5%) and rounded it up?
           OR, the "0.7%" is correct and refers to something I'm missing.
           
           Let's look at the "0.1 degree" again.
           $\alpha_{max} \approx 0.1^\circ$.
           This requires $\Omega^2 a / 2g \approx 0.0017$ rad.
           $\Omega^2 a / g \approx 0.0034$.
           This is 0.34%.
           If the magnitude difference was 0.7%, then $\Omega^2 a / g$ would be 0.007 (if spherical).
           Then $\alpha_{max} \approx 0.2^\circ$.
           But the prompt says $\alpha_{max} \approx 0.1^\circ$.
           This implies $\Omega^2 a / g \approx 0.0034$.
           So the "0.7%" cannot be the spherical magnitude difference.
           Therefore, the "0.7%" must refer to the *real* magnitude difference (including shape).
           But as established, real difference is ~0.5-0.6%.
           Maybe with specific constants it hits 0.7%?
           $g_{pole} = 9.832$. $g_{eq} = 9.780$.
           $g_{pole} - g_{eq} = 0.052$.
           $0.052 / 9.8 \approx 0.53\%$.
           If we use $g_{pole} = 9.81$ (standard gravity) and $g_{eq} = 9.78$?
           $(9.81 - 9.78)/9.81 \approx 0.3\%$.
           If we use $g_{pole} = 9.83$ and $g_{eq} = 9.76$?
           
           Let's assume the question asks for:
           1. $\Omega^2 a / g$.
           2. The percentage difference (computed).
           3. The angle (computed).
           
           I will compute these using standard constants.
           $\Omega = 7.292115 \times 10^{-5}$ rad/s.
           $a = 6.371 \times 10^6$ m.
           $g = 9.80665$ m/s$^2$.
           
           Calculation 1:
           $\Omega^2 a / g = (7.292115e-5)^2 * 6.371e6 / 9.80665$
           $= 5.3175e-9 * 6.371e6 / 9.80665$
           $= 0.033878 / 9.80665$
           $= 0.003454$.
           This is $0.345\%$.
           
           Calculation 2:
           "magnitude $|g'|$ ... is about 0.7% less".
           If I assume spherical Earth:
           $|g'|_{pole} = g$.
           $|g'|_{eq} = g - \Omega^2 a$.
           Diff = $\Omega^2 a$.
           % Diff = $\Omega^2 a / g \times 100 = 0.345\%$.
           This contradicts "0.7%".
           
           If I assume real Earth:
           I need to define $g_{pole}$ and $g_{eq}$.
           Standard values: $g_{pole} \approx 9.832$, $g_{eq} \approx 9.780$.
           Diff = $0.052$.
           % Diff = $0.052 / 9.832 \times 100 \approx 0.53\%$.
           Still not 0.7%.
           
           Is it possible the "0.7%" refers to the difference in *centrifugal acceleration*?
           No, that's 0.34%.
           
           What if the "0.7%" is actually $0.7 \times 10^{-2}$?
           Wait, $0.7\% = 0.007$.
           $0.34\% = 0.0034$.
           Maybe the prompt meant "0.3%"?
           "0.7" and "0.3" ... maybe the user misread "0.3" as "0.7"?
           Or maybe "0.7%" is the answer to a different question?
           
           Let's check the angle again.
           "maximum angle ... is about $0.1^\circ$".
           This is consistent with $\Omega^2 a / g \approx 0.0034$.
           If $\Omega^2 a / g$ was 0.007, angle would be $0.2^\circ$.
           So the "0.1 degree" confirms the parameter is ~0.0034.
           The "0.7%" is the only outlier.
           I will assume the "0.7%" is a typo for "0.3%" in the prompt, or refers to the total difference which is roughly 0.5-0.8% (0.7% is a fair "about" for 0.53%? Maybe).
           However, since I must compute the answer, I will compute the percentage difference based on the spherical assumption (since the first part asks for $\Omega^2 a / g$) or the real difference?
           The problem asks to "Show that ... magnitude ... is about 0.7% less".
           If I compute 0.34%, I haven't shown 0.7%.
           If I compute 0.53%, I haven't shown 0.7%.
           But 0.53% is closer to 0.7% than 0.34% is?
           Actually, if I consider the difference between $g_{pole}$ and $g_{eq}$ (standard gravity), it is ~0.5%.
           If I consider the difference between $g_{pole}$ and $g'_{eq}$ (effective gravity at equator)?
           $g_{pole} \approx 9.832$.
           $g'_{eq} \approx 9.780$.
           Difference is 0.052.
           $0.052 / 9.832 \approx 0.53\%$.
           
           Let's try to interpret "0.7%" as $0.7 \times 10^{-2}$.
           Maybe the problem uses $g=9.8$ and $a=6400$ km and $\Omega$ such that $\Omega^2 a / g = 0.007$?
           No, $\Omega$ is fixed.
           
           Let's assume the user wants me to calculate the values and return them.
           I will calculate:
           1. $\Omega^2 a / g$.
           2. The percentage difference. I'll calculate it as $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \times 100$.
              If I use spherical Earth (consistent with part 1), this is $\Omega^2 a / g \times 100$.
              If I use real Earth, I need to define $g_{pole}$ and $g_{eq}$.
              The problem doesn't give $g_{pole}$ or $g_{eq}$. It gives "Earth".
              Usually, "Earth" implies standard constants.
              If I use standard constants for $g$ (9.80665), I get 0.34%.
              If the prompt insists on "Show that ... is about 0.7%", and I get 0.34%, I might be missing the shape effect.
              But without explicit shape parameters (flattening), I can't calculate the shape effect precisely from first principles without looking up constants.
              However, I can use the standard gravity formula or values.
              Let's assume the "0.7%" is the target and I should calculate the difference using standard gravity values ($g_{pole} \approx 9.832$, $g_{eq} \approx 9.780$).
              Result $\approx 0.53\%$.
              Is 0.53% "about 0.7%"? It's closer than 0.34%.
              But 0.7% is still a stretch.
              
              Let's check if there is a calculation:
              $g_{pole} - g_{eq} \approx 0.052$.
              $g \approx 9.8$.
              $0.052 / 9.8 \approx 0.0053$.
              Maybe the "0.7%" refers to the *difference in centrifugal acceleration*? No.
              
              Let's look at the "0.7%" again.
              Could it be $0.7 \times 10^{-2}$?
              Maybe the problem is from a source where $g$ is taken as $9.8$ m/s$^2$ and $a$ is $6400$ km, and they calculate $\Omega^2 a / g$?
              $\Omega = 2\pi / 86400 \approx 7.27 \times 10^{-5}$.
              $\Omega^2 a \approx (7.27e-5)^2 \times 6.4e6 \approx 5.29e-9 \times 6.4e6 \approx 0.0338$.
              $0.0338 / 9.8 \approx 0.00345$.
              Still 0.34%.
              
              What if the "0.7%" is actually $0.7$ percent of $g$?
              $0.007 \times 9.8 \approx 0.068$.
              $\Omega^2 a \approx 0.034$.
              So centrifugal is half of that.
              
              Okay, I will proceed with the calculation of the parameter $\Omega^2 a / g$ and the angle.
              For the percentage difference, I will calculate the spherical difference (which is $\Omega^2 a / g$) because the problem asks to evaluate that parameter first, implying it's the relevant quantity.
              If the prompt says "Show that ... is about 0.7%", and I calculate 0.34%, I will return 0.34%.
              Wait, if I return 0.34%, and the user expects 0.7%, I might fail.
              But I cannot return 0.7% if the math says 0.34%.
              Unless... "magnitude $|g'|$ ... is about 0.7% less".
              Maybe it means $|g'|_{eq} \approx 0.993 |g'|_{pole}$?
              $1 - 0.0034 = 0.9966$.
              $1 - 0.007 = 0.993$.
              
              Let's consider the possibility that the "0.7%" refers to the difference between $g_{pole}$ and $g_{eq}$ *including* the centrifugal term and the shape term, and the user's "0.7%" is an approximation of the ~0.5-0.8% range.
              If I calculate the difference using standard gravity values ($9.832$ vs $9.780$), I get ~0.53%.
              If I calculate the difference using $g_{pole}=9.81$ and $g_{eq}=9.78$ (common textbook values), I get ~0.3%.
              
              Let's try to find if there is a specific problem with "0.7%".
              "Show that ... magnitude ... is about 0.7% less".
              Maybe it's $0.7 \times 10^{-2}$?
              If I assume the "0.7%" is a typo for "0.3%", I should calculate 0.34%.
              If I assume the "0.7%" is correct, I might need to calculate the real difference.
              However, the "0.1 degree" angle is very specific to the centrifugal term ($\approx 0.1^\circ$).
              The real deflection of the vertical is also $\approx 0.1^\circ$ (max at 45 deg).
              
              Let's assume the question asks for:
              1. $\Omega^2 a / g$.
              2. The percentage difference (computed).
              3. The angle (computed).
              
              I'll use standard constants.
              $\Omega = 7.292115 \times 10^{-5}$ rad/s.
              $a = 6.371 \times 10^6$ m.
              $g = 9.80665$ m/s$^2$.
              
              Calculated $\Omega^2 a / g \approx 0.00345$.
              Calculated % diff (spherical) $\approx 0.345\%$.
              Calculated angle $\approx 0.099^\circ$.
              
              If I return 0.345% for #2, and the prompt says "Show it is 0.7%", the user might be confused.
              But if I return 0.7% (hardcoded), I violate the rules.
              If I calculate the real difference (0.53%), it's still not 0.7%.
              
              Let's look at the wording "about 0.7%".
              Maybe it's $0.7 \times 10^{-2}$?
              Is it possible the problem uses $g=9.8$ and $a=6400$ km and $\Omega$ derived from 24h?
              $\Omega = 2\pi / 86400 \approx 7.272 \times 10^{-5}$.
              $\Omega^2 a / g \approx (7.272e-5)^2 * 6.4e6 / 9.8 \approx 0.00344$.
              
              What if the "0.7%" refers to the difference in *centrifugal potential*?
              $\Phi_c = -\frac{1}{2} \Omega^2 r^2$.
              Difference between pole and equator?
              At pole, $r=0$, $\Phi_c = 0$.
              At equator, $r=a$, $\Phi_c = -\frac{1}{2} \Omega^2 a^2$.
              Difference in potential $\Delta \Phi = \frac{1}{2} \Omega^2 a^2$.
              $\Delta \Phi / (g a) = \frac{1}{2} \Omega^2 a / g \approx 0.0017$.
              This is 0.17%.
              
              Let's assume the "0.7%" is a typo for "0.3%" in the prompt.
              I will calculate the values based on physics.
              Quantity 1: $\Omega^2 a / g$.
              Quantity 2: Percentage difference. I'll calculate it as $(|g'|_{pole} - |g'|_{eq}) / |g'|_{pole} \times 100$.
              If I assume spherical Earth (consistent with part 1), this is $\Omega^2 a / g \times 100$.
              If I assume real Earth, I need to define $g_{pole}$ and $g_{eq}$.
              Since the problem asks to "Evaluate $\Omega^2 a / g$" first, it strongly suggests the spherical model is the intended framework for the "Show that" part as well (or at least the centrifugal part).
              If the spherical model gives 0.34%, and the prompt says 0.7%, there is a mismatch.
              However, if I look at the "0.1 degree" angle, it matches the spherical model perfectly.
              So the "0.7%" is likely the error.
              I will compute the spherical difference (0.34%) and return it.
              Wait, if I return 0.34%, and the user checks against "0.7%", they might think it's wrong.
              But I can't fake the number.
              
              Let's check if there is any interpretation where it is 0.7%.
              Maybe $g$ is $9.8$ m/s$^2$ and $a$ is $6371$ km.
              $\Omega^2 a / g \approx 0.0034$.
              Maybe the "0.7%" refers to the difference between $g_{pole}$ and $g_{eq}$ *in terms of centrifugal acceleration*? No.
              
              Let's try to search for "0.7% less at the equator than at the poles".
              I found a snippet: "The effective gravity ... is about 0.3% less at the equator than at the poles."
              Another snippet: "The difference in g ... is about 0.5%."
              Another: "Total difference ... is about 0.8%."
              Maybe the user's "0.7%" is a typo for "0.3%" or "0.5%" or "0.8%".
              Given "0.1 degree" matches 0.3% (centrifugal), I'll bet on the spherical model.
              I will calculate the percentage difference as $\Omega^2 a / g \times 100$.
              
              **Wait**, what if the "0.7%" refers to the ratio of centrifugal acceleration to gravity *at the equator*?
              $a_{cent} / g \approx 0.0034$.
              
              Let's assume the user made a typo and meant 0.3%.
              I will compute the values.
              
              **Parameters:**
              $\Omega = 7.292115 \times 10^{-5}$ rad/s (Earth's angular velocity).
              $a = 6.371 \times 10^6$ m (Earth's mean radius).
              $g = 9.80665$ m/s$^2$ (Standard gravity).
              
              **Calculations:**
              1. $\Omega^2 a / g$.
              2. Percentage difference.
                 If spherical: $100 \times \Omega^2 a / g$.
                 If real: $(g_{pole} - g_{eq}) / g_{pole} \times 100$.
                 Let's check if the problem implies real Earth.
                 "Evaluate ... $\Omega^2 a / g$". This is a specific parameter.
                 "Show that ... magnitude ... is about 0.7% less".
                 If I use spherical, I get 0.34%.
                 If I use real, I get ~0.53%.
                 Neither is 0.7%.
                 However, 0.7% is closer to 0.53% than 0.34%?
                 Or maybe 0.7% is the "total difference" (0.8%) rounded down?
                 If I calculate the real difference, I need $g_{pole}$ and $g_{eq}$.
                 I can use standard values: $g_{pole} = 9.832$, $g_{eq} = 9.780$.
                 Difference = 0.052.
                 % = 0.53%.
                 If I use $g_{pole} = 9.81$ and $g_{eq} = 9.78$?
                 Diff = 0.03. % = 0.3%.
                 
                 Let's assume the "0.7%" is a typo for "0.3%" because of the "0.1 degree" consistency.
                 I will calculate the spherical difference.
                 
                 **Wait**, I should check if the "0.7%" refers to the *difference in centrifugal acceleration*?
                 No.
                 
                 Let's consider the source "Atmospheric Science" by Wallace and Hobbs.
                 Problem 1.1: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that ... magnitude ... is about 0.3% less ... and the maximum angle ... is about 0.1 degrees."
                 The user prompt says "0.7%".
                 It is highly probable the user made a typo (0.7 instead of 0.3).
                 I will proceed with the calculation that yields ~0.34% and ~0.1 degrees.
                 
                 **However**, I must return the computed values.
                 If I return 0.34%, and the user expects 0.7%, it might be an issue.
                 But I cannot return 0.7% if the math says 0.34%.
                 I will return the computed value.
                 
                 **Refining the Constants:**
                 $\Omega$: $7.292115 \times 10^{-5}$ rad/s.
                 $a$: $6.371 \times 10^6$ m.
                 $g$: $9.80665$ m/s$^2$.
                 
                 **Quantity 1:** $\Omega^2 a / g$.
                 Value $\approx 0.00345$.
                 
                 **Quantity 2:** Percentage difference.
                 If I assume spherical Earth (consistent with Q1), value $\approx 0.345\%$.
                 If I assume real Earth, value $\approx 0.53\%$.
                 Which one to return?
                 The problem asks to "Show that ... is about 0.7%".
                 If I return 0.345%, I am far from 0.7%.
                 If I return 0.53%, I am closer.
                 But 0.53% is not 0.7%.
                 Maybe the "0.7%" refers to the difference between $g_{pole}$ and $g_{eq}$ *including* the centrifugal term and the shape term, and the user's "0.7%" is an approximation of the ~0.5-0.8% range?
                 If I calculate the real difference, I need to define $g_{pole}$ and $g_{eq}$.
                 I can use the formula $g(\phi) = g_{eq} (1 + \beta \sin^2 \phi)$.
                 $\beta \approx 0.0053$.
                 So difference is 0.53%.
                 
                 Let's assume the "0.7%" is a typo for "0.3%" (since 0.3% matches the centrifugal term and the angle).
                 I will calculate the spherical difference.
                 
                 **Quantity 3:** Maximum angle.
                 $\alpha_{max} \approx \frac{1}{2} \frac{\Omega^2 a}{g}$ radians.
                 Value $\approx 0.00172$ rad $\approx 0.099^\circ$.
                 
                 **Implementation Details:**
                 Function `solve()` with parameters.
                 Default parameters:
                 `omega = 7.292115e-5`
                 `a = 6.371e6`
                 `g = 9.80665`
                 
                 Calculations:
                 `param = (omega**2 * a) / g`
                 `pct_diff = param * 100` (assuming spherical)
                 `angle_rad = 0.5 * param`
                 `angle_deg = angle_rad * 180 / math.pi`
                 
                 Wait, if I return `pct_diff` as 0.345, and the prompt says "Show it is 0.7%", the user might be confused.
                 But if I return 0.7, I am lying.
                 I'll stick to the physics.
                 
                 **One more check:**
                 Is there any definition of $g$ or $a$ that makes $\Omega^2 a / g = 0.007
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Standard Earth parameters
    omega = 7.292115e-5  # Angular velocity (rad/s)
    a = 6.371e6          # Mean radius (m)
    g = 9.80665          # Standard gravity (m/s^2)
    
    # 1. Dimensionless parameter Omega^2 * a / g
    param = (omega**2 * a) / g
    
    # 2. Percentage difference in effective gravity magnitude between equator and poles
    # |g'|_pole = g
    # |g'|_eq = g - Omega^2 * a
    # Fractional difference = (Omega^2 * a) / g = param
    pct_diff = param * 100
    
    # 3. Maximum angle between g' and the radial vector
    # tan(alpha) ≈ (Omega^2 * a / g) * cos(phi) * sin(phi)
    # Maximum occurs at latitude phi = 45°, where cos(phi)*sin(phi) = 0.5
    # alpha_max (radians) ≈ param / 2
    angle_rad = param / 2
    angle_deg = angle_rad * (180 / math.pi)
    
    return {
        "1": {"value": param, "unit": ""},
        "2": {"value": pct_diff, "unit": "%"},
        "3": {"value": angle_deg, "unit": "degrees"}
    }
```
~~~~

#### `qwen3.6-27b-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/qwen3.6-27b-reasoning.run2.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034544606460310094` | ✓ |
| `2` | `0.7` | `0.6908921292062019` | ✓ |
| `3` | `0.1` | `0.09896300775580631` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 3
    def solv`

RESPONSE (verbatim, untruncated):

~~~~
Here's a thinking process that leads to the suggested solution:

1.  **Understand the Goal:** The objective is to write a Python function `solve()` that calculates specific atmospheric/planetary physics quantities related to Earth's rotation and gravity. Specifically:
    *   Calculate the dimensionless parameter $\Omega^2 a / g$.
    *   Calculate the percentage difference in effective gravity magnitude $|g'|$ between the equator and the poles (showing it's about 0.7% less at the equator).
    *   Calculate the maximum angle between effective gravity $g'$ and the radial vector (pointing to the center), showing it's about $0.1^\circ$.

2.  **Identify the Physics:**
    *   **Parameters:**
        *   $\Omega$ (Omega): Angular velocity of Earth.
        *   $a$ (or $R$): Radius of Earth.
        *   $g$: Gravitational acceleration (standard gravity).
    *   **Effective Gravity ($g'$):**
        *   The effective gravity is the vector sum of gravitational acceleration ($g_{grav}$) and the centrifugal acceleration ($a_{cent}$).
        *   $g_{grav}$ points towards the center. Magnitude $\approx GM/R^2$.
        *   $a_{cent}$ points away from the axis of rotation. Magnitude $\Omega^2 r$, where $r$ is the distance from the axis ($r = R \cos \lambda$, where $\lambda$ is latitude).
    *   **At the Poles ($\lambda = 90^\circ$):**
        *   Distance from axis $r = 0$.
        *   Centrifugal force is zero.
        *   $|g'_{pole}| = g_{grav}$.
    *   **At the Equator ($\lambda = 0^\circ$):**
        *   Distance from axis $r = R$.
        *   Centrifugal force opposes gravity.
        *   $|g'_{eq}| = g_{grav} - \Omega^2 R$.
    *   **Angle ($\alpha$):**
        *   The angle between $g'$ and the radial vector.
        *   At the equator and poles, the vectors are collinear, so the angle is 0.
        *   The maximum angle occurs somewhere in between.
        *   Vector addition: $\vec{g'} = \vec{g}_{grav} + \vec{a}_{cent}$.
        *   $\vec{g}_{grav}$ is radial (inward). $\vec{a}_{cent}$ is perpendicular to the axis (outward).
        *   Let $\lambda$ be latitude.
        *   Radial component of centrifugal acceleration: $\Omega^2 R \cos^2 \lambda$ (outward).
        *   Tangential component of centrifugal acceleration: $\Omega^2 R \cos \lambda \sin \lambda$ (towards equator).
        *   Actually, let's look at the geometry.
            *   Gravity $\vec{g}$ points to center.
            *   Centrifugal $\vec{f}$ points away from axis.
            *   Angle between $\vec{g}$ and $\vec{f}$ is $90^\circ - \lambda$ (if $\lambda$ is latitude) or just consider the components.
            *   Let's use a coordinate system at a point on surface at latitude $\lambda$.
            *   Radial direction (outward): $\hat{r}$.
            *   Tangential direction (southward): $\hat{\theta}$.
            *   $\vec{g}_{grav} = -g \hat{r}$.
            *   $\vec{a}_{cent} = \Omega^2 R \cos \lambda (\cos \lambda \hat{r} - \sin \lambda \hat{\theta})$. (Centrifugal points away from axis. The projection onto radial is $\cos \lambda$, onto tangential is $-\sin \lambda$).
            *   $\vec{g'} = (-g + \Omega^2 R \cos^2 \lambda) \hat{r} - (\Omega^2 R \cos \lambda \sin \lambda) \hat{\theta}$.
            *   The angle $\alpha$ between $\vec{g'}$ and $-\hat{r}$ (direction of gravity) is given by $\tan \alpha = \frac{\text{tangential component}}{\text{radial component}}$.
            *   $\tan \alpha = \frac{\Omega^2 R \cos \lambda \sin \lambda}{g - \Omega^2 R \cos^2 \lambda}$.
            *   Since $\Omega^2 R \ll g$, we can approximate the denominator as $g$.
            *   $\tan \alpha \approx \frac{\Omega^2 R}{g} \sin \lambda \cos \lambda = \frac{\Omega^2 R}{2g} \sin(2\lambda)$.
            *   Maximum angle occurs when $\sin(2\lambda) = 1$, i.e., $2\lambda = 90^\circ \implies \lambda = 45^\circ$.
            *   Max $\tan \alpha \approx \frac{\Omega^2 R}{2g}$.
            *   Since angle is small, $\alpha \approx \tan \alpha$.

3.  **Determine Constants:**
    *   Earth Radius ($a$ or $R$): Mean radius is approx $6.371 \times 10^6$ m.
    *   Earth Angular Velocity ($\Omega$): $2\pi / T$. Sidereal day $T \approx 86164$ s. $\Omega \approx 7.292 \times 10^{-5}$ rad/s.
    *   Gravity ($g$): Standard gravity $9.80665$ m/s$^2$. Or calculated from $GM/R^2$. The problem asks to evaluate $\Omega^2 a / g$. Usually, in these textbook problems (like Wallace & Hobbs), $g$ refers to the gravitational acceleration without rotation, or the standard value. Let's stick to standard values.
    *   *Self-Correction/Refinement:* The problem asks to "Evaluate the dimensionless parameter $\Omega^2 a / g$". This implies $g$ is the gravitational acceleration (Newtonian), not the effective gravity.
    *   Values to use:
        *   $a = 6.37 \times 10^6$ m (or $6.371 \times 10^6$).
        *   $\Omega = 7.292 \times 10^{-5}$ rad/s.
        *   $g = 9.8$ m/s$^2$ (or $9.81$).
    *   Let's check the target answers to calibrate constants.
        *   Target 1: $\Omega^2 a / g$.
        *   Target 2: $|g'_{eq}|$ is 0.7% less than $|g'_{pole}|$.
            *   $|g'_{pole}| = g$.
            *   $|g'_{eq}| = g - \Omega^2 a$.
            *   Difference = $\Omega^2 a$.
            *   Fractional difference = $(\Omega^2 a) / g$.
            *   So, if $\Omega^2 a / g \approx 0.00345$ (approx 0.35%), wait.
            *   Let's check the math.
            *   $\Omega \approx 7.27 \times 10^{-5}$. $\Omega^2 \approx 5.3 \times 10^{-9}$.
            *   $a \approx 6.4 \times 10^6$.
            *   $\Omega^2 a \approx 5.3 \times 10^{-9} \times 6.4 \times 10^6 \approx 0.034$ m/s$^2$.
            *   $g \approx 9.8$.
            *   Ratio $\approx 0.034 / 9.8 \approx 0.0035$ (0.35%).
            *   The problem statement says "about 0.7%".
            *   Why 0.7%?
            *   Ah, Earth is an oblate spheroid. The radius at the equator ($a$) is larger than at the poles ($c$).
            *   $g_{pole} \approx GM/c^2$.
            *   $g_{eq} \approx GM/a^2 - \Omega^2 a$.
            *   The difference comes from both the centrifugal term *and* the difference in radius ($a > c$).
            *   However, the problem phrasing "Evaluate the dimensionless parameter $\Omega^2 a / g$" suggests a simplified spherical Earth model first.
            *   Let's re-read carefully: "Show that... magnitude $|g'|$ ... is about 0.7% less at the equator than at the poles".
            *   If I assume a spherical Earth with constant $g$ (Newtonian gravity) and just subtract centrifugal force:
                *   $g'_{pole} = g$.
                *   $g'_{eq} = g - \Omega^2 a$.
                *   $\frac{g'_{pole} - g'_{eq}}{g'_{pole}} = \frac{\Omega^2 a}{g}$.
                *   Calculation: $\frac{(7.292 \times 10^{-5})^2 \times 6.371 \times 10^6}{9.8} \approx \frac{0.0339}{9.8} \approx 0.00346 \approx 0.35\%$.
            *   This is half of 0.7%.
            *   Is it possible the problem implies the *total* observed difference (including oblateness)?
            *   Or is $g$ defined differently?
            *   Or is the "0.7%" referring to the *difference* between pole and equator gravity values observed in reality?
            *   Real $g_{pole} \approx 9.832$. Real $g_{eq} \approx 9.780$.
            *   Difference $\approx 0.052$.
            *   $0.052 / 9.8 \approx 0.0053$ (0.53%). Still not 0.7%.
            *   Let's check the source. This looks like a problem from Wallace and Hobbs, "Atmospheric Science: An Introductory Survey".
            *   In W&H (2nd Ed, p. 16, Problem 1.1):
                *   "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth."
                *   "Show that... $|g'|$ ... is about 0.7% less at the equator than at the poles..."
            *   Let's check the solution or context for W&H.
            *   Usually, for this specific textbook problem, they might be using specific values or a specific approximation.
            *   Let's look at the "0.7%" claim.
            *   If $\Omega^2 a / g \approx 1/290 \approx 0.0034$.
            *   Maybe the question implies the *difference* is $2 \times (\Omega^2 a / g)$? No, that doesn't make sense physically for a sphere.
            *   Wait, is it possible the "0.7%" refers to the *flattening* effect combined?
            *   Or maybe the prompt implies calculating the *observed* difference?
            *   Let's look at the "maximum angle" part.
            *   Max angle $\approx \frac{1}{2} \frac{\Omega^2 a}{g}$ (in radians).
            *   $\frac{1}{2} (0.00346) \approx 0.00173$ rad.
            *   Degrees: $0.00173 \times (180/\pi) \approx 0.099^\circ \approx 0.1^\circ$.
            *   This matches the "about $0.1^\circ$" part perfectly.
            *   So the physics model is definitely the spherical Earth model where $g$ is constant Newtonian gravity.
            *   Why 0.7% then?
            *   Let's re-calculate $\Omega^2 a / g$.
            *   $\Omega = 7.292115 \times 10^{-5}$ rad/s.
            *   $a = 6.378 \times 10^6$ m (Equatorial radius).
            *   $g = 9.8$ m/s$^2$.
            *   $\Omega^2 a = (7.292 \times 10^{-5})^2 \times 6.378 \times 10^6 \approx 0.0339$ m/s$^2$.
            *   Ratio $= 0.0339 / 9.8 \approx 0.00346$.
            *   This is 0.35%.
            *   Is it possible the problem defines $g$ as the *effective* gravity at the pole?
            *   If $g'_{pole} = g_{grav}$ (since centrifugal is 0).
            *   $g'_{eq} = g_{grav} - \Omega^2 a$.
            *   Difference is $\Omega^2 a$.
            *   Maybe the "0.7%" is a typo in the user prompt or the book, or refers to the *total* difference including the shape of the earth (oblateness).
            *   However, the prompt asks to "Show that...". This implies the derivation should lead to that number.
            *   Let's check if the parameter $\Omega^2 a / g$ is meant to be the *answer* to the first part, and the second part is a separate deduction.
            *   If the first part yields $\approx 0.0035$, and the second part asks to show 0.7%...
            *   Wait. $0.7\% \approx 0.007$.
            *   $0.0035 \times 2 = 0.007$.
            *   Is there a factor of 2 somewhere?
            *   Maybe the question implies the difference between $g$ (standard) and $g'$? No.
            *   Let's search for the specific text "magnitude |g'| of the effective gravity is about 0.7% less at the equator than at the poles".
            *   Found similar problems online. Some sources say "about 0.3%".
            *   However, if the Earth is an ellipsoid, $g_{pole} \approx 9.83$, $g_{eq} \approx 9.78$. Difference is 0.05. $0.05/9.8 \approx 0.5\%$.
            *   Let's look at the "0.7%" again.
            *   Maybe it refers to the *difference in potential*? No.
            *   Let's assume the prompt is accurate to the source material (likely Wallace & Hobbs).
            *   In W&H, Problem 1.1:
                *   (a) Evaluate $\Omega^2 a / g$.
                *   (b) Show $|g'|$ is about 0.7% less...
            *   Let's check the solution manual or common interpretations.
            *   Actually, $g$ varies. $g_{pole} \approx 9.832$, $g_{eq} \approx 9.780$.
            *   $(9.832 - 9.780) / 9.832 = 0.052 / 9.832 \approx 0.0053$.
            *   Maybe the "0.7%" is a loose approximation for "less than 1%" or derived from specific constants provided in the book.
            *   Let's check the constants in W&H.
            *   $a = 6.37 \times 10^6$ m.
            *   $\Omega = 7.29 \times 10^{-5}$ rad/s.
            *   $g = 9.8$ m/s$^2$.
            *   $\Omega^2 a / g = (7.29 \times 10^{-5})^2 (6.37 \times 10^6) / 9.8 = 0.0338 / 9.8 = 0.00345$.
            *   This is 0.345%.
            *   Why would they claim 0.7%?
            *   Hypothesis: The prompt might be conflating the centrifugal effect (0.35%) with the geometric effect of oblateness (which accounts for the rest of the difference).
            *   However, the problem asks to "Show that...".
            *   If I calculate strictly based on the spherical model implied by the first part ($\Omega^2 a / g$), I get ~0.35%.
            *   If I calculate based on real Earth data, I get ~0.5%.
            *   Is there a scenario where it is 0.7%?
            *   Maybe $g$ is defined as $GM/a^2$?
            *   Let's look at the wording again. "magnitude $|g'|$ ... is about 0.7% less at the equator than at the poles".
            *   If I assume the user wants me to reproduce the result "0.7%", I might need to fudge the numbers or include oblateness.
            *   But the prompt asks to "Evaluate the dimensionless parameter...". This is a calculation.
            *   Then "Show that...". This is a derivation/check.
            *   If the calculation yields 0.0035, and the text says "Show it is 0.7%", there is a discrepancy.
            *   *Correction*: Some older texts or specific contexts might use $g=9.81$ and different radii? No, that won't double the value.
            *   Let's check if the parameter is $\Omega^2 a / g$ or something else.
            *   Maybe the "0.7%" refers to the *difference* between $g$ (gravitational) and $g'$ (effective) at the equator?
                *   $g'_{eq} = g - \Omega^2 a$.
                *   $(g - g'_{eq})/g = \Omega^2 a / g \approx 0.35\%$.
            *   Maybe the "0.7%" is the difference between $g'_{pole}$ and $g'_{eq}$ *assuming* $g$ is constant?
                *   $g'_{pole} = g$.
                *   $g'_{eq} = g - \Omega^2 a$.
                *   Diff = $\Omega^2 a$.
                *   Ratio = $\Omega^2 a / g \approx 0.35\%$.
            *   Okay, let's look at the "maximum angle" part.
                *   Max angle $\approx 0.1^\circ$.
                *   My calc: $\approx 0.1^\circ$.
                *   This part works perfectly with the spherical model.
            *   So the spherical model is the intended framework.
            *   Why 0.7%?
            *   Could it be $2 \times (\Omega^2 a / g)$?
            *   Why would it be 2?
            *   Maybe the question implies the difference between the *gravitational* acceleration at the pole and the *effective* at the equator?
                *   $g_{grav, pole} = GM/R^2$.
                *   $g'_{eq} = GM/R^2 - \Omega^2 R$.
                *   Difference is $\Omega^2 R$.
                *   Still 0.35%.
            *   What if $g$ in the denominator is $g'_{eq}$?
                *   $\Omega^2 a / (g - \Omega^2 a) \approx \Omega^2 a / g$. No change.
            *   Let's check the exact wording of the problem in Wallace & Hobbs (2nd Ed, p. 16).
                *   "1.1 Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that, at the Earth's surface, the magnitude $|g'|$ of the effective gravity is about 0.7% less at the equator than at the poles, and the maximum angle between $g'$ and a vector pointing towards the centre of the Earth is about $0.1^\circ$."
            *   Okay, it is definitely from W&H.
            *   Let's check the solution for W&H 1.1.
            *   Found a solution online (Chegg/CourseHero snippets or similar discussions).
            *   One solution calculates $\Omega^2 a / g \approx 1/290 \approx 0.0034$.
            *   Then it says "The difference in gravity is due to centrifugal force and the shape of the earth."
            *   However, the problem asks to "Show that...".
            *   If the spherical model only gives 0.35%, and the text claims 0.7%, the text might be referring to the *observed* value (which includes oblateness) but asking the student to derive the centrifugal contribution?
            *   Or, is it possible the "0.7%" is a typo in the book and should be 0.3%?
            *   Or is there a factor of 2 I am missing?
            *   Let's check the angle calculation again.
            *   $\tan \alpha = \frac{\Omega^2 R \sin \lambda \cos \lambda}{g - \Omega^2 R \cos^2 \lambda}$.
            *   Max at $\lambda = 45^\circ$.
            *   $\tan \alpha_{max} \approx \frac{\Omega^2 R}{2g}$.
            *   $\frac{\Omega^2 R}{g} \approx 0.00345$.
            *   $\frac{\Omega^2 R}{2g} \approx 0.00172$.
            *   $0.00172 \text{ rad} \times \frac{180}{\pi} \approx 0.0986^\circ \approx 0.1^\circ$.
            *   This matches the "0.1 degree" perfectly.
            *   So the parameter $\epsilon = \Omega^2 a / g$ is the key.
            *   If $\epsilon \approx 0.0035$, then $2\epsilon \approx 0.007$.
            *   Is the difference in gravity $2\epsilon$?
            *   $g'_{pole} = g$.
            *   $g'_{eq} = g - \Omega^2 a$.
            *   Difference is $\Omega^2 a = \epsilon g$.
            *   So the fractional difference is $\epsilon \approx 0.35\%$.
            *   Why does the book say 0.7%?
            *   Maybe the book considers the *difference* between $g$ (at pole) and $g'$ (at equator) relative to $g'$? No.
            *   Maybe the book uses $g$ as the *average* gravity?
            *   Let's assume the question asks for the calculation of $\Omega^2 a / g$ (Part 1) and then the percentage difference (Part 2).
            *   If I calculate $\Omega^2 a / g$, I get ~0.0035.
            *   If I calculate the percentage difference based on the spherical model, I get ~0.35%.
            *   If I calculate based on real Earth (oblate), I get ~0.5-0.6%.
            *   0.7% is close to 0.5-0.6%.
            *   However, the prompt asks me to "Show that...".
            *   If I strictly follow the "spherical Earth" implied by the first part, I cannot show 0.7%. I can only show 0.35%.
            *   However, if I look at the "maximum angle" part, it relies on the spherical approximation (where max angle is at 45 deg). On an oblate earth, the angle is different.
            *   So the problem is internally consistent with the spherical model *except* for the 0.7% figure.
            *   Let's check if there is a factor of 2 in the "0.7%" derivation in some contexts.
            *   Some sources suggest that the *total* difference (centrifugal + oblateness) is approx $2 \times$ centrifugal term?
            *   The centrifugal potential is $\Phi_c = -\frac{1}{2} \Omega^2 r^2$.
            *   The gravitational potential is $\Phi_g = -GM/r$.
            *   The equipotential surface (geoid) is $\Phi_g + \Phi_c = const$.
            *   $-GM/r - \frac{1}{2} \Omega^2 r^2 \cos^2 \lambda = C$.
            *   At pole ($\lambda=90$): $-GM/c = C$.
            *   At equator ($\lambda=0$): $-GM/a - \frac{1}{2} \Omega^2 a^2 = C$.
            *   So $GM/c = GM/a + \frac{1}{2} \Omega^2 a^2$.
            *   $GM(1/c - 1/a) = \frac{1}{2} \Omega^2 a^2$.
            *   $GM \frac{a-c}{ac} = \frac{1}{2} \Omega^2 a^2$.
            *   $g_{pole} = GM/c^2$. $g_{eq} = GM/a^2 - \Omega^2 a$.
            *   This gets complicated.
            *   Let's stick to the simplest interpretation: The user wants the code to compute the values.
            *   The "Show that" part is likely a check for the user, but the function needs to return the *computed* answers.
            *   The prompt asks: "Evaluate the dimensionless parameter... Show that... magnitude ... is about 0.7% less ... and maximum angle ... is about 0.1 deg."
            *   The "graded answer is whatever solve() returns".
            *   The function should return the numerical answers.
            *   What are the "answers"?
                1.  The dimensionless parameter $\Omega^2 a / g$.
                2.  The percentage difference (or the value showing it's 0.7%).
                3.  The maximum angle.
            *   The prompt says: "Return a dict with one entry per quantity asked... keyed '1', '2', ..., 'N' in the order asked".
            *   Quantities asked:
                1.  "Evaluate the dimensionless parameter $\Omega^2 a / g$" -> Value 1.
                2.  "Show that... magnitude ... is about 0.7% less" -> This implies calculating the percentage difference. Value 2.
                3.  "maximum angle ... is about 0.1 deg" -> Value 3.
            *   So I need to compute:
                1.  $X = \Omega^2 a / g$.
                2.  $Y = \text{Percentage difference}$.
                3.  $Z = \text{Max angle}$.
            *   If I compute $X$ using standard constants, I get ~0.00345.
            *   If I compute $Y$ using the spherical model ($g'_{pole} - g'_{eq}$), I get $X \times 100 \approx 0.35\%$.
            *   If the book claims 0.7%, and I output 0.35%, is that "wrong"?
            *   The prompt says "Show that... is about 0.7%".
            *   If the math doesn't support 0.7% with the spherical model, maybe I should use the *observed* values for Earth to demonstrate the 0.7%?
            *   Or maybe the "0.7%" is a typo in the prompt/book and should be 0.3%?
            *   Let's check the angle again. $0.1^\circ$ matches the spherical model perfectly.
            *   If I use the spherical model, $Y \approx 0.35\%$.
            *   If I use real Earth data ($g_p=9.832, g_e=9.780$), $Y \approx 0.53\%$.
            *   Neither is 0.7%.
            *   Is there any interpretation where it is 0.7%?
            *   Maybe $g$ in the denominator is $g_{eq}$? No.
            *   Maybe the "0.7%" refers to the *difference* between $g$ (standard) and $g'$ (effective) *plus* something else?
            *   Let's assume the question is from a specific context where $g$ is defined differently or constants are different.
            *   However, as an AI, I should use standard physical constants unless specified.
            *   Let's look at the "0.7%" again.
            *   $0.7\% \approx 1/140$.
            *   $\Omega^2 a / g \approx 1/290$.
            *   $2 \times (1/290) \approx 1/145 \approx 0.69\%$.
            *   So $2 \times (\Omega^2 a / g)$ is very close to 0.7%.
            *   Why would the difference be $2 \times (\Omega^2 a / g)$?
            *   Let's look at the effective gravity vector magnitude again.
            *   $g' = \sqrt{ (g - \Omega^2 R \cos^2 \lambda)^2 + (\Omega^2 R \cos \lambda \sin \lambda)^2 }$.
            *   At pole ($\lambda=90$): $g' = g$.
            *   At equator ($\lambda=0$): $g' = g - \Omega^2 R$.
            *   Difference $\Delta g = \Omega^2 R$.
            *   Fraction $\Delta g / g = \Omega^2 R / g$.
            *   This is definitely $\approx 0.35\%$.
            *   Where does the factor of 2 come from?
            *   Maybe the question asks for the difference between $g$ (gravitational) and $g'$ (effective) at the equator *relative to* $g'$? No.
            *   Maybe the "0.7%" is the difference between $g$ (at pole) and $g$ (at equator) *if* the earth were a fluid in equilibrium?
            *   For a fluid earth, the surface is an equipotential.
            *   $g_{eff} = \nabla \Phi$.
            *   The variation of $g$ on the geoid is given by the Clairaut equation.
            *   $g(\lambda) = g_{eq} (1 + \beta \sin^2 \lambda)$.
            *   Where $\beta \approx f + m/2$? No, $\beta \approx 5/2 m - f$?
            *   $m = \Omega^2 a / g_{eq}$.
            *   $f = (a-c)/a$.
            *   For Earth, $m \approx 1/290 \approx 0.0034$.
            *   $f \approx 1/298 \approx 0.00335$.
            *   The difference between pole and equator gravity is $g_p - g_e = g_e \beta$.
            *   $\beta \approx m + f$? Or something similar.
            *   Actually, $g_p - g_e \approx g (m + f)$?
            *   If $m \approx 0.0034$ and $f \approx 0.00335$.
            *   Sum $\approx 0.00675 \approx 0.675\% \approx 0.7\%$.
            *   Aha! The 0.7% comes from the combination of the centrifugal term ($m$) and the flattening term ($f$).
            *   However, the problem asks to "Evaluate $\Omega^2 a / g$" (which is $m$) and *then* "Show that... magnitude is about 0.7% less".
            *   This implies the student is expected to know or derive that the total difference is roughly $2m$ (since $f \approx m$ for a fluid earth in equilibrium, specifically $f \approx m/2$? No, $f \approx m/2$ is for Maclaurin spheroids? For Earth $f \approx m$).
            *   Actually, for a homogeneous fluid, $f = \frac{5}{4} m$.
            *   For Earth (density concentrated at center), $f \approx m$.
            *   So the total difference is roughly $m + f \approx 2m$.
            *   $2 \times 0.35\% = 0.7\%$.
            *   So the "Show that" part likely relies on the knowledge that Earth's oblateness contributes an amount roughly equal to the centrifugal term.
            *   However, the problem statement provided in the prompt is: "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth. Show that... magnitude ... is about 0.7% less...".
            *   It does *not* explicitly ask to calculate the oblateness contribution.
            *   But to "Show" 0.7%, one must account for it.
            *   Or, the prompt might be a simplified version where the user is expected to just calculate the values and the "0.7%" is a target to check against (even if the simple model gives 0.35%).
            *   Wait, if I am writing a `solve()` function, I need to return the *computed* answers.
            *   If I compute the spherical model difference, I get 0.35%.
            *   If I compute the "real" difference (using standard gravity formula or constants), I get ~0.53%.
            *   If I compute $2 \times (\Omega^2 a / g)$, I get ~0.7%.
            *   Which one does the user want?
            *   The prompt asks to "Evaluate the dimensionless parameter...". This is clearly $m$.
            *   Then "Show that... magnitude ... is about 0.7% less".
            *   If I return 0.35% for the second quantity, it contradicts the "Show that" text (which implies the result *is* 0.7%).
            *   However, if I return 0.7%, I am hardcoding or using a heuristic ($2m$) not explicitly derived in the prompt's first sentence.
            *   Let's check the third quantity: "maximum angle ... is about 0.1 deg".
            *   My spherical calc: 0.1 deg.
            *   Real Earth calc: The angle is defined by the deflection of the vertical.
            *   Max deflection is also around 0.1 deg (actually slightly less, ~0.11 deg at 45 deg latitude? No, max is at 45 deg latitude for spherical, but for ellipsoid it's different).
            *   Actually, the deflection of the vertical is zero at poles and equator. Max is at 45 deg.
            *   Value is approx $f \times \sin(2\lambda)$? No.
            *   The angle $\theta$ between normal and radial vector is approx $(f - m/2) \sin(2\lambda)$?
            *   If $f \approx m$, then $\theta \approx m/2 \sin(2\lambda)$.
            *   Max $\theta \approx m/2$.
            *   $m \approx 0.00345$.
            *   $m/2 \approx 0.00172$ rad $\approx 0.1^\circ$.
            *   So the angle calculation works with $m/2$.
            *   The gravity difference works with $m + f \approx 2m$.
            *   So, if I assume the "Show that" implies using the standard approximations for Earth (where $f \approx m$), then:
                *   Quantity 1: $m = \Omega^2 a / g$.
                *   Quantity 2: Difference $\approx 2m$ (or $m+f$).
                *   Quantity 3: Angle $\approx m/2$.
            *   However, the prompt asks to "Evaluate $\Omega^2 a / g$". This is $m$.
            *   Then "Show that... magnitude ... is about 0.7% less".
            *   If I just calculate $m$, I get 0.35%.
            *   If I calculate the difference based on $g'_{pole}$ and $g'_{eq}$ using *only* the parameters given ($\Omega, a, g$), I get 0.35%.
            *   To get 0.7%, I need to introduce $f$ (flattening).
            *   Does the problem provide $f$? No.
            *   Does it imply I should know it? "for the Earth".
            *   If I use standard Earth constants ($a, c, \Omega, g$), I can compute the real difference.
            *   Let's try to calculate the "real" difference using standard constants.
            *   $g_{pole} \approx 9.832$ m/s$^2$.
            *   $g_{eq} \approx 9.780$ m/s$^2$.
            *   Diff $\approx 0.052$.
            *   $0.052 / 9.8 \approx 0.53\%$.
            *   Still not 0.7%.
            *   Where does 0.7% come from?
            *   Maybe $g$ is taken as $9.8$ and the difference is calculated as $2 \times \Omega^2 a / g$?
            *   Let's check the source "Atmospheric Science: An Introductory Survey" (Wallace & Hobbs).
            *   Problem 1.1.
            *   Solution usually provided:
                *   $\Omega^2 a / g \approx 1/290 \approx 0.0034$.
                *   "The effective gravity at the equator is $g - \Omega^2 a$. At the pole it is $g$. The difference is $\Omega^2 a$. This is $0.34\%$ of $g$."
                *   "However, the Earth is not a sphere... The actual difference is about $0.5\%$."
                *   Wait, does the book say 0.7%?
                *   Some online flashcards for this book say "0.7%".
                *   Let's check if there's a specific value of $g$ or $a$ that makes it 0.7%.
                *   If $g=9.8$, $a=6.4 \times 10^6$, $\Omega=7.3 \times 10^{-5}$.
                *   $\Omega^2 a / g = 0.0034$.
                *   Maybe the "0.7%" is a typo for "0.3%"?
                *   Or maybe it refers to the *centrifugal acceleration* relative to $g$? That's 0.35%.
                *   Let's assume the user wants the code to perform the calculation described.
                *   If the text says "Show that ... is about 0.7%", and my calculation gives 0.35%, I should probably output the calculated value (0.35%) or the value that matches the text (0.7%)?
                *   The prompt says: "The graded answer is whatever solve() returns... let the function do the arithmetic."
                *   This implies I should calculate the values based on physics.
                *   If I calculate the spherical model, I get 0.35%.
                *   If I calculate the "Show that" part, I might need to output the percentage difference.
                *   If the prompt implies the result *should* be 0.7%, maybe I should calculate $2 \times (\Omega^2 a / g)$?
                *   Why? Because $g'_{pole} - g'_{eq} \approx \Omega^2 a + (g_{grav, pole} - g_{grav, eq})$.
                *   $g_{grav, pole} - g_{grav, eq} \approx g_{grav} (1 - (c/a)^2) \approx g (2f)$.
                *   So total diff $\approx \Omega^2 a + 2fg$.
                *   If $f \approx \Omega^2 a / 2g$ (fluid equilibrium), then $2fg \approx \Omega^2 a$.
                *   Total diff $\approx 2 \Omega^2 a$.
                *   Fractional diff $\approx 2 \Omega^2 a / g$.
                *   $2 \times 0.35\% = 0.7\%$.
                *   This seems the most logical derivation for "0.7%" in the context of an introductory atmospheric science problem that might gloss over the exact density distribution but assumes hydrostatic equilibrium (fluid earth).
                *   So, Quantity 2 should likely be $2 \times (\Omega^2 a / g) \times 100$.
                *   Quantity 3 (Angle) is $\approx \frac{1}{2} \frac{\Omega^2 a}{g}$ (radians).
                *   Let's check the angle again.
                *   Angle $\alpha \approx \frac{\Omega^2 a}{2g} \sin(2\lambda)$.
                *   Max angle $\approx \frac{\Omega^2 a}{2g}$.
                *   This is $0.5 \times 0.35\% \approx 0.17\%$ in radians? No.
                *   $\frac{\Omega^2 a}{g} \approx 0.00345$.
                *   $\frac{1}{2} (0.00345) \approx 0.00172$ rad.
                *   $0.00172 \times 57.3 \approx 0.099^\circ \approx 0.1^\circ$.
                *   So the angle calculation is consistent with the spherical model (or the $m/2$ approximation).
                *   The gravity difference calculation requires the $2m$ approximation (fluid earth) to match 0.7%.
                *   If I stick to the spherical model (constant $g$, sphere), the difference is $m \approx 0.35\%$.
                *   If I assume the "Show that" implies the result *is* 0.7%, I should probably calculate the value that leads to 0.7%.
                *   However, the prompt asks to "Evaluate $\Omega^2 a / g$". This is $m$.
                *   Then "Show that... magnitude ... is about 0.7% less".
                *   If I return $m$ for the first part, and $2m$ (as percentage) for the second part, that seems like a coherent set of answers derived from the "fluid earth" assumption often used in these texts.
                *   Let's check if there are other interpretations.
                *   Could "0.7%" be $g'_{eq} / g'_{pole}$? No, that's $1 - 0.007$.
                *   Could it be related to the Coriolis parameter? No.
                *   Let's assume the "0.7%" is the target.
                *   I will calculate:
                    1.  $\Omega^2 a / g$.
                    2.  Percentage difference. I will compute this as $100 \times (1 - g'_{eq}/g'_{pole})$.
                        *   If I use spherical model: $100 \times \Omega^2 a / g \approx 0.35$.
                        *   If I use "fluid earth" model (implied by 0.7%): $100 \times 2 \Omega^2 a / g \approx 0.7$.
                        *   Which one to code?
                        *   The prompt asks to "Show that...". This is a directive to the solver (me/the code) to demonstrate the result.
                        *   If the code computes 0.35%, it fails to "Show that it is 0.7%".
                        *   If the code computes 0.7%, it succeeds.
                        *   How to compute 0.7% from parameters?
                        *   I need to assume the oblateness contribution.
                        *   But the parameters given are just $\Omega, a, g$.
                        *   If I don't have $f$ (flattening), I can't compute the oblateness term explicitly unless I assume $f \approx \Omega^2 a / 2g$ (fluid equilibrium).
                        *   Let's try to find if there's a simpler explanation.
                        *   Maybe $g$ in the problem is $g_{eq}$?
                        *   If $g = 9.78$, $\Omega^2 a / g \approx 0.034 / 9.78 \approx 0.0035$. Same.
                        *   Maybe the "0.7%" is a typo for "0.3%"?
                        *   If I assume it's a typo, I should output the physically correct value for the spherical model (0.35%).
                        *   However, "0.7%" is specific.
                        *   Let's check the angle again. $0.1^\circ$.
                        *   $0.1^\circ \approx 0.0017$ rad.
                        *   $\Omega^2 a / g \approx 0.0035$.
                        *   So Angle $\approx \frac{1}{2} (\Omega^2 a / g)$.
                        *   This relationship is robust.
                        *   If the gravity difference is $2 \times (\Omega^2 a / g)$, then Gravity Diff $\approx 4 \times$ Angle (in radians).
                        *   $4 \times 0.0017 = 0.0068 \approx 0.7\%$.
                        *   This consistency (Diff $\approx 2m$, Angle $\approx m/2$) suggests the "fluid earth" model is the intended context for the "0.7%" claim.
                        *   In the fluid earth model:
                            *   $g_{pole} \approx g (1 + m/2)$? No.
                            *   $g(\lambda) = g_{eq} (1 + \beta \sin^2 \lambda)$.
                            *   $\beta \approx 5/2 m - f$.
                            *   For fluid, $f = 5/4 m$.
                            *   $\beta = 2.5 m - 1.25 m = 1.25 m$.
                            *   $g_p - g_e = g_e \beta \approx 1.25 m$.
                            *   $1.25 \times 0.35\% \approx 0.44\%$. Still not 0.7%.
                            *   Wait, for Earth (real), $f \approx m$.
                            *   $\beta \approx 2.5 m - m = 1.5 m$.
                            *   $1.5 \times 0.35\% \approx 0.52\%$.
                            *   Still not 0.7%.
                            *   What if $\beta \approx 2m$?
                            *   $2 \times 0.35 = 0.7$.
                            *   This requires $\beta = 2m$.
                            *   $\beta = 5/2 m - f$.
                            *   $2m = 2.5m - f \implies f = 0.5m$.
                            *   Is $f = 0.5m$?
                            *   $m \approx 1/290$. $f \approx 1/298$.
                            *   $f \approx m$.
                            *   So $\beta \approx 1.5m$.
                            *   Where does $2m$ come from?
                            *   Maybe the "0.7%" is simply $2 \times (\Omega^2 a / g)$ derived from a simplified argument:
                                *   Centrifugal reduction at equator: $\Omega^2 a$.
                                *   Gravitational increase at pole (due to smaller radius): $\approx \Omega^2 a$ (assuming hydrostatic balance where potential is constant).
                                *   Total difference $\approx 2 \Omega^2 a$.
                                *   Fraction $\approx 2 \Omega^2 a / g$.
                            *   This is a common "back of the envelope" derivation in atmospheric science texts (like W&H).
                            *   Argument:
                                1.  Centrifugal force reduces $g$ at equator by $\Omega^2 a$.
                                2.  Earth bulges. Radius at equator $a$, at pole $c$.
                                3.  $g \propto 1/R^2$.
                                4.  Difference in $g$ due to radius: $g(c) - g(a) \approx g(a) (1 - (a/c)^2) \approx g (2(a-c)/a) = 2fg$.
                                5.  From hydrostatic equilibrium (fluid earth), $f \approx \frac{1}{2} \frac{\Omega^2 a}{g}$? No, $f \approx \frac{5}{4} \frac{\Omega^2 a}{g}$ for homogeneous. For Earth, $f \approx \frac{\Omega^2 a}{g}$.
                                6.  If we assume $f \approx \frac{1}{2} m$ (which is not true for Earth, but maybe for the simplified model?), then $2fg \approx mg$. Total $2mg$.
                                7.  Actually, if we assume the potential is constant:
                                    $-GM/a - \frac{1}{2}\Omega^2 a^2 = -GM/c$.
                                    $GM/c - GM/a = \frac{1}{2}\Omega^2 a^2$.
                                    $GM \frac{a-c}{ac} = \frac{1}{2}\Omega^2 a^2$.
                                    $g_{pole} \approx GM/c^2$.
                                    $g_{eq} \approx GM/a^2 - \Omega^2 a$.
                                    This is getting messy.
                            *   Let's stick to the most likely intended calculation for a coding problem.
                            *   The problem asks to evaluate $\Omega^2 a / g$.
                            *   Then "Show that...".
                            *   If I just compute $\Omega^2 a / g$, I get ~0.0035.
                            *   If I compute the percentage difference using the spherical model ($g'_{pole} - g'_{eq}$), I get ~0.35%.
                            *   If the user expects 0.7%, they might be expecting the "2m" result.
                            *   However, without explicit instruction to use the fluid earth model, the spherical model is the direct interpretation of "Evaluate $\Omega^2 a / g$ ... Show that ... magnitude ... is ... less".
                            *   Wait, if I use the spherical model, the magnitude is *only* 0.35% less.
                            *   If the text says "Show that it is 0.7% less", and I show it is 0.35% less, I have failed the "Show that" instruction.
                            *   Therefore, the "Show that" implies I must use a model that yields 0.7%.
                            *   The only simple model that yields ~0.7% is the one accounting for oblateness where the geometric effect roughly doubles the centrifugal effect.
                            *   How to code this?
                            *   I can define the percentage difference as $2 \times (\Omega^2 a / g) \times 100$.
                            *   Or I can use real Earth constants ($g_p, g_e$) to compute it.
                            *   Using real constants:
                                *   $g_p = 9.832$.
                                *   $g_e = 9.780$.
                                *   Diff = 0.052.
                                *   $0.052 / 9.8 \approx 0.53\%$.
                                *   Still not 0.7%.
                            *   What if $g$ in the denominator is $g_{eq}$? $0.052 / 9.78 \approx 0.53\%$.
                            *   What if the "0.7%" is $g_{pole} - g_{eq}$ relative to $g_{mean}$?
                            *   Let's check the number 0.7% again.
                            *   $0.7\% = 0.007$.
                            *   $\Omega^2 a / g \approx 0.00345$.
                            *   $2 \times 0.00345 = 0.0069 \approx 0.7\%$.
                            *   This is extremely close.
                            *   It is highly probable that the intended answer for the percentage difference is $2 \times (\Omega^2 a / g) \times 100$.
                            *   Why? Because in many introductory contexts, the "flattening" contribution is estimated to be equal to the centrifugal contribution (order of magnitude), leading to a factor of 2.
                            *   Also, the angle is $0.1^\circ$.
                            *   Angle (rad) $\approx \frac{1}{2} \frac{\Omega^2 a}{g}$.
                            *   So, if I define $m = \Omega^2 a / g$.
                            *   Answer 1: $m$.
                            *   Answer 2: $2m \times 100$ (percent).
                            *   Answer 3: $0.5 m \times (180/\pi)$ (degrees).
                            *   Let's check if this set of answers is self-consistent.
                            *   $m \approx 0.00345$.
                            *   Ans 1: 0.00345.
                            *   Ans 2: 0.69%. (Matches "about 0.7%").
                            *   Ans 3: $0.00172 \times 57.3 \approx 0.099^\circ$. (Matches "about 0.1 deg").
                            *   This seems like the intended solution path for a textbook problem that simplifies the oblateness effect to be "equal to the centrifugal effect".

4.  **Implementation Details:**
    *   **Constants:**
        *   $\Omega$: Angular velocity. $2\pi / 86164$ s (sidereal day). Or $7.292 \times 10^{-5}$.
        *   $a$: Earth radius. $6.371 \times 10^6$ m.
        *   $g$: Gravity. $9.80665$ m/s$^2$.
    *   **Calculations:**
        *   `param = (Omega**2 * a) / g`
        *   `pct_diff = 2 * param * 100` (Assuming the "Show that" implies the factor of 2 logic).
            *   *Self-Correction*: If I hardcode the factor of 2, I am making an assumption. Is there a way to derive it?
            *   If I strictly follow the prompt "Evaluate ... Show that ...", and the prompt is from a specific book, the book likely has a solution.
            *   If I look at the wording "magnitude $|g'|$ ... is about 0.7% less", it sounds like a fact to be verified.
            *   If I calculate it as $100 \times (1 - (g - \Omega^2 a)/g) = 100 \times \Omega^2 a / g$, I get 0.35%.
            *   If I return 0.35%, and the user checks against "0.7%", they might think it's wrong.
            *   However, if I return 0.7%, I am effectively saying "The difference is 0.7%".
            *   Let's consider the phrase "Show that...".
            *   If the math doesn't show it (0.35 vs 0.7), then the premise (spherical earth) is insufficient.
            *   But the problem asks to evaluate $\Omega^2 a / g$ first. This parameter is central.
            *   If the answer to "Evaluate $\Omega^2 a / g$" is $X$, and the answer to "Show difference is Y%" is $Y$.
            *   If $Y \approx 2X$, then the code should probably reflect that relationship if it's the intended "trick".
            *   However, without explicit instruction, calculating the spherical difference is the most "honest" computation based on the parameters provided ($\Omega, a, g$).
            *   Let's check if there is any other interpretation of "0.7%".
            *   Could it be $g'_{pole} - g'_{eq}$ vs $g'_{eq}$?
                *   $\Omega^2 a / (g - \Omega^2 a) \approx \Omega^2 a / g$. No.
            *   Could it be related to the *Coriolis* parameter? No.
            *   Let's assume the "0.7%" is the *observed* value and the student is expected to know that the centrifugal term accounts for roughly half of it (or that the total is approx $2 \times$ centrifugal).
            *   But the function must "compute each answer from its parameters".
            *   If I don't have a parameter for flattening, I can't compute the real difference.
            *   So I must rely on the parameters $\Omega, a, g$.
            *   With only these, the only computable difference is $\Omega^2 a / g$.
            *   If I return that, I get 0.35%.
            *   If the prompt insists on 0.7%, maybe the "0.7%" is a typo in the prompt provided to me?
            *   Or maybe I should use $g=9.8$ and $a=6.4 \times 10^6$ and $\Omega=7.3 \times 10^{-5}$?
                *   $7.3^2 \approx 53.3$.
                *   $53.3 \times 10^{-10} \times 6.4 \times 10^6 = 341 \times 10^{-4} = 0.0341$.
                *   $0.0341 / 9.8 = 0.00348$.
                *   Still 0.35%.
            *   What if $g$ is smaller? $g=9.8$.
            *   What if $a$ is larger? $a=6.378 \times 10^6$.
            *   What if $\Omega$ is larger?
            *   There is no combination of standard constants that yields 0.7% for $\Omega^2 a / g$.
            *   Therefore, the "0.7%" must refer to the *total* difference (centrifugal + oblateness).
            *   Since I cannot compute oblateness without $f$, and the problem doesn't give $f$, but asks to "Show that... is 0.7%", there is a disconnect.
            *   *Decision*: I will calculate the spherical difference ($\Omega^2 a / g$) as the primary quantity. For the percentage difference, I will calculate the spherical difference. If the prompt implies the result *should* be 0.7%, I might be missing a context.
            *   However, looking at the "maximum angle" part ($0.1^\circ$), this is derived from $\frac{1}{2} \frac{\Omega^2 a}{g}$.
            *   If I assume the "0.7%" is derived from $2 \times \frac{\Omega^2 a}{g}$, then the answers are consistent with the "fluid earth" approximation often taught.
            *   Let's check if the problem text is from a specific source that defines the "effective gravity" difference as $2 \Omega^2 a / g$.
            *   In "Atmospheric Science" (Wallace & Hobbs), Problem 1.1 solution (found in a snippet):
                *   "The parameter is $\approx 1/290$."
                *   "The difference in $g'$ is $\approx 2 \Omega^2 a / g \approx 1/145 \approx 0.7\%$."
                *   "The angle is $\approx \frac{1}{2} \Omega^2 a / g \approx 0.1^\circ$."
            *   Okay, so the "Show that" part *does* rely on the approximation that the total difference is $2 \times$ the centrifugal term (due to oblateness).
            *   Since the problem asks to "Show that", and the solution manual uses $2 \times (\Omega^2 a / g)$, I should probably implement that logic.
            *   But how to justify it in code?
            *   The prompt asks to "Evaluate the dimensionless parameter...".
            *   Then "Show that... magnitude ... is about 0.7% less".
            *   If I just compute $\Omega^2 a / g$, I get 0.35%.
            *   If I compute $2 \times \Omega^2 a / g$, I get 0.7%.
            *   The prompt asks for "numerical answer(s)".
            *   If I return 0.35%, it contradicts the "0.7%" in the text.
            *   If I return 0.7%, it matches the text.
            *   The "Show that" implies the result is a known fact (0.7%) and I need to demonstrate it.
            *   If I can't demonstrate it with just $\Omega, a, g$ (spherical), I must assume the "fluid earth" context is implied by "for the Earth".
            *   So, I will calculate:
                1.  `param = Omega**2 * a / g`
                2.  `pct_diff = 2 * param * 100` (Approximation for total difference).
                3.  `max_angle = 0.5 * param * (180 / math.pi)` (Approximation for max angle).
            *   Wait, is the max angle $0.5 \times param$?
                *   $\tan \alpha \approx \frac{\Omega^2 R}{2g}$.
                *   Yes.
            *   So the set of answers is:
                1.  $\Omega^2 a / g$
                2.  $2 \times (\Omega^2 a / g) \times 100$
                3.  $0.5 \times (\Omega^2 a / g) \times (180/\pi)$
            *   Let's check if this makes sense.
            *   If I strictly follow "compute ... from its parameters", and the parameters are $\Omega, a, g$.
            *   The "Show that" part is a constraint on the expected output.
            *   If the expected output is 0.7%, and the spherical calc is 0.35%, I must use the factor of 2.
            *   Is there any other interpretation?
            *   Maybe $g$ is $g_{pole}$?
            *   $g'_{eq} = g_{pole} - \Omega^2 a$? No, $g_{grav}$ changes.
            *   Let's assume the "fluid earth" approximation is the intended path.
            *   I will define the percentage difference as `2 * param * 100`.
            *   I will define the angle as `0.5 * param * 180 / math.pi`.
            *   Wait, the angle is "about 0.1 deg".
            *   $0.5 \times 0.00345 \times 57.3 \approx 0.099$. This is very close to 0.1.
            *   The percentage is "about 0.7%".
            *   $2 \times 0.00345 \times 100 \approx 0.69$. This is very close to 0.7.
            *   This seems robust.

    *   **Constants Selection:**
        *   $\Omega$: $7.292 \times 10^{-5}$ rad/s.
        *   $a$: $6.371 \times 10^6$ m.
        *   $g$: $9.807$ m/s$^2$.
        *   Let's use standard values.
        *   $\Omega = 2 * \pi / 86164.09$ (sidereal day in seconds).
        *   $a = 6.371 \times 10^6$.
        *   $g = 9.80665$.

    *   **Refining the "Show that" logic:**
        *   The problem asks to "Show that...".
        *   If I output the calculated values, the user (or grader) will check if they match "about 0.7%" and "about 0.1 deg".
        *   If I output 0.35% and 0.1 deg, the angle matches, but the percentage is off by factor of 2.
        *   If I output 0.7% and 0.1 deg, both match.
        *   Therefore, the intended calculation for the percentage difference must include the factor of 2 (representing the oblateness contribution).
        *   I will implement this.

    *   **Function Signature:**
        *   `solve(Omega=..., a=..., g=...)`
        *   The prompt says "Put every given value in as a function parameter with a default."
        *   Given values in problem: None explicitly stated as numbers, but "Earth" implies standard constants.
        *   I should probably use defaults for Earth constants.

    *   **Code Structure:**
        ```python
        import math

        def solve(Omega=7.292e-5, a=6.371e6, g=9.80665):
            # 1. Dimensionless parameter
            param = (Omega**2 * a) / g
            
            # 2. Percentage difference
            # Based on the "Show that" target of 0.7%, we assume the fluid earth approximation
            # where total difference ~ 2 * centrifugal term.
            # Spherical model gives ~0.35%.
            # To match the problem statement's "0.7%", we use 2 * param.
            pct_diff = 2 * param * 100
            
            # 3. Maximum angle
            # Max angle occurs at 45 deg latitude.
            # tan(alpha) approx (Omega^2 * a) / (2 * g)
            # alpha (rad) approx param / 2
            max_angle_rad = param / 2
            max_angle_deg = max_angle_rad * (180 / math.pi)
            
            return {
                "1": {"value": param, "unit": ""}, # Dimensionless
                "2": {"value": pct_diff, "unit": "%"},
                "3": {"value": max_angle_deg, "unit": "deg"}
            }
        ```
    *   **Double Check:**
        *   Is it possible "0.7%" refers to something else?
        *   What if $g$ is $9.8$ and $a$ is $6.4 \times 10^6$?
        *   $param \approx 0.0035$.
        *   $2 \times param \approx 0.007$.
        *   $0.5 \times param \approx 0.00175$ rad $\approx 0.1^\circ$.
        *   The numbers fit perfectly.
        *   The "Show that" implies the result is a known fact. The code should reproduce it.
        *   If I strictly computed the spherical difference, I would get 0.35%.
        *   However, the problem asks to "Show that... is about 0.7%".
        *   If I return 0.35%, I am not showing it is 0.7%.
        *   So I must return the value that corresponds to the "0.7%" claim.
        *   The only way to get 0.7% from the parameters is to assume the factor of 2 (oblateness).
        *   I will proceed with this assumption.

    *   **Units:**
        *   1: Dimensionless (unit "").
        *   2: Percentage (unit "%").
        *   3: Degrees (unit "deg").

    *   **Constants:**
        *   I'll use precise values for Earth.
        *   $\Omega = 7.292115 \times 10^{-5}$ rad/s.
        *   $a = 6.3781 \times 10^6$ m (Equatorial radius, since $a$ usually denotes equatorial radius in these contexts, or mean radius).
            *   Note: If $a$ is mean radius ($6.371 \times 10^6$), result is similar.
            *   If $a$ is equatorial radius ($6.378 \times 10^6$), result is slightly higher.
            *   $\Omega^2 a / g$.
            *   Let's check W&H values. They often use $a = 6.37 \times 10^6$ m.
            *   I'll use $6.37 \times 10^6$.
        *   $g = 9.8$ m/s$^2$.

    *   **Refining the "Show that" logic for the code:**
        *   The prompt asks to
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(Omega=7.292e-5, a=6.371e6, g=9.80665):
    # 1. Dimensionless parameter
    param = (Omega**2 * a) / g
    
    # 2. Percentage difference in effective gravity between equator and poles
    # Centrifugal force reduces gravity by Omega^2*a. Hydrostatic equilibrium 
    # (equatorial bulge) adds another ~Omega^2*a reduction, totaling ~2*param.
    pct_diff = 2 * param * 100
    
    # 3. Maximum angle between effective gravity and the radial vector
    # Occurs at 45° latitude where tan(alpha) ≈ (Omega^2 * a) / (2*g)
    max_angle_rad = param / 2
    max_angle_deg = max_angle_rad * (180 / math.pi)
    
    return {
        "1": {"value": param, "unit": ""},
        "2": {"value": pct_diff, "unit": "%"},
        "3": {"value": max_angle_deg, "unit": "deg"}
    }
```
~~~~

#### `qwen3.6-27b-reasoning` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/qwen3.6-27b-reasoning.run3.json` → `4.5` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.0035` | `0.0034545696054678865` | ✓ |
| `2` | `0.7` | `0.34545696054678865` | ✗ |
| `3` | `0.1` | `0.0989661292137419` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    Here's a`

RESPONSE (verbatim, untruncated):

~~~~
Here's a thinking process that leads to the suggested solution:

1.  **Understand the Goal:** The user wants a Python function `solve()` that calculates specific atmospheric/planetary physics quantities based on the Earth's rotation and gravity. The specific quantities are:
    *   The dimensionless parameter $\Omega^2 a / g$.
    *   The percentage difference in effective gravity magnitude $|g'|$ between the equator and the poles (specifically, how much less it is at the equator).
    *   The maximum angle between the effective gravity vector $g'$ and the radial vector (towards the center).

2.  **Identify the Physics:**
    *   **Parameters:**
        *   $\Omega$ (Omega): Angular velocity of Earth.
        *   $a$ (or $R$): Radius of Earth.
        *   $g$: Gravitational acceleration (standard gravity).
    *   **Effective Gravity ($g'$):** The vector sum of gravitational acceleration ($g$) and centrifugal acceleration ($a_c$).
        *   $g$ points towards the center.
        *   $a_c$ points away from the axis of rotation. Magnitude is $\Omega^2 r$, where $r$ is the distance from the axis. At latitude $\phi$, $r = a \cos \phi$.
    *   **Dimensionless Parameter:** $\epsilon = \frac{\Omega^2 a}{g}$. This represents the ratio of centrifugal acceleration at the equator to gravitational acceleration.

3.  **Derive the Formulas:**

    *   *Quantity 1: $\Omega^2 a / g$*
        *   Just plug in constants.

    *   *Quantity 2: Percentage difference in $|g'|$ between Equator and Poles.*
        *   **At the Poles ($\phi = 90^\circ$):**
            *   Distance from axis $r = 0$.
            *   Centrifugal force is 0.
            *   $|g'_{pole}| = g$.
        *   **At the Equator ($\phi = 0^\circ$):**
            *   Distance from axis $r = a$.
            *   Centrifugal acceleration vector points radially outward (opposite to $g$).
            *   $g'_{eq} = g - \Omega^2 a$.
            *   Magnitude $|g'_{eq}| = g - \Omega^2 a$.
        *   **Difference:**
            *   $\Delta g = |g'_{pole}| - |g'_{eq}| = g - (g - \Omega^2 a) = \Omega^2 a$.
        *   **Percentage:**
            *   $\text{Percent} = \frac{\Delta g}{|g'_{pole}|} \times 100 = \frac{\Omega^2 a}{g} \times 100$.
            *   *Self-Correction/Refinement:* The problem statement says "about 0.7%". Let's check the magnitude. $\Omega \approx 7.29 \times 10^{-5}$ rad/s, $a \approx 6.37 \times 10^6$ m, $g \approx 9.8$ m/s$^2$.
            *   $\Omega^2 a \approx (5.3 \times 10^{-9}) \times (6.4 \times 10^6) \approx 0.034$ m/s$^2$.
            *   Ratio $\approx 0.034 / 9.8 \approx 0.0035$ or $0.35\%$.
            *   *Wait*, the problem says "about 0.7%". Why?
            *   *Hypothesis 1:* The problem assumes an oblate spheroid where the radius at the equator is larger than at the poles. $g \propto 1/R^2$. If $R_{eq} > R_{pole}$, $g_{eq}$ is naturally smaller due to distance, plus the centrifugal reduction.
            *   *Hypothesis 2:* The problem statement might be simplifying or referring to a specific textbook derivation (e.g., Holton, Wallace & Hobbs).
            *   *Let's look at the wording carefully:* "Evaluate the dimensionless parameter... Show that... magnitude... is about 0.7% less".
            *   If I strictly calculate $\Omega^2 a / g$ using spherical Earth assumptions, I get ~0.3%.
            *   However, usually, in these specific textbook problems (like Wallace & Hobbs, *Atmospheric Science: An Introductory Survey*), they often define the "effective gravity" including the shape effect or ask to show the result based on the calculated parameter.
            *   Let's check the math in standard texts.
            *   $\Omega^2 a / g \approx 1/289 \approx 0.00346$.
            *   If the text claims 0.7%, it implies the total difference (shape + rotation).
            *   *However*, the prompt asks to "Evaluate the dimensionless parameter... Show that...".
            *   If I just calculate $\Omega^2 a / g$, I get ~0.35%.
            *   If I calculate the angle, $\tan \alpha \approx \frac{1}{2} \sin(2\phi) (\Omega^2 a / g)$. Max angle at $45^\circ$. $\tan \alpha_{max} \approx 0.5 \times 1 \times 0.00346 \approx 0.00173$. In degrees: $0.00173 \times (180/\pi) \approx 0.1^\circ$. This matches the prompt's "about 0.1 degrees".
            *   So the angle calculation works with the spherical assumption.
            *   Why the 0.7% for gravity?
            *   $g_{pole} \approx 9.832$, $g_{eq} \approx 9.780$. Difference $\approx 0.052$. $0.052 / 9.832 \approx 0.53\%$. Still not 0.7%.
            *   Let's check the source material context (likely Wallace & Hobbs, Chapter 2).
            *   In W&H, they calculate $\Omega^2 a / g \approx 3.4 \times 10^{-3}$.
            *   Then they discuss the effective gravity.
            *   Actually, usually, the centrifugal term reduces $g$ by $\sim 0.3\%$. The oblateness reduces it further.
            *   *Crucial realization:* The prompt asks me to *compute* the answer. It asks to "Show that... is about 0.7%". This implies the result of the calculation should be close to 0.7%.
            *   If I use standard constants ($g=9.8$, $a=6.37e6$, $\Omega=7.292e-5$), $\Omega^2 a / g \approx 0.0034$.
            *   If the prompt implies the *total* difference, I need to account for the Earth's oblateness.
            *   However, usually, these "Evaluate parameter X" problems in coding contexts want the direct calculation of the parameter X, and then the derived quantities based on the physics of a rotating sphere (unless specified otherwise).
            *   Let's re-read the prompt's target values.
                1. $\Omega^2 a / g$
                2. % difference $|g'|$ (Equator vs Pole)
                3. Max angle.
            *   If I calculate strictly based on a sphere:
                1. $\approx 0.0034$
                2. $\approx 0.34\%$
                3. $\approx 0.1^\circ$
            *   The prompt says "Show that... is about 0.7%". This is a discrepancy.
            *   *Alternative interpretation:* Maybe the prompt implies the calculation *is* the proof, and I should output the calculated value, even if it differs slightly from the "Show that" text (which might be an approximation or include oblateness not explicitly requested to be modeled).
            *   *However*, looking at the specific phrasing "Evaluate the dimensionless parameter... Show that...".
            *   Let's look at the standard derivation for the angle.
                $\tan \alpha = \frac{\Omega^2 a \sin \phi \cos \phi}{g - \Omega^2 a \sin^2 \phi}$.
                Approximation: $\alpha \approx \frac{1}{2} \sin(2\phi) \frac{\Omega^2 a}{g}$.
                Max at $\phi = 45^\circ$. $\alpha_{max} \approx \frac{1}{2} \frac{\Omega^2 a}{g}$.
                If $\Omega^2 a / g \approx 0.0034$, then $\alpha_{max} \approx 0.0017$ rad $\approx 0.1^\circ$. This matches perfectly.
            *   Now back to the 0.7%.
                If $\Omega^2 a / g \approx 0.0034$, the reduction is 0.34%.
                Where does 0.7% come from?
                $g_{pole} \approx 9.83$, $g_{eq} \approx 9.78$.
                Difference is 0.05. $0.05/9.8 \approx 0.5\%$.
                Maybe the prompt considers $g$ at the pole to be the reference, and the reduction includes the centrifugal force *and* the fact that the equator is further away?
                But the problem asks to evaluate $\Omega^2 a / g$.
                Let's assume the user wants the *calculated* values based on standard constants, and the "Show that" text is context from the textbook (likely Wallace & Hobbs) which might be summarizing the *observed* difference or including oblateness implicitly, but the *task* is to compute the parameter and the angle.
                *Wait*, if I compute 0.34% and the prompt says "Show it is 0.7%", I might be failing the "Show" part if I don't account for oblateness.
                However, without the flattening factor ($f$) or equatorial/polar radii given as parameters, I cannot model oblateness.
                *Decision:* I will calculate based on the spherical model (standard for this specific derivation of the angle and the parameter $\Omega^2 a / g$). The "0.7%" might be a typo in the user's prompt (confusing 0.3% with 0.7%?) or referring to the total observed difference.
                *Actually*, checking Wallace & Hobbs (2nd Ed, p. 33):
                "The value of $\Omega^2 a / g$ is $3.4 \times 10^{-3}$."
                "At the equator... $g'$ is less than $g$ by about $0.3\%$."
                "At the poles... $g' = g$."
                "The maximum angle... is about $0.1^\circ$."
                The prompt provided by the user says "about 0.7%".
                Let's check if there is a factor of 2 somewhere.
                Maybe the prompt meant "0.3%" but wrote "0.7%"? Or maybe it's referring to the difference between $g_{pole}$ and $g_{eq}$ on the *real* Earth (which is ~0.5-0.6%).
                *However*, the prompt asks to "Evaluate the dimensionless parameter...".
                If I output 0.0034 for the parameter, and 0.34 for the percent, and 0.1 for the angle, I am physically correct for the spherical model.
                If I try to force 0.7%, I'd have to fudge numbers.
                *Let's check the prompt again:* "Show that... magnitude... is about 0.7% less".
                Is it possible the prompt implies $g$ is the gravity at the *equator*? No, "less at the equator than at the poles".
                Let's assume the prompt text is fixed and I must provide the calculation.
                If I calculate $\Omega^2 a / g$, I get ~0.0034.
                If I calculate the % difference for a sphere, I get ~0.34%.
                If the prompt insists on 0.7%, maybe they are using different constants?
                $g=9.8$, $a=6371$km, $\Omega = 2\pi / 86400$.
                $\Omega = 7.272 \times 10^{-5}$.
                $\Omega^2 = 5.28 \times 10^{-9}$.
                $\Omega^2 a = 5.28 \times 10^{-9} \times 6.371 \times 10^6 = 0.0336$.
                Ratio = $0.0336 / 9.8 = 0.00343$.
                This is definitely ~0.34%.
                
                *Self-Correction:* Is it possible the problem asks for the difference between $g_{pole}$ and $g_{eq}$ *including* the centrifugal term acting on the *mass*? No, that's what we did.
                
                *Hypothesis:* The user might have copied a problem where the text says "0.3%" but typed "0.7%", OR the problem comes from a source that accounts for the Earth's oblateness (flattening $f \approx 1/298$).
                The potential due to rotation is $-\frac{1}{2}\Omega^2 r^2$. The potential due to mass is $-GM/r$.
                The equipotential surface (geoid) determines the shape.
                If we assume the Earth is an equipotential surface, $g_{eff}$ varies.
                However, usually, "Evaluate $\Omega^2 a / g$" is the first step.
                Let's look at the "0.7%" again.
                $g_{pole} \approx 9.832$. $g_{eq} \approx 9.780$.
                $(9.832 - 9.780) / 9.832 = 0.0052 \approx 0.5\%$.
                Still not 0.7%.
                
                *What if the "0.7%" refers to the centrifugal force relative to gravity at the equator?*
                $F_c / F_g = \Omega^2 a / g \approx 0.34\%$.
                
                *Let's check the angle again.*
                $\alpha_{max} \approx 0.1^\circ$.
                $\tan \alpha \approx \alpha$.
                $\alpha \approx \frac{1}{2} \sin(2\phi) \frac{\Omega^2 a}{g}$.
                Max at 45 deg. $\alpha \approx 0.5 \times 0.0034 = 0.0017$ rad.
                $0.0017 \times 57.3 \approx 0.097^\circ \approx 0.1^\circ$.
                This matches the prompt perfectly.
                
                *Conclusion on the 0.7%:* The prompt likely contains a typo (0.7% instead of 0.3%) or refers to a specific context not fully detailed (e.g. comparing to a non-rotating Earth of the same mass but different radius?).
                *However*, as an AI, I should compute the values based on the physics defined by the parameters $\Omega, a, g$.
                If I return 0.34% for the second quantity, and the user expects 0.7%, they might think it's wrong.
                But if I return 0.7% by hardcoding or fudging, I violate the rule "do not hard-code".
                I will calculate the values based on standard constants.
                Wait, is there *any* interpretation where it is 0.7%?
                Maybe $g$ is defined differently?
                What if $a$ is the polar radius? No, $a$ is usually equatorial.
                What if the question implies the difference between $g$ (gravity) and $g'$ (effective)?
                At the equator, $g' = g - \Omega^2 a$.
                Difference is $\Omega^2 a$.
                Ratio is $\Omega^2 a / g$.
                This is the dimensionless parameter.
                If the dimensionless parameter is ~0.0034, the percentage is 0.34%.
                
                *Let's check the source "Atmospheric Science" by Wallace and Hobbs.*
                Problem 2.1 (or similar).
                "Evaluate the dimensionless parameter $\Omega^2 a / g$ for the Earth."
                "Show that... magnitude... is about 0.3% less..." (Checking online snippets of this book).
                Most snippets say "0.3%".
                The user prompt says "0.7%".
                It is highly probable the user made a typo or the OCR of the problem statement they pasted has an error.
                *Strategy:* I will compute the values rigorously. I will use standard constants.
                Constants:
                $\Omega = 7.292115 \times 10^{-5}$ rad/s (Earth's rotation rate).
                $a = 6.371 \times 10^6$ m (Mean radius or Equatorial? Usually equatorial for this derivation, $6.378 \times 10^6$). Let's use $6.37 \times 10^6$ or $6.378 \times 10^6$.
                $g = 9.80665$ m/s$^2$ (Standard gravity).
                
                Let's refine the constants to be "standard" for such problems.
                $\Omega \approx 7.29 \times 10^{-5}$ rad/s.
                $a \approx 6.37 \times 10^6$ m.
                $g \approx 9.8$ m/s$^2$.
                
                Calculation 1: $\Omega^2 a / g$.
                Calculation 2: Percentage difference.
                For a sphere: $\frac{g - (g - \Omega^2 a)}{g} \times 100 = \frac{\Omega^2 a}{g} \times 100$.
                This yields ~0.34%.
                Calculation 3: Max angle.
                $\alpha_{max} \approx \frac{1}{2} \frac{\Omega^2 a}{g}$ (in radians).
                Convert to degrees.
                
                *Addressing the "0.7%" in the prompt:*
                If I output 0.34%, the user might be confused.
                However, if I look at the wording "Show that... is about 0.7% less", maybe they mean the difference between $g_{pole}$ and $g_{eq}$ on the *real* Earth?
                Real Earth: $g_p \approx 9.832$, $g_e \approx 9.780$.
                Diff $\approx 0.052$.
                $0.052 / 9.832 \approx 0.53\%$.
                Still not 0.7%.
                
                What if the "0.7%" refers to the centrifugal acceleration relative to $g$ *at the equator*?
                $a_c = 0.034$. $g_{eq} = 9.78$.
                $0.034 / 9.78 \approx 0.35\%$.
                
                Is it possible the problem uses $g=9.8$ and $a=6400$km?
                $\Omega = 2\pi / 86400 \approx 7.27 \times 10^{-5}$.
                $\Omega^2 a \approx 5.29 \times 10^{-9} \times 6.4 \times 10^6 \approx 0.0338$.
                $0.0338 / 9.8 \approx 0.00345$.
                
                Let's search for "0.7% less at the equator than at the poles".
                Some sources cite the difference in $g$ as ~0.5%.
                Some older texts might use different values?
                
                *Wait!*
                Is it possible the prompt implies the *centrifugal force* reduces the weight by 0.3%, and the *oblateness* reduces it by another 0.3-0.4%?
                If the problem asks to "Evaluate the dimensionless parameter... Show that...", it implies the parameter *leads* to the result.
                If the parameter is ~0.0034, and the result is 0.7%, there is a factor of ~2 missing.
                Is there a factor of 2 in the effective gravity difference?
                $g'_{eq} = g - \Omega^2 a$.
                $g'_{pole} = g$.
                Difference is $\Omega^2 a$.
                This is exactly the parameter (times $g$).
                So the percentage difference is exactly the parameter (times 100).
                If the parameter is 0.0034, the percentage is 0.34%.
                There is no factor of 2 in the spherical derivation.
                
                *Possibility:* The user prompt has a typo "0.7%" instead of "0.3%".
                *Possibility:* The user prompt refers to the *total* difference (including oblateness) but asks to calculate the *parameter* first.
                
                *Action Plan:*
                I will implement the calculation based on the physics of the rotating sphere (which yields ~0.34% and ~0.1 deg).
                I will define the constants clearly.
                I will return the computed values.
                If the user's prompt text "0.7%" is a hard constraint for the *output*, I would have to fake it, but the instructions say "do not hard-code".
                I will assume the "0.7%" is a typo for "0.3%" in the user's source or the user's transcription, or I will simply provide the calculated value which is the "truth" of the physics model requested.
                *However*, looking at the "0.1 degree" part.
                $0.1^\circ$ corresponds to $\approx 0.0017$ rad.
                $\alpha_{max} \approx \frac{1}{2} \epsilon$.
                So $\epsilon \approx 0.0034$.
                This confirms $\epsilon \approx 0.34\%$.
                If $\epsilon$ were $0.7\%$, $\alpha_{max}$ would be $0.35\% \approx 0.0035$ rad $\approx 0.2^\circ$.
                Since the prompt asks for "about 0.1 degrees", the parameter *must* be around 0.34%.
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    omega = 7.292115e-5  # Earth's angular velocity in rad/s
    a = 6.371e6          # Earth's mean radius in m
    g = 9.80665          # Standard gravity in m/s^2
    
    # 1. Dimensionless parameter Omega^2 * a / g
    param = omega**2 * a / g
    
    # 2. Percentage difference in effective gravity magnitude |g'|
    # At poles: |g'| = g
    # At equator: |g'| = g - Omega^2 * a
    # Percentage difference relative to pole gravity: (Omega^2 * a / g) * 100
    pct_diff = param * 100
    
    # 3. Maximum angle between g' and the radial vector
    # tan(alpha) approx (Omega^2 * a / g) * sin(phi) * cos(phi)
    # Maximum occurs at latitude phi = 45 degrees
    # alpha_max approx 0.5 * param (in radians)
    max_angle_rad = 0.5 * param
    max_angle_deg = max_angle_rad * 180 / math.pi
    
    return {
        "1": {"value": param, "unit": ""},
        "2": {"value": pct_diff, "unit": "%"},
        "3": {"value": max_angle_deg, "unit": "deg"}
    }
```
~~~~

---

## `2.10` — two mechanisms at once: answer completeness and a prefactor

### Problem `2.10`

Source: `An Introduction to Atmospheric Physics` · category `atmospheric_thermodynamics` · difficulty `high`

**problem (verbatim)**

~~~~
Show that the density of water vapour at saturation is given as a function of temperature by

$$
\rho _ { \mathrm { v s } } = { \frac { A e ^ { - T _ { 1 } / T } } { T } } ,
$$

where $T _ { 1 } = L / R _ { \mathrm { v } }$ and $A$ is a constant. Assuming a constant lapse rate, as in Problem 2.3, show that the following approximations are valid for heights $z \ll T _ { 0 } / \Gamma$ :

$$
T ^ { - 1 } \approx T _ { 0 } ^ { - 1 } \left( 1 + \frac { \Gamma z } { T _ { 0 } } \right) \approx T _ { 0 } ^ { - 1 } \exp \left( \frac { \Gamma z } { T _ { 0 } } \right) .
$$

Hence show that $\rho _ { \mathrm { v s } }$ decays exponentially with $z$ under these approximations. Evaluate the $e$ -folding height $( \mathrm { i n } \mathrm { k m } )$ ) for this decay in a tropical atmosphere with $T _ { 0 } = 3 0 0 \mathrm { K }$ and $\Gamma = 6 . 5 \mathrm { K } \mathrm { k m } ^ { - 1 }$ and comment on how it compares with a typical pressure scale height. Check the self-consistency of your approximations in this case.

Given a relative humidity of $80 \%$ , calculate the total mass of water vapour per unit horizontal area in a vertical column of atmosphere. If all this water vapour were to precipitate out, how many millimetres of rain would result? How much latent heat per unit horizontal area would be released? Give the depth of rain in mm and the latent heat per unit area in MJ/m^2.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `2.7` | km |
| `2` | `57.0` | kg/m^2 |
| `3` | `57.0` | mm |
| `4` | `140.0` | MJ/m^2 |

**reference solve()**

~~~~python
def solve(T0=300.0, Gamma=6.5, relative_humidity=80.0):
    import math

    # Physical constants
    R_v = 461.5                 # J kg^-1 K^-1, gas constant for water vapour
    L_v = 2.5e6                 # J kg^-1, latent heat of vaporization
    T_ref = 273.15              # K
    e_s_ref = 611.2             # Pa, saturation vapour pressure at T_ref
    rho_liquid_water = 1000.0   # kg m^-3

    # Unit conversions
    Gamma_K_per_m = Gamma / 1000.0
    RH = relative_humidity / 100.0

    # Clausius-Clapeyron parameter
    T1 = L_v / R_v

    # Exponential e-folding height for rho_vs, retaining the 1/T prefactor
    H_m = T0 * T0 / (Gamma_K_per_m * (T1 - T0))
    H_km = H_m / 1000.0

    # Saturation vapour pressure at T0 from integrated Clausius-Clapeyron
    e_s_T0 = e_s_ref * math.exp((L_v / R_v) * (1.0 / T_ref - 1.0 / T0))

    # Saturation vapour density at the surface from ideal gas law
    rho_vs_0 = e_s_T0 / (R_v * T0)

    # Column water vapour mass per unit area using exponential profile
    column_mass = RH * rho_vs_0 * H_m

    # Equivalent rainfall depth
    rain_m = column_mass / rho_liquid_water
    rain_mm = rain_m * 1000.0

    # Latent heat release per unit horizontal area
    latent_heat_J_per_m2 = L_v * column_mass
    latent_heat_MJ_per_m2 = latent_heat_J_per_m2 / 1.0e6

    return {
        "1": {"value": H_km, "unit": "km"},
        "2": {"value": column_mass, "unit": "kg/m^2"},
        "3": {"value": rain_mm, "unit": "mm"},
        "4": {"value": latent_heat_MJ_per_m2, "unit": "MJ/m^2"},
    }
~~~~

### What the failures actually consist of (16 configurations × 3 = 48 measurements)

| case | count |
|---|--:|
| under-answered (3 values) and also miscalculated | 16 |
| under-answered (3 values) but all three physically correct | 11 |
| all four answered, passes | 9 |
| all four answered, but hits the 1/T prefactor error (2.556) | 9 |
| all four answered, other error | 3 |

**56% is an answer-completeness problem and only 19% is a physics error.** The statement asks for four quantities explicitly.

### Answer distribution over all 48 measurements

| configuration | run | passed | `details[].actual` |
|---|---|:---:|---|
| `deepseek-v4-flash` | 1 | ✗ | `[2.553, 52.58, 131.45, None]` |
| `deepseek-v4-flash` | 2 | ✗ | `[2.553230769230769, 53.34494441566541, 53.34494441566541, 133.36236103916352]` |
| `deepseek-v4-flash` | 3 | ✗ | `[2.702746717651236, 25722.16016905577, 25722.16016905577, 64305.40042263942]` |
| `deepseek-v4-flash-reasoning` | 1 | ✓ | `[2.7027467176512356, 57.08816232501946, 57.08816232501946, 142.72040581254865]` |
| `deepseek-v4-flash-reasoning` | 2 | ✗ | `[2.553, 52.2, 130.51, None]` |
| `deepseek-v4-flash-reasoning` | 3 | ✗ | `[2.7027467176512356, 57.08816232501946, 142.72040581254865, None]` |
| `deepseek-v4-pro` | 1 | ✗ | `[2.7058499714170776, 56.38222289208464, 140.9555572302116, None]` |
| `deepseek-v4-pro` | 2 | ✗ | `[2.705849971417078, 55.254453154137686, 138.1361328853442, None]` |
| `deepseek-v4-pro` | 3 | ✗ | `[2.7058499714170776, 56.322866703666016, 140.80716675916506, None]` |
| `deepseek-v4-pro-reasoning` | 1 | ✗ | `[2.556, 53.24234745134838, 53.24234745134838, 133.10586862837096]` |
| `deepseek-v4-pro-reasoning` | 2 | ✗ | `[2.556, 53.24234745134846, 53.24234745134846, 133.10586862837116]` |
| `deepseek-v4-pro-reasoning` | 3 | ✗ | `[2.556, 53.24234745134838, 53.24234745134838, 133.10586862837096]` |
| `gemini-3.1-pro` | 1 | ✗ | `[2.705849971417078, 56.363773211818916, 140.9094330295473, None]` |
| `gemini-3.1-pro` | 2 | ✗ | `[2.7058499714170776, 56.3637732118189, 140.90943302954724, None]` |
| `gemini-3.1-pro` | 3 | ✗ | `[2.7058499714170776, 56.38222289208464, 140.9555572302116, None]` |
| `gpt55` | 1 | ✗ | `[2.7058499714170785, 56.38222289208466, 140.95555723021164, None]` |
| `gpt55` | 2 | ✗ | `[2.556, 52.346880000000006, 130.86720000000003, None]` |
| `gpt55` | 3 | ✗ | `[2.705849971417078, 55.41580741462176, 138.5395185365544, None]` |
| `gpt55-reasoning` | 1 | ✓ | `[2.7058499714170776, 56.38222289208464, 56.38222289208464, 140.9555572302116]` |
| `gpt55-reasoning` | 2 | ✓ | `[2.7058499714170776, 56.38222289208464, 56.38222289208464, 140.9555572302116]` |
| `gpt55-reasoning` | 3 | ✓ | `[2.705849971417078, 56.38222289208465, 56.38222289208465, 140.9555572302116]` |
| `kimi-k2.6` | 1 | ✓ | `[2.7082638857973045, 56.300807441304755, 56.300807441304755, 140.7520186032619]` |
| `kimi-k2.6` | 2 | ✗ | `[2.556, 52.20213661867032, 130.5053415466758, None]` |
| `kimi-k2.6` | 3 | ✗ | `[2.556, 53.25977538832108, 133.14943847080272, None]` |
| `kimi-k2.6-reasoning` | 1 | ✓ | `[2.705849971417078, 56.363773211819, 56.363773211819, 140.9094330295475]` |
| `kimi-k2.6-reasoning` | 2 | ✗ | `[2.556, 53.24234745134838, 53.24234745134838, 133.10586862837096]` |
| `kimi-k2.6-reasoning` | 3 | ✓ | `[2.7058499714170776, 56.38222289208464, 56.38222289208464, 140.9555572302116]` |
| `qwen-2.5-72b` | 1 | ✗ | `[0.0693895012143495, 2.033640602983601e-08, 5.0841015074590026e-08, None]` |
| `qwen-2.5-72b` | 2 | ✗ | `[0.0693895012143495, 2.1250232522078342e-08, 5.3125581305195855e-08, None]` |
| `qwen-2.5-72b` | 3 | ✗ | `[16.979051130989646, 2.718281828459045, 174309.22560596865, 435773.0640149216]` |
| `qwen3.5-397b` | 1 | ✗ | `[2.556, 53.24234745134838, 133.10586862837096, None]` |
| `qwen3.5-397b` | 2 | ✗ | `[2.556, 52.102460857176695, 130.25615214294174, None]` |
| `qwen3.5-397b` | 3 | ✗ | `[2.556, 53.221121634109835, 133.0528040852746, None]` |
| `qwen3.5-397b-reasoning` | 1 | ✗ | `[2.556, 53.259775388320996, 133.1494384708025, None]` |
| `qwen3.5-397b-reasoning` | 2 | ✗ | `[2.556, 52.19400571806855, 130.48501429517137, None]` |
| `qwen3.5-397b-reasoning` | 3 | ✗ | `[2.556, 53.24234745134838, 133.10586862837096, None]` |
| `qwen3.5-9b` | 1 | ✗ | `[2.7058499714170776, 8.778287461773699, 0.05862674938070335, 56.3637732118189]` |
| `qwen3.5-9b` | 2 | ✗ | `[5.538e-05, 1.1310462934045236e-05, 2.827615733511309e-05, None]` |
| `qwen3.5-9b` | 3 | ✗ | `[2.556, 173742.37001400098, 434355.92503500247, 0.05538]` |
| `qwen3.5-9b-reasoning` | 1 | ✗ | `[2.6081632653061226, 53.13434425430405, 130.17914342304493, None]` |
| `qwen3.5-9b-reasoning` | 2 | ✗ | `[2.556, 52.20213661867032, 52.20213661867032, 130.5053415466758]` |
| `qwen3.5-9b-reasoning` | 3 | ✓ | `[2.7058499714170776, 55.26257819935034, 55.26257819935034, 138.15644549837583]` |
| `qwen3.6-27b` | 1 | ✗ | `[2.7058499714170776, 55.26257819935035, 138.15644549837586, None]` |
| `qwen3.6-27b` | 2 | ✓ | `[2.7047046623351885, 55.23918712690771, 55.23918712690771, 138.15320700439617]` |
| `qwen3.6-27b` | 3 | ✗ | `[2.556, 53.25977538832107, 133.14943847080266, None]` |
| `qwen3.6-27b-reasoning` | 1 | ✗ | `[2.556, 53.221121634109835, 53.221121634109835, 133.0528040852746]` |
| `qwen3.6-27b-reasoning` | 2 | ✗ | `[2.7027467176512356, 56.46879833982451, 141.17199584956128, None]` |
| `qwen3.6-27b-reasoning` | 3 | ✗ | `[2.556, 53.221121634109835, 53.221121634109835, 133.0528040852746]` |

### Both DeepSeek-V4-pro variants, all three runs

#### `deepseek-v4-pro` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro.run1.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.7058499714170776` | ✓ |
| `2` | `57.0` | `56.38222289208464` | ✓ |
| `3` | `57.0` | `140.9555572302116` | ✗ |
| `4` | `140.0` | `None` | ✗ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
Show that the density of water vapour at saturation is given as a function of temperature by

$$
\rho _ { \mathrm { v s } } = { \frac { A e ^ { - T _ { 1 } / T } } { T } } ,
$$

where $T _ { 1 } = L / R _ { \mathrm { v } }$ and $A$ is a constant. Assuming a constant lapse rate, as in Problem 2.3, show that the following approximations are valid for heights $z \ll T _ { 0 } / \Gamma$ :

$$
T ^ { - 1 } \approx T _ { 0 } ^ { - 1 } \left( 1 + \frac { \Gamma z } { T _ { 0 } } \right) \approx T _ { 0 } ^ { - 1 } \exp \left( \frac { \Gamma z } { T _ { 0 } } \right) .
$$

Hence show that $\rho _ { \mathrm { v s } }$ decays exponentially with $z$ under these approximations. Evaluate the $e$ -folding height $( \mathrm { i n } \mathrm { k m } )$ ) for this decay in a tropical atmosphere with $T _ { 0 } = 3 0 0 \mathrm { K }$ and $\Gamma = 6 . 5 \mathrm { K } \mathrm { k m } ^ { - 1 }$ and comment on how it compares with a typical pressure scale height. Check the self-consistency of your approximations in this case.

Given a relative humidity of $80 \%$ , calculate the total mass of water vapour per unit horizontal area in a vertical column of atmosphere. If all this water vapour were to precipitate out, how many millimetres of rain would result? How much latent heat per unit horizontal area would be released? Give the depth of rain in mm and the latent heat per unit area in MJ/m^2.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    T0=300.0,          # K
    Gamma=6.5,         # K/km
    RH=0.80,           # relative humidity (dimensionless)
    L=2.5e6,           # latent heat of vaporization, J/kg
    Rv=461.5,          # gas constant for water vapour, J/(kg K)
    # Derived constants
    g=9.81,            # m/s^2
    Rd=287.0,          # J/(kg K) for dry air
    # We need A constant, but it cancels in e-folding height.
    # For column mass we need actual rho_vs at surface.
    # Use Clausius-Clapeyron: es = A * exp(-T1/T) / T  with A from standard es0 at T0.
    # es0 at T0=300 K ~ 3534 Pa (approx). We can compute A from standard saturation vapour pressure.
    # Use standard formula: es(T) = 611.2 * exp( (L/Rv)*(1/273.15 - 1/T) )
    # Then rho_vs = es / (Rv * T)
    # We'll compute A implicitly.
):
    # 1. e-folding height for rho_vs
    # rho_vs = (A / T) * exp(-T1 / T)
    # T1 = L / Rv
    T1 = L / Rv
    # Approximations: T^-1 ≈ T0^-1 * exp(Gamma z / T0)
    # So rho_vs ∝ (1/T) * exp(-T1/T) ≈ (1/T0) * exp(Gamma z / T0) * exp(-T1/T0 * (1 + Gamma z / T0))
    # = (1/T0) * exp(-T1/T0) * exp( (Gamma/T0) * z ) * exp( - (T1 * Gamma / T0^2) * z )
    # = const * exp( - (T1 * Gamma / T0^2 - Gamma/T0) * z )
    # e-folding height H_v = 1 / (T1 * Gamma / T0^2 - Gamma/T0)
    # = T0^2 / (Gamma * (T1 - T0))
    H_v = T0**2 / (Gamma * (T1 - T0))  # km
    # Check self-consistency: z << T0/Gamma = 300/6.5 ≈ 46.15 km, H_v should be much less than that.
    
    # 2. Total mass of water vapour per unit horizontal area
    # rho_vs(z) = rho_vs0 * exp(-z / H_v)  (with H_v in km)
    # rho_vs0 = es0 / (Rv * T0)
    # es0 from standard formula
    es0 = 611.2 * math.exp((L / Rv) * (1/273.15 - 1/T0))  # Pa
    rho_vs0 = es0 / (Rv * T0)  # kg/m^3
    # actual vapour density at surface = RH * rho_vs0
    rho_v0 = RH * rho_vs0
    # Column mass = integral_0^inf rho_v0 * exp(-z/H_v) dz
    # H_v in km, need in meters for integration: H_v_m = H_v * 1000
    H_v_m = H_v * 1000.0  # m
    column_mass = rho_v0 * H_v_m  # kg/m^2
    
    # 3. Depth of rain in mm
    # density of water = 1000 kg/m^3
    rho_water = 1000.0  # kg/m^3
    rain_depth_m = column_mass / rho_water  # meters
    rain_depth_mm = rain_depth_m * 1000.0  # mm
    
    # 4. Latent heat released per unit area
    latent_heat_per_area = column_mass * L  # J/m^2
    latent_heat_MJ_per_m2 = latent_heat_per_area / 1e6  # MJ/m^2
    
    return {
        "1": {"value": H_v, "unit": "km"},
        "2": {"value": rain_depth_mm, "unit": "mm"},
        "3": {"value": latent_heat_MJ_per_m2, "unit": "MJ/m^2"}
    }
```
~~~~

#### `deepseek-v4-pro` · core_code · run 2 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro.run2.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.705849971417078` | ✓ |
| `2` | `57.0` | `55.254453154137686` | ✓ |
| `3` | `57.0` | `138.1361328853442` | ✗ |
| `4` | `140.0` | `None` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    T0=300.0,          # K
    Gamma=6.5,         # K/km
    L=2.5e6,           # J/kg (latent heat of vaporization of water)
    Rv=461.5,          # J/(kg K) (gas constant for water vapour)
    RH=0.80,           # relative humidity
    # Constants for water vapour saturation density formula:
    # rho_vs = A * exp(-T1/T) / T
    # We need A to compute absolute values. A can be derived from the Clausius-Clapeyron
    # relation and the ideal gas law. At T0=300 K, saturation vapour pressure e_s ~ 3534 Pa.
    # Using e_s = rho_vs * Rv * T, we can find A.
    # But the problem does not give A directly. We can compute A from standard values.
    # Alternatively, we can use the fact that at T0, rho_vs0 = e_s(T0)/(Rv*T0).
    # e_s(T0) can be approximated by the August-Roche-Magnus formula or similar.
    # For consistency with the given exponential form, we'll use the Clausius-Clapeyron
    # integrated with constant L: e_s = C * exp(-L/(Rv*T)).
    # Then rho_vs = e_s/(Rv*T) = (C/Rv) * exp(-L/(Rv*T)) / T.
    # So A = C/Rv. We need C. At T0=300 K, typical e_s ~ 3534 Pa.
    # Let's compute C from e_s(T0) = 3534 Pa.
    # C = e_s(T0) * exp(L/(Rv*T0))
    e_s0=3534.0,       # Pa, saturation vapour pressure at 300 K
):
    # Derived constants
    T1 = L / Rv  # K
    # Compute A from e_s0 at T0
    C = e_s0 * math.exp(L / (Rv * T0))
    A = C / Rv

    # 1. e-folding height for rho_vs decay
    # Under approximations: T^{-1} ≈ T0^{-1} * exp(Gamma*z/T0)
    # rho_vs = A * exp(-T1/T) / T
    # Using T^{-1} ≈ T0^{-1} * exp(Gamma*z/T0) and T ≈ T0 in denominator (since z << T0/Gamma)
    # Actually more carefully: rho_vs ∝ exp(-T1/T) / T.
    # With T ≈ T0 - Gamma*z, 1/T ≈ 1/T0 * (1 + Gamma*z/T0) ≈ 1/T0 * exp(Gamma*z/T0)
    # So exp(-T1/T) ≈ exp(-T1/T0 * exp(Gamma*z/T0))
    # For small z, exp(Gamma*z/T0) ≈ 1 + Gamma*z/T0, so exp(-T1/T) ≈ exp(-T1/T0) * exp(-T1*Gamma*z/T0^2)
    # Denominator 1/T ≈ 1/T0 * exp(Gamma*z/T0)
    # So overall rho_vs ∝ exp(-(T1*Gamma/T0^2 - Gamma/T0)*z) = exp(-Gamma*z/T0 * (T1/T0 - 1))
    # Since T1 >> T0 (T1 = 2.5e6/461.5 ≈ 5417 K), T1/T0 ≈ 18, so dominant term is T1*Gamma/T0^2.
    # e-folding height H_v = 1 / (Gamma * T1 / T0**2 - Gamma/T0) ≈ T0**2 / (Gamma * T1)
    # Let's compute exact e-folding from the approximate exponential form.
    # rho_vs(z) ≈ rho_vs(0) * exp(-z / H_v)
    # where H_v = T0**2 / (Gamma * T1)  (neglecting the -Gamma/T0 term)
    H_v_exact = 1.0 / (Gamma * T1 / T0**2 - Gamma / T0)  # km
    # Convert to km (already in km because Gamma is K/km)
    H_v_km = H_v_exact  # km

    # 2. Check self-consistency: z << T0/Gamma
    T0_over_Gamma = T0 / Gamma  # km
    # H_v should be much less than T0/Gamma for approximations to hold?
    # Actually the approximation requires z << T0/Gamma. The e-folding height H_v is the scale we are interested in.
    # We'll comment in the answer, but just compute the value.

    # 3. Total mass of water vapour per unit horizontal area
    # Column integrated water vapour (IWV) = ∫ rho_v dz
    # rho_v = RH * rho_vs
    # Using exponential decay: rho_vs(z) = rho_vs0 * exp(-z/H_v)
    # IWV = RH * rho_vs0 * H_v
    # rho_vs0 at surface (z=0) = A * exp(-T1/T0) / T0
    rho_vs0 = A * math.exp(-T1 / T0) / T0
    IWV = RH * rho_vs0 * (H_v_km * 1000.0)  # convert H_v from km to m -> kg/m^2

    # 4. Depth of rain if all precipitated (mm)
    # 1 kg/m^2 of water = 1 mm depth (since density of water = 1000 kg/m^3)
    rain_depth_mm = IWV  # mm

    # 5. Latent heat released per unit area
    latent_heat_per_area = IWV * L  # J/m^2
    latent_heat_MJ_per_m2 = latent_heat_per_area / 1e6  # MJ/m^2

    return {
        "1": {"value": H_v_km, "unit": "km"},
        "2": {"value": rain_depth_mm, "unit": "mm"},
        "3": {"value": latent_heat_MJ_per_m2, "unit": "MJ/m^2"},
    }
```
~~~~

#### `deepseek-v4-pro` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro.run3.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.7058499714170776` | ✓ |
| `2` | `57.0` | `56.322866703666016` | ✓ |
| `3` | `57.0` | `140.80716675916506` | ✗ |
| `4` | `140.0` | `None` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    T0=300.0,          # K
    Gamma=6.5,         # K/km
    L=2.5e6,           # J/kg (latent heat of vaporization)
    Rv=461.5,          # J/(kg·K) (gas constant for water vapour)
    RH=0.80,           # relative humidity
    # standard values for saturation vapour pressure (Clausius-Clapeyron)
    es0=611.0,         # Pa at 273.16 K
    T_ref=273.16,      # K
    # pressure scale height (for comparison)
    H_p=8.0,           # km (typical)
    # density of liquid water
    rho_w=1000.0,      # kg/m^3
):
    # 1. e-folding height for water vapour density decay
    T1 = L / Rv  # K
    # The exponential decay scale height H_v for rho_vs:
    # rho_vs ~ (A/T) * exp(-T1/T)
    # With T ≈ T0 - Gamma*z, and approximations for z << T0/Gamma:
    # T^{-1} ≈ T0^{-1} * exp(Gamma*z / T0)
    # exp(-T1/T) ≈ exp(-T1/T0) * exp(-T1*Gamma*z / T0^2)
    # So rho_vs ~ exp( (Gamma/T0 - T1*Gamma/T0^2) * z ) = exp( -Gamma*(T1 - T0)/T0^2 * z )
    # e-folding height H_v = T0^2 / (Gamma * (T1 - T0))
    H_v = T0**2 / (Gamma * (T1 - T0))  # km

    # 2. Total mass of water vapour per unit horizontal area
    # We need the vertical integral of rho_v = RH * rho_vs
    # rho_vs(z) = rho_vs(0) * exp(-z / H_v)
    # rho_vs(0) = (A / T0) * exp(-T1/T0)
    # We can find A from saturation vapour pressure at T0:
    # es(T) = es0 * exp( (L/Rv) * (1/T_ref - 1/T) )
    # Using ideal gas law: rho_vs = es / (Rv * T)
    # So rho_vs(0) = es(T0) / (Rv * T0)
    es_T0 = es0 * math.exp((L / Rv) * (1.0 / T_ref - 1.0 / T0))
    rho_vs0 = es_T0 / (Rv * T0)  # kg/m^3

    # Column integral: M = ∫_0^∞ RH * rho_vs0 * exp(-z/H_v) dz = RH * rho_vs0 * H_v
    # Convert H_v from km to m
    H_v_m = H_v * 1000.0  # m
    M = RH * rho_vs0 * H_v_m  # kg/m^2

    # 3. Depth of rain if all precipitated
    # depth = M / rho_w  (in m), convert to mm
    depth_m = M / rho_w
    depth_mm = depth_m * 1000.0

    # 4. Latent heat released per unit area
    Q = M * L  # J/m^2
    Q_MJ = Q / 1e6  # MJ/m^2

    return {
        "1": {"value": H_v, "unit": "km"},
        "2": {"value": depth_mm, "unit": "mm"},
        "3": {"value": Q_MJ, "unit": "MJ/m^2"},
    }
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run1.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.556` | ✗ |
| `2` | `57.0` | `53.24234745134838` | ✗ |
| `3` | `57.0` | `53.24234745134838` | ✗ |
| `4` | `140.0` | `133.10586862837096` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(T0=300.0, Gamma=6.5, RH=0.8,
          L=2.5e6, R_v=461.5,
          e_s0=611.0, T_ref=273.15,
          rho_w=1000.0):
    """
    Compute e-folding height, column water vapour mass,
    rain depth and latent heat release.
    
    Parameters
    ----------
    T0 : float
        Surface temperature (K)
    Gamma : float
        Lapse rate (K/km)
    RH : float
        Relative humidity (0-1)
    L : float
        Latent heat of vaporization (J/kg)
    R_v : float
        Gas constant for water vapour (J/(kg K))
    e_s0 : float
        Saturation vapour pressure at T_ref (Pa)
    T_ref : float
        Reference temperature for e_s0 (K)
    rho_w : float
        Density of liquid water (kg/m^3)
    """
    # T1 = L / R_v
    T1 = L / R_v

    # e-folding height (km)
    H_v_km = T0**2 / (T1 * Gamma)

    # Saturation vapour pressure at T0 (Pa)
    e_s_T0 = e_s0 * math.exp(T1 * (1.0/T_ref - 1.0/T0))

    # Saturation vapour density at surface (kg/m^3)
    rho_vs0 = e_s_T0 / (R_v * T0)

    # Column mass per unit area using exponential decay approximation
    H_v_m = H_v_km * 1000.0          # convert km -> m
    M = RH * rho_vs0 * H_v_m         # kg/m^2

    # Rain depth in mm (1 kg/m^2 = 1 mm)
    rain_mm = M

    # Latent heat per unit area (MJ/m^2)
    latent_heat_MJ = (L * M) / 1e6   # J/m^2 -> MJ/m^2

    return {
        "1": {"value": H_v_km, "unit": "km"},
        "2": {"value": M, "unit": "kg/m^2"},
        "3": {"value": rain_mm, "unit": "mm"},
        "4": {"value": latent_heat_MJ, "unit": "MJ/m^2"}
    }
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 2 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run2.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.556` | ✗ |
| `2` | `57.0` | `53.24234745134846` | ✗ |
| `3` | `57.0` | `53.24234745134846` | ✗ |
| `4` | `140.0` | `133.10586862837116` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(T0=300.0, Gamma=6.5, RH=0.8,
          L=2.5e6, R_v=461.5,
          e_s0=611.0, T_ref=273.15,
          rho_water=1000.0):
    """
    Compute e-folding height, column water vapour mass,
    rain depth and latent heat release.
    
    Parameters
    ----------
    T0 : float
        Surface temperature (K)
    Gamma : float
        Lapse rate (K / km)
    RH : float
        Relative humidity (0 to 1)
    L : float
        Latent heat of vaporization (J / kg)
    R_v : float
        Gas constant for water vapour (J / (kg K))
    e_s0 : float
        Saturation vapour pressure at T_ref (Pa)
    T_ref : float
        Reference temperature for e_s0 (K)
    rho_water : float
        Density of liquid water (kg / m^3)
    """
    # T1 = L / R_v  (K)
    T1 = L / R_v

    # e-folding height for water vapour density
    # Using H_v = T0^2 / (T1 * Gamma) with Gamma in K/km gives km directly
    H_v_km = T0**2 / (T1 * Gamma)
    H_v_m = H_v_km * 1000.0   # convert to metres for column integration

    # Surface saturation vapour density using the given form
    # A is determined from the reference state
    A = e_s0 * math.exp(T1 / T_ref) / R_v
    rho_vs0 = A * math.exp(-T1 / T0) / T0   # kg / m^3

    # Total column water vapour mass per unit horizontal area (precipitable water)
    W = RH * rho_vs0 * H_v_m   # kg / m^2

    # Rain depth in mm
    depth_mm = (W / rho_water) * 1000.0   # mm

    # Latent heat per unit area in MJ / m^2
    latent_heat_MJ_per_m2 = (L * W) / 1e6

    return {
        "1": {"value": H_v_km, "unit": "km"},
        "2": {"value": W, "unit": "kg/m^2"},
        "3": {"value": depth_mm, "unit": "mm"},
        "4": {"value": latent_heat_MJ_per_m2, "unit": "MJ/m^2"}
    }
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run3.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.556` | ✗ |
| `2` | `57.0` | `53.24234745134838` | ✗ |
| `3` | `57.0` | `53.24234745134838` | ✗ |
| `4` | `140.0` | `133.10586862837096` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(T0=300.0, Gamma=6.5, RH=0.8, L=2.5e6, R_v=461.5, T_ref=273.15, e_s_ref=611.0):
    """
    Compute the requested quantities for the tropical atmosphere problem.
    
    Parameters
    ----------
    T0 : float
        Surface temperature in K (default 300).
    Gamma : float
        Lapse rate in K/km (default 6.5).
    RH : float
        Relative humidity as a fraction (default 0.8).
    L : float
        Latent heat of vaporization of water in J/kg (default 2.5e6).
    R_v : float
        Gas constant for water vapour in J/(kg K) (default 461.5).
    T_ref : float
        Reference temperature in K (default 273.15, 0°C).
    e_s_ref : float
        Saturation vapour pressure at T_ref in Pa (default 611.0).
    
    Returns
    -------
    dict
        Keys "1" to "4" with values and units for:
        1. e-folding height (km)
        2. total water vapour mass per unit area (kg/m^2)
        3. depth of rain (mm)
        4. latent heat per unit area (MJ/m^2)
    """
    # T1 = L / R_v
    T1 = L / R_v
    
    # e-folding height for water vapour density (km)
    # H_v = T0^2 / (T1 * Gamma) with Gamma in K/km
    H_v_km = (T0**2 * R_v) / (L * Gamma)
    
    # Convert lapse rate to K/m for SI calculations
    Gamma_SI = Gamma / 1000.0   # K/m
    H_v_m = H_v_km * 1000.0     # m
    
    # Saturation vapour pressure at T0 from Clausius–Clapeyron
    e_s0 = e_s_ref * math.exp((L / R_v) * (1.0 / T_ref - 1.0 / T0))
    
    # Saturation vapour density at the surface (ideal gas law)
    rho_vs0 = e_s0 / (R_v * T0)
    
    # Total column water vapour mass per unit area (precipitable water)
    W = RH * rho_vs0 * H_v_m   # kg/m^2
    
    # Rain depth in mm (1 kg/m^2 of water is equivalent to 1 mm)
    rain_mm = W
    
    # Latent heat released per unit area
    latent_heat_J = L * W          # J/m^2
    latent_heat_MJ = latent_heat_J / 1.0e6   # MJ/m^2
    
    return {
        "1": {"value": H_v_km, "unit": "km"},
        "2": {"value": W, "unit": "kg/m^2"},
        "3": {"value": rain_mm, "unit": "mm"},
        "4": {"value": latent_heat_MJ, "unit": "MJ/m^2"}
    }
```
~~~~

### One correct transcript

#### `deepseek-v4-flash-reasoning` · core_code · run 1 · **PASS**

Source: `experiments/core_code/deepseek-v4-flash-reasoning.run1.json` → `2.10` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.7` | `2.7027467176512356` | ✓ |
| `2` | `57.0` | `57.08816232501946` | ✓ |
| `3` | `57.0` | `57.08816232501946` | ✓ |
| `4` | `140.0` | `142.72040581254865` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(T0=300.0, Gamma=6.5, RH=0.8, L=2.5e6, Rv=461.0,
          e_s0=611.0, T_ref=273.0, rho_w=1000.0):
    """
    Compute:
    1. e-folding height (km) for water vapour density decay
    2. total mass of water vapour per unit area (kg/m^2)
    3. depth of rain if all vapour precipitates (mm)
    4. latent heat released per unit area (MJ/m^2)
    """
    # Constants
    T1 = L / Rv                     # ~5423 K
    # Saturation vapour pressure at T0 (Pa)
    e_s_T0 = e_s0 * math.exp(T1 * (1.0/T_ref - 1.0/T0))
    # Saturation density at surface (kg/m^3)
    rho_vs0 = e_s_T0 / (Rv * T0)

    # e-folding height in km
    H_km = T0**2 / (Gamma * (T1 - T0))
    # Convert to m
    H_m = H_km * 1000.0

    # Total mass per unit area (kg/m^2)
    total_mass = RH * rho_vs0 * H_m

    # Rain depth (mm)
    rain_mm = (total_mass / rho_w) * 1000.0

    # Latent heat per unit area (MJ/m^2)
    latent_MJ = total_mass * L / 1e6

    return {
        "1": {"value": H_km, "unit": "km"},
        "2": {"value": total_mass, "unit": "kg/m^2"},
        "3": {"value": rain_mm, "unit": "mm"},
        "4": {"value": latent_MJ, "unit": "MJ/m^2"}
    }
```
~~~~

---

## `ry_7.7` — compositional brittleness: failed answers span more than 40 orders of magnitude

### Problem `ry_7.7`

Source: `A Short Course in Cloud Physics` · category `cloud_physics` · difficulty `high`

**problem (verbatim)**

~~~~
In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of O.6 μm. Given that the cloud water content is $0 . 2 \mathrm { g } / \mathrm { \dot { m } } ^ { 3 }$ ,estimate the supersaturationinanupdraft of8m/s.Assume a temperature of $0 ^ { \circ } \bar { C }$ and a pressure of 80 kPa.

Express your answer as a percentage.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `0.52` | % |

**reference solve()**

~~~~python
import math
import json

def solve(
    mean_radius_um=4.0,
    sigma_um=0.6,
    cloud_water_content_g_per_m3=0.2,
    updraft_m_per_s=8.0,
    temperature_C=0.0,
    pressure_kPa=80.0,
):
    # Constants
    rho_l = 1000.0          # kg/m^3
    g = 9.81                # m/s^2
    c_p = 1004.0            # J/(kg K)
    R_d = 287.0             # J/(kg K)
    R_v = 461.0             # J/(kg K)
    epsilon = 0.622         # Mw/Md
    L_v = 2.50e6            # J/kg
    D_v0 = 2.11e-5          # m^2/s at 273.15 K, 101325 Pa
    p0 = 101325.0           # Pa
    T0 = 273.15             # K
    k_air = 0.0243          # W/(m K), air near 0 C

    # Unit conversions
    r_bar = mean_radius_um * 1.0e-6
    sigma = sigma_um * 1.0e-6
    lwc = cloud_water_content_g_per_m3 * 1.0e-3
    w = updraft_m_per_s
    T = temperature_C + 273.15
    p = pressure_kPa * 1.0e3

    # Saturation vapor pressure over liquid water (Pa), Bolton form
    e_s = 611.2 * math.exp(17.67 * temperature_C / (temperature_C + 243.5))

    # Saturation mixing ratio (kg/kg)
    q_vs = epsilon * e_s / (p - e_s)

    # Supersaturation tendency coefficients:
    # ds/dt = Q1*w - Q2*C, with C in kg kg^-1 s^-1
    Q1 = g * (L_v / (c_p * R_v * T * T) - 1.0 / (R_d * T))
    Q2 = 1.0 / q_vs + (L_v * L_v) / (c_p * R_v * T * T)

    # Diffusional droplet growth denominator:
    # r dr/dt = s / (F_k + F_d)
    D_v = D_v0 * (T / T0) ** 1.94 * (p0 / p)
    F_k = ((L_v / (R_v * T)) - 1.0) * L_v * rho_l / (k_air * T)
    F_d = rho_l * R_v * T / (D_v * e_s)

    # G(p,T) in percent * s / kg
    G = 100.0 * Q1 * (F_k + F_d) / (4.0 * math.pi * rho_l * Q2)

    # Gaussian droplet spectrum third raw moment: <r^3> = mu^3 + 3 mu sigma^2
    r3_mean = r_bar**3 + 3.0 * r_bar * sigma**2

    # Number concentration from liquid water content
    mass_per_drop = (4.0 / 3.0) * math.pi * rho_l * r3_mean
    n_per_m3 = lwc / mass_per_drop

    # Air density and number concentration per kg of air
    rho_air = p / (R_d * T)
    nu0 = n_per_m3 / rho_air  # kg^-1

    # Quasi-steady supersaturation in percent
    s_inf_percent = G * w / (nu0 * r_bar)

    return {"1": {"value": round(s_inf_percent, 2), "unit": "%"}}

print(json.dumps(solve(), separators=(",", ":")))
~~~~

### Answer distribution over all 48 measurements

| configuration | run | passed | `details[].actual` |
|---|---|:---:|---|
| `deepseek-v4-flash` | 1 | ✗ | `[0.0]` |
| `deepseek-v4-flash` | 2 | ✗ | `[0.4679484079167672]` |
| `deepseek-v4-flash` | 3 | ✗ | `[0.0113]` |
| `deepseek-v4-flash-reasoning` | 1 | ✗ | `[0.9644251340723677]` |
| `deepseek-v4-flash-reasoning` | 2 | ✗ | `[1.154717318342412]` |
| `deepseek-v4-flash-reasoning` | 3 | ✗ | `[0.9519054287211914]` |
| `deepseek-v4-pro` | 1 | ✗ | `[0.0007850802760718114]` |
| `deepseek-v4-pro` | 2 | ✗ | `[1.2635158193735423]` |
| `deepseek-v4-pro` | 3 | ✗ | `[0.46428754256893745]` |
| `deepseek-v4-pro-reasoning` | 1 | ✓ | `[0.5088815496865593]` |
| `deepseek-v4-pro-reasoning` | 2 | ✓ | `[0.4978926694332834]` |
| `deepseek-v4-pro-reasoning` | 3 | ✓ | `[0.5288263945568786]` |
| `gemini-3.1-pro` | 1 | ✓ | `[0.5074368651158522]` |
| `gemini-3.1-pro` | 2 | ✓ | `[0.5275625589617555]` |
| `gemini-3.1-pro` | 3 | ✓ | `[0.526670317481641]` |
| `gpt55` | 1 | ✗ | `[-30.304515855423773]` |
| `gpt55` | 2 | ✗ | `[0.9686528397626203]` |
| `gpt55` | 3 | ✗ | `[1052.274987482195]` |
| `gpt55-reasoning` | 1 | ✓ | `[0.5190074744991111]` |
| `gpt55-reasoning` | 2 | ✓ | `[0.5149175626621061]` |
| `gpt55-reasoning` | 3 | ✓ | `[0.519007474499111]` |
| `kimi-k2.6` | 1 | ✗ | `[0.9952643295485727]` |
| `kimi-k2.6` | 2 | ✗ | `[0.0946]` |
| `kimi-k2.6` | 3 | ✗ | `[0.5867835480213847]` |
| `kimi-k2.6-reasoning` | 1 | ✗ | `[0.6130668868867]` |
| `kimi-k2.6-reasoning` | 2 | ✓ | `[0.5193113783181564]` |
| `kimi-k2.6-reasoning` | 3 | ✓ | `[0.5242838759567193]` |
| `qwen-2.5-72b` | 1 | ✗ | `[12988.791086533269]` |
| `qwen-2.5-72b` | 2 | ✗ | `[0.02382861156294707]` |
| `qwen-2.5-72b` | 3 | ✗ | `[1.7167071851014884e-20]` |
| `qwen3.5-397b` | 1 | ✗ | `[0.9077646285762652]` |
| `qwen3.5-397b` | 2 | ✗ | `[201.44947704462254]` |
| `qwen3.5-397b` | 3 | ✗ | `[1.8694970550373909e-06]` |
| `qwen3.5-397b-reasoning` | 1 | ✗ | `[1.6781157139838143]` |
| `qwen3.5-397b-reasoning` | 2 | ✗ | `[10.160559451104243]` |
| `qwen3.5-397b-reasoning` | 3 | ✗ | `[0.941720844757035]` |
| `qwen3.5-9b` | 1 | ✗ | `[0.6371457948365394]` |
| `qwen3.5-9b` | 2 | ✗ | `[161744.06015926308]` |
| `qwen3.5-9b` | 3 | ✗ | `[1564792.17603912]` |
| `qwen3.5-9b-reasoning` | 1 | ✗ | `[6.379474874966854e-05]` |
| `qwen3.5-9b-reasoning` | 2 | ✗ | `[0.0]` |
| `qwen3.5-9b-reasoning` | 3 | ✗ | `[63.99999999999999]` |
| `qwen3.6-27b` | 1 | ✗ | `[5.566051868782093e+20]` |
| `qwen3.6-27b` | 2 | ✗ | `[7143.4]` |
| `qwen3.6-27b` | 3 | ✗ | `[1396059.942420474]` |
| `qwen3.6-27b-reasoning` | 1 | ✓ | `[0.528871621377951]` |
| `qwen3.6-27b-reasoning` | 2 | ✗ | `[0.6065731392107304]` |
| `qwen3.6-27b-reasoning` | 3 | ✗ | `[7.105160998018041e-05]` |

### A correct transcript from the frontier

#### `deepseek-v4-pro-reasoning` · core_code · run 1 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run1.json` → `ry_7.7` · `num_attempts` = 3 · 3 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `0.5088815496865593` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of O.6 μm. Given that the cloud water content is $0 . 2 \mathrm { g } / \mathrm { \dot { m } } ^ { 3 }$ ,estimate the supersaturationinanupdraft of8m/s.Assume a temperature of $0 ^ { \circ } \bar { C }$ and a pressure of 80 kPa.

Express your answer as a percentage.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
We need to solve an atmospheric science problem: estimate supersaturation in an updraft of 8 m/s given a developing cumulus cloud with droplet spectrum Gaussian, mean radius 4 μm, std dev 0.6 μm, cloud water content 0.2 g/m^3, temperature 0°C, pressure 80 kPa. Express answer as a percentage.

We need to compute supersaturation. This is a classic cloud physics problem: supersaturation in an updraft is determined by the balance between cooling by adiabatic ascent (which increases relative humidity) and depletion by droplet growth (condensation). In a steady state, the supersaturation s is given by something like:

s ≈ (w * A) / (4π N r_mean ...) or similar.

Actually, the typical equation for quasi-steady supersaturation in a cloud with given droplet spectrum and updraft w is:

s = (w * A) / (4π D_v * ρ_l * integral of r * n(r) dr) ... Wait, let's recall.

The rate of change of supersaturation s = (e - e_s)/e_s. For an adiabatic parcel, the production of supersaturation due to updraft is:

ds/dt|_prod = (ξ * w) where ξ = (L_v/(R_v T^2) - g/(R_d T))? Actually, the "production term" is often given by:

P = w * (dT/dz)_adiabatic * something. More standard: The supersaturation equation:

ds/dt = P w - C s

where P is a factor depending on temperature and pressure (the "production" of supersaturation by adiabatic cooling), and C is the "condensation sink" depending on the droplet spectrum.

For a steady state, ds/dt = 0, so s = P w / C.

We need to compute P and C.

Given:
Temperature T = 0°C = 273.15 K
Pressure p = 80 kPa = 80000 Pa
Updraft w = 8 m/s
Cloud water content LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3? Actually 0.2 g/m^3 = 0.0002 kg/m^3.
Droplet spectrum: Gaussian with mean radius r0 = 4 μm = 4e-6 m, std dev σ = 0.6 μm = 0.6e-6 m.

We need to estimate the supersaturation s as a percentage.

First, find the condensation sink C. The condensation rate is given by the diffusion equation. For a single droplet of radius r, the mass growth rate is:

dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (r + ...) but usually simplified to dm/dt = 4π r D_v (ρ_v - ρ_vs) for large droplets? Actually, for cloud droplets, the growth equation is:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d) ... but for typical cloud droplets > 1 μm, curvature and solute effects are small, so we can approximate:

r dr/dt ≈ s / (F_k + F_d) where F_k and F_d are thermodynamic and diffusion terms. Alternatively, the condensation rate for a population is:

dLWC/dt = 4π D_v (ρ_v - ρ_vs) ∫ r n(r) dr = 4π D_v ρ_vs s ∫ r n(r) dr (if s small). But careful: The mass growth rate of a droplet is dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (1 + ...). Actually, the standard equation for condensation in a cloud is:

ds/dt = P w - C s

where C = 4π D_v N r_mean? No, C = 4π D_v ∫ r n(r) dr * (ρ_l / ρ_vs)? Let's derive.

The supersaturation s = (e - e_s)/e_s ≈ (ρ_v - ρ_vs)/ρ_vs (using ideal gas). The rate of change of s due to condensation is:

ds/dt|_cond = - (L_v/(R_v T^2) - ...) dq_v/dt? Actually, the standard formulation (e.g., Rogers and Yau, "A Short Course in Cloud Physics"):

The supersaturation equation:

ds/dt = Q_1 w - Q_2 dq_l/dt

where Q_1 = (L_v g)/(R_v T^2 c_p) - g/(R_d T) ??? Let's check.

In Rogers and Yau, 3rd edition, Chapter 7, Eq. (7.29):

ds/dt = (ξ w) - (γ dq_l/dt)

where ξ = (L_v/(R_v T^2) - 1/(e_s de_s/dT?)) ... Actually, they give:

ξ = (L_v/(R_v T^2)) (g/(c_p)) - g/(R_d T) ??? Let's derive properly.

The supersaturation s = q_v / q_vs - 1 ≈ q_v/q_vs - 1. For small s, s ≈ ln(q_v/q_vs). The rate of change of s following a parcel:

ds/dt = d/dt (q_v/q_vs - 1) = (1/q_vs) dq_v/dt - (q_v/q_vs^2) dq_vs/dt ≈ (1/q_vs) dq_v/dt - (1/q_vs) dq_vs/dt (since q_v ≈ q_vs).

Now dq_v/dt = - dq_l/dt (condensation). And dq_vs/dt = dq_vs/dT * dT/dt.

For adiabatic ascent, dT/dt = w * dT/dz. dT/dz for dry adiabatic? But in cloud, it's moist adiabatic. However, for small liquid water content, we can approximate dT/dz ≈ -g/c_p (dry adiabatic) or use moist adiabatic? Usually, the production term uses the dry adiabatic lapse rate because the latent heat release is accounted for in the dq_l/dt term. Actually, the standard derivation (e.g., Politovich and Cooper, 1988; or Rogers and Yau) gives:

ds/dt = P w - C s

where P = (L_v/(R_v T^2) - 1/(e_s de_s/dT)) * (g/(c_p))? Let's find exact formulas.

From Rogers and Yau, Eq. (7.29):

ds/dt = (ξ w) - (γ dq_l/dt)

where ξ = (L_v/(R_v T^2)) (g/(c_p)) - g/(R_d T) ??? Wait, I recall:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) ? No.

Let's derive from first principles.

We have s = e/e_s - 1. e = ρ_v R_v T. e_s = saturation vapor pressure.

d e_s / dT = (L_v e_s) / (R_v T^2) (Clausius-Clapeyron).

For an adiabatic parcel, the first law: c_p dT - α dp = -L_v dq_v (if saturated). But for supersaturation, we consider the evolution of s.

Standard approach: The rate of change of s is:

ds/dt = (∂s/∂t)_adiabatic + (∂s/∂t)_condensation

The adiabatic production term is the rate of change of s if no condensation occurs (i.e., dq_l/dt = 0). So we set dq_l/dt = 0, then dq_v/dt = 0. Then s changes because T and p change.

s = e/e_s - 1. e = q_v p / ε (where ε = R_d/R_v). So e ∝ q_v p. If q_v is constant (no condensation), then e ∝ p. So:

ds/dt|_prod = (1/e_s) de/dt - (e/e_s^2) de_s/dt ≈ (1/e_s) de/dt - (1/e_s) de_s/dt (since e ≈ e_s).

de/dt = d/dt (q_v p / ε) = (q_v/ε) dp/dt = (e/p) dp/dt.

dp/dt = w dp/dz. dp/dz = -ρ g. So de/dt = -e ρ g w / p = -e g w / (R_d T) (since p = ρ R_d T).

de_s/dt = de_s/dT * dT/dt. dT/dt = w dT/dz. For dry adiabatic (no condensation), dT/dz = -g/c_p. So dT/dt = -w g/c_p.

de_s/dT = L_v e_s / (R_v T^2).

So ds/dt|_prod = (1/e_s)(-e g w/(R_d T)) - (1/e_s)(L_v e_s/(R_v T^2))(-w g/c_p) = - (g w)/(R_d T) + (L_v g w)/(R_v T^2 c_p).

Thus P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

This is the production term. Note: Some texts include a factor of (1 + s) but for small s it's this.

Now the condensation term: dq_l/dt is the rate of increase of liquid water mixing ratio. dq_l/dt = - dq_v/dt.

The change in s due to condensation: ds/dt|_cond = - γ dq_l/dt, where γ = (∂s/∂q_v) + (∂s/∂T) (dT/dq_v)? Actually, from the equation:

ds = (1/e_s) de - (e/e_s^2) de_s.

de = d(ρ_v R_v T) = R_v T dρ_v + ρ_v R_v dT. But it's easier to use mixing ratio.

q_v = ε e / p. So e = q_v p / ε.

Then s = (q_v p / ε) / e_s - 1.

Take logarithmic derivative: ds ≈ dq_v/q_v + dp/p - de_s/e_s.

But dp/p is related to dynamics. In the condensation term, we consider the change in s due to change in q_v (condensation) while the parcel rises. The standard formulation (e.g., Rogers and Yau Eq. 7.28) gives:

ds/dt = ξ w - γ dq_l/dt

where γ = (L_v/(c_p T) - 1) * (p/(ε e_s))? Let's check.

Actually, from Rogers and Yau (3rd ed., p. 110):

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) ? No, they have:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ? Let's look up memory.

I recall the formula for the production term P (often called the "supersaturation production rate"):

P = (L_v g)/(R_v T^2 c_p) - g/(R_d T)  (units: s^-1 per m/s? Actually P has units 1/m? Wait: ds/dt has units s^-1. w has units m/s. So P has units 1/m. Let's check: g/(R_d T) has units (m/s^2) / (J/kg K * K) = (m/s^2) / (m^2/s^2) = 1/m. Yes. So P is in m^-1. Then P w is in s^-1.

Now the condensation sink C. The rate of condensation dq_l/dt is related to s. For a droplet population, the total mass growth rate per unit volume is:

d(ρ_l)/dt = ∫ (dm/dt) n(r) dr, where dm/dt is the mass growth rate of a single droplet.

For a single droplet, dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (r + Δ) ... but for cloud droplets, the growth is often approximated by:

dm/dt = 4π r D_v (ρ_v - ρ_vs)  (if ignoring ventilation and kinetic effects, and assuming steady-state diffusion). Actually, the exact equation is:

dm/dt = 4π r D_v (ρ_v - ρ_v_∞) / (1 + D_v/(α r) ...) but for typical cloud droplets > 1 μm, the simple equation dm/dt = 4π r D_v (ρ_v - ρ_vs) is a reasonable approximation. However, we also need to account for the heat conduction. The combined heat and mass transfer gives:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d)

where F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) and F_d = (ρ_l R_v T)/(D_v e_s). But for a steady-state supersaturation in a cloud, the curvature and solute terms are often neglected, so r dr/dt ≈ s / (F_k + F_d). Then dm/dt = 4π r^2 ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d).

Alternatively, the condensation sink C is often given by:

C = 4π D_v ∫ r n(r) dr * (ρ_l / ρ_vs)? Let's derive.

We have dq_l/dt = (1/ρ_air) d(ρ_l)/dt. ρ_l is liquid water density (mass of liquid per volume of air). d(ρ_l)/dt = ∫ (dm/dt) n(r) dr.

dm/dt = 4π r D_v (ρ_v - ρ_vs) = 4π r D_v ρ_vs s (since s = (ρ_v - ρ_vs)/ρ_vs).

So d(ρ_l)/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

Then dq_l/dt = (4π D_v ρ_vs s / ρ_air) ∫ r n(r) dr.

Now, the condensation term in ds/dt is -γ dq_l/dt. We need γ.

From the derivation, ds/dt|_cond = - (L_v/(c_p T) - 1) * (p/(ε e_s)) * dq_l/dt? Let's derive γ.

We have s = q_v/q_vs - 1. q_vs = ε e_s / p.

ds = dq_v/q_vs - q_v/q_vs^2 dq_vs ≈ dq_v/q_vs - dq_vs/q_vs.

d q_vs = d(ε e_s/p) = q_vs (de_s/e_s - dp/p).

In the condensation process, we consider the change in s due to change in q_v (d q_v = - d q_l) and the associated latent heat release which changes T and thus e_s. The pressure change is due to the updraft, which is already in the production term. So in the condensation term, we assume dp=0? Actually, the standard separation is: the production term includes the adiabatic changes (p, T) with no condensation; the condensation term includes the changes due to latent heat release and vapor depletion at constant pressure? Or is the pressure change included in both? Typically, the supersaturation equation is derived as:

ds/dt = Q_1 w - Q_2 dq_l/dt

where Q_1 = (L_v g)/(R_v T^2 c_p) - g/(R_d T) (as above)
and Q_2 = (L_v^2/(c_p R_v T^2) + ...) Actually, let's check Rogers and Yau.

In Rogers and Yau, Eq. (7.29):

ds/dt = ξ w - γ dq_l/dt

where ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * T? No, they have:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ??? Let's compute units.

I found online a common formula: 
P = (L_v g)/(R_v T^2 c_p) - g/(R_d T)  (m^-1)
and C = 4π D_v N r_mean * (ρ_l / ρ_vs) * something? Wait.

Let's derive the condensation term carefully.

We have s = e/e_s - 1.
e = ρ_v R_v T.
e_s = saturation vapor pressure.

ds = de/e_s - e de_s/e_s^2 ≈ de/e_s - de_s/e_s.

de = R_v T dρ_v + ρ_v R_v dT = R_v T dρ_v + (e/T) dT.
de_s = (L_v e_s)/(R_v T^2) dT.

So ds = (R_v T/e_s) dρ_v + (e/(e_s T)) dT - (L_v/(R_v T^2)) dT.

Since e ≈ e_s, ds ≈ (R_v T/e_s) dρ_v + (1/T - L_v/(R_v T^2)) dT.

Now dρ_v = - dρ_l (condensation). dT comes from latent heat release: dT = (L_v/c_p) dq_l? Actually, for adiabatic process with condensation, the first law: c_p dT - dp/ρ = -L_v dq_v. If we isolate the condensation part, we consider the change in T due to latent heat release at constant pressure? Or we need to be consistent with the production term.

The standard approach (e.g., Cooper, 1989; Politovich and Cooper, 1988) gives the supersaturation equation as:

ds/dt = P w - C s

where P = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ??? Let's check units: P w must have units s^-1. P has units m^-1. w m/s -> s^-1. So P must be m^-1.

My derived P = (L_v g)/(R_v T^2 c_p) - g/(R_d T). Let's check units:
L_v: J/kg = m^2/s^2
g: m/s^2
R_v: J/kg K = m^2/s^2 K
T: K
c_p: J/kg K = m^2/s^2 K
So L_v g/(R_v T^2 c_p): (m^2/s^2 * m/s^2) / (m^2/s^2 K * K^2 * m^2/s^2 K) = (m^3/s^4) / (m^4/s^4 K^2) = 1/(m K^2)? That doesn't match. Let's re-evaluate.

L_v: J/kg = m^2/s^2
g: m/s^2
Product: m^3/s^4
R_v: J/(kg K) = m^2/(s^2 K)
T^2: K^2
c_p: J/(kg K) = m^2/(s^2 K)
Denominator: R_v T^2 c_p = (m^2/(s^2 K)) * K^2 * (m^2/(s^2 K)) = m^4/(s^4 K) * K? Wait: m^2/(s^2 K) * K^2 = m^2 K / s^2. Then times m^2/(s^2 K) = m^4/s^4. So L_v g/(R_v T^2 c_p) has units (m^3/s^4) / (m^4/s^4) = 1/m. Good.

Second term: g/(R_d T): g m/s^2, R_d J/(kg K) = m^2/(s^2 K), T K. So g/(R_d T) = (m/s^2) / (m^2/s^2) = 1/m. So P is in 1/m. Good.

Now for the condensation term: ds/dt|_cond = - C s. We need C in s^-1.

We have dρ_l/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

Now we need to relate ds/dt to dρ_l/dt. From ds = (R_v T/e_s) dρ_v + (1/T - L_v/(R_v T^2)) dT.

In the condensation process, dρ_v = - dρ_l. And dT is the temperature change due to latent heat release. If we consider the parcel rising, the total dT is from adiabatic expansion and latent heat. But we already accounted for adiabatic expansion in the production term. So in the condensation term, we should consider the temperature change due to latent heat release only, at constant pressure? Or is it included in the coefficient?

The standard coefficient γ in ds/dt = ... - γ dq_l/dt is derived by considering the change in s due to a change in q_l at constant total water and constant pressure? Let's check Rogers and Yau.

In Rogers and Yau, Eq. (7.28):

ds/dt = (L_v/(R_v T^2) - 1/T) * (g/c_p) * w - (L_v/(R_v T^2) - 1/T) * (L_v/c_p) * dq_l/dt - (1/q_v) dq_l/dt

Wait, that seems different. Let's derive from their approach.

They start with s = q_v/q_vs - 1.
d s/dt = (1/q_vs) dq_v/dt - (q_v/q_vs^2) dq_vs/dt ≈ (1/q_vs) dq_v/dt - (1/q_vs) dq_vs/dt.

Now dq_v/dt = - dq_l/dt (if no other sources).

dq_vs/dt = d/dt (ε e_s/p) = q_vs (1/e_s de_s/dt - 1/p dp/dt).

de_s/dt = (L_v e_s)/(R_v T^2) dT/dt.

dp/dt = -ρ g w.

dT/dt = - (g/c_p) w + (L_v/c_p) dq_l/dt (from first law: c_p dT/dt - (1/ρ) dp/dt = -L_v dq_v/dt = L_v dq_l/dt; and dp/dt = -ρ g w, so c_p dT/dt + g w = L_v dq_l/dt => dT/dt = -g w/c_p + (L_v/c_p) dq_l/dt).

Substitute:

ds/dt = - (1/q_vs) dq_l/dt - (1/q_vs) * q_vs [ (1/e_s) de_s/dt - (1/p) dp/dt ]
= - dq_l/dt / q_vs - (L_v/(R_v T^2)) dT/dt + (1/p) dp/dt.

Now plug dT/dt and dp/dt:

dp/dt = -ρ g w = - (p/(R_d T)) g w.

dT/dt = -g w/c_p + (L_v/c_p) dq_l/dt.

So:

ds/dt = - dq_l/dt / q_vs - (L_v/(R_v T^2)) (-g w/c_p + (L_v/c_p) dq_l/dt) + (1/p) (- (p/(R_d T)) g w)
= - dq_l/dt / q_vs + (L_v g w)/(R_v T^2 c_p) - (L_v^2/(R_v T^2 c_p)) dq_l/dt - (g w)/(R_d T).

Group terms with w and dq_l/dt:

ds/dt = [ (L_v g)/(R_v T^2 c_p) - g/(R_d T) ] w  - [ 1/q_vs + (L_v^2)/(R_v T^2 c_p) ] dq_l/dt.

So P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

And γ = 1/q_vs + L_v^2/(R_v T^2 c_p).

Now dq_l/dt is the rate of change of liquid water mixing ratio. dq_l/dt = (1/ρ_air) dρ_l/dt.

We have dρ_l/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

But wait: Is the growth equation dm/dt = 4π r D_v (ρ_v - ρ_vs) accurate? It ignores the heat conduction effect on the droplet surface temperature. The full growth equation including heat conduction gives a modified coefficient. Usually, the growth equation is:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d)

where F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) and F_d = (ρ_l R_v T)/(D_v e_s). For typical conditions, F_k and F_d are often combined into a single factor. The mass growth rate is:

dm/dt = 4π r ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d) (ignoring curvature and solute).

So dm/dt = 4π r s / ( (F_k + F_d)/ρ_l )? Actually, dm/dt = 4π r ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d).

Then dρ_l/dt = ∫ (dm/dt) n(r) dr = 4π ρ_l s / (F_k + F_d) ∫ r n(r) dr.

But note: F_k and F_d depend on T and p. They are:

F_d = (ρ_l R_v T) / (D_v e_s)
F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T)

where K is thermal conductivity of air, D_v is diffusivity of water vapor in air.

Often, the combined term is written as:

dm/dt = 4π r D_v (ρ_v - ρ_vs) / (1 + D_v/(α r) ...) but for cloud droplets > 1 μm, the simple diffusion equation with the psychrometric correction is used. Actually, the standard equation for condensational growth of a single droplet is:

dm/dt = 4π r (s) / ( (L_v^2/(K R_v T^2) + (R_v T)/(D_v e_s) ) )? Let's derive.

The growth equation from diffusion of vapor and heat conduction:

dm/dt = 4π r D_v (ρ_v_∞ - ρ_v_r) (vapor diffusion)
and heat conduction: L_v dm/dt = 4π r K (T_r - T_∞)

At the droplet surface, ρ_v_r = ρ_vs(T_r). For small s, we linearize:

ρ_v_r - ρ_vs(T_∞) ≈ ρ_vs(T_∞) * ( (L_v/(R_v T^2)) (T_r - T_∞) + s_∞? Actually, s_∞ = (ρ_v_∞ - ρ_vs(T_∞))/ρ_vs(T_∞).

Then we can solve for dm/dt:

dm/dt = 4π r ρ_vs(T_∞) s_∞ / ( (L_v^2/(K R_v T^2)) + (R_v T)/(D_v e_s) )? Wait, let's do it carefully.

Let ρ_v_∞ = ρ_vs (1 + s). At the droplet surface, ρ_v_r = ρ_vs(T_r). We approximate ρ_vs(T_r) ≈ ρ_vs(T_∞) + (dρ_vs/dT)(T_r - T_∞). dρ_vs/dT = (L_v/(R_v T^2) - 1/T) ρ_vs ≈ (L_v/(R_v T^2)) ρ_vs (since L_v/(R_v T^2) >> 1/T).

So ρ_v_r ≈ ρ_vs(T_∞) [1 + (L_v/(R_v T^2)) (T_r - T_∞)].

Vapor diffusion: dm/dt = 4π r D_v (ρ_v_∞ - ρ_v_r) = 4π r D_v ρ_vs [ s - (L_v/(R_v T^2)) (T_r - T_∞) ].

Heat conduction: L_v dm/dt = 4π r K (T_r - T_∞) => T_r - T_∞ = (L_v dm/dt) / (4π r K).

Substitute:

dm/dt = 4π r D_v ρ_vs [ s - (L_v/(R_v T^2)) * (L_v dm/dt) / (4π r K) ].

Solve for dm/dt:

dm/dt = 4π r D_v ρ_vs s - (L_v^2 D_v ρ_vs)/(R_v T^2 K) dm/dt.

dm/dt [1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)] = 4π r D_v ρ_vs s.

So dm/dt = 4π r D_v ρ_vs s / [1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)].

Note that ρ_vs = e_s/(R_v T). So:

dm/dt = 4π r D_v (e_s/(R_v T)) s / [1 + (L_v^2 D_v e_s)/(R_v^2 T^3 K)].

This is the standard equation. Often written as:

dm/dt = 4π r s / ( (R_v T)/(D_v e_s) + (L_v^2)/(K R_v T^2) )? Let's check:

From above: dm/dt = 4π r D_v ρ_vs s / (1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)).
Divide numerator and denominator by D_v ρ_vs:
dm/dt = 4π r s / (1/(D_v ρ_vs) + L_v^2/(R_v T^2 K)).
Now 1/(D_v ρ_vs) = (R_v T)/(D_v e_s).
So dm/dt = 4π r s / ( (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ).

This matches the F_k + F_d form if we multiply by ρ_l? Actually, earlier I had F_d = (ρ_l R_v T)/(D_v e_s) and F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) ≈ (L_v^2 ρ_l)/(K R_v T^2). Then F_k + F_d = ρ_l [ (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ]. Then dm/dt = 4π r ρ_l s / (F_k + F_d) = 4π r s / [ (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ]. Yes, consistent.

So the mass growth rate per droplet is dm/dt = 4π r s / G, where G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2).

Then dρ_l/dt = ∫ (dm/dt) n(r) dr = (4π s / G) ∫ r n(r) dr.

Now, the total number concentration N = ∫ n(r) dr, and the mean radius r_mean = (1/N) ∫ r n(r) dr. But we have a Gaussian spectrum, so we can compute ∫ r n(r) dr = N * r_mean. However, we are not given N directly. We are given cloud water content (LWC) = 0.2 g/m^3 = 0.2e-3 kg/m^3. LWC = ρ_l = (4/3)π ρ_w ∫ r^3 n(r) dr, where ρ_w is density of liquid water (≈ 1000 kg/m^3). For a Gaussian distribution, we can compute the moments.

Let n(r) = (N / (√(2π) σ)) exp(-(r - r0)^2/(2σ^2)). But we don't know N. However, we can relate LWC to N and the moments.

LWC = ρ_w * (4/3)π ∫ r^3 n(r) dr.

We need ∫ r n(r) dr for the condensation sink.

So we need to compute the ratio (∫ r n(r) dr) / LWC? Or we can find N from LWC and then compute ∫ r n(r) dr.

Given r0 = 4 μm, σ = 0.6 μm. We can compute the moments of a Gaussian. However, note that r is positive, but Gaussian extends to negative. For small σ/r0 = 0.15, the negative part is negligible. We can approximate the moments by integrating from 0 to ∞, or just use the Gaussian moments ignoring truncation.

For a Gaussian with mean μ and std σ, the moments:
E[r] = μ
E[r^2] = μ^2 + σ^2
E[r^3] = μ^3 + 3μσ^2
E[r^4] = μ^4 + 6μ^2σ^2 + 3σ^4
etc.

But we need ∫ r n(r) dr = N μ.
And LWC = ρ_w (4/3)π N E[r^3] = ρ_w (4/3)π N (μ^3 + 3μσ^2).

So we can solve for N:
N = LWC / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

Then ∫ r n(r) dr = N μ = LWC * μ / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

Thus the condensation sink term: dρ_l/dt = (4π s / G) * N μ.

Then dq_l/dt = (1/ρ_air) dρ_l/dt.

Now we need ρ_air, the density of air at T=273.15 K, p=80 kPa.

ρ_air = p / (R_d T) where R_d = 287.05 J/(kg K). (We'll use standard values.)

Now we have ds/dt = P w - γ dq_l/dt.

And dq_l/dt = (4π s / G) * (N μ) / ρ_air.

So ds/dt = P w - γ * (4π N μ / (ρ_air G)) s.

In steady state, ds/dt = 0, so s = (P w) / (γ * 4π N μ / (ρ_air G)).

Thus s = (P w ρ_air G) / (4π γ N μ).

We need to compute P, G, γ, N, μ, ρ_air.

Let's gather constants:

T = 273.15 K
p = 80000 Pa
w = 8 m/s
LWC = 0.2e-3 kg/m^3 (0.2 g/m^3)
μ = 4e-6 m
σ = 0.6e-6 m

Constants:
R_d = 287.0 J/(kg K) (dry air gas constant)
R_v = 461.5 J/(kg K) (water vapor gas constant)
c_p = 1005 J/(kg K) (specific heat of dry air at constant pressure)
L_v = 2.5e6 J/kg (latent heat of vaporization at 0°C? Actually L_v varies with T. At 0°C, L_v ≈ 2.5e6 J/kg. We'll use 2.5e6.)
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3 (density of liquid water)

We need e_s at 0°C. Saturation vapor pressure over water at 0°C: e_s = 611.2 Pa (approx). Or we can use the Clausius-Clapeyron equation or a standard formula. 611 Pa is standard. We'll use e_s = 611.2 Pa.

We need D_v: diffusivity of water vapor in air. At 0°C and 80 kPa? D_v depends on T and p. D_v ≈ 2.26e-5 m^2/s at 0°C and 100 kPa? Actually, D_v = 2.26e-5 * (T/273.15)^1.81 * (101325/p) m^2/s. We'll compute.

We need K: thermal conductivity of air. At 0°C, K ≈ 0.0243 W/(m K) at 100 kPa? Thermal conductivity of air is roughly independent of pressure. K ≈ 0.0243 W/(m K) at 0°C. We can use that.

Now compute step by step.

First, ρ_air = p / (R_d T) = 80000 / (287 * 273.15) = 80000 / 78394.05 ≈ 1.0205 kg/m^3.

e_s = 611.2 Pa.

D_v: standard value at 0°C, 101325 Pa is about 2.26e-5 m^2/s. Adjust for pressure: D_v ∝ 1/p. So D_v = 2.26e-5 * (101325 / 80000) = 2.26e-5 * 1.26656 = 2.862e-5 m^2/s. (Temperature is 0°C, so no T adjustment needed if we use 0°C reference.)

K: thermal conductivity of air at 0°C: K ≈ 0.0243 W/(m K). (It varies slightly with T but we'll use 0.0243.)

Now compute G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2).

First term: R_v T = 461.5 * 273.15 = 126,000? Let's compute: 461.5 * 273.15 = 461.5 * 273.15 = 126,000 (approx). Actually: 461.5 * 273.15 = 126,058.7.
D_v e_s = 2.862e-5 * 611.2 = 0.01749.
So (R_v T)/(D_v e_s) = 126058.7 / 0.01749 = 7,207,000 s/m^2? Units: (J/kg K * K) / (m^2/s * Pa) = (m^2/s^2) / (m^2/s^2 * m?) Wait: Pa = N/m^2 = kg/(m s^2). J/kg = m^2/s^2. So R_v T has units m^2/s^2. D_v e_s has units m^2/s * kg/(m s^2) = kg/(s^3)? Let's do carefully: D_v [m^2/s], e_s [Pa] = [kg/(m s^2)]. So D_v e_s [kg m/s^3]. R_v T [m^2/s^2]. So ratio has units (m^2/s^2) / (kg m/s^3) = m s / kg. This is not dimensionless. But G should have units such that dm/dt = 4π r s / G. dm/dt [kg/s]. 4π r [m], s dimensionless. So G must have units [m s / kg]? Actually, dm/dt = 4π r s / G => G = 4π r s / (dm/dt). dm/dt has units kg/s. r has m. So G has m / (kg/s) = m s / kg. Yes, that matches.

Second term: L_v^2/(K R_v T^2).
L_v = 2.5e6 J/kg = 2.5e6 m^2/s^2.
L_v^2 = 6.25e12 m^4/s^4.
K = 0.0243 W/(m K) = 0.0243 kg m/(s^3 K) [W = J/s = kg m^2/s^3, so W/(m K) = kg m/s^3 K].
R_v T^2 = 461.5 * (273.15)^2 = 461.5 * 74610 = 34,430,000? Let's compute: 273.15^2 = 74610.9. 461.5 * 74610.9 = 34,430,000 m^2/s^2 * K? R_v has J/(kg K) = m^2/(s^2 K). So R_v T^2 has m^2 K/s^2.
So L_v^2/(K R_v T^2) = (m^4/s^4) / ( (kg m/s^3 K) * (m^2 K/s^2) ) = (m^4/s^4) / (kg m^3/s^5) = m s / kg. Good.

Compute:
L_v^2 = 6.25e12.
K = 0.0243.
R_v T^2 = 461.5 * 74610.9 = 34,430,000 (approx). Let's do precisely:
461.5 * 273.15^2.
273.15^2 = 74610.9225.
461.5 * 74610.9225 = 34,432,000? 461.5 * 74610 = 34,432,515. Let's use 34,432,000.
So K R_v T^2 = 0.0243 * 34,432,000 = 836,700 (approx). 0.0243 * 34,432,000 = 836,697.6.
Then L_v^2/(K R_v T^2) = 6.25e12 / 8.366976e5 = 7,469,000? 6.25e12 / 8.37e5 = 7.47e6. Let's compute: 6.25e12 / 836,697.6 = 7,469,000. So about 7.47e6 m s/kg.

First term: (R_v T)/(D_v e_s) = 126,058.7 / (2.862e-5 * 611.2) = 126,058.7 / 0.01749 = 7,207,000. So both terms are similar magnitude. G = 7.207e6 + 7.469e6 = 1.4676e7 m s/kg.

Now compute P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

First part: L_v g = 2.5e6 * 9.81 = 24,525,000.
R_v T^2 c_p = 461.5 * 74610.9 * 1005 = 34,432,000 * 1005 = 34,604,160,000? Wait: 34,432,000 * 1005 = 34,604,160,000.
So (L_v g)/(R_v T^2 c_p) = 24,525,000 / 34,604,160,000 = 7.086e-4? Let's compute: 24.525e6 / 34.604e9 = 7.086e-4 1/m.

Second part: g/(R_d T) = 9.81 / (287 * 273.15) = 9.81 / 78394.05 = 1.251e-4 1/m.

So P = 7.086e-4 - 1.251e-4 = 5.835e-4 1/m.

Now compute γ = 1/q_vs + L_v^2/(R_v T^2 c_p).

First, q_vs = ε e_s / p, where ε = R_d/R_v = 287/461.5 = 0.6219.
e_s = 611.2 Pa, p = 80000 Pa.
q_vs = 0.6219 * 611.2 / 80000 = 0.6219 * 0.00764 = 0.00475 kg/kg? Let's compute: 611.2/80000 = 0.00764. 0.6219 * 0.00764 = 0.00475. So q_vs ≈ 0.00475 kg/kg.
1/q_vs = 1/0.00475 = 210.5.

Second term: L_v^2/(R_v T^2 c_p) = 6.25e12 / (34,432,000 * 1005) = 6.25e12 / 34,604,160,000 = 180.6? Wait: 6.25e12 / 3.4604e10 = 180.6. Let's compute: 34,604,160,000 = 3.4604e10. 6.25e12 / 3.4604e10 = 180.6. So γ = 210.5 + 180.6 = 391.1 (dimensionless).

Now compute N μ. We need N = LWC / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

μ = 4e-6 m, σ = 0.6e-6 m.
μ^3 = (4e-6)^3 = 64e-18 = 6.4e-17 m^3.
3μσ^2 = 3 * 4e-6 * (0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18 m^3.
Sum = 6.4e-17 + 0.432e-17 = 6.832e-17 m^3.
ρ_w = 1000 kg/m^3.
(4/3)π = 4.18879.
Denom = 1000 * 4.18879 * 6.832e-17 = 4188.79 * 6.832e-17 = 2.862e-13 kg? Let's compute: 4188.79 * 6.832e-17 = 2.862e-13 kg per droplet? Actually, this is the mass per droplet times N? Wait: LWC = N * (4/3)π ρ_w E[r^3]. So N = LWC / [ (4/3)π ρ_w E[r^3] ].
LWC = 0.2e-3 kg/m^3 = 2e-4 kg/m^3.
N = 2e-4 / 2.862e-13 = 6.99e8 m^-3. About 700 per cm^3? 6.99e8 m^-3 = 699 cm^-3. That's reasonable for a cumulus cloud.

Then N μ = 6.99e8 * 4e-6 = 2796 m^{-2}? Units: N [m^-3], μ [m] -> N μ [m^-2]. 6.99e8 * 4e-6 = 2796 m^-2.

Now compute the denominator of s: 4π γ N μ / (ρ_air G).

4π = 12.566.
γ = 391.1.
N μ = 2796.
Product = 12.566 * 391.1 * 2796 = let's compute: 12.566 * 391.1 = 4915. 4915 * 2796 = 13,740,000? 4915 * 2796 = 4915*2800 - 4915*4 = 13,762,000 - 19,660 = 13,742,340.
ρ_air = 1.0205 kg/m^3.
G = 1.4676e7 m s/kg.
ρ_air G = 1.0205 * 1.4676e7 = 1.497e7 kg/m^3 * m s/kg = m s/m^3? Wait: ρ_air [kg/m^3], G [m s/kg] -> ρ_air G [s/m^2]. Actually: kg/m^3 * m s/kg = s/m^2. Yes.
So denominator = (4π γ N μ) / (ρ_air G) = 13,742,340 / 1.497e7 = 0.918 s^-1? Units: N μ [m^-2], γ dimensionless, so numerator has m^-2. Denominator has s/m^2. So ratio has s^-1. Good.

Now P w = 5.835e-4 1/m * 8 m/s = 4.668e-3 s^-1.

So s = (P w) / (denom) = 4.668e-3 / 0.918 = 0.005085. That's about 0.51% supersaturation.

But wait: Is this the correct formula? Let's double-check the derivation.

We had ds/dt = P w - γ dq_l/dt.
And dq_l/dt = (1/ρ_air) dρ_l/dt.
dρ_l/dt = (4π s / G) ∫ r n(r) dr = (4π s / G) N μ.
So dq_l/dt = (4π N μ / (ρ_air G)) s.
Then ds/dt = P w - γ (4π N μ / (ρ_air G)) s.
Steady state: s = (P w ρ_air G) / (4π γ N μ).

This matches my expression.

Now check if we missed any factor. In some formulations, the condensation sink includes the integral of r n(r) dr, but sometimes they use the mean radius of the surface area distribution? Actually, the integral of r n(r) dr is proportional to the total surface area? Total surface area = 4π ∫ r^2 n(r) dr. But here we have ∫ r n(r) dr. That comes from dm/dt ∝ r. So it's correct.

But wait: In the growth equation, dm/dt = 4π r D_v ρ_vs s / (1 + ...). We used G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2). This is correct for the combined heat and mass transfer. However, sometimes the growth equation is written as:

dm/dt = 4π r s / (A + B) where A = (L_v^2)/(K R_v T^2) and B = (R_v T)/(D_v e_s). Yes.

Now check the values of constants. Are we using the correct L_v? At 0°C, L_v is about 2.5e6 J/kg. Some sources use 2.5e6, others 2.501e6. It's fine.

Check D_v: At 0°C and 1000 hPa, D_v ≈ 2.26e-5 m^2/s. At 800 hPa, D_v = 2.26e-5 * (1013/800) = 2.86e-5. Good.

Check K: At 0°C, K ≈ 0.0243 W/(m K). Good.

Check e_s: At 0°C, e_s = 611.2 Pa. Good.

Check ρ_air: p=80 kPa, T=273.15, R_d=287. ρ = 80000/(287*273.15) = 1.02 kg/m^3. Good.

Check moments: For Gaussian, E[r^3] = μ^3 + 3μσ^2. μ=4, σ=0.6. μ^3=64, 3μσ^2=3*4*0.36=4.32. Sum=68.32 μm^3. In m^3: 68.32e-18 = 6.832e-17. Good.

LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3 = 2e-4 kg/m^3.
N = 2e-4 / (1000 * 4.18879 * 6.832e-17) = 2e-4 / (2.862e-13) = 6.99e8 m^-3 = 699 cm^-3. Typical cumulus droplet concentrations are 100-500 cm^-3. 699 is a bit high but plausible for developing cumulus (maybe continental). With mean radius 4 μm, LWC 0.2 g/m^3, N = LWC / (ρ_w * 4/3 π r_vol^3). If we used mean volume radius r_vol = (E[r^3])^(1/3) = (68.32)^(1/3) ≈ 4.09 μm. Then N = 0.2e-3 / (1000 * 4/3 π (4.09e-6)^3) = 2e-4 / (1000 * 4.1888 * 68.4e-18) = same. So N ~ 700 cm^-3. Acceptable.

Now compute s = 0.005085 = 0.5085%. So about 0.51%.

But let's double-check the production term P. Some sources give P = (L_v g)/(c_p R_v T^2) - g/(R_d T). That's what I used. However, sometimes the production term is given as:

P = (dT/dz)_moist? No, for supersaturation, the production term is the rate of change of s due to adiabatic cooling if no condensation. That is what we derived.

Another common formula: s = (w * A) / (4π D_v N r_mean) where A is a function of T and p. Let's see if our formula reduces to that.

If we ignore the heat conduction term (G ≈ (R_v T)/(D_v e_s)), and ignore the γ term (γ ≈ 1/q_vs), then s ≈ (P w ρ_air (R_v T)/(D_v e_s)) / (4π (1/q_vs) N μ). Note ρ_air = p/(R_d T), q_vs = ε e_s/p. So 1/q_vs = p/(ε e_s). Then s ≈ P w * (p/(R_d T)) * (R_v T)/(D_v e_s) * (ε e_s/p) / (4π N μ) = P w * (R_v/R_d) * ε / (D_v 4π N μ) = P w * 1 / (D_v 4π N μ) since ε = R_d/R_v. So s ≈ P w / (4π D_v N μ). And P = (L_v g)/(c_p R_v T^2) - g/(R_d T). This is a common simplified formula. Our full formula includes the heat conduction and the γ correction.

Now, is the steady-state assumption valid? The problem says "estimate the supersaturation in an updraft of 8 m/s". It likely expects the quasi-steady supersaturation in a cloud with given droplet spectrum. So our approach is standard.

Let's recompute with more precise constants to ensure accuracy.

Constants:
R_d = 287.058 J/(kg K) (often 287)
R_v = 461.5 J/(kg K)
c_p = 1005 J/(kg K) (for dry air, sometimes 1004)
L_v = 2.501e6 J/kg at 0°C? Actually, latent heat of vaporization varies: at 0°C it's 2.501e6, at 100°C it's 2.26e6. We'll use 2.5e6.
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3

T = 273.15 K
p = 80000 Pa
w = 8 m/s
LWC = 0.2 g/m^3 = 0.0002 kg/m^3
μ = 4e-6 m
σ = 0.6e-6 m

e_s at 0°C: 611.2 Pa (some use 611.0). We'll use 611.2.
D_v at 0°C, 101325 Pa: 2.26e-5 m^2/s. Adjust to 80000 Pa: D_v = 2.26e-5 * (101325/80000) = 2.26e-5 * 1.2665625 = 2.8624e-5 m^2/s.
K at 0°C: 0.0243 W/(m K). (Some sources: 0.0240 at 0°C? Let's check: Thermal conductivity of air at 0°C is about 0.0243 W/mK. At -10°C it's 0.0236, at 10°C 0.0250. So 0.0243 is fine.)

Now compute step by step with high precision.

1. ρ_air = p / (R_d * T) = 80000 / (287.058 * 273.15) = 80000 / 78409.5 = 1.0203 kg/m^3.

2. e_s = 611.2 Pa.

3. q_vs = (R_d/R_v) * e_s / p = (287.058/461.5) * 611.2 / 80000 = 0.62198 * 0.00764 = 0.004752.

4. P = (L_v * g) / (R_v * T^2 * c_p) - g / (R_d * T)
   L_v * g = 2.5e6 * 9.81 = 24,525,000.
   R_v * T^2 = 461.5 * (273.15^2) = 461.5 * 74610.9225 = 34,432,000 (approx). Let's compute exactly: 273.15^2 = 74610.9225. 461.5 * 74610.9225 = 34,432,000? 461.5 * 74610 = 34,432,515. 461.5 * 0.9225 = 425.7. So 34,432,940.7.
   c_p = 1005.
   R_v * T^2 * c_p = 34,432,940.7 * 1005 = 34,605,105,403.
   First term = 24,525,000 / 34,605,105,403 = 7.087e-4.
   Second term = 9.81 / (287.058 * 273.15) = 9.81 / 78409.5 = 1.251e-4.
   P = 7.087e-4 - 1.251e-4 = 5.836e-4 m^-1.

5. G = (R_v * T) / (D_v * e_s) + L_v^2 / (K * R_v * T^2)
   R_v * T = 461.5 * 273.15 = 126,058.7.
   D_v * e_s = 2.8624e-5 * 611.2 = 0.017495.
   First term = 126058.7 / 0.017495 = 7,205,000.
   L_v^2 = 6.25e12.
   K * R_v * T^2 = 0.0243 * 34,432,940.7 = 836,720.
   Second term = 6.25e12 / 836720 = 7,469,000.
   G = 7,205,000 + 7,469,000 = 14,674,000 m s/kg.

6. γ = 1/q_vs + L_v^2 / (R_v * T^2 * c_p)
   1/q_vs = 1/0.004752 = 210.44.
   L_v^2 / (R_v * T^2 * c_p) = 6.25e12 / 34,605,105,403 = 180.6.
   γ = 210.44 + 180.6 = 391.04.

7. Compute E[r^3] = μ^3 + 3μσ^2.
   μ = 4e-6, σ = 0.6e-6.
   μ^3 = 64e-18 = 6.4e-17.
   3μσ^2 = 3 * 4e-6 * (0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18.
   Sum = 6.832e-17 m^3.

8. N = LWC / (ρ_w * (4/3)π * E[r^3])
   LWC = 0.0002 kg/m^3.
   ρ_w = 1000.
   (4/3)π = 4.1887902.
   Denom = 1000 * 4.1887902 * 6.832e-17 = 4188.79 * 6.832e-17 = 2.8618e-13.
   N = 2e-4 / 2.8618e-13 = 6.988e8 m^-3.

9. N * μ = 6.988e8 * 4e-6 = 2795.2 m^-2.

10. Denominator of s: C_sink = (4π * γ * N * μ) / (ρ_air *
~~~~

**attempt 1** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

<details><summary>PROMPT（逐字）</summary>

~~~~
Your solve() function failed to run. Fix the bug and return the corrected function.

## Problem
In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of O.6 μm. Given that the cloud water content is $0 . 2 \mathrm { g } / \mathrm { \dot { m } } ^ { 3 }$ ,estimate the supersaturationinanupdraft of8m/s.Assume a temperature of $0 ^ { \circ } \bar { C }$ and a pressure of 80 kPa.

Express your answer as a percentage.

## Your code
We need to solve an atmospheric science problem: estimate supersaturation in an updraft of 8 m/s given a developing cumulus cloud with droplet spectrum Gaussian, mean radius 4 μm, std dev 0.6 μm, cloud water content 0.2 g/m^3, temperature 0°C, pressure 80 kPa. Express answer as a percentage.

We need to compute supersaturation. This is a classic cloud physics problem: supersaturation in an updraft is determined by the balance between cooling by adiabatic ascent (which increases relative humidity) and depletion by droplet growth (condensation). In a steady state, the supersaturation s is given by something like:

s ≈ (w * A) / (4π N r_mean ...) or similar.

Actually, the typical equation for quasi-steady supersaturation in a cloud with given droplet spectrum and updraft w is:

s = (w * A) / (4π D_v * ρ_l * integral of r * n(r) dr) ... Wait, let's recall.

The rate of change of supersaturation s = (e - e_s)/e_s. For an adiabatic parcel, the production of supersaturation due to updraft is:

ds/dt|_prod = (ξ * w) where ξ = (L_v/(R_v T^2) - g/(R_d T))? Actually, the "production term" is often given by:

P = w * (dT/dz)_adiabatic * something. More standard: The supersaturation equation:

ds/dt = P w - C s

where P is a factor depending on temperature and pressure (the "production" of supersaturation by adiabatic cooling), and C is the "condensation sink" depending on the droplet spectrum.

For a steady state, ds/dt = 0, so s = P w / C.

We need to compute P and C.

Given:
Temperature T = 0°C = 273.15 K
Pressure p = 80 kPa = 80000 Pa
Updraft w = 8 m/s
Cloud water content LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3? Actually 0.2 g/m^3 = 0.0002 kg/m^3.
Droplet spectrum: Gaussian with mean radius r0 = 4 μm = 4e-6 m, std dev σ = 0.6 μm = 0.6e-6 m.

We need to estimate the supersaturation s as a percentage.

First, find the condensation sink C. The condensation rate is given by the diffusion equation. For a single droplet of radius r, the mass growth rate is:

dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (r + ...) but usually simplified to dm/dt = 4π r D_v (ρ_v - ρ_vs) for large droplets? Actually, for cloud droplets, the growth equation is:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d) ... but for typical cloud droplets > 1 μm, curvature and solute effects are small, so we can approximate:

r dr/dt ≈ s / (F_k + F_d) where F_k and F_d are thermodynamic and diffusion terms. Alternatively, the condensation rate for a population is:

dLWC/dt = 4π D_v (ρ_v - ρ_vs) ∫ r n(r) dr = 4π D_v ρ_vs s ∫ r n(r) dr (if s small). But careful: The mass growth rate of a droplet is dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (1 + ...). Actually, the standard equation for condensation in a cloud is:

ds/dt = P w - C s

where C = 4π D_v N r_mean? No, C = 4π D_v ∫ r n(r) dr * (ρ_l / ρ_vs)? Let's derive.

The supersaturation s = (e - e_s)/e_s ≈ (ρ_v - ρ_vs)/ρ_vs (using ideal gas). The rate of change of s due to condensation is:

ds/dt|_cond = - (L_v/(R_v T^2) - ...) dq_v/dt? Actually, the standard formulation (e.g., Rogers and Yau, "A Short Course in Cloud Physics"):

The supersaturation equation:

ds/dt = Q_1 w - Q_2 dq_l/dt

where Q_1 = (L_v g)/(R_v T^2 c_p) - g/(R_d T) ??? Let's check.

In Rogers and Yau, 3rd edition, Chapter 7, Eq. (7.29):

ds/dt = (ξ w) - (γ dq_l/dt)

where ξ = (L_v/(R_v T^2) - 1/(e_s de_s/dT?)) ... Actually, they give:

ξ = (L_v/(R_v T^2)) (g/(c_p)) - g/(R_d T) ??? Let's derive properly.

The supersaturation s = q_v / q_vs - 1 ≈ q_v/q_vs - 1. For small s, s ≈ ln(q_v/q_vs). The rate of change of s following a parcel:

ds/dt = d/dt (q_v/q_vs - 1) = (1/q_vs) dq_v/dt - (q_v/q_vs^2) dq_vs/dt ≈ (1/q_vs) dq_v/dt - (1/q_vs) dq_vs/dt (since q_v ≈ q_vs).

Now dq_v/dt = - dq_l/dt (condensation). And dq_vs/dt = dq_vs/dT * dT/dt.

For adiabatic ascent, dT/dt = w * dT/dz. dT/dz for dry adiabatic? But in cloud, it's moist adiabatic. However, for small liquid water content, we can approximate dT/dz ≈ -g/c_p (dry adiabatic) or use moist adiabatic? Usually, the production term uses the dry adiabatic lapse rate because the latent heat release is accounted for in the dq_l/dt term. Actually, the standard derivation (e.g., Politovich and Cooper, 1988; or Rogers and Yau) gives:

ds/dt = P w - C s

where P = (L_v/(R_v T^2) - 1/(e_s de_s/dT)) * (g/(c_p))? Let's find exact formulas.

From Rogers and Yau, Eq. (7.29):

ds/dt = (ξ w) - (γ dq_l/dt)

where ξ = (L_v/(R_v T^2)) (g/(c_p)) - g/(R_d T) ??? Wait, I recall:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) ? No.

Let's derive from first principles.

We have s = e/e_s - 1. e = ρ_v R_v T. e_s = saturation vapor pressure.

d e_s / dT = (L_v e_s) / (R_v T^2) (Clausius-Clapeyron).

For an adiabatic parcel, the first law: c_p dT - α dp = -L_v dq_v (if saturated). But for supersaturation, we consider the evolution of s.

Standard approach: The rate of change of s is:

ds/dt = (∂s/∂t)_adiabatic + (∂s/∂t)_condensation

The adiabatic production term is the rate of change of s if no condensation occurs (i.e., dq_l/dt = 0). So we set dq_l/dt = 0, then dq_v/dt = 0. Then s changes because T and p change.

s = e/e_s - 1. e = q_v p / ε (where ε = R_d/R_v). So e ∝ q_v p. If q_v is constant (no condensation), then e ∝ p. So:

ds/dt|_prod = (1/e_s) de/dt - (e/e_s^2) de_s/dt ≈ (1/e_s) de/dt - (1/e_s) de_s/dt (since e ≈ e_s).

de/dt = d/dt (q_v p / ε) = (q_v/ε) dp/dt = (e/p) dp/dt.

dp/dt = w dp/dz. dp/dz = -ρ g. So de/dt = -e ρ g w / p = -e g w / (R_d T) (since p = ρ R_d T).

de_s/dt = de_s/dT * dT/dt. dT/dt = w dT/dz. For dry adiabatic (no condensation), dT/dz = -g/c_p. So dT/dt = -w g/c_p.

de_s/dT = L_v e_s / (R_v T^2).

So ds/dt|_prod = (1/e_s)(-e g w/(R_d T)) - (1/e_s)(L_v e_s/(R_v T^2))(-w g/c_p) = - (g w)/(R_d T) + (L_v g w)/(R_v T^2 c_p).

Thus P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

This is the production term. Note: Some texts include a factor of (1 + s) but for small s it's this.

Now the condensation term: dq_l/dt is the rate of increase of liquid water mixing ratio. dq_l/dt = - dq_v/dt.

The change in s due to condensation: ds/dt|_cond = - γ dq_l/dt, where γ = (∂s/∂q_v) + (∂s/∂T) (dT/dq_v)? Actually, from the equation:

ds = (1/e_s) de - (e/e_s^2) de_s.

de = d(ρ_v R_v T) = R_v T dρ_v + ρ_v R_v dT. But it's easier to use mixing ratio.

q_v = ε e / p. So e = q_v p / ε.

Then s = (q_v p / ε) / e_s - 1.

Take logarithmic derivative: ds ≈ dq_v/q_v + dp/p - de_s/e_s.

But dp/p is related to dynamics. In the condensation term, we consider the change in s due to change in q_v (condensation) while the parcel rises. The standard formulation (e.g., Rogers and Yau Eq. 7.28) gives:

ds/dt = ξ w - γ dq_l/dt

where γ = (L_v/(c_p T) - 1) * (p/(ε e_s))? Let's check.

Actually, from Rogers and Yau (3rd ed., p. 110):

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) ? No, they have:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ? Let's look up memory.

I recall the formula for the production term P (often called the "supersaturation production rate"):

P = (L_v g)/(R_v T^2 c_p) - g/(R_d T)  (units: s^-1 per m/s? Actually P has units 1/m? Wait: ds/dt has units s^-1. w has units m/s. So P has units 1/m. Let's check: g/(R_d T) has units (m/s^2) / (J/kg K * K) = (m/s^2) / (m^2/s^2) = 1/m. Yes. So P is in m^-1. Then P w is in s^-1.

Now the condensation sink C. The rate of condensation dq_l/dt is related to s. For a droplet population, the total mass growth rate per unit volume is:

d(ρ_l)/dt = ∫ (dm/dt) n(r) dr, where dm/dt is the mass growth rate of a single droplet.

For a single droplet, dm/dt = 4π r ρ_l D_v (ρ_v - ρ_vs) / (r + Δ) ... but for cloud droplets, the growth is often approximated by:

dm/dt = 4π r D_v (ρ_v - ρ_vs)  (if ignoring ventilation and kinetic effects, and assuming steady-state diffusion). Actually, the exact equation is:

dm/dt = 4π r D_v (ρ_v - ρ_v_∞) / (1 + D_v/(α r) ...) but for typical cloud droplets > 1 μm, the simple equation dm/dt = 4π r D_v (ρ_v - ρ_vs) is a reasonable approximation. However, we also need to account for the heat conduction. The combined heat and mass transfer gives:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d)

where F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) and F_d = (ρ_l R_v T)/(D_v e_s). But for a steady-state supersaturation in a cloud, the curvature and solute terms are often neglected, so r dr/dt ≈ s / (F_k + F_d). Then dm/dt = 4π r^2 ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d).

Alternatively, the condensation sink C is often given by:

C = 4π D_v ∫ r n(r) dr * (ρ_l / ρ_vs)? Let's derive.

We have dq_l/dt = (1/ρ_air) d(ρ_l)/dt. ρ_l is liquid water density (mass of liquid per volume of air). d(ρ_l)/dt = ∫ (dm/dt) n(r) dr.

dm/dt = 4π r D_v (ρ_v - ρ_vs) = 4π r D_v ρ_vs s (since s = (ρ_v - ρ_vs)/ρ_vs).

So d(ρ_l)/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

Then dq_l/dt = (4π D_v ρ_vs s / ρ_air) ∫ r n(r) dr.

Now, the condensation term in ds/dt is -γ dq_l/dt. We need γ.

From the derivation, ds/dt|_cond = - (L_v/(c_p T) - 1) * (p/(ε e_s)) * dq_l/dt? Let's derive γ.

We have s = q_v/q_vs - 1. q_vs = ε e_s / p.

ds = dq_v/q_vs - q_v/q_vs^2 dq_vs ≈ dq_v/q_vs - dq_vs/q_vs.

d q_vs = d(ε e_s/p) = q_vs (de_s/e_s - dp/p).

In the condensation process, we consider the change in s due to change in q_v (d q_v = - d q_l) and the associated latent heat release which changes T and thus e_s. The pressure change is due to the updraft, which is already in the production term. So in the condensation term, we assume dp=0? Actually, the standard separation is: the production term includes the adiabatic changes (p, T) with no condensation; the condensation term includes the changes due to latent heat release and vapor depletion at constant pressure? Or is the pressure change included in both? Typically, the supersaturation equation is derived as:

ds/dt = Q_1 w - Q_2 dq_l/dt

where Q_1 = (L_v g)/(R_v T^2 c_p) - g/(R_d T) (as above)
and Q_2 = (L_v^2/(c_p R_v T^2) + ...) Actually, let's check Rogers and Yau.

In Rogers and Yau, Eq. (7.29):

ds/dt = ξ w - γ dq_l/dt

where ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * T? No, they have:

ξ = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ??? Let's compute units.

I found online a common formula: 
P = (L_v g)/(R_v T^2 c_p) - g/(R_d T)  (m^-1)
and C = 4π D_v N r_mean * (ρ_l / ρ_vs) * something? Wait.

Let's derive the condensation term carefully.

We have s = e/e_s - 1.
e = ρ_v R_v T.
e_s = saturation vapor pressure.

ds = de/e_s - e de_s/e_s^2 ≈ de/e_s - de_s/e_s.

de = R_v T dρ_v + ρ_v R_v dT = R_v T dρ_v + (e/T) dT.
de_s = (L_v e_s)/(R_v T^2) dT.

So ds = (R_v T/e_s) dρ_v + (e/(e_s T)) dT - (L_v/(R_v T^2)) dT.

Since e ≈ e_s, ds ≈ (R_v T/e_s) dρ_v + (1/T - L_v/(R_v T^2)) dT.

Now dρ_v = - dρ_l (condensation). dT comes from latent heat release: dT = (L_v/c_p) dq_l? Actually, for adiabatic process with condensation, the first law: c_p dT - dp/ρ = -L_v dq_v. If we isolate the condensation part, we consider the change in T due to latent heat release at constant pressure? Or we need to be consistent with the production term.

The standard approach (e.g., Cooper, 1989; Politovich and Cooper, 1988) gives the supersaturation equation as:

ds/dt = P w - C s

where P = (L_v/(R_v T^2) - 1/T) * (g/c_p) * (T) ??? Let's check units: P w must have units s^-1. P has units m^-1. w m/s -> s^-1. So P must be m^-1.

My derived P = (L_v g)/(R_v T^2 c_p) - g/(R_d T). Let's check units:
L_v: J/kg = m^2/s^2
g: m/s^2
R_v: J/kg K = m^2/s^2 K
T: K
c_p: J/kg K = m^2/s^2 K
So L_v g/(R_v T^2 c_p): (m^2/s^2 * m/s^2) / (m^2/s^2 K * K^2 * m^2/s^2 K) = (m^3/s^4) / (m^4/s^4 K^2) = 1/(m K^2)? That doesn't match. Let's re-evaluate.

L_v: J/kg = m^2/s^2
g: m/s^2
Product: m^3/s^4
R_v: J/(kg K) = m^2/(s^2 K)
T^2: K^2
c_p: J/(kg K) = m^2/(s^2 K)
Denominator: R_v T^2 c_p = (m^2/(s^2 K)) * K^2 * (m^2/(s^2 K)) = m^4/(s^4 K) * K? Wait: m^2/(s^2 K) * K^2 = m^2 K / s^2. Then times m^2/(s^2 K) = m^4/s^4. So L_v g/(R_v T^2 c_p) has units (m^3/s^4) / (m^4/s^4) = 1/m. Good.

Second term: g/(R_d T): g m/s^2, R_d J/(kg K) = m^2/(s^2 K), T K. So g/(R_d T) = (m/s^2) / (m^2/s^2) = 1/m. So P is in 1/m. Good.

Now for the condensation term: ds/dt|_cond = - C s. We need C in s^-1.

We have dρ_l/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

Now we need to relate ds/dt to dρ_l/dt. From ds = (R_v T/e_s) dρ_v + (1/T - L_v/(R_v T^2)) dT.

In the condensation process, dρ_v = - dρ_l. And dT is the temperature change due to latent heat release. If we consider the parcel rising, the total dT is from adiabatic expansion and latent heat. But we already accounted for adiabatic expansion in the production term. So in the condensation term, we should consider the temperature change due to latent heat release only, at constant pressure? Or is it included in the coefficient?

The standard coefficient γ in ds/dt = ... - γ dq_l/dt is derived by considering the change in s due to a change in q_l at constant total water and constant pressure? Let's check Rogers and Yau.

In Rogers and Yau, Eq. (7.28):

ds/dt = (L_v/(R_v T^2) - 1/T) * (g/c_p) * w - (L_v/(R_v T^2) - 1/T) * (L_v/c_p) * dq_l/dt - (1/q_v) dq_l/dt

Wait, that seems different. Let's derive from their approach.

They start with s = q_v/q_vs - 1.
d s/dt = (1/q_vs) dq_v/dt - (q_v/q_vs^2) dq_vs/dt ≈ (1/q_vs) dq_v/dt - (1/q_vs) dq_vs/dt.

Now dq_v/dt = - dq_l/dt (if no other sources).

dq_vs/dt = d/dt (ε e_s/p) = q_vs (1/e_s de_s/dt - 1/p dp/dt).

de_s/dt = (L_v e_s)/(R_v T^2) dT/dt.

dp/dt = -ρ g w.

dT/dt = - (g/c_p) w + (L_v/c_p) dq_l/dt (from first law: c_p dT/dt - (1/ρ) dp/dt = -L_v dq_v/dt = L_v dq_l/dt; and dp/dt = -ρ g w, so c_p dT/dt + g w = L_v dq_l/dt => dT/dt = -g w/c_p + (L_v/c_p) dq_l/dt).

Substitute:

ds/dt = - (1/q_vs) dq_l/dt - (1/q_vs) * q_vs [ (1/e_s) de_s/dt - (1/p) dp/dt ]
= - dq_l/dt / q_vs - (L_v/(R_v T^2)) dT/dt + (1/p) dp/dt.

Now plug dT/dt and dp/dt:

dp/dt = -ρ g w = - (p/(R_d T)) g w.

dT/dt = -g w/c_p + (L_v/c_p) dq_l/dt.

So:

ds/dt = - dq_l/dt / q_vs - (L_v/(R_v T^2)) (-g w/c_p + (L_v/c_p) dq_l/dt) + (1/p) (- (p/(R_d T)) g w)
= - dq_l/dt / q_vs + (L_v g w)/(R_v T^2 c_p) - (L_v^2/(R_v T^2 c_p)) dq_l/dt - (g w)/(R_d T).

Group terms with w and dq_l/dt:

ds/dt = [ (L_v g)/(R_v T^2 c_p) - g/(R_d T) ] w  - [ 1/q_vs + (L_v^2)/(R_v T^2 c_p) ] dq_l/dt.

So P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

And γ = 1/q_vs + L_v^2/(R_v T^2 c_p).

Now dq_l/dt is the rate of change of liquid water mixing ratio. dq_l/dt = (1/ρ_air) dρ_l/dt.

We have dρ_l/dt = 4π D_v ρ_vs s ∫ r n(r) dr.

But wait: Is the growth equation dm/dt = 4π r D_v (ρ_v - ρ_vs) accurate? It ignores the heat conduction effect on the droplet surface temperature. The full growth equation including heat conduction gives a modified coefficient. Usually, the growth equation is:

r dr/dt = (s - a/r + b/r^3) / (F_k + F_d)

where F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) and F_d = (ρ_l R_v T)/(D_v e_s). For typical conditions, F_k and F_d are often combined into a single factor. The mass growth rate is:

dm/dt = 4π r ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d) (ignoring curvature and solute).

So dm/dt = 4π r s / ( (F_k + F_d)/ρ_l )? Actually, dm/dt = 4π r ρ_l dr/dt = 4π r ρ_l s / (F_k + F_d).

Then dρ_l/dt = ∫ (dm/dt) n(r) dr = 4π ρ_l s / (F_k + F_d) ∫ r n(r) dr.

But note: F_k and F_d depend on T and p. They are:

F_d = (ρ_l R_v T) / (D_v e_s)
F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T)

where K is thermal conductivity of air, D_v is diffusivity of water vapor in air.

Often, the combined term is written as:

dm/dt = 4π r D_v (ρ_v - ρ_vs) / (1 + D_v/(α r) ...) but for cloud droplets > 1 μm, the simple diffusion equation with the psychrometric correction is used. Actually, the standard equation for condensational growth of a single droplet is:

dm/dt = 4π r (s) / ( (L_v^2/(K R_v T^2) + (R_v T)/(D_v e_s) ) )? Let's derive.

The growth equation from diffusion of vapor and heat conduction:

dm/dt = 4π r D_v (ρ_v_∞ - ρ_v_r) (vapor diffusion)
and heat conduction: L_v dm/dt = 4π r K (T_r - T_∞)

At the droplet surface, ρ_v_r = ρ_vs(T_r). For small s, we linearize:

ρ_v_r - ρ_vs(T_∞) ≈ ρ_vs(T_∞) * ( (L_v/(R_v T^2)) (T_r - T_∞) + s_∞? Actually, s_∞ = (ρ_v_∞ - ρ_vs(T_∞))/ρ_vs(T_∞).

Then we can solve for dm/dt:

dm/dt = 4π r ρ_vs(T_∞) s_∞ / ( (L_v^2/(K R_v T^2)) + (R_v T)/(D_v e_s) )? Wait, let's do it carefully.

Let ρ_v_∞ = ρ_vs (1 + s). At the droplet surface, ρ_v_r = ρ_vs(T_r). We approximate ρ_vs(T_r) ≈ ρ_vs(T_∞) + (dρ_vs/dT)(T_r - T_∞). dρ_vs/dT = (L_v/(R_v T^2) - 1/T) ρ_vs ≈ (L_v/(R_v T^2)) ρ_vs (since L_v/(R_v T^2) >> 1/T).

So ρ_v_r ≈ ρ_vs(T_∞) [1 + (L_v/(R_v T^2)) (T_r - T_∞)].

Vapor diffusion: dm/dt = 4π r D_v (ρ_v_∞ - ρ_v_r) = 4π r D_v ρ_vs [ s - (L_v/(R_v T^2)) (T_r - T_∞) ].

Heat conduction: L_v dm/dt = 4π r K (T_r - T_∞) => T_r - T_∞ = (L_v dm/dt) / (4π r K).

Substitute:

dm/dt = 4π r D_v ρ_vs [ s - (L_v/(R_v T^2)) * (L_v dm/dt) / (4π r K) ].

Solve for dm/dt:

dm/dt = 4π r D_v ρ_vs s - (L_v^2 D_v ρ_vs)/(R_v T^2 K) dm/dt.

dm/dt [1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)] = 4π r D_v ρ_vs s.

So dm/dt = 4π r D_v ρ_vs s / [1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)].

Note that ρ_vs = e_s/(R_v T). So:

dm/dt = 4π r D_v (e_s/(R_v T)) s / [1 + (L_v^2 D_v e_s)/(R_v^2 T^3 K)].

This is the standard equation. Often written as:

dm/dt = 4π r s / ( (R_v T)/(D_v e_s) + (L_v^2)/(K R_v T^2) )? Let's check:

From above: dm/dt = 4π r D_v ρ_vs s / (1 + (L_v^2 D_v ρ_vs)/(R_v T^2 K)).
Divide numerator and denominator by D_v ρ_vs:
dm/dt = 4π r s / (1/(D_v ρ_vs) + L_v^2/(R_v T^2 K)).
Now 1/(D_v ρ_vs) = (R_v T)/(D_v e_s).
So dm/dt = 4π r s / ( (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ).

This matches the F_k + F_d form if we multiply by ρ_l? Actually, earlier I had F_d = (ρ_l R_v T)/(D_v e_s) and F_k = (L_v/(R_v T) - 1) * (L_v ρ_l)/(K T) ≈ (L_v^2 ρ_l)/(K R_v T^2). Then F_k + F_d = ρ_l [ (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ]. Then dm/dt = 4π r ρ_l s / (F_k + F_d) = 4π r s / [ (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2) ]. Yes, consistent.

So the mass growth rate per droplet is dm/dt = 4π r s / G, where G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2).

Then dρ_l/dt = ∫ (dm/dt) n(r) dr = (4π s / G) ∫ r n(r) dr.

Now, the total number concentration N = ∫ n(r) dr, and the mean radius r_mean = (1/N) ∫ r n(r) dr. But we have a Gaussian spectrum, so we can compute ∫ r n(r) dr = N * r_mean. However, we are not given N directly. We are given cloud water content (LWC) = 0.2 g/m^3 = 0.2e-3 kg/m^3. LWC = ρ_l = (4/3)π ρ_w ∫ r^3 n(r) dr, where ρ_w is density of liquid water (≈ 1000 kg/m^3). For a Gaussian distribution, we can compute the moments.

Let n(r) = (N / (√(2π) σ)) exp(-(r - r0)^2/(2σ^2)). But we don't know N. However, we can relate LWC to N and the moments.

LWC = ρ_w * (4/3)π ∫ r^3 n(r) dr.

We need ∫ r n(r) dr for the condensation sink.

So we need to compute the ratio (∫ r n(r) dr) / LWC? Or we can find N from LWC and then compute ∫ r n(r) dr.

Given r0 = 4 μm, σ = 0.6 μm. We can compute the moments of a Gaussian. However, note that r is positive, but Gaussian extends to negative. For small σ/r0 = 0.15, the negative part is negligible. We can approximate the moments by integrating from 0 to ∞, or just use the Gaussian moments ignoring truncation.

For a Gaussian with mean μ and std σ, the moments:
E[r] = μ
E[r^2] = μ^2 + σ^2
E[r^3] = μ^3 + 3μσ^2
E[r^4] = μ^4 + 6μ^2σ^2 + 3σ^4
etc.

But we need ∫ r n(r) dr = N μ.
And LWC = ρ_w (4/3)π N E[r^3] = ρ_w (4/3)π N (μ^3 + 3μσ^2).

So we can solve for N:
N = LWC / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

Then ∫ r n(r) dr = N μ = LWC * μ / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

Thus the condensation sink term: dρ_l/dt = (4π s / G) * N μ.

Then dq_l/dt = (1/ρ_air) dρ_l/dt.

Now we need ρ_air, the density of air at T=273.15 K, p=80 kPa.

ρ_air = p / (R_d T) where R_d = 287.05 J/(kg K). (We'll use standard values.)

Now we have ds/dt = P w - γ dq_l/dt.

And dq_l/dt = (4π s / G) * (N μ) / ρ_air.

So ds/dt = P w - γ * (4π N μ / (ρ_air G)) s.

In steady state, ds/dt = 0, so s = (P w) / (γ * 4π N μ / (ρ_air G)).

Thus s = (P w ρ_air G) / (4π γ N μ).

We need to compute P, G, γ, N, μ, ρ_air.

Let's gather constants:

T = 273.15 K
p = 80000 Pa
w = 8 m/s
LWC = 0.2e-3 kg/m^3 (0.2 g/m^3)
μ = 4e-6 m
σ = 0.6e-6 m

Constants:
R_d = 287.0 J/(kg K) (dry air gas constant)
R_v = 461.5 J/(kg K) (water vapor gas constant)
c_p = 1005 J/(kg K) (specific heat of dry air at constant pressure)
L_v = 2.5e6 J/kg (latent heat of vaporization at 0°C? Actually L_v varies with T. At 0°C, L_v ≈ 2.5e6 J/kg. We'll use 2.5e6.)
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3 (density of liquid water)

We need e_s at 0°C. Saturation vapor pressure over water at 0°C: e_s = 611.2 Pa (approx). Or we can use the Clausius-Clapeyron equation or a standard formula. 611 Pa is standard. We'll use e_s = 611.2 Pa.

We need D_v: diffusivity of water vapor in air. At 0°C and 80 kPa? D_v depends on T and p. D_v ≈ 2.26e-5 m^2/s at 0°C and 100 kPa? Actually, D_v = 2.26e-5 * (T/273.15)^1.81 * (101325/p) m^2/s. We'll compute.

We need K: thermal conductivity of air. At 0°C, K ≈ 0.0243 W/(m K) at 100 kPa? Thermal conductivity of air is roughly independent of pressure. K ≈ 0.0243 W/(m K) at 0°C. We can use that.

Now compute step by step.

First, ρ_air = p / (R_d T) = 80000 / (287 * 273.15) = 80000 / 78394.05 ≈ 1.0205 kg/m^3.

e_s = 611.2 Pa.

D_v: standard value at 0°C, 101325 Pa is about 2.26e-5 m^2/s. Adjust for pressure: D_v ∝ 1/p. So D_v = 2.26e-5 * (101325 / 80000) = 2.26e-5 * 1.26656 = 2.862e-5 m^2/s. (Temperature is 0°C, so no T adjustment needed if we use 0°C reference.)

K: thermal conductivity of air at 0°C: K ≈ 0.0243 W/(m K). (It varies slightly with T but we'll use 0.0243.)

Now compute G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2).

First term: R_v T = 461.5 * 273.15 = 126,000? Let's compute: 461.5 * 273.15 = 461.5 * 273.15 = 126,000 (approx). Actually: 461.5 * 273.15 = 126,058.7.
D_v e_s = 2.862e-5 * 611.2 = 0.01749.
So (R_v T)/(D_v e_s) = 126058.7 / 0.01749 = 7,207,000 s/m^2? Units: (J/kg K * K) / (m^2/s * Pa) = (m^2/s^2) / (m^2/s^2 * m?) Wait: Pa = N/m^2 = kg/(m s^2). J/kg = m^2/s^2. So R_v T has units m^2/s^2. D_v e_s has units m^2/s * kg/(m s^2) = kg/(s^3)? Let's do carefully: D_v [m^2/s], e_s [Pa] = [kg/(m s^2)]. So D_v e_s [kg m/s^3]. R_v T [m^2/s^2]. So ratio has units (m^2/s^2) / (kg m/s^3) = m s / kg. This is not dimensionless. But G should have units such that dm/dt = 4π r s / G. dm/dt [kg/s]. 4π r [m], s dimensionless. So G must have units [m s / kg]? Actually, dm/dt = 4π r s / G => G = 4π r s / (dm/dt). dm/dt has units kg/s. r has m. So G has m / (kg/s) = m s / kg. Yes, that matches.

Second term: L_v^2/(K R_v T^2).
L_v = 2.5e6 J/kg = 2.5e6 m^2/s^2.
L_v^2 = 6.25e12 m^4/s^4.
K = 0.0243 W/(m K) = 0.0243 kg m/(s^3 K) [W = J/s = kg m^2/s^3, so W/(m K) = kg m/s^3 K].
R_v T^2 = 461.5 * (273.15)^2 = 461.5 * 74610 = 34,430,000? Let's compute: 273.15^2 = 74610.9. 461.5 * 74610.9 = 34,430,000 m^2/s^2 * K? R_v has J/(kg K) = m^2/(s^2 K). So R_v T^2 has m^2 K/s^2.
So L_v^2/(K R_v T^2) = (m^4/s^4) / ( (kg m/s^3 K) * (m^2 K/s^2) ) = (m^4/s^4) / (kg m^3/s^5) = m s / kg. Good.

Compute:
L_v^2 = 6.25e12.
K = 0.0243.
R_v T^2 = 461.5 * 74610.9 = 34,430,000 (approx). Let's do precisely:
461.5 * 273.15^2.
273.15^2 = 74610.9225.
461.5 * 74610.9225 = 34,432,000? 461.5 * 74610 = 34,432,515. Let's use 34,432,000.
So K R_v T^2 = 0.0243 * 34,432,000 = 836,700 (approx). 0.0243 * 34,432,000 = 836,697.6.
Then L_v^2/(K R_v T^2) = 6.25e12 / 8.366976e5 = 7,469,000? 6.25e12 / 8.37e5 = 7.47e6. Let's compute: 6.25e12 / 836,697.6 = 7,469,000. So about 7.47e6 m s/kg.

First term: (R_v T)/(D_v e_s) = 126,058.7 / (2.862e-5 * 611.2) = 126,058.7 / 0.01749 = 7,207,000. So both terms are similar magnitude. G = 7.207e6 + 7.469e6 = 1.4676e7 m s/kg.

Now compute P = (L_v g)/(R_v T^2 c_p) - g/(R_d T).

First part: L_v g = 2.5e6 * 9.81 = 24,525,000.
R_v T^2 c_p = 461.5 * 74610.9 * 1005 = 34,432,000 * 1005 = 34,604,160,000? Wait: 34,432,000 * 1005 = 34,604,160,000.
So (L_v g)/(R_v T^2 c_p) = 24,525,000 / 34,604,160,000 = 7.086e-4? Let's compute: 24.525e6 / 34.604e9 = 7.086e-4 1/m.

Second part: g/(R_d T) = 9.81 / (287 * 273.15) = 9.81 / 78394.05 = 1.251e-4 1/m.

So P = 7.086e-4 - 1.251e-4 = 5.835e-4 1/m.

Now compute γ = 1/q_vs + L_v^2/(R_v T^2 c_p).

First, q_vs = ε e_s / p, where ε = R_d/R_v = 287/461.5 = 0.6219.
e_s = 611.2 Pa, p = 80000 Pa.
q_vs = 0.6219 * 611.2 / 80000 = 0.6219 * 0.00764 = 0.00475 kg/kg? Let's compute: 611.2/80000 = 0.00764. 0.6219 * 0.00764 = 0.00475. So q_vs ≈ 0.00475 kg/kg.
1/q_vs = 1/0.00475 = 210.5.

Second term: L_v^2/(R_v T^2 c_p) = 6.25e12 / (34,432,000 * 1005) = 6.25e12 / 34,604,160,000 = 180.6? Wait: 6.25e12 / 3.4604e10 = 180.6. Let's compute: 34,604,160,000 = 3.4604e10. 6.25e12 / 3.4604e10 = 180.6. So γ = 210.5 + 180.6 = 391.1 (dimensionless).

Now compute N μ. We need N = LWC / [ ρ_w (4/3)π (μ^3 + 3μσ^2) ].

μ = 4e-6 m, σ = 0.6e-6 m.
μ^3 = (4e-6)^3 = 64e-18 = 6.4e-17 m^3.
3μσ^2 = 3 * 4e-6 * (0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18 m^3.
Sum = 6.4e-17 + 0.432e-17 = 6.832e-17 m^3.
ρ_w = 1000 kg/m^3.
(4/3)π = 4.18879.
Denom = 1000 * 4.18879 * 6.832e-17 = 4188.79 * 6.832e-17 = 2.862e-13 kg? Let's compute: 4188.79 * 6.832e-17 = 2.862e-13 kg per droplet? Actually, this is the mass per droplet times N? Wait: LWC = N * (4/3)π ρ_w E[r^3]. So N = LWC / [ (4/3)π ρ_w E[r^3] ].
LWC = 0.2e-3 kg/m^3 = 2e-4 kg/m^3.
N = 2e-4 / 2.862e-13 = 6.99e8 m^-3. About 700 per cm^3? 6.99e8 m^-3 = 699 cm^-3. That's reasonable for a cumulus cloud.

Then N μ = 6.99e8 * 4e-6 = 2796 m^{-2}? Units: N [m^-3], μ [m] -> N μ [m^-2]. 6.99e8 * 4e-6 = 2796 m^-2.

Now compute the denominator of s: 4π γ N μ / (ρ_air G).

4π = 12.566.
γ = 391.1.
N μ = 2796.
Product = 12.566 * 391.1 * 2796 = let's compute: 12.566 * 391.1 = 4915. 4915 * 2796 = 13,740,000? 4915 * 2796 = 4915*2800 - 4915*4 = 13,762,000 - 19,660 = 13,742,340.
ρ_air = 1.0205 kg/m^3.
G = 1.4676e7 m s/kg.
ρ_air G = 1.0205 * 1.4676e7 = 1.497e7 kg/m^3 * m s/kg = m s/m^3? Wait: ρ_air [kg/m^3], G [m s/kg] -> ρ_air G [s/m^2]. Actually: kg/m^3 * m s/kg = s/m^2. Yes.
So denominator = (4π γ N μ) / (ρ_air G) = 13,742,340 / 1.497e7 = 0.918 s^-1? Units: N μ [m^-2], γ dimensionless, so numerator has m^-2. Denominator has s/m^2. So ratio has s^-1. Good.

Now P w = 5.835e-4 1/m * 8 m/s = 4.668e-3 s^-1.

So s = (P w) / (denom) = 4.668e-3 / 0.918 = 0.005085. That's about 0.51% supersaturation.

But wait: Is this the correct formula? Let's double-check the derivation.

We had ds/dt = P w - γ dq_l/dt.
And dq_l/dt = (1/ρ_air) dρ_l/dt.
dρ_l/dt = (4π s / G) ∫ r n(r) dr = (4π s / G) N μ.
So dq_l/dt = (4π N μ / (ρ_air G)) s.
Then ds/dt = P w - γ (4π N μ / (ρ_air G)) s.
Steady state: s = (P w ρ_air G) / (4π γ N μ).

This matches my expression.

Now check if we missed any factor. In some formulations, the condensation sink includes the integral of r n(r) dr, but sometimes they use the mean radius of the surface area distribution? Actually, the integral of r n(r) dr is proportional to the total surface area? Total surface area = 4π ∫ r^2 n(r) dr. But here we have ∫ r n(r) dr. That comes from dm/dt ∝ r. So it's correct.

But wait: In the growth equation, dm/dt = 4π r D_v ρ_vs s / (1 + ...). We used G = (R_v T)/(D_v e_s) + L_v^2/(K R_v T^2). This is correct for the combined heat and mass transfer. However, sometimes the growth equation is written as:

dm/dt = 4π r s / (A + B) where A = (L_v^2)/(K R_v T^2) and B = (R_v T)/(D_v e_s). Yes.

Now check the values of constants. Are we using the correct L_v? At 0°C, L_v is about 2.5e6 J/kg. Some sources use 2.5e6, others 2.501e6. It's fine.

Check D_v: At 0°C and 1000 hPa, D_v ≈ 2.26e-5 m^2/s. At 800 hPa, D_v = 2.26e-5 * (1013/800) = 2.86e-5. Good.

Check K: At 0°C, K ≈ 0.0243 W/(m K). Good.

Check e_s: At 0°C, e_s = 611.2 Pa. Good.

Check ρ_air: p=80 kPa, T=273.15, R_d=287. ρ = 80000/(287*273.15) = 1.02 kg/m^3. Good.

Check moments: For Gaussian, E[r^3] = μ^3 + 3μσ^2. μ=4, σ=0.6. μ^3=64, 3μσ^2=3*4*0.36=4.32. Sum=68.32 μm^3. In m^3: 68.32e-18 = 6.832e-17. Good.

LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3 = 2e-4 kg/m^3.
N = 2e-4 / (1000 * 4.18879 * 6.832e-17) = 2e-4 / (2.862e-13) = 6.99e8 m^-3 = 699 cm^-3. Typical cumulus droplet concentrations are 100-500 cm^-3. 699 is a bit high but plausible for developing cumulus (maybe continental). With mean radius 4 μm, LWC 0.2 g/m^3, N = LWC / (ρ_w * 4/3 π r_vol^3). If we used mean volume radius r_vol = (E[r^3])^(1/3) = (68.32)^(1/3) ≈ 4.09 μm. Then N = 0.2e-3 / (1000 * 4/3 π (4.09e-6)^3) = 2e-4 / (1000 * 4.1888 * 68.4e-18) = same. So N ~ 700 cm^-3. Acceptable.

Now compute s = 0.005085 = 0.5085%. So about 0.51%.

But let's double-check the production term P. Some sources give P = (L_v g)/(c_p R_v T^2) - g/(R_d T). That's what I used. However, sometimes the production term is given as:

P = (dT/dz)_moist? No, for supersaturation, the production term is the rate of change of s due to adiabatic cooling if no condensation. That is what we derived.

Another common formula: s = (w * A) / (4π D_v N r_mean) where A is a function of T and p. Let's see if our formula reduces to that.

If we ignore the heat conduction term (G ≈ (R_v T)/(D_v e_s)), and ignore the γ term (γ ≈ 1/q_vs), then s ≈ (P w ρ_air (R_v T)/(D_v e_s)) / (4π (1/q_vs) N μ). Note ρ_air = p/(R_d T), q_vs = ε e_s/p. So 1/q_vs = p/(ε e_s). Then s ≈ P w * (p/(R_d T)) * (R_v T)/(D_v e_s) * (ε e_s/p) / (4π N μ) = P w * (R_v/R_d) * ε / (D_v 4π N μ) = P w * 1 / (D_v 4π N μ) since ε = R_d/R_v. So s ≈ P w / (4π D_v N μ). And P = (L_v g)/(c_p R_v T^2) - g/(R_d T). This is a common simplified formula. Our full formula includes the heat conduction and the γ correction.

Now, is the steady-state assumption valid? The problem says "estimate the supersaturation in an updraft of 8 m/s". It likely expects the quasi-steady supersaturation in a cloud with given droplet spectrum. So our approach is standard.

Let's recompute with more precise constants to ensure accuracy.

Constants:
R_d = 287.058 J/(kg K) (often 287)
R_v = 461.5 J/(kg K)
c_p = 1005 J/(kg K) (for dry air, sometimes 1004)
L_v = 2.501e6 J/kg at 0°C? Actually, latent heat of vaporization varies: at 0°C it's 2.501e6, at 100°C it's 2.26e6. We'll use 2.5e6.
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3

T = 273.15 K
p = 80000 Pa
w = 8 m/s
LWC = 0.2 g/m^3 = 0.0002 kg/m^3
μ = 4e-6 m
σ = 0.6e-6 m

e_s at 0°C: 611.2 Pa (some use 611.0). We'll use 611.2.
D_v at 0°C, 101325 Pa: 2.26e-5 m^2/s. Adjust to 80000 Pa: D_v = 2.26e-5 * (101325/80000) = 2.26e-5 * 1.2665625 = 2.8624e-5 m^2/s.
K at 0°C: 0.0243 W/(m K). (Some sources: 0.0240 at 0°C? Let's check: Thermal conductivity of air at 0°C is about 0.0243 W/mK. At -10°C it's 0.0236, at 10°C 0.0250. So 0.0243 is fine.)

Now compute step by step with high precision.

1. ρ_air = p / (R_d * T) = 80000 / (287.058 * 273.15) = 80000 / 78409.5 = 1.0203 kg/m^3.

2. e_s = 611.2 Pa.

3. q_vs = (R_d/R_v) * e_s / p = (287.058/461.5) * 611.2 / 80000 = 0.62198 * 0.00764 = 0.004752.

4. P = (L_v * g) / (R_v * T^2 * c_p) - g / (R_d * T)
   L_v * g = 2.5e6 * 9.81 = 24,525,000.
   R_v * T^2 = 461.5 * (273.15^2) = 461.5 * 74610.9225 = 34,432,000 (approx). Let's compute exactly: 273.15^2 = 74610.9225. 461.5 * 74610.9225 = 34,432,000? 461.5 * 74610 = 34,432,515. 461.5 * 0.9225 = 425.7. So 34,432,940.7.
   c_p = 1005.
   R_v * T^2 * c_p = 34,432,940.7 * 1005 = 34,605,105,403.
   First term = 24,525,000 / 34,605,105,403 = 7.087e-4.
   Second term = 9.81 / (287.058 * 273.15) = 9.81 / 78409.5 = 1.251e-4.
   P = 7.087e-4 - 1.251e-4 = 5.836e-4 m^-1.

5. G = (R_v * T) / (D_v * e_s) + L_v^2 / (K * R_v * T^2)
   R_v * T = 461.5 * 273.15 = 126,058.7.
   D_v * e_s = 2.8624e-5 * 611.2 = 0.017495.
   First term = 126058.7 / 0.017495 = 7,205,000.
   L_v^2 = 6.25e12.
   K * R_v * T^2 = 0.0243 * 34,432,940.7 = 836,720.
   Second term = 6.25e12 / 836720 = 7,469,000.
   G = 7,205,000 + 7,469,000 = 14,674,000 m s/kg.

6. γ = 1/q_vs + L_v^2 / (R_v * T^2 * c_p)
   1/q_vs = 1/0.004752 = 210.44.
   L_v^2 / (R_v * T^2 * c_p) = 6.25e12 / 34,605,105,403 = 180.6.
   γ = 210.44 + 180.6 = 391.04.

7. Compute E[r^3] = μ^3 + 3μσ^2.
   μ = 4e-6, σ = 0.6e-6.
   μ^3 = 64e-18 = 6.4e-17.
   3μσ^2 = 3 * 4e-6 * (0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18.
   Sum = 6.832e-17 m^3.

8. N = LWC / (ρ_w * (4/3)π * E[r^3])
   LWC = 0.0002 kg/m^3.
   ρ_w = 1000.
   (4/3)π = 4.1887902.
   Denom = 1000 * 4.1887902 * 6.832e-17 = 4188.79 * 6.832e-17 = 2.8618e-13.
   N = 2e-4 / 2.8618e-13 = 6.988e8 m^-3.

9. N * μ = 6.988e8 * 4e-6 = 2795.2 m^-2.

10. Denominator of s: C_sink = (4π * γ * N * μ) / (ρ_air *

## Error when it was executed
Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need 

Return the COMPLETE corrected solve(): a dict keyed "1".."N" in the order asked, each
{"value": <number>, "unit": "<unit>"}, standard library only. Put all arithmetic in the function; give the corrected solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
We need to fix the bug in the provided code. The user says: "Your solve() function failed to run. Fix the bug and return the corrected function." The provided code is not a complete Python function; it's a long comment/derivation that ends abruptly. The error message shows: "Runtime error in solve(): ... We need". So the code they tried to run was not a valid Python function. They likely pasted the whole derivation as code, which is not executable. We need to write a proper solve() function that computes the supersaturation and returns the answer as a percentage.

The problem: "In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of 0.6 μm. Given that the cloud water content is 0.2 g/m^3, estimate the supersaturation in an updraft of 8 m/s. Assume a temperature of 0°C and a pressure of 80 kPa. Express your answer as a percentage."

We need to return a dict with keys "1" (since only one answer) with value and unit "%". The format: {"1": {"value": <number>, "unit": "%"}}.

We need to implement the calculation correctly. Based on the derivation above, we got s ≈ 0.005085 = 0.5085%. Let's double-check the calculation and ensure it's correct. We'll write a Python function that computes it using standard constants.

We'll use the steady-state supersaturation formula:

s = (P * w * ρ_air * G) / (4π * γ * N * μ)

where:
P = (L_v * g) / (R_v * T^2 * c_p) - g / (R_d * T)
G = (R_v * T) / (D_v * e_s) + L_v^2 / (K * R_v * T^2)
γ = 1/q_vs + L_v^2 / (R_v * T^2 * c_p)
q_vs = ε * e_s / p, ε = R_d / R_v
N = LWC / (ρ_w * (4/3)π * (μ^3 + 3μσ^2))
μ = 4e-6 m, σ = 0.6e-6 m
LWC = 0.2 g/m^3 = 0.0002 kg/m^3
ρ_air = p / (R_d * T)
D_v = D_v0 * (p0 / p) * (T / T0)^1.81? At 0°C, T = T0, so just pressure correction: D_v = 2.26e-5 * (101325 / p)
K = 0.0243 W/(m K) (approx at 0°C)
e_s = 611.2 Pa at 0°C
L_v = 2.5e6 J/kg (or 2.501e6)
c_p = 1005 J/(kg K)
R_d = 287.058 J/(kg K)
R_v = 461.5 J/(kg K)
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3

We'll compute s and express as percentage: s * 100.

Let's recalc with precise numbers to ensure no off-by-one errors.

I'll write a Python function that does all arithmetic and returns the result. We'll include all constants.

But wait: The derivation used the steady-state assumption ds/dt=0. Is that what the problem expects? The problem says "estimate the supersaturation in an updraft of 8 m/s". In a developing cumulus cloud, the supersaturation is often near a quasi-steady value. So this is standard.

Let's double-check the formula for s. Some textbooks give:

s = (w * A) / (4π * D_v * N * r_mean) where A = (L_v * g)/(c_p * R_v * T^2) - g/(R_d * T). That's the simplified version ignoring heat conduction and γ correction. Our full version includes those. The simplified version would give:

s_simple = P * w / (4π * D_v * N * μ)  (since γ ≈ 1/q_vs and ρ_air G ≈ ρ_air * (R_v T)/(D_v e_s) = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * (p/(D_v e_s)) = (1/ε) * (p/(D_v e_s)). Then 1/q_vs = p/(ε e_s). So γ * (ρ_air G) ≈ (p/(ε e_s)) * (1/ε) * (p/(D_v e_s))? That seems off. Let's re-derive the simplified version.

From earlier: s = (P w ρ_air G) / (4π γ N μ). If we ignore the heat conduction term in G (i.e., G ≈ (R_v T)/(D_v e_s)) and ignore the L_v^2 term in γ (i.e., γ ≈ 1/q_vs), then:

ρ_air G = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * p/(D_v e_s) = (1/ε) * p/(D_v e_s).
γ = 1/q_vs = p/(ε e_s).
So γ * (ρ_air G) = (p/(ε e_s)) * (1/ε) * p/(D_v e_s) = p^2/(ε^2 e_s^2 D_v). That doesn't simplify to 1/(D_v). Wait, my earlier simplification was wrong. Let's redo:

s = (P w ρ_air G) / (4π γ N μ). Substitute ρ_air G and γ:

ρ_air G = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * (p/(D_v e_s)).
γ = 1/q_vs = p/(ε e_s) = p/((R_d/R_v) e_s) = (R_v p)/(R_d e_s).
So γ = (R_v/R_d) * (p/e_s).
Then γ * (ρ_air G) = (R_v/R_d) * (p/e_s) * (R_v/R_d) * (p/(D_v e_s)) = (R_v/R_d)^2 * p^2/(D_v e_s^2).
Then s = P w / (4π N μ) * (ρ_air G / γ) = P w / (4π N μ) * [ (R_v/R_d) * p/(D_v e_s) ] / [ (R_v/R_d) * p/e_s ] = P w / (4π N μ) * (1/D_v). Yes! Because (ρ_air G)/γ = [ (R_v/R_d) * p/(D_v e_s) ] / [ (R_v/R_d) * p/e_s ] = 1/D_v. So s_simple = P w / (4π D_v N μ). That matches the common simplified formula. Good.

So our full formula includes the heat conduction and the L_v^2 term in γ. The simplified formula gives s = P w / (4π D_v N μ). Let's compute that to compare.

P = 5.836e-4 m^-1, w=8 m/s => P w = 4.6688e-3 s^-1.
D_v = 2.8624e-5 m^2/s.
N μ = 2795.2 m^-2.
4π D_v N μ = 12.566 * 2.8624e-5 * 2795.2 = 12.566 * 0.0800? Let's compute: 2.8624e-5 * 2795.2 = 0.0800. 12.566 * 0.0800 = 1.005. So s_simple = 4.6688e-3 / 1.005 = 0.004645 = 0.4645%. Our full formula gave 0.5085%. So the full formula gives slightly higher s because the heat conduction and γ correction increase the sink? Actually, the full formula gave s = 0.5085%, which is larger than 0.4645%. Let's check the denominator in full: we had denominator = (4π γ N μ)/(ρ_air G) = 0.918 s^-1. P w = 0.0046688 s^-1. s = 0.0046688/0.918 = 0.005085. In simplified, denominator = 4π D_v N μ = 1.005 s^-1? Wait, 4π D_v N μ = 4π * D_v
~~~~

**attempt 2** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
Your solve() function failed to run. Fix the bug and return the corrected function.

## Problem
In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of O.6 μm. Given that the cloud water content is $0 . 2 \mathrm { g } / \mathrm { \dot { m } } ^ { 3 }$ ,estimate the supersaturationinanupdraft of8m/s.Assume a temperature of $0 ^ { \circ } \bar { C }$ and a pressure of 80 kPa.

Express your answer as a percentage.

## Your code
We need to fix the bug in the provided code. The user says: "Your solve() function failed to run. Fix the bug and return the corrected function." The provided code is not a complete Python function; it's a long comment/derivation that ends abruptly. The error message shows: "Runtime error in solve(): ... We need". So the code they tried to run was not a valid Python function. They likely pasted the whole derivation as code, which is not executable. We need to write a proper solve() function that computes the supersaturation and returns the answer as a percentage.

The problem: "In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of 0.6 μm. Given that the cloud water content is 0.2 g/m^3, estimate the supersaturation in an updraft of 8 m/s. Assume a temperature of 0°C and a pressure of 80 kPa. Express your answer as a percentage."

We need to return a dict with keys "1" (since only one answer) with value and unit "%". The format: {"1": {"value": <number>, "unit": "%"}}.

We need to implement the calculation correctly. Based on the derivation above, we got s ≈ 0.005085 = 0.5085%. Let's double-check the calculation and ensure it's correct. We'll write a Python function that computes it using standard constants.

We'll use the steady-state supersaturation formula:

s = (P * w * ρ_air * G) / (4π * γ * N * μ)

where:
P = (L_v * g) / (R_v * T^2 * c_p) - g / (R_d * T)
G = (R_v * T) / (D_v * e_s) + L_v^2 / (K * R_v * T^2)
γ = 1/q_vs + L_v^2 / (R_v * T^2 * c_p)
q_vs = ε * e_s / p, ε = R_d / R_v
N = LWC / (ρ_w * (4/3)π * (μ^3 + 3μσ^2))
μ = 4e-6 m, σ = 0.6e-6 m
LWC = 0.2 g/m^3 = 0.0002 kg/m^3
ρ_air = p / (R_d * T)
D_v = D_v0 * (p0 / p) * (T / T0)^1.81? At 0°C, T = T0, so just pressure correction: D_v = 2.26e-5 * (101325 / p)
K = 0.0243 W/(m K) (approx at 0°C)
e_s = 611.2 Pa at 0°C
L_v = 2.5e6 J/kg (or 2.501e6)
c_p = 1005 J/(kg K)
R_d = 287.058 J/(kg K)
R_v = 461.5 J/(kg K)
g = 9.81 m/s^2
ρ_w = 1000 kg/m^3

We'll compute s and express as percentage: s * 100.

Let's recalc with precise numbers to ensure no off-by-one errors.

I'll write a Python function that does all arithmetic and returns the result. We'll include all constants.

But wait: The derivation used the steady-state assumption ds/dt=0. Is that what the problem expects? The problem says "estimate the supersaturation in an updraft of 8 m/s". In a developing cumulus cloud, the supersaturation is often near a quasi-steady value. So this is standard.

Let's double-check the formula for s. Some textbooks give:

s = (w * A) / (4π * D_v * N * r_mean) where A = (L_v * g)/(c_p * R_v * T^2) - g/(R_d * T). That's the simplified version ignoring heat conduction and γ correction. Our full version includes those. The simplified version would give:

s_simple = P * w / (4π * D_v * N * μ)  (since γ ≈ 1/q_vs and ρ_air G ≈ ρ_air * (R_v T)/(D_v e_s) = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * (p/(D_v e_s)) = (1/ε) * (p/(D_v e_s)). Then 1/q_vs = p/(ε e_s). So γ * (ρ_air G) ≈ (p/(ε e_s)) * (1/ε) * (p/(D_v e_s))? That seems off. Let's re-derive the simplified version.

From earlier: s = (P w ρ_air G) / (4π γ N μ). If we ignore the heat conduction term in G (i.e., G ≈ (R_v T)/(D_v e_s)) and ignore the L_v^2 term in γ (i.e., γ ≈ 1/q_vs), then:

ρ_air G = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * p/(D_v e_s) = (1/ε) * p/(D_v e_s).
γ = 1/q_vs = p/(ε e_s).
So γ * (ρ_air G) = (p/(ε e_s)) * (1/ε) * p/(D_v e_s) = p^2/(ε^2 e_s^2 D_v). That doesn't simplify to 1/(D_v). Wait, my earlier simplification was wrong. Let's redo:

s = (P w ρ_air G) / (4π γ N μ). Substitute ρ_air G and γ:

ρ_air G = (p/(R_d T)) * (R_v T)/(D_v e_s) = (p R_v)/(R_d D_v e_s) = (R_v/R_d) * (p/(D_v e_s)).
γ = 1/q_vs = p/(ε e_s) = p/((R_d/R_v) e_s) = (R_v p)/(R_d e_s).
So γ = (R_v/R_d) * (p/e_s).
Then γ * (ρ_air G) = (R_v/R_d) * (p/e_s) * (R_v/R_d) * (p/(D_v e_s)) = (R_v/R_d)^2 * p^2/(D_v e_s^2).
Then s = P w / (4π N μ) * (ρ_air G / γ) = P w / (4π N μ) * [ (R_v/R_d) * p/(D_v e_s) ] / [ (R_v/R_d) * p/e_s ] = P w / (4π N μ) * (1/D_v). Yes! Because (ρ_air G)/γ = [ (R_v/R_d) * p/(D_v e_s) ] / [ (R_v/R_d) * p/e_s ] = 1/D_v. So s_simple = P w / (4π D_v N μ). That matches the common simplified formula. Good.

So our full formula includes the heat conduction and the L_v^2 term in γ. The simplified formula gives s = P w / (4π D_v N μ). Let's compute that to compare.

P = 5.836e-4 m^-1, w=8 m/s => P w = 4.6688e-3 s^-1.
D_v = 2.8624e-5 m^2/s.
N μ = 2795.2 m^-2.
4π D_v N μ = 12.566 * 2.8624e-5 * 2795.2 = 12.566 * 0.0800? Let's compute: 2.8624e-5 * 2795.2 = 0.0800. 12.566 * 0.0800 = 1.005. So s_simple = 4.6688e-3 / 1.005 = 0.004645 = 0.4645%. Our full formula gave 0.5085%. So the full formula gives slightly higher s because the heat conduction and γ correction increase the sink? Actually, the full formula gave s = 0.5085%, which is larger than 0.4645%. Let's check the denominator in full: we had denominator = (4π γ N μ)/(ρ_air G) = 0.918 s^-1. P w = 0.0046688 s^-1. s = 0.0046688/0.918 = 0.005085. In simplified, denominator = 4π D_v N μ = 1.005 s^-1? Wait, 4π D_v N μ = 4π * D_v

## Error when it was executed
Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need 

Return the COMPLETE corrected solve(): a dict keyed "1".."N" in the order asked, each
{"value": <number>, "unit": "<unit>"}, standard library only. Put all arithmetic in the function; give the corrected solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Constants
    R_d = 287.058          # J/(kg K)
    R_v = 461.5            # J/(kg K)
    epsilon = R_d / R_v    # 0.622
    g = 9.81               # m/s^2
    L_v = 2.5e6            # J/kg
    c_p = 1005.0           # J/(kg K)
    T = 273.15             # K (0°C)
    p = 80e3               # Pa
    e_s = 611.2            # Pa at 0°C
    D_v0 = 2.26e-5         # m^2/s at 101325 Pa, 0°C
    D_v = D_v0 * (101325.0 / p)  # pressure correction, T same
    K = 0.0243             # W/(m K) thermal conductivity of air at 0°C
    rho_w = 1000.0         # kg/m^3

    # Cloud parameters
    mu = 4e-6              # m
    sigma = 0.6e-6         # m
    LWC = 0.2e-3           # kg/m^3 (0.2 g/m^3)
    w = 8.0                # m/s

    # Number concentration N from LWC and Gaussian moments
    # E[r^3] = mu^3 + 3*mu*sigma^2
    Er3 = mu**3 + 3 * mu * sigma**2
    mean_volume = (4.0/3.0) * math.pi * Er3
    N = LWC / (rho_w * mean_volume)

    # P term
    P = (L_v * g) / (R_v * T**2 * c_p) - g / (R_d * T)

    # G term
    G = (R_v * T) / (D_v * e_s) + L_v**2 / (K * R_v * T**2)

    # gamma term
    q_vs = epsilon * e_s / p
    gamma = 1.0 / q_vs + L_v**2 / (R_v * T**2 * c_p)

    # air density
    rho_air = p / (R_d * T)

    # Supersaturation s (dimensionless)
    numerator = P * w * rho_air * G
    denominator = 4.0 * math.pi * gamma * N * mu
    s = numerator / denominator

    # Convert to percentage
    s_percent = s * 100.0

    return {"1": {"value": s_percent, "unit": "%"}}
```
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run2.json` → `ry_7.7` · `num_attempts` = 3 · 3 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `0.4978926694332834` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1
    We need `

RESPONSE (verbatim, untruncated):

~~~~
We need to solve an atmospheric science problem: estimate supersaturation in an updraft of 8 m/s given a droplet spectrum with Gaussian shape, mean radius 4 μm, standard deviation 0.6 μm, cloud water content 0.2 g/m^3, temperature 0°C, pressure 80 kPa. Express answer as a percentage.

We need to recall the physics: supersaturation in a cloud updraft is determined by the balance between the production of supersaturation by adiabatic cooling (updraft) and the depletion by condensation onto droplets. The quasi-steady supersaturation s can be estimated from the equation:

ds/dt = a1 * w - a2 * s * (integral of droplet surface area or something)

Typically, the supersaturation equation: 
ds/dt = (ξ) w - (something) s, where ξ = (L_v g)/(c_p R_v T^2) - (g)/(R_d T) ... Actually, the standard formula for supersaturation tendency in an updraft without condensation is:
ds/dt ≈ (L_v/(R_v T^2) - 1/(R_d T)) * (g w)/(c_p) ? Wait, need to recall.

In cloud physics, the rate of change of supersaturation s = (e - e_s)/e_s ≈ q_v - q_vs (with some factors). The production term due to adiabatic cooling is often given by:
P = a w, where a ≈ (L_v g)/(c_p R_v T^2) - (g)/(R_d T) or something. For typical atmospheric conditions, a ~ 10^-4 m^-1? Actually, typical value is about 1.5e-4 m^-1 at 0°C? Let's derive.

The supersaturation s = e/e_s - 1. For small s, s ≈ ln(e/e_s). The rate of change of s following a parcel:
ds/dt = (1/e_s) de/dt - (e/e_s^2) de_s/dt ≈ (1/e_s) de/dt - (1/e_s) de_s/dt (since e≈e_s).

From Clausius-Clapeyron: de_s/dT = L_v e_s / (R_v T^2).
Also, for adiabatic ascent, dT/dz = -g/c_p (dry adiabatic) or moist adiabatic, but for condensation we consider dry adiabatic cooling initially. The pressure change also affects e. The parcel's vapor pressure e = q_v p / ε, where ε = R_d/R_v ≈ 0.622. For constant q_v (no condensation), de/dt = (q_v/ε) dp/dt. dp/dt = -ρ g w. Also dT/dt = - (g/c_p) w.

Then ds/dt = (1/e_s) de/dt - (1/e_s) de_s/dT dT/dt.
de/dt = (q_v/ε) dp/dt = (q_v/ε) (-ρ g w). But q_v/ε = e/p. So de/dt = (e/p) (-ρ g w) = -e (ρ g w)/p.
Using ideal gas law: p = ρ R_d T_v ≈ ρ R_d T. So ρ/p = 1/(R_d T). Thus de/dt = -e g w / (R_d T).

dT/dt = -g w / c_p.
de_s/dt = de_s/dT * dT/dt = (L_v e_s/(R_v T^2)) * (-g w / c_p).

So ds/dt = (1/e_s)(-e g w/(R_d T)) - (1/e_s)(L_v e_s/(R_v T^2))(-g w/c_p) = - (e/e_s) g w/(R_d T) + (L_v g w)/(c_p R_v T^2).

Since e/e_s ≈ 1, ds/dt ≈ g w [ L_v/(c_p R_v T^2) - 1/(R_d T) ].

This is the production term. Let's call it α w. α = g [ L_v/(c_p R_v T^2) - 1/(R_d T) ].

At T = 0°C = 273.15 K. L_v = 2.5e6 J/kg? Actually latent heat of vaporization at 0°C is about 2.5e6 J/kg. c_p = 1005 J/(kg K). R_v = 461.5 J/(kg K). R_d = 287 J/(kg K). g = 9.81 m/s^2.

Compute α:
Term1 = L_v/(c_p R_v T^2) = 2.5e6 / (1005 * 461.5 * 273.15^2)
Term2 = 1/(R_d T) = 1/(287 * 273.15)

Let's calculate:
T = 273.15
T^2 = 74610.9
c_p R_v T^2 = 1005 * 461.5 * 74610.9 ≈ 1005 * 461.5 = 463,807.5; *74610.9 ≈ 3.46e10? Let's do more precisely:
461.5 * 1005 = 463,807.5
463807.5 * 74610.9 = 3.460e10? Actually 463807.5 * 74610.9 = 34,600,000,000? Let's compute: 4.638e5 * 7.461e4 = 3.46e10. So Term1 = 2.5e6 / 3.46e10 = 7.225e-5.
Term2 = 1/(287*273.15) = 1/78400 = 1.275e-5.
Difference = 7.225e-5 - 1.275e-5 = 5.95e-5.
Multiply by g=9.81: α = 9.81 * 5.95e-5 = 5.84e-4 m^{-1}? Wait, units: ds/dt has units s^{-1}. w in m/s, so α in m^{-1}. 5.84e-4 m^{-1} is typical? Actually typical value is around 1.5e-4 m^{-1}? Let's check: I recall α ≈ 10^-4 m^{-1}. Maybe my L_v is too high? At 0°C, L_v = 2.5e6 J/kg. c_p = 1005. R_v = 461.5. T=273.15. Let's compute exactly:
Term1 = 2.5e6 / (1005 * 461.5 * 273.15^2)
1005 * 461.5 = 463807.5
273.15^2 = 74610.9225
463807.5 * 74610.9225 = 34,607,000,000? 4.638e5 * 7.461e4 = 3.46e10. 2.5e6 / 3.46e10 = 7.22e-5.
Term2 = 1/(287 * 273.15) = 1/78394.05 = 1.2756e-5.
Difference = 5.95e-5.
Times 9.81 = 5.84e-4. That seems high. Maybe I'm missing a factor? Actually, the supersaturation equation often is written as ds/dt = a1 w - a2 s, where a1 ~ 1.5e-4 m^{-1} at 0°C? Let's check standard values: In Rogers and Yau, "A Short Course in Cloud Physics", the coefficient for supersaturation production is about 1.5e-4 m^{-1} at 10°C? Let's recalc with more accurate constants:
L_v at 0°C is 2.501e6 J/kg. c_p = 1005 J/kgK. R_v = 461.5 J/kgK. R_d = 287.0 J/kgK. T = 273.15 K.
Term1 = L_v/(c_p R_v T^2) = 2.501e6/(1005*461.5*273.15^2) = 2.501e6/(1005*461.5*74610.9) = 2.501e6/(3.46e10) = 7.23e-5.
Term2 = 1/(R_d T) = 1/(287*273.15) = 1/78394 = 1.276e-5.
Difference = 5.95e-5. Times g=9.81 = 5.84e-4. But I recall the formula is often: a1 = (g/(R_d T)) * ( (L_v R_d)/(c_p R_v T) - 1 )? Let's derive differently.
Another common expression: ds/dt = (1/(1+s)) [ (L_v/(c_p T)) (g w)/(R_d T) - (g w)/(R_d T) ]? No.
Let's check standard derivation: 
dθ/dt = 0 for dry adiabatic, but with condensation it's different. The supersaturation s = q_v/q_{vs} - 1. 
dq_v/dt = -C, where C is condensation rate.
dq_{vs}/dt = d(ε e_s/p)/dt = ε/p de_s/dt - ε e_s/p^2 dp/dt.
de_s/dt = (L_v e_s)/(R_v T^2) dT/dt.
dT/dt = -g w/c_p + L_v/c_p C.
dp/dt = -ρ g w.
For steady state, dq_v/dt ≈ dq_{vs}/dt? Actually, the quasi-steady supersaturation is obtained by setting ds/dt = 0, where s = q_v/q_{vs} - 1.
ds/dt = (1/q_{vs}) dq_v/dt - (q_v/q_{vs}^2) dq_{vs}/dt ≈ (1/q_{vs}) dq_v/dt - (1/q_{vs}) dq_{vs}/dt (since q_v ≈ q_{vs}).
dT/dt = -g w/c_p + L_v/c_p C.
dp/dt = -ρ g w.
d q_{vs}/dt = d(ε e_s/p)/dt = ε/p de_s/dt - ε e_s/p^2 dp/dt = q_{vs} (1/e_s de_s/dt - 1/p dp/dt).
1/e_s de_s/dt = L_v/(R_v T^2) dT/dt.
1/p dp/dt = -ρ g w / p = -g w/(R_d T) (using p=ρ R_d T).
So dq_{vs}/dt = q_{vs} [ L_v/(R_v T^2) dT/dt + g w/(R_d T) ].
dT/dt = -g w/c_p + L_v/c_p C.
So dq_{vs}/dt = q_{vs} [ L_v/(R_v T^2) (-g w/c_p + L_v/c_p C) + g w/(R_d T) ].
dq_v/dt = -C.
Then ds/dt = -C/q_{vs} - [ L_v/(R_v T^2) (-g w/c_p + L_v/c_p C) + g w/(R_d T) ].
Set ds/dt = 0 for steady state:
0 = -C/q_{vs} + L_v/(R_v T^2) g w/c_p - L_v^2/(R_v T^2 c_p) C - g w/(R_d T).
C [ 1/q_{vs} + L_v^2/(c_p R_v T^2) ] = g w [ L_v/(c_p R_v T^2) - 1/(R_d T) ].
C = q_{vs} g w [ L_v/(c_p R_v T^2) - 1/(R_d T) ] / [ 1 + q_{vs} L_v^2/(c_p R_v T^2) ].
The denominator is often close to 1. So C ≈ q_{vs} α w, where α = g [ L_v/(c_p R_v T^2) - 1/(R_d T) ].
But the supersaturation s is related to C via the droplet growth equation.
For a single droplet, dm/dt = 4π r ρ_l D_v (ρ_{vs} - ρ_v) or something. In terms of radius, dr/dt = (S - 1) / (r F_k + F_d) where S = e/e_s = 1+s. For small s, dr/dt ≈ s / (r F_k + F_d). The condensation rate C = (4π ρ_l N) ∫ r^2 dr/dt n(r) dr? Actually, C = dq_l/dt = (4π ρ_l)/ρ_a ∫ r^2 (dr/dt) n(r) dr, where n(r) is number density per unit mass? Usually, C = (4π ρ_l)/ρ_a ∫ r^2 (dr/dt) n(r) dr, where n(r) is number per volume? Let's be careful.

The water vapor mixing ratio q_v decreases by condensation: dq_v/dt = -C, where C is the condensation rate (mass of water condensed per unit mass of air per unit time). The liquid water mixing ratio q_l increases: dq_l/dt = C.
The droplet growth equation: r dr/dt = (S-1) / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ]? Actually, the standard form:
dr/dt = (S-1) / [ r (F_k + F_d) ]? Wait, the equation is:
r dr/dt = (S-1) / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ].
Let's define G = [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ]^{-1}. Then r dr/dt = G (S-1) ≈ G s.
So dr/dt = G s / r.
Then the rate of change of liquid water mixing ratio q_l = (4/3 π ρ_l ∫ r^3 n(r) dr) / ρ_a? Actually, q_l = (ρ_l/ρ_a) * (4/3 π ∫ r^3 n(r) dr) where n(r) is number density per volume of air. So dq_l/dt = (ρ_l/ρ_a) * 4π ∫ r^2 (dr/dt) n(r) dr.
Substitute dr/dt: dq_l/dt = (ρ_l/ρ_a) * 4π ∫ r^2 (G s / r) n(r) dr = (ρ_l/ρ_a) * 4π G s ∫ r n(r) dr.
So C = (4π ρ_l G / ρ_a) s ∫ r n(r) dr.
But ∫ r n(r) dr = N * r_mean? Actually, the total droplet number concentration N = ∫ n(r) dr. The mean radius is r_mean = (1/N) ∫ r n(r) dr. So ∫ r n(r) dr = N r_mean.
Thus C = (4π ρ_l G / ρ_a) s N r_mean.
Equate this to the steady-state C from the supersaturation equation:
C = q_{vs} α w / (1 + q_{vs} L_v^2/(c_p R_v T^2)) ≈ q_{vs} α w (since denominator ~1).
So s = [ q_{vs} α w ρ_a ] / [ 4π ρ_l G N r_mean ].
But we are given cloud water content (liquid water content) LWC = 0.2 g/m^3. LWC = ρ_l * (4/3 π ∫ r^3 n(r) dr) = ρ_l * (4/3 π) * N * <r^3>.
For a Gaussian distribution, we can compute <r> and <r^3> from mean and standard deviation.
Given: mean radius r0 = 4 μm, standard deviation σ = 0.6 μm. The distribution is Gaussian: n(r) = (N / (σ sqrt(2π))) exp(-(r - r0)^2/(2σ^2)). But note: Gaussian distribution extends to negative radii, which is unphysical, but we assume it's narrow enough that it's okay. We need <r> and <r^3>.
For a Gaussian, the mean is r0. So <r> = r0 = 4 μm.
The third moment <r^3> = ∫ r^3 n(r) dr / N. For a Gaussian, we can compute: r = r0 + x, where x ~ N(0, σ^2). Then r^3 = (r0 + x)^3 = r0^3 + 3 r0^2 x + 3 r0 x^2 + x^3. Expectation: <r^3> = r0^3 + 3 r0 <x^2> + <x^3>. Since Gaussian is symmetric, <x^3>=0. <x^2> = σ^2. So <r^3> = r0^3 + 3 r0 σ^2.
Thus LWC = ρ_l * (4/3 π) * N * (r0^3 + 3 r0 σ^2).
We can solve for N: N = LWC / [ ρ_l * (4/3 π) * (r0^3 + 3 r0 σ^2) ].
Then ∫ r n(r) dr = N r0.
So C = (4π ρ_l G / ρ_a) s N r0.
We also need q_{vs} and ρ_a.
Given T = 0°C = 273.15 K, p = 80 kPa = 80000 Pa.
Saturation vapor pressure over water at 0°C: e_s = 611.2 Pa? Actually, at 0°C, e_s = 6.112 hPa = 611.2 Pa. (Standard value: 6.11 hPa at 0°C). More precisely, 611.15 Pa. We'll use 611.2 Pa.
Then saturation mixing ratio q_{vs} = ε e_s / (p - e_s) ≈ ε e_s / p, since e_s << p. ε = R_d/R_v = 287/461.5 = 0.622.
q_{vs} = 0.622 * 611.2 / 80000 = 0.622 * 0.00764 = 0.00475 kg/kg? Actually 611.2/80000 = 0.00764. 0.622 * 0.00764 = 0.00475. So q_{vs} ≈ 4.75 g/kg.
Air density ρ_a = p / (R_d T) = 80000 / (287 * 273.15) = 80000 / 78394 = 1.0205 kg/m^3.
LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3? Wait: 0.2 g/m^3 = 0.2 * 10^-3 kg/m^3 = 2e-4 kg/m^3.
ρ_l = 1000 kg/m^3.
Compute <r^3>: r0 = 4 μm = 4e-6 m, σ = 0.6 μm = 0.6e-6 m.
r0^3 = (4e-6)^3 = 64e-18 = 6.4e-17 m^3.
3 r0 σ^2 = 3 * 4e-6 * (0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18 m^3.
Sum = 6.4e-17 + 0.432e-17 = 6.832e-17 m^3.
Then N = LWC / [ ρ_l * (4/3 π) * <r^3> ] = 2e-4 / [ 1000 * (4/3 * π) * 6.832e-17 ].
4/3 π ≈ 4.18879.
Denom = 1000 * 4.18879 * 6.832e-17 = 4188.79 * 6.832e-17 = 2.862e-13? Let's compute: 4188.79 * 6.832e-17 = 2.862e-13.
N = 2e-4 / 2.862e-13 = 6.99e8 m^{-3}? That's about 700 per cm^3, which is reasonable for cumulus clouds.
Now we need G. G = [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ]^{-1}.
We need thermal conductivity K and diffusivity D_v.
At 0°C and 80 kPa, we need values for K and D_v.
K for air: thermal conductivity of air at 0°C is about 0.0243 W/(m K)? Actually, K ≈ 2.43e-2 W m^{-1} K^{-1}. Let's check: at 0°C, K = 0.0243 W/(m K). At 80 kPa, K is roughly independent of pressure for ideal gases? Thermal conductivity of gases is independent of pressure over a wide range. So K ≈ 0.0243.
D_v: diffusivity of water vapor in air. At 0°C and 1 atm, D_v ≈ 2.26e-5 m^2/s? Actually, D_v at 0°C is about 2.2e-5 m^2/s. It varies with pressure and temperature: D_v ∝ T^{1.94} / p. At standard pressure 101325 Pa, D_v ≈ 2.26e-5 m^2/s at 0°C? Let's use a known formula: D_v = 2.11e-5 * (T/273.15)^{1.94} * (101325/p) m^2/s. At T=273.15, p=80000, D_v = 2.11e-5 * 1 * (101325/80000) = 2.11e-5 * 1.26656 = 2.67e-5 m^2/s. Alternatively, some sources give D_v = 2.26e-5 at 0°C and 1 atm. Let's use 2.26e-5 * (101325/80000) = 2.26e-5 * 1.26656 = 2.86e-5. I'll use a standard value: D_v = 2.36e-5 m^2/s at 0°C and 1 atm? Actually, I recall D_v ≈ 2.5e-5 at 0°C? Let's check: In Rogers and Yau, D_v = 0.226 cm^2/s at 0°C and 1000 hPa? 0.226 cm^2/s = 2.26e-5 m^2/s. So at 80 kPa, D_v = 2.26e-5 * (1013.25/800) = 2.26e-5 * 1.2666 = 2.86e-5 m^2/s. We'll use that.
K: thermal conductivity of air at 0°C: 2.43e-2 W/(m K). It is independent of pressure.
L_v = 2.5e6 J/kg (or 2.501e6). ρ_l = 1000 kg/m^3. R_v = 461.5 J/(kg K). T = 273.15 K. e_s = 611.2 Pa.
Compute the two terms in G:
Term A = L_v^2 ρ_l / (K R_v T^2) = (2.5e6)^2 * 1000 / (0.0243 * 461.5 * 273.15^2)
Term B = ρ_l R_v T / (D_v e_s) = 1000 * 461.5 * 273.15 / (D_v * 611.2)
Compute Term A:
L_v^2 = 6.25e12.
ρ_l = 1000 => 6.25e15.
Denom: K = 0.0243, R_v = 461.5, T^2 = 74610.9. Product = 0.0243 * 461.5 * 74610.9 = 0.0243 * 34,430,000? 461.5*74610.9 = 34,430,000. 0.0243 * 34,430,000 = 836,649. So Term A = 6.25e15 / 8.36649e5 = 7.47e9? Wait: 6.25e15 / 8.37e5 = 7.47e9. Units: (J^2/kg^2 * kg/m^3) / (W/(m K) * J/(kg K) * K^2) = (J^2/m^3) / (J/(m s K) * J/(kg K) * K^2?) Let's not worry.
Term B:
ρ_l R_v T = 1000 * 461.5 * 273.15 = 1000 * 126,000 = 1.26e8? Actually: 461.5 * 273.15 = 126,058. 1000 * 126,058 = 1.26058e8.
D_v = 2.86e-5 m^2/s. e_s = 611.2 Pa.
Denom = 2.86e-5 * 611.2 = 0.01748. Term B = 1.26058e8 / 0.01748 = 7.21e9.
So Term A ≈ 7.47e9, Term B ≈ 7.21e9. Sum = 1.468e10. G = 1 / Sum = 6.81e-11.
Units of G: m^2/s? Actually, G has units of m^2/s? From r dr/dt = G s, so G is m^2/s. Yes.

Now compute α = g [ L_v/(c_p R_v T^2) - 1/(R_d T) ].
c_p = 1005 J/(kg K). R_d = 287 J/(kg K).
Term1 = L_v/(c_p R_v T^2) = 2.5e6 / (1005 * 461.5 * 74610.9) = 2.5e6 / (1005 * 34,430,000) = 2.5e6 / 3.46e10 = 7.225e-5.
Term2 = 1/(R_d T) = 1/(287 * 273.15) = 1/78394 = 1.2756e-5.
Difference = 5.949e-5.
α = 9.81 * 5.949e-5 = 5.836e-4 m^{-1}.
w = 8 m/s.
q_{vs} = 0.622 * e_s / p = 0.622 * 611.2 / 80000 = 0.00475.
ρ_a = p/(R_d T) = 80000/(287*273.15) = 1.0205 kg/m^3.
N r0 = N * 4e-6. N = 6.99e8 m^{-3}. So N r0 = 6.99e8 * 4e-6 = 2796 m^{-2}? Actually, units: m^{-3} * m = m^{-2}. So ∫ r n(r) dr = 2796 m^{-2}.
Now C = q_{vs} α w (ignoring denominator, which is 1 + q_{vs} L_v^2/(c_p R_v T^2). Let's check denominator: q_{vs} L_v^2/(c_p R_v T^2) = 0.00475 * (6.25e12)/(1005*461.5*74610.9) = 0.00475 * (6.25e12/3.46e10) = 0.00475 * 180.6 = 0.858. So denominator = 1.858. That's not negligible! We must include it.
So C = q_{vs} α w / (1 + q_{vs} L_v^2/(c_p R_v T^2)).
Compute denominator: 1 + 0.00475 * (2.5e6)^2 / (1005 * 461.5 * 273.15^2).
We already computed L_v^2/(c_p R_v T^2) = (2.5e6)^2 / (1005*461.5*74610.9) = 6.25e12 / 3.46e10 = 180.6. Then q_{vs} * 180.6 = 0.00475 * 180.6 = 0.85785. So denominator = 1.85785.
Thus C = q_{vs} α w / 1.85785.
q_{vs} α w = 0.00475 * 5.836e-4 * 8 = 0.00475 * 0.0046688 = 2.218e-5 s^{-1}.
C = 2.218e-5 / 1.85785 = 1.194e-5 s^{-1}.
Now equate C to condensation rate from droplets:
C = (4π ρ_l G / ρ_a) s N r0.
So s = C ρ_a / (4π ρ_l G N r0).
Compute numerator: C ρ_a = 1.194e-5 * 1.0205 = 1.218e-5.
Denominator: 4π ρ_l G N r0 = 4π * 1000 * 6.81e-11 * 2796.
4π = 12.566.
1000 * 6.81e-11 = 6.81e-8.
12.566 * 6.81e-8 = 8.56e-7.
Times 2796 = 8.56e-7 * 2796 = 0.002394.
So s = 1.218e-5 / 0.002394 = 0.00509.
Supersaturation s is about 0.00509, which is 0.509%.
But we need to express as a percentage. So answer ≈ 0.51%.
Let's double-check all numbers and assumptions.

We need to be careful with the droplet growth equation. The standard equation for droplet growth by condensation is:
r dr/dt = (S - 1) / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ].
This is for a single droplet. The condensation rate per unit mass of air is:
C = dq_l/dt = (ρ_l/ρ_a) d/dt (4/3 π ∫ r^3 n(r) dr) = (ρ_l/ρ_a) 4π ∫ r^2 (dr/dt) n(r) dr.
Substitute dr/dt = G (S-1)/r, where G = 1 / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ].
Then C = (ρ_l/ρ_a) 4π G (S-1) ∫ r n(r) dr.
So C = (4π ρ_l G / ρ_a) s ∫ r n(r) dr, with s = S-1.
We have ∫ r n(r) dr = N <r> = N r0.
So C = (4π ρ_l G / ρ_a) s N r0.
We also have the supersaturation tendency equation:
ds/dt = α w - β C, where β = (1/q_{vs} + L_v^2/(c_p R_v T^2))? Actually, from earlier derivation:
ds/dt = -C/q_{vs} + L_v/(R_v T^2) g w/c_p - L_v^2/(c_p R_v T^2) C - g w/(R_d T).
= g w (L_v/(c_p R_v T^2) - 1/(R_d T)) - C (1/q_{vs} + L_v^2/(c_p R_v T^2)).
So ds/dt = α w - β C, with α = g (L_v/(c_p R_v T^2) - 1/(R_d T)), β = 1/q_{vs} + L_v^2/(c_p R_v T^2).
Set ds/dt = 0 for steady state: C = (α/β) w.
Then s = (α w / β) * ρ_a / (4π ρ_l G N r0).
We computed α = 5.836e-4 m^{-1}. β = 1/0.00475 + 180.6 = 210.5 + 180.6 = 391.1? Wait: 1/q_{vs} = 1/0.00475 = 210.5. L_v^2/(c_p R_v T^2) = 180.6. So β = 391.1 s? Units: 1/q_{vs} is dimensionless? Actually, q_{vs} is kg/kg, so 1/q_{vs} is dimensionless. L_v^2/(c_p R_v T^2) has units: (J^2/kg^2) / (J/(kg K) * J/(kg K) * K^2) = dimensionless. So β is dimensionless. Then C = (α/β) w has units m^{-1} * m/s = s^{-1}. That matches.
Earlier I had C = q_{vs} α w / (1 + q_{vs} L_v^2/(c_p R_v T^2)). Let's check: α/β = α / (1/q_{vs} + L_v^2/(c_p R_v T^2)) = α q_{vs} / (1 + q_{vs} L_v^2/(c_p R_v T^2)). Yes, that's exactly what I had. So C = q_{vs} α w / (1 + q_{vs} L_v^2/(c_p R_v T^2)). I computed denominator = 1.85785. So C = 0.00475 * 5.836e-4 * 8 / 1.85785 = 2.218e-5 / 1.85785 = 1.194e-5 s^{-1}. That matches.
Now compute s = C ρ_a / (4π ρ_l G N r0).
We need G, N, r0, ρ_a.
Let's recompute everything with high precision and consistent units.

Constants:
T = 273.15 K
p = 80000 Pa
e_s = 611.15 Pa (I'll use 611.15, but 611.2 is fine. Let's use 611.15 for accuracy? Actually, saturation vapor pressure at 0°C is exactly 6.112 hPa? I think it's 6.112 hPa = 611.2 Pa. We'll use 611.2.)
L_v = 2.5e6 J/kg (or 2.501e6? Let's use 2.5e6 as typical.)
c_p = 1005 J/(kg K)
R_d = 287.0 J/(kg K)
R_v = 461.5 J/(kg K)
g = 9.81 m/s^2
ρ_l = 1000 kg/m^3
K = 0.0243 W/(m K) (thermal conductivity of air at 0°C)
D_v at 0°C and 1 atm = 2.26e-5 m^2/s. At p=80 kPa, D_v = 2.26e-5 * (101325/80000) = 2.26e-5 * 1.2665625 = 2.862e-5 m^2/s.
w = 8 m/s
LWC = 0.2 g/m^3 = 0.2e-3 kg/m^3 = 2e-4 kg/m^3.
r0 = 4 μm = 4e-6 m
σ = 0.6 μm = 0.6e-6 m

Compute q_{vs}:
ε = R_d/R_v = 287/461.5 = 0.6219.
q_{vs} = ε * e_s / (p - e_s) ≈ ε * e_s / p = 0.6219 * 611.2 / 80000 = 0.6219 * 0.00764 = 0.004751. Let's do exactly: 611.2/80000 = 0.00764. 0.6219*0.00764 = 0.0047513.
ρ_a = p/(R_d T) = 80000/(287*273.15) = 80000/78394.05 = 1.0205 kg/m^3.

Compute α:
Term1 = L_v/(c_p R_v T^2) = 2.5e6 / (1005 * 461.5 * 273.15^2)
273.15^2 = 74610.9225
c_p R_v T^2 = 1005 * 461.5 * 74610.9225 = 1005 * 34,432,000? 461.5 * 74610.9225 = 34,432,000 (approx). Let's compute: 461.5 * 74610.9225 = 34,432,000. 1005 * 34,432,000 = 3.4604e10.
Term1 = 2.5e6 / 3.4604e10 = 7.2246e-5.
Term2 = 1/(R_d T) = 1/(287 * 273.15) = 1/78394.05 = 1.2756e-5.
α = 9.81 * (7.2246e-5 - 1.2756e-5) = 9.81 * 5.949e-5 = 5.836e-4.

Compute denominator for C:
L_v^2/(c_p R_v T^2) = (2.5e6)^2 / 3.4604e10 = 6.25e12 / 3.4604e10 = 180.6.
q_{vs} * 180.6 = 0.0047513 * 180.6 = 0.8581.
Denom = 1.8581.
C = q_{vs} * α * w / Denom = 0.0047513 * 5.836e-4 * 8 / 1.8581 = 0.0047513 * 0.0046688 / 1.8581 = 2.218e-5 / 1.8581 = 1.1937e-5 s^{-1}.

Compute G:
Term A = L_v^2 ρ_l / (K R_v T^2) = (6.25e12 * 1000) / (0.0243 * 461.5 * 74610.9225) = 6.25e15 / (0.0243 * 34,432,000) = 6.25e15 / 836,700 = 7.469e9.
Term B = ρ_l R_v T / (D_v e_s) = (1000 * 461.5 * 273.15) / (2.862e-5 * 611.2) = (126,058,000) / (0.01749) = 7.207e9? Let's compute: 1000 * 461.5 = 461,500. 461,500 * 273.15 = 126,058,725. D_v * e_s = 2.862e-5 * 611.2 = 1.749e-2? 2.862e-5 * 611.2 = 0.01749. 126,058,725 / 0.01749 = 7.207e9.
Sum = 7.469e9 + 7.207e9 = 1.4676e10.
G = 1 / 1.4676e10 = 6.814e-11 m^2/s.

Compute N:
<r^3> = r0^3 + 3 r0 σ^2.
r0 = 4e-6, r0^3 = 64e-18 = 6.4e-17.
σ = 0.6e-6, σ^2 = 0.36e-12 = 3.6e-13.
3 r0 σ^2 = 3 * 4e-6 * 3.6e-13 = 12e-6 * 3.6e-13 = 4.32e-18.
Sum = 6.4e-17 + 0.432e-17 = 6.832e-17 m^3.
LWC = 2e-4 kg/m^3.
ρ_l = 1000 kg/m^3.
Volume fraction = LWC/ρ_l = 2e-7.
Total droplet volume per m^3 = N * (4/3 π <r^3>) = LWC/ρ_l = 2e-7 m^3/m^3.
So N = (2e-7) / (4/3 π * 6.832e-17) = 2e-7 / (4.18879 * 6.832e-17) = 2e-7 / (2.862e-16) = 6.99e8 m^{-3}.
N r0 = 6.99e8 * 4e-6 = 2796 m^{-2}.

Now compute s:
s = C * ρ_a / (4π ρ_l G N r0) = 1.1937e-5 * 1.0205 / (4π * 1000 * 6.814e-11 * 2796)
Numerator = 1.218e-5.
Denom = 12.566 * 1000 * 6.814e-11 * 2796 = 12.566 * 6.814e-8 * 2796 = 12.566 * 1.905e-4? Let's compute step by step:
1000 * 6.814e-11 = 6.814e-8.
4π = 12.56637.
12.56637 * 6.814e-8 = 8.563e-7.
8.563e-7 * 2796 = 0.002394.
s = 1.218e-5 / 0.002394 = 0.005088.
As percentage: 0.5088% ≈ 0.51%.

But wait: Is the Gaussian distribution for droplet spectrum given in terms of radius or diameter? "centered at a mean radius of 4 μm" so it's radius. Standard deviation 0.6 μm. So our calculation is correct.

We should check if there are any other factors. Sometimes the droplet growth equation includes ventilation effects, but for small droplets (<20 μm) ventilation is negligible. Also, the curvature and solute effects are neglected for supersaturation estimate? Usually, in a developing cumulus cloud, the droplets are large enough that curvature effect is small, but we might need to consider it? The problem says "estimate the supersaturation", likely using the standard quasi-steady supersaturation in cloud with given droplet spectrum. The Gaussian spectrum is used to compute the integral of r n(r) dr and the total liquid water content to get N. That seems correct.

Let's double-check the formula for G. Some texts use:
G = [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ]^{-1}.
Yes, that's standard (e.g., Rogers and Yau, 3rd ed., Eq. 7.17). The units: L_v^2 ρ_l/(K R_v T^2) has units (J^2/kg^2 * kg/m^3) / (J/(s m K) * J/(kg K) * K^2) = (J^2/m^3) / (J^2/(s m kg))? Let's do: K has W/(m K) = J/(s m K). R_v has J/(kg K). T^2 has K^2. So K R_v T^2 has J/(s m K) * J/(kg K) * K^2 = J^2/(s m kg). L_v^2 ρ_l has J^2/m^3. So ratio = (J^2/m^3) / (J^2/(s m kg)) = s kg / m^2? Not m^2/s? Wait, G should have units of m^2/s because r dr/dt = G s, and r dr/dt has m^2/s. Let's check: ρ_l R_v T/(D_v e_s): ρ_l kg/m^3, R_v J/(kg K) = m^2/(s^2 K), T K, so numerator = kg/m^3 * m^2/s^2 = kg/(m s^2). D_v m^2/s, e_s Pa = kg/(m s^2). So denominator = m^2/s * kg/(m s^2) = kg m / s^3. Then ratio = (kg/(m s^2)) / (kg m / s^3) = s/m^2? That's inverse. Actually, G is the inverse of that sum. So G has units of m^2/s? Let's recompute: Term A: L_v^2 ρ_l/(K R_v T^2). L_v J/kg, ρ_l kg/m^3, K J/(s m K), R_v J/(kg K), T^2 K^2. Numerator: (J^2/kg^2) * (kg/m^3) = J^2/(kg m^3). Denominator: (J/(s m K)) * (J/(kg K)) * K^2 = J^2/(s m kg). So Term A = (J^2/(kg m^3)) / (J^2/(s m kg)) = s/m^2. Term B: ρ_l R_v T/(D_v e_s). ρ_l kg/m^3, R_v J/(kg K) = m^2/(s^2 K), T K => numerator = kg/m^3 * m^2/s^2 = kg/(m s^2). D_v m^2/s, e_s Pa = kg/(m s^2) => denominator = m^2/s * kg/(m s^2) = kg m / s^3. Ratio = (kg/(m s^2)) / (kg m / s^3) = s/m^2. So both terms have units s/m^2. Their sum has units s/m^2. G = 1/sum has units m^2/s. Yes, correct.

Now, is there any factor of 4π or something in the condensation rate integral? C = dq_l/dt = (ρ_l/ρ_a) d/dt (∫ 4/3 π r^3 n(r) dr) = (ρ_l/ρ_a) ∫ 4π r^2 dr/dt n(r) dr. dr/dt = G s / r. So C = (ρ_l/ρ_a) 4π G s ∫ r n(r) dr. That's what we used.

Now, the supersaturation equation: ds/dt = α w - β C. We derived β = 1/q_{vs} + L_v^2/(c_p R_v T^2). Let's verify this from standard sources. In Rogers and Yau, the equation for supersaturation is often written as:
ds/dt = a1 w - a2 dq_l/dt
where a1 = (L_v g)/(c_p R_v T^2) - g/(R_d T) (this is α)
a2 = (1/q_{vs} + L_v^2/(c_p R_v T^2)) (this is β)
Yes, that's correct. So steady state: dq_l/dt = (a1/a2) w.
Then s = (a1/a2) w ρ_a / (4π ρ_l G ∫ r n(r) dr).
We have all.

Now, check if we need to include the curvature effect (Kelvin effect) and solute effect. The problem says "estimate the supersaturation", and typically in a developing cumulus cloud, the droplets are large enough that the equilibrium supersaturation is small, but we might need to account for the mean radius? Actually, the growth equation we used is for a flat surface (no curvature). For droplets, the equilibrium vapor pressure is e_r = e_s exp(2σ/(ρ_l R_v T r)) ≈ e_s (1 + a/r), where a = 2σ/(ρ_l R_v T). σ is surface tension of water, about 0.075 N/m at 0°C. a ≈ 2*0.075/(1000*461.5*273.15) = 0.15 / 126,000,000 = 1.19e-9 m = 0.0012 μm. For r=4 μm, a/r = 0.0003, so Kelvin effect is very small (supersaturation of 0.03%). The solute effect might lower it, but typically for cloud droplets, the equilibrium supersaturation is negligible compared to the dynamical supersaturation we computed (~0.5%). So it's fine to neglect.

But wait: The problem might expect the use of the "supersaturation in an updraft" formula that directly uses the liquid water content and the mean radius. There is a known approximation: s ≈ (w / N r_mean) * something. Let's see if our result is reasonable. Typical supersaturations in cumulus clouds are on the order of 0.1-1%. Our 0.51% is reasonable.

Let's double-check the values of K and D_v. Sometimes K is taken as 2.5e-2 W/(m K). D_v at 0°C and 1 atm is 2.26e-5. At 80 kPa, D_v = 2.26e-5 * (1013.25/800) = 2.86e-5. That's fine.
What about the latent heat? L_v at 0°C is 2.501e6 J/kg. We used 2.5e6. Small difference.
c_p = 1005 J/(kg K). R_d = 287. R_v = 461.5.
e_s at 0°C: 6.112 hPa = 611.2 Pa. Some use 611.15. Fine.
ρ_a = p/(R_d T) = 80000/(287*273.15) = 1.0205.
q_{vs} = 0.622 * 611.2 / (80000 - 611.2) = 0.622 * 611.2 / 79388.8 = 0.00478? Let's compute exactly: 611.2 / 79388.8 = 0.007698. 0.622 * 0.007698 = 0.004788. Using p - e_s instead of p changes q_{vs} slightly. Let's use exact: q_{vs} = ε e_s / (p - e_s) = 0.6219 * 611.2 / (80000 - 611.2) = 0.6219 * 611.2 / 79388.8 = 380.1 / 79388.8 = 0.004788. Previously I had 0.00475. That's a 0.8% difference. Let's recompute with exact q_{vs}.

p = 80000 Pa, e_s = 611.2 Pa.
p - e_s = 79388.8 Pa.
ε = 287/461.5 = 0.621885.
q_{vs} = 0.621885 * 611.2 / 79388.8 = 380.0 / 79388.8 = 0.004786.
ρ_a = p/(R_d T) = 80000/(287*273.15) = 1.0205. (Using p, not p-e_s, because dry air density? Actually, ρ_a is density of moist air, but we can approximate with dry air density. The difference is small.)
Now recompute α and β.
α = g (L_v/(c_p R_v T^2) - 1/(R_d T)).
L_v = 2.5e6.
c_p = 1005.
R_v = 461.5.
T = 273.15.
T^2 = 74610.9225.
L_v/(c_p R_v T^2) = 2.5e6 / (1005 * 461.5 * 74610.9225) = 2.5e6 / 3.4604e10 = 7.2246e-5.
1/(R_d T) = 1/(287*273.15) = 1/78394.05 = 1.2756e-5.
Difference = 5.949e-5.
α = 9.81 * 5.949e-5 = 5.836e-4.
L_v^2/(c_p R_v T^2) = (2.5e6)^2 / 3.4604e10 = 6.25e12 / 3.4604e10 = 180.6.
β = 1/q_{vs} + 180.6 = 1/0.004786 + 180.6 = 208.9 + 180.6 = 389.5.
C = (α/β) w = (5.836e-4 / 389.5) * 8 = (1.498e-6) * 8 = 1.198e-5 s^{-1}. (Previously 1.194e-5, very close).
Now G: Term A = L_v^2 ρ_l/(K R_v T^2) = 6.25e15 / (0.0243 * 461.5 * 74610.9225) = 6.25e15 / 836,700 = 7.469e9.
Term B = ρ_l R_v T/(D_v e_s). D_v = 2.26e-5 * (101325/80000) = 2.26e-5 * 1.2665625 = 2.862e-5. e_s = 611.2. D_v e_s = 2.862e-5 * 611.2 = 0.01749. ρ_l R_v T = 1000 * 461.5 * 273.15 = 126,058,725. Term B = 1.2606e8 / 0.01749 = 7.207e9.
Sum = 1.4676e10. G = 6.814e-11.
N: <r^3> = r0^3 + 3 r0 σ^2 = 6.4e-17 + 4.32e-18 = 6.832e-17.
LWC = 0.2 g/m^3 = 2e-4 kg/m^3.
N = (2e-4 / 1000) / (4/3 π * 6.832e-17) = 2e-7 / (2.862e-16) = 6.99e8.
N r0 = 6.99e8 * 4e-6 = 2796.
s = C ρ_a / (4π ρ_l G N r0) = 1.198e-5 * 1.0205 / (12.566 * 1000 * 6.814e-11 * 2796) = 1.222e-5 / 0.002394 = 0.00510.
Percentage = 0.51%.

Now, are there any other factors? Sometimes the droplet growth equation includes a factor of (1 + s) or something, but for small s it's negligible. Also, the density of air ρ_a in the condensation rate equation: C = (1/ρ_a) dq_l/dt? Wait, we defined C = dq_l/dt, where q_l is mixing ratio (kg/kg). The equation for q_l is: q_l = (ρ_l/ρ_a) * (4/3 π ∫ r^3 n(r) dr), where n(r) is number per volume of air. So dq_l/dt = (ρ_l/ρ_a) * 4π ∫ r^2 dr/dt n(r) dr. That's what we used. So C is per unit mass of air. The supersaturation equation ds/dt = α w - β C uses C in same units. So that's consistent.

Now, check if the problem expects the answer as a percentage with how many decimal places? "Express your answer as a percentage." Probably one or two decimal places. 0.51% seems fine.

But let's verify the standard deviation: "O.6 μm" is probably "0.6 μm" (the letter O instead of 0). So σ = 0.6 μm.

Let's also check if the Gaussian is in radius or diameter. "centered at a mean radius of 4 μm" so it's radius.

Now, could there be a simpler formula? Sometimes the steady-state supersaturation is given by:
s ≈ (w / (2π N r_mean G)) * (something). But we did the full derivation.

Let's double-check the integral of r n(r) dr for a Gaussian. The mean radius is r0, so ∫ r n(r) dr = N r0. That's correct. The third moment we used for LWC to get N. LWC = ρ_l * (4/3 π) ∫ r^3 n(r) dr. For Gaussian, ∫ r^3 n(r) dr = N (r0^3 + 3 r0 σ^2). That's correct.

Now, is there any issue with the Gaussian extending to negative radii? With r0=4, σ=0.6, the fraction of negative radii is negligible (4/0.6 = 6.67 standard deviations, so essentially zero). So it's fine.

Now, let's consider if we need to use the exact formula for supersaturation including the curvature and solute effects. The problem says "estimate the supersaturation", and in a developing cumulus cloud, the droplets are typically >10 μm? Here mean radius is 4 μm, which is small. At 4 μm, the Kelvin effect is a/r = 2σ/(ρ_l R_v T r). σ for water at 0°C is about 0.0756 N/m? Actually, surface tension of water at 0°C is 0.0756 N/m. Let's compute a = 2σ/(ρ_l R_v T) = 2*0.0756/(1000*461.5*273.15) = 0.1512 / 126,058,725 = 1.2e-9 m = 0.0012 μm. So a/r = 0.0012/4 = 0.0003. So equilibrium supersaturation is 0.03%. Our dynamical supersaturation is 0.51%, so the Kelvin effect is small but not negligible? 0.03% is about 6% of 0.51%. The solute effect would reduce it. Typically, for cloud droplets, the equilibrium supersaturation is often neglected in such estimates because the droplets are assumed to be in a quasi-steady state where the ambient supersaturation is much larger than the equilibrium value. However, some textbooks include the curvature effect in the growth equation: dr/dt = (S - 1 - a/r + b/r^3) / (r F_k + F_d). But usually for "estimate the supersaturation" in a cloud with given LWC and spectrum, we use the simplified growth equation without curvature/solute, because those effects are small for the mean droplet. But let's check if the problem expects it. The problem statement: "In a developing cumulus cloud the droplet spectrum has a Gaussian shape... estimate the supersaturation in an updraft of 8 m/s." It doesn't mention surface tension or solute, so likely we ignore them.

Another thing: The cloud water content is given as $0 . 2 \mathrm { g } / \mathrm { \dot { m } } ^ { 3 }$ — that's probably a typo for "g/m^3". So LWC = 0.2 g/m^3.

Now, let's re-evaluate the constants to see if there's a standard set used in such problems. Often in cloud physics problems, they use:
L_v = 2.5e6 J/kg
c_p = 1005 J/(kg K)
R_d = 287 J/(kg K)
R_v = 461 J/(kg K)
g = 9.81 m/s^2
K = 2.43e-2 W/(m K)
D_v = 2.26e-5 m^2/s at 1 atm, adjusted for pressure.
e_s at 0°C = 6.11 hPa = 611 Pa.
ρ_l = 1000 kg/m^3.
These are all standard.

Let's compute with R_v = 461 (instead of 461.5). Then ε = 287/461 = 0.6226.
q_{vs} = 0.6226 * 611.2 / 79388.8 = 0.00479.
Term1 = 2.5e6/(1005*461*74610.9) = 2.5e6/(1005*34,400,000) = 2.5e6/3.457e10 = 7.23e-5.
Term2 = 1/(287*273.15) = 1.2756e-5.
α = 9.81*(5.954e-5) = 5.84e-4.
L_v^2/(c_p R_v T^2) = 6.25e12/3.457e10 = 180.8.
β = 1/0.00479 + 180.8 = 208.8 + 180.8 = 389.6.
C = (5.84e-4/389.6)*8 = 1.20e-5.
G: Term A = 6.25e15/(0.0243*461*74610.9) = 6.25e15/(0.0243*34,400,000) = 6.25e15/835,920 = 7.48e9.
Term B = 1000*461*273.15/(2.862e-5*611.2) = 125,900,000/0.01749 = 7.20e9.
Sum = 1.468e10, G = 6.81e-11.
N same.
s = 1.20e-5 * 1.0205 / (12.566*1000*6.81e-11*2796) = 1.224e-5/0.00239 = 0.00512 = 0.51%.
So it's robust.

Now, could there be a factor of 4π missing? In some derivations, the condensation rate is written as dq_l/dt = 4π ρ_l N r_mean G s / ρ_a. That's what we have. But sometimes the integral of r n(r) dr is N r_mean, yes.

Wait: The droplet growth equation is often written as:
r dr/dt = (S-1) / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ].
But sometimes the denominator has an additional factor? Let's check Rogers and Yau, Eq. (7.17):
r dr/dt = (S-1) / [ (L_v^2 ρ_l)/(K R_v T^2) + (ρ_l R_v T)/(D_v e_s) ].
Yes, that's exactly what we used. G is the inverse of the bracket.

Now, the supersaturation equation: Rogers and Yau Eq. (7.29) or similar:
ds/dt = (ξ - η) w - (ξ + η) dq_l/dt? Actually, let's derive from Rogers and Yau.
In Rogers and Yau, 3rd edition, Chapter 7:
The rate of change of supersaturation s = q_v/q_{vs} - 1.
ds/dt = (1/q_{vs}) dq_v/dt - (q_v/q_{vs}^2) dq_{vs}/dt.
With dq_v/dt = -C, and dq_{vs}/dt = q_{vs} [ (L_v/(R_v T^2)) dT/dt - (1/p) dp/dt ].
dT/dt = -g w/c_p + L_v C/c_p.
dp/dt = -ρ g w.
Then ds/dt = -C/q_{vs} - [ (L_v/(R_v T^2))(-g w/c_p + L_v C/c_p) + (ρ g w)/p ].
Note: (1/p) dp/dt = -ρ g w/p = -g w/(R_d T) (since p = ρ R_d T).
So ds/dt = -C/q_{vs} + (L_v g w)/(c_p R_v T^2) - (L_v^2 C)/(c_p R_v T^2) + g w/(R_d T).
= g w [ L_v/(c_p R_v T^2) + 1/(R_d T)
~~~~

**attempt 1** — `outcome` = `ungradable: solve() returned list, expected dict`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve():
    # Constants
    T = 273.15               # K
    p = 80000.0              # Pa
    e_s = 611.2              # Pa, saturation vapor pressure at 0°C
    L_v = 2.5e6              # J/kg, latent heat of vaporization
    c_p = 1005.0             # J/(kg K), specific heat of dry air
    R_d = 287.0              # J/(kg K), gas constant dry air
    R_v = 461.5              # J/(kg K), gas constant water vapor
    g = 9.81                 # m/s^2
    rho_l = 1000.0           # kg/m^3, density of liquid water
    K = 0.0243               # W/(m K), thermal conductivity of air at 0°C
    D_v_1atm = 2.26e-5       # m^2/s, diffusivity of water vapor at 0°C, 1 atm
    p_1atm = 101325.0        # Pa
    w = 8.0                  # m/s, updraft speed
    LWC = 0.2e-3             # kg/m^3, liquid water content (0.2 g/m^3)
    r0 = 4.0e-6              # m, mean radius
    sigma = 0.6e-6           # m, standard deviation

    # Adjust diffusivity for pressure
    D_v = D_v_1atm * (p_1atm / p)

    # Saturation mixing ratio
    epsilon = R_d / R_v
    q_vs = epsilon * e_s / (p - e_s)

    # Air density
    rho_a = p / (R_d * T)

    # Coefficient alpha (supersaturation production)
    term1 = L_v / (c_p * R_v * T**2)
    term2 = 1.0 / (R_d * T)
    alpha = g * (term1 - term2)

    # Coefficient beta (supersaturation depletion)
    beta = 1.0 / q_vs + L_v**2 / (c_p * R_v * T**2)

    # Condensation rate at steady state
    C = (alpha / beta) * w

    # Growth parameter G
    termA = L_v**2 * rho_l / (K * R_v * T**2)
    termB = rho_l * R_v * T / (D_v * e_s)
    G = 1.0 / (termA + termB)

    # Droplet number concentration N from LWC and spectrum
    mean_r3 = r0**3 + 3.0 * r0 * sigma**2
    N = LWC / (rho_l * (4.0/3.0 * math.pi * mean_r3))

    # Integral of r * n(r) dr = N * r0
    integral_r = N * r0

    # Steady-state supersaturation s
    s = C * rho_a / (4.0 * math.pi * rho_l * G * integral_r)

    # Express as percentage
    s_percent = s * 100.0

    return [{"value": s_percent, "unit": "%"}]
```
~~~~

**attempt 2** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
We need to fix the function so that it returns a dict instead of a list. The problem statement says: "Return the COMPLETE corrected solve(): a dict keyed '1'..'N' in the order asked, each {'value': <number>, 'unit': '<unit>'}, standard library only." So the function should return a dict like {"1": {"value": s_percent, "unit": "%"}}.

Also, there might be other bugs. Let's check the physics. The problem: "In a developing cumulus cloud the droplet spectrum has a Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of 0.6 μm. Given that the cloud water content is 0.2 g/m^3, estimate the supersaturation in an updraft of 8 m/s. Assume a temperature of 0°C and a pressure of 80 kPa. Express your answer as a percentage."

The code uses a steady-state supersaturation model. Let's verify the formulas.

The supersaturation s = (alpha/beta)*w * rho_a / (4*pi*rho_l*G*integral_r). But is that correct? Typically, the supersaturation equation: ds/dt = alpha w - beta * (condensation rate). At steady state, ds/dt=0 => condensation rate = (alpha/beta) w. The condensation rate (mass of water condensed per unit mass of air per unit time) is related to droplet growth: dm/dt = 4*pi*rho_l*G*s*r (for a single droplet). Total condensation rate per unit volume = integral N(r) * dm/dt dr = 4*pi*rho_l*G*s * integral N(r) r dr. Then per unit mass of air: condensation rate = (1/rho_a) * 4*pi*rho_l*G*s * integral_r. Equate to (alpha/beta) w => s = (alpha/beta) w * rho_a / (4*pi*rho_l*G*integral_r). That matches the code.

Now check the integral_r: For a Gaussian distribution of radii, n(r) = N * (1/(sqrt(2*pi)*sigma)) * exp(-(r-r0)^2/(2*sigma^2)). The integral of r * n(r) dr = N * r0 (since the mean of a Gaussian is r0). So integral_r = N * r0. That's correct.

But the code uses mean_r3 = r0**3 + 3.0 * r0 * sigma**2. That's the third moment for a Gaussian? For a Gaussian distribution, the expected value of r^3 is not simply r0^3 + 3 r0 sigma^2. Actually, for a normal distribution with mean mu and variance sigma^2, the third central moment is 0, so E[r^3] = mu^3 + 3 mu sigma^2. Yes, that's correct. So N = LWC / (rho_l * (4/3 pi mean_r3)). That's correct.

Now check the constants: T=273.15 K, p=80000 Pa, e_s=611.2 Pa (saturation vapor pressure at 0°C). L_v=2.5e6 J/kg, c_p=1005 J/(kg K), R_d=287, R_v=461.5, g=9.81, rho_l=1000, K=0.0243 W/(m K), D_v_1atm=2.26e-5 m^2/s, p_1atm=101325 Pa. w=8 m/s, LWC=0.2e-3 kg/m^3 (0.2 g/m^3). r0=4e-6 m, sigma=0.6e-6 m.

Check the diffusivity adjustment: D_v = D_v_1atm * (p_1atm / p). That's correct for pressure dependence (D inversely proportional to pressure). Temperature dependence? At 0°C it's given for 0°C, so fine.

Saturation mixing ratio: q_vs = epsilon * e_s / (p - e_s). epsilon = R_d/R_v = 287/461.5 ≈ 0.622. That's standard.

Air density: rho_a = p/(R_d * T). Correct.

Alpha: term1 = L_v/(c_p * R_v * T**2), term2 = 1/(R_d * T). alpha = g*(term1 - term2). This is from the supersaturation equation: alpha = (g/(R_d T)) * (L_v R_d/(c_p R_v T) - 1) maybe? Let's derive: The supersaturation production term is usually alpha w, where alpha = (L_v/(c_p T) - 1) * (g/(R_d T))? Actually, the standard formula for the vertical gradient of saturation mixing ratio: dq_vs/dz = - (g/(R_d T)) * q_vs * (L_v/(R_v T) - c_p/R_d?) Wait, I'm more familiar with: alpha = (g/(R_d T)) * (L_v R_d/(c_p R_v T) - 1). Let's check: term1 = L_v/(c_p R_v T^2), term2 = 1/(R_d T). Multiply by g: g*L_v/(c_p R_v T^2) - g/(R_d T). Factor g/(R_d T): g/(R_d T) * (L_v R_d/(c_p R_v T) - 1). Yes, that's correct. So alpha is correct.

Beta: beta = 1/q_vs + L_v^2/(c_p R_v T^2). This is from the linearized Clausius-Clapeyron and the definition of saturation mixing ratio. Standard.

Condensation rate C = (alpha/beta) * w. That's the steady-state condensation rate (mass of water condensed per unit mass of air per unit time). Units: alpha has units 1/m? Actually alpha is (1/s?) Let's check: alpha * w has units 1/s? Supersaturation s is dimensionless. ds/dt = alpha w - beta * (condensation rate). So alpha w has units 1/s, alpha has units 1/m. beta has units 1/(kg/kg) = dimensionless? Actually condensation rate is dq_l/dt, units kg/kg/s. So beta * dq_l/dt has units 1/s, so beta has units (1/s)/(kg/kg/s) = 1/(kg/kg) = dimensionless. So beta is dimensionless. So C = (alpha/beta)*w has units (1/m)/(dimensionless) * m/s = 1/s. That's a rate of change of mixing ratio? Actually condensation rate dq_l/dt has units kg/kg/s. So C is dq_l/dt. Good.

Then s = C * rho_a / (4 pi rho_l G integral_r). Check units: C [kg/kg/s] * rho_a [kg/m^3] = kg/(m^3 s). Denominator: 4 pi rho_l [kg/m^3] * G [m^2/s?] * integral_r [1/m^3 * m = 1/m^2?]. Let's check G: G = 1/(termA + termB). termA = L_v^2 rho_l/(K R_v T^2). L_v^2: J^2/kg^2, rho_l: kg/m^3, K: W/(m K)=J/(s m K), R_v: J/(kg K), T^2: K^2. So termA units: (J^2/kg^2 * kg/m^3) / (J/(s m K) * J/(kg K) * K^2) = (J^2/(kg m^3)) / (J^2/(s m kg)) = (J^2/(kg m^3)) * (s m kg/J^2) = s/m^2. termB: rho_l R_v T/(D_v e_s). rho_l: kg/m^3, R_v: J/(kg K), T: K, D_v: m^2/s, e_s: Pa = J/m^3. So termB: (kg/m^3 * J/(kg K) * K) / (m^2/s * J/m^3) = (J/m^3) / (J/(m s)) = s/m. So termA has s/m^2, termB has s/m. They are not dimensionally consistent! That's a bug. G should have units of m^2/s? Actually, in droplet growth equation: dr/dt = G * s / r, where G is a growth parameter with units m^2/s. Let's check standard formula: G = (rho_l R_v T)/(D_v e_s) + (L_v rho_l)/(K T) * (L_v/(R_v T) - 1) ... Actually, the standard G is: 1/G = (rho_l R_v T)/(D_v e_s) + (L_v^2 rho_l)/(K R_v T^2). Wait, termA is L_v^2 rho_l/(K R_v T^2). Units: L_v^2: J^2/kg^2, rho_l: kg/m^3, K: J/(s m K), R_v: J/(kg K), T^2: K^2. So L_v^2 rho_l/(K R_v T^2) = (J^2/(kg^2) * kg/m^3) / (J/(s m K) * J/(kg K) * K^2) = (J^2/(kg m^3)) / (J^2/(s m kg)) = s/m^2. That's not 1/(m^2/s) = s/m^2. Actually, 1/G should have units s/m^2. So termA is s/m^2, termB is s/m. They are not additive. There's a missing factor of r? Wait, the growth equation is r dr/dt = G s. So dr/dt = G s / r. Then G has units m^2/s. The formula for G is: G = 1 / ( (L_v^2 rho_l)/(K R_v T^2) + (rho_l R_v T)/(D_v e_s) ). But the second term has units: rho_l R_v T/(D_v e_s) = (kg/m^3 * J/(kg K) * K) / (m^2/s * J/m^3) = (J/m^3) / (J/(m s)) = s/m. That's not s/m^2. So there's an inconsistency. Actually, the correct G is: G = 1 / ( (L_v^2 rho_l)/(K R_v T^2) + (rho_l R_v T)/(D_v e_s) )? But that would give units s/m^2 + s/m, which is wrong. I recall the standard G for droplet growth by condensation is: G = (S - 1) / (r * (F_k + F_d)) where F_k and F_d are terms. Actually, the growth equation is: r dr/dt = (S-1) / (F_k + F_d), where F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) and F_d = (rho_l R_v T)/(D_v e_s). So G = 1/(F_k + F_d). Then F_k has units: (L_v/(R_v T) - 1) is dimensionless, L_v rho_l/(K T): L_v J/kg, rho_l kg/m^3, K J/(s m K), T K => (J/kg * kg/m^3) / (J/(s m K) * K) = (J/m^3) / (J/(s m)) = s/m. F_d: rho_l R_v T/(D_v e_s) = s/m. So both F_k and F_d have units s/m. Then G has units m/s. But then r dr/dt = G s, so dr/dt = G s / r, units: (m/s)/m = 1/s, correct. So G should have units m/s, not m^2/s. In the code, termA = L_v^2 rho_l/(K R_v T^2) has units s/m^2, which is wrong. The correct F_k is (L_v/(R_v T) - 1) * (L_v rho_l)/(K T). The code uses L_v^2 rho_l/(K R_v T^2) which is missing the -1 term and has an extra R_v in denominator? Let's derive: F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) = (L_v^2 rho_l)/(K R_v T^2) - (L_v rho_l)/(K T). So termA in code is only the first part, missing the second part. And termB is correct: rho_l R_v T/(D_v e_s). So the code's G is incorrect. This is a common mistake. The correct G should be: G = 1 / ( (L_v^2 rho_l)/(K R_v T^2) - (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s) ). But wait, the standard formula often combines the heat conduction and vapor diffusion terms. Actually, the full expression for the growth parameter is: G = 1 / ( (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s) ). So termA should be (L_v/(R_v T) - 1) * (L_v rho_l)/(K T). The code's termA is L_v^2 rho_l/(K R_v T^2) which is only the first part of that product. So it's missing the - (L_v rho_l)/(K T) term. That's a bug.

Also, check the beta expression: beta = 1/q_vs + L_v^2/(c_p R_v T^2). That's correct for the linearized supersaturation equation? Actually, the standard beta is: beta = 1/q_vs + (L_v^2)/(c_p R_v T^2) * (something)? Wait, the supersaturation equation: ds/dt = alpha w - beta * dq_l/dt. The beta term comes from the change in saturation mixing ratio due to latent heat release and temperature change. The standard formula is: beta = (1/q_vs) + (L_v^2)/(c_p R_v T^2). That's correct. But sometimes there's a factor of (R_d/R_v)? No, that's standard.

Now, the integral_r: The code uses N * r0. That's correct for a Gaussian distribution. But note: The droplet spectrum is Gaussian in radius, but the integral of r * n(r) dr is N * mean radius = N * r0. That's fine.

Now, the steady-state supersaturation formula: s = (alpha/beta) * w * rho_a / (4 * pi * rho_l * G * integral_r). But check the units: alpha/beta * w has units 1/s? alpha: 1/m, beta: dimensionless, so alpha/beta: 1/m, times w m/s gives 1/s. That's dq_l/dt? Actually, dq_l/dt = (alpha/beta) w. Units: 1/s. But dq_l/dt is mixing ratio per second, which is dimensionless per second, so 1/s is correct. Then multiply by rho_a (kg/m^3) gives kg/(m^3 s). Denominator: 4 pi rho_l (kg/m^3) * G (m/s) * integral_r (1/m^2? Let's check integral_r units: N is number per volume (1/m^3), r0 is m, so integral_r = N * r0 has units 1/m^2. So denominator: kg/m^3 * m/s * 1/m^2 = kg/(m^4 s)? That doesn't match. Wait: 4 pi rho_l * G * integral_r: rho_l kg/m^3, G m/s, integral_r 1/m^2 => product: kg/(m^3) * m/s * 1/m^2 = kg/(m^4 s). Numerator: kg/(m^3 s). So s would have units m. That's wrong; s should be dimensionless. So there's a unit mismatch. Let's re-derive.

The condensation rate per unit volume: C_vol = integral (dm/dt) n(r) dr. dm/dt = 4 pi r^2 rho_l dr/dt. And dr/dt = G s / r. So dm/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi rho_l G s r. So C_vol = 4 pi rho_l G s * integral r n(r) dr = 4 pi rho_l G s * (N r0). Units: rho_l kg/m^3, G m/s, s dimensionless, integral_r 1/m^2 => C_vol kg/(m^3 s). That's correct.

The condensation rate per unit mass of air: dq_l/dt = C_vol / rho_a. So dq_l/dt = (4 pi rho_l G s * N r0) / rho_a. Set equal to (alpha/beta) w. So s = (alpha/beta) w * rho_a / (4 pi rho_l G N r0). That's what the code has. But check units: alpha/beta w: 1/s. rho_a: kg/m^3. Denominator: rho_l kg/m^3, G m/s, N r0 1/m^2. So s = (1/s * kg/m^3) / (kg/m^3 * m/s * 1/m^2) = (kg/(m^3 s)) / (kg/(m^4 s)) = m. So s has units of meters! That's clearly wrong. The error is that G should have units m^2/s, not m/s. Let's re-check the growth equation. Standard: r dr/dt = G s, where G is in m^2/s. Then dr/dt = G s / r. Then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi rho_l G s r. So G has units m^2/s. Then C_vol = 4 pi rho_l G s * integral r n(r) dr. Units: rho_l kg/m^3, G m^2/s, s dimensionless, integral_r 1/m^2 => kg/(m^3) * m^2/s * 1/m^2 = kg/(m^3 s). That works. So G must be m^2/s. The code's G has units m/s because termA and termB are s/m^2 and s/m? Actually, if G is m^2/s, then 1/G should have units s/m^2. The standard formula for 1/G is: 1/G = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s). Let's check units: first term: (L_v/(R_v T) - 1) dimensionless, L_v rho_l/(K T): (J/kg * kg/m^3) / (J/(s m K) * K) = (J/m^3) / (J/(s m)) = s/m. That's s/m, not s/m^2. So that would give G in m/s. But we need G in m^2/s. There's a discrepancy. Actually, the growth equation is often written as: r dr/dt = (S-1) / (F_k + F_d) where F_k and F_d have units s/m. Then G = 1/(F_k + F_d) has units m/s. But then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi rho_l G s r. That still gives G in m/s. Then C_vol = 4 pi rho_l G s * integral r n(r) dr. Units: rho_l kg/m^3, G m/s, integral_r 1/m^2 => kg/(m^4 s). That's wrong. So there's a missing factor of something. Let's re-derive carefully.

The diffusional growth equation for a single droplet: dm/dt = 4 pi r (S-1) / (F_k + F_d) where F_k = (L_v/(R_v T) - 1) * (L_v/(K T)) and F_d = (R_v T)/(D_v e_s). Wait, I need to check standard references. From Rogers and Yau, "A Short Course in Cloud Physics", the growth equation is: r dr/dt = (S-1) / (F_k + F_d) where F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) and F_d = (rho_l R_v T)/(D_v e_s). So r dr/dt has units m^2/s. Then G = 1/(F_k + F_d) has units m^2/s? Let's check: F_k: (L_v/(R_v T) - 1) dimensionless, L_v rho_l/(K T): (J/kg * kg/m^3) / (J/(s m K) * K) = (J/m^3) / (J/(s m)) = s/m. So F_k has units s/m. F_d: rho_l R_v T/(D_v e_s) = (kg/m^3 * J/(kg K) * K) / (m^2/s * J/m^3) = (J/m^3) / (J/(m s)) = s/m. So both F_k and F_d have units s/m. Then G = 1/(F_k + F_d) has units m/s. But r dr/dt = G s, so r dr/dt has units m * m/s = m^2/s. That matches. So G is in m/s. Then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi rho_l G s r. Units: rho_l kg/m^3, G m/s, s dimensionless, r m => kg/(m^3) * m/s * m = kg/(m s). That's mass per time per droplet. Multiply by N (1/m^3) gives kg/(m^3 s). So C_vol = 4 pi rho_l G s * integral r n(r) dr. integral r n(r) dr has units: N (1/m^3) * r (m) = 1/m^2. So C_vol units: kg/m^3 * m/s * 1/m^2 = kg/(m^4 s). That's off by 1/m. There's a mistake: dm/dt for a single droplet is mass per time, units kg/s. 4 pi rho_l G s r: rho_l kg/m^3, G m/s, s dimensionless, r m => product: kg/m^3 * m/s * m = kg/(m s). That's kg per meter per second, not kg/s. So dm/dt should be kg/s. The correct dm/dt = 4 pi r^2 rho_l dr/dt. dr/dt = G s / r, so dm/dt = 4 pi r^2 rho_l * G s / r = 4 pi rho_l G s r. That gives kg/(m s). But r is in meters, so kg/(m s) is not kg/s. There's a missing factor of m? Wait, 4 pi r^2 has units m^2, rho_l kg/m^3, dr/dt m/s => product: m^2 * kg/m^3 * m/s = kg/s. Yes, that's correct. Let's recompute: r^2 * rho_l * dr/dt: m^2 * kg/m^3 * m/s = kg/s. So dm/dt = 4 pi r^2 rho_l dr/dt. Substitute dr/dt = G s / r: dm/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi r rho_l G s. Units: r (m) * rho_l (kg/m^3) * G (m/s) * s (dimensionless) = m * kg/m^3 * m/s = kg/(m s). That's not kg/s. There's an inconsistency: r^2 * (1/r) = r, so it's 4 pi r rho_l G s. That gives kg/(m s). But r^2 * dr/dt gave kg/s. So dr/dt must have units m/s, G s / r has units (m/s)/m = 1/s? No, G is m/s, so G s / r has units (m/s)/m = 1/s. That's wrong; dr/dt should be m/s. So G must have units m^2/s. Let's re-evaluate: If r dr/dt = G s, then G has units m^2/s. Then dr/dt = G s / r has units m^2/s / m = m/s. Good. Then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi r rho_l G s. Units: r (m) * rho_l (kg/m^3) * G (m^2/s) * s = m * kg/m^3 * m^2/s = kg/s. Yes! So G must be m^2/s. Then F_k and F_d must have units s/m^2 to make 1/G in s/m^2. But earlier I computed F_k and F_d as s/m. So there's a missing factor of 1/m. Let's check the standard formula again. In Rogers and Yau, the equation is: r dr/dt = (S-1) / (F_k + F_d) where F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) and F_d = (rho_l R_v T)/(D_v e_s). Wait, that gives r dr/dt in m^2/s. So (S-1) is dimensionless, so 1/(F_k + F_d) must have units m^2/s. Therefore F_k + F_d must have units s/m^2. Let's recompute units of F_k: L_v/(R_v T) dimensionless, L_v rho_l/(K T): L_v J/kg, rho_l kg/m^3, K J/(s m K), T K. So L_v rho_l/(K T) = (J/kg * kg/m^3) / (J/(s m K) * K) = (J/m^3) / (J/(s m)) = s/m. That's s/m, not s/m^2. So there's a discrepancy. Perhaps the formula is: F_k = (L_v/(R_v T) - 1) * (L_v/(K T)) and F_d = (R_v T)/(D_v e_s), without rho_l? Then F_k: (L_v/(K T)) has units (J/kg) / (J/(s m K) * K) = (J/kg) / (J/(s m)) = s m / kg? That's messy. Let's look up the correct expression for G.

Standard diffusional growth equation: dm/dt = 4 pi r (S-1) / ( (L_v/(R_v T) - 1) * (L_v/(K T)) + (R_v T)/(D_v e_s) )? Actually, the equation is often written: dm/dt = 4 pi r (S-1) / (A + B) where A = L_v/(K T) * (L_v/(R_v T) - 1) and B = R_v T/(D_v e_s). Then dm/dt has units: r (m) * (dimensionless) / (A+B). A: L_v/(K T) has units (J/kg) / (J/(s m K) * K) = s m / kg. B: R_v T/(D_v e_s) = (J/(kg K) * K) / (m^2/s * J/m^3) = (J/kg) / (J/(m s)) = s m / kg. So A and B have units s m / kg. Then 1/(A+B) has units kg/(s m). Multiply by r (m) gives kg/s. So dm/dt = 4 pi r (S-1) / (A+B) is correct. Then the growth parameter G is often defined such that r dr/dt = G s. Let's relate: dm/dt = 4 pi r^2 rho_l dr/dt. So 4 pi r^2 rho_l dr/dt = 4 pi r s / (A+B). Thus r dr/dt = s / (rho_l (A+B)). So G = 1/(rho_l (A+B)). Then A+B has units s m / kg, so rho_l*(A+B) has units (kg/m^3)*(s m/kg) = s/m^2. Then G has units m^2/s. Perfect. So the correct G is: G = 1 / ( rho_l * ( (L_v/(R_v T) - 1) * (L_v/(K T)) + (R_v T)/(D_v e_s) ) ). Alternatively, G = 1 / ( (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s) )? Let's check: rho_l * A = rho_l * L_v/(K T) * (L_v/(R_v T) - 1) = (L_v rho_l)/(K T) * (L_v/(R_v T) - 1). That's exactly what I had earlier as F_k. And rho_l * B = rho_l * R_v T/(D_v e_s) = (rho_l R_v T)/(D_v e_s). So indeed, G = 1 / ( F_k + F_d ) where F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) and F_d = (rho_l R_v T)/(D_v e_s). But earlier I computed units of F_k as s/m. Let's recompute with rho_l: F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T). L_v rho_l/(K T): L_v J/kg, rho_l kg/m^3, K J/(s m K), T K. So L_v rho_l = J/m^3. Divide by K T: (J/m^3) / (J/(s m K) * K) = (J/m^3) / (J/(s m)) = s/m. So F_k has units s/m. F_d: rho_l R_v T/(D_v e_s) = (kg/m^3 * J/(kg K) * K) / (m^2/s * J/m^3) = (J/m^3) / (J/(m s)) = s/m. So F_k and F_d have units s/m. Then G = 1/(F_k + F_d) has units m/s. But we need G in m^2/s. There's a contradiction. Let's re-evaluate the equation r dr/dt = G s. If G is m/s, then r dr/dt has units m * m/s = m^2/s. That's fine. Then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi r rho_l (r dr/dt) = 4 pi r rho_l G s. Units: r (m) * rho_l (kg/m^3) * G (m/s) * s = m * kg/m^3 * m/s = kg/(m s). That's not kg/s. So there's a missing r? Wait, r dr/dt = G s, so dr/dt = G s / r. Then dm/dt = 4 pi r^2 rho_l dr/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi r rho_l G s. That's what I got. But if G is m/s, then dm/dt has units kg/(m s). That's wrong. So G must be m^2/s to make dm/dt kg/s. Let's test: if G is m^2/s, then r dr/dt = G s => dr/dt = G s / r (m/s). dm/dt = 4 pi r^2 rho_l * (G s / r) = 4 pi r rho_l G s. Units: r (m) * rho_l (kg/m^3) * G (m^2/s) * s = m * kg/m^3 * m^2/s = kg/s. Yes! So G must be m^2/s. Therefore F_k + F_d must have units s/m^2. But we computed F_k and F_d as s/m. So there's a factor of 1/m missing. Let's check the standard formula from a reliable source. In Pruppacher and Klett, or Rogers and Yau, the growth parameter is often given as: G = 1 / ( (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s) ). But that gives G in m/s. However, I recall that sometimes the equation is written as: r dr/dt = (S-1) / (F_k + F_d) where F_k and F_d are as above. Then r dr/dt has units m^2/s. So (S-1) is dimensionless, so 1/(F_k + F_d) must have units m^2/s. Therefore F_k + F_d must have units s/m^2. Let's recompute F_k with rho_l: L_v rho_l/(K T). L_v rho_l: J/m^3. K T: J/(s m K) * K = J/(s m). So L_v rho_l/(K T) = (J/m^3) / (J/(s m)) = s/m^2. Yes! I made a mistake: K has units J/(s m K), so K T has units J/(s m). L_v rho_l has units J/m^3. So (J/m^3) / (J/(s m)) = s/m^2. Because (1/m^3) / (1/(s m)) = s/m^2. Let's do carefully: J/m^3 divided by J/(s m) = (J/m^3) * (s m/J) = s/m^2. Yes! So F_k has units s/m^2. Similarly, F_d: rho_l R_v T/(D_v e_s). rho_l R_v T: (kg/m^3) * (J/(kg K)) * K = J/m^3. D_v e_s: (m^2/s) * (J/m^3) = J/(m s). So (J/m^3) / (J/(m s)) = s/m^2. Perfect! So F_k and F_d have units s/m^2. Then G = 1/(F_k + F_d) has units m^2/s. So the code's termA and termB should have units s/m^2. Let's check the code's termA: L_v^2 rho_l/(K R_v T^2). L_v^2: J^2/kg^2, rho_l: kg/m^3, K: J/(s m K), R_v: J/(kg K), T^2: K^2. So numerator: J^2/(kg^2) * kg/m^3 = J^2/(kg m^3). Denominator: J/(s m K) * J/(kg K) * K^2 = J^2/(s m kg) * K? Wait: K * K^2 = K^3? Actually: K * R_v * T^2: K [J/(s m K)] * R_v [J/(kg K)] * T^2 [K^2] = J^2/(s m kg) * (K^2/K)?? Let's do: K * T^2: (J/(s m K)) * K^2 = J K / (s m). Then times R_v: (J K/(s m)) * (J/(kg K)) = J^2/(s m kg). So termA = (J^2/(kg m^3)) / (J^2/(s m kg)) = s/m^2. Yes! So termA has units s/m^2. termB: rho_l R_v T/(D_v e_s). rho_l: kg/m^3, R_v: J/(kg K), T: K => J/m^3. D_v: m^2/s, e_s: J/m^3 => J/(m s). So termB = (J/m^3) / (J/(m s)) = s/m^2. So both termA and termB have units s/m^2. Then G = 1/(termA + termB) has units m^2/s. That's correct! My earlier unit analysis for termA was wrong because I forgot that K T has units J/(s m), not J/(s m K)*K? Actually K is thermal conductivity, units W/(m K) = J/(s m K). So K * T has units J/(s m). So L_v rho_l/(K T) has units (J/m^3) / (J/(s m)) = s/m^2. But the code's termA is L_v^2 rho_l/(K R_v T^2). That's different: it has an extra L_v and R_v and T. Let's see if termA equals the correct F_k? The correct F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) = L_v^2 rho_l/(K R_v T^2) - L_v rho_l/(K T). So the code's termA is only the first part, missing the second part. So the code's G is missing the - L_v rho_l/(K T) term. That is a bug. The correct G should be 1 / ( L_v^2 rho_l/(K R_v T^2) - L_v rho_l/(K T) + rho_l R_v T/(D_v e_s) ). Alternatively, sometimes the formula is written with the approximation that L_v/(R_v T) >> 1, so the -1 is neglected. At 0°C, L_v=2.5e6, R_v=461.5, T=273.15, L_v/(R_v T) = 2.5e6/(461.5*273.15) ≈ 2.5e6/126,000 ≈ 19.8. So it's about 20, so neglecting the 1 introduces about a 5% error. In many simple models, they do neglect it. But the problem might expect the full expression? The code as written uses termA = L_v^2 rho_l/(K R_v T^2) and termB = rho_l R_v T/(D_v e_s). That's the simplified G without the -1. Is that acceptable? Possibly, but it's a common simplification. However, the problem statement doesn't specify which formula to use. The code might have other bugs.

Let's check the beta expression: beta = 1/q_vs + L_v^2/(c_p R_v T^2). That's standard.

Now, the integral_r: N * r0. But is the droplet spectrum Gaussian in radius? Yes, "Gaussian shape, centered at a mean radius of 4 μm with a standard deviation of 0.6 μm." So n(r) = N * (1/(sqrt(2 pi) sigma)) exp(-(r-r0)^2/(2 sigma^2)). The integral of r n(r) dr = N * r0. That's correct. The integral of r^3 n(r) dr = N * (r0^3 + 3 r0 sigma^2). That's correct for a Gaussian. So N = LWC / (rho_l * (4/3 pi) * mean_r3). That's correct.

Now, the steady-state supersaturation formula: s = (alpha/beta) * w * rho_a / (4 pi rho_l G N r0). Let's check units again with G in m^2/s. alpha: 1/m, beta: dimensionless, w: m/s => alpha/beta * w: 1/s. rho_a: kg/m^3. Denominator: 4 pi rho_l (kg/m^3) * G (m^2/s) * N r0 (1/m^2) => kg/m^3 * m^2/s * 1/m^2 = kg/(m^3 s). So s = (1/s * kg/m^3) / (kg/(m^3 s)) = dimensionless. Perfect.

So the code's G formula is missing the - L_v rho_l/(K T) term. But is that term significant? Let's compute both. We'll need to decide whether to correct it. The problem might be from a textbook where they use the simplified G. However, the error message was only about returning a list instead of a dict. But the instruction says: "Your solve() function failed to run. Fix the bug and return the corrected function." The bug that caused the failure is that it returned a list instead of a dict. But there might be other bugs that would cause incorrect output. The user wants the corrected function. We should fix the return type and also check for any other potential issues. The code as written might produce a reasonable answer, but the G expression is incomplete. Let's see if the missing term is commonly omitted. In many cloud physics problems, the full G is used. I'll check the standard formula from Rogers and Yau: G = 1 / ( (L_v/(R_v T) - 1) * (L_v rho_l)/(K T) + (rho_l R_v T)/(D_v e_s) ). That's the exact. The code's termA is L_v^2 rho_l/(K R_v T^2) which is the first term of the expansion. So it's missing - L_v rho_l/(K T). I'll include the full expression to be accurate.

Also, check the alpha expression: term1 = L_v/(c_p R_v T**2), term2 = 1.0/(R_d T). alpha = g*(term1 - term2). That's correct.

Check the beta expression: beta = 1.0/q_vs + L_v**2/(c_p R_v T**2). That's correct.

Now, the code uses e_s = 611.2 Pa. At 0°C, saturation vapor pressure over water is 611.2 Pa? Actually, it's 611.2 Pa at 0°C? I think it's 611.2 Pa at 0°C? Wait, the standard is 611.2 Pa at 0°C? Actually, the saturation vapor pressure at 0°C is about 611 Pa. 611.2 is a common value. So that's fine.

Pressure is 80 kPa = 80000 Pa. The code uses p_1atm = 101325 Pa. D_v_1atm = 2.26e-5 m^2/s. That's typical for water vapor diffusivity at 0°C and 1 atm. Adjusting for pressure: D_v = D_v_1atm * (p_1atm / p). That's correct.

Now, check the calculation of N: mean_r3 = r0**3 + 3.0 * r0 * sigma**2. For r0=4e-6, sigma=0.6e-6. r0^3 = 64e-18 = 6.4e-17? Actually 4e-6 cubed = 64e-18 = 6.4e-17 m^3. 3*r0*sigma^2 = 3*4e-6*(0.6e-6)^2 = 12e-6 * 0.36e-12 = 4.32e-18. So mean_r3 ≈ 6.4e-17 + 4.32e-18 = 6.832e-17 m^3. Then volume = 4/3 pi mean_r3 ≈ 4.1888 * 6.832e-17 = 2.86e-16 m^3. Mass per droplet = rho_l * volume = 1000 * 2.86e-16 = 2.86e-13 kg. LWC = 0.2e-3 kg/m^3. N = LWC / mass_per_droplet = 2e-4 / 2.86e-13 ≈ 7e8 m^-3. That seems reasonable.

Now, integral_r = N * r0 = 7e8 * 4e-6 = 2800 m^-2? Actually 7e8 * 4e-6 = 2800 m^-2. That's fine.

Now, compute G. We'll compute both the simplified and full G to see the difference. But the problem likely expects the full expression. I'll implement the full G.

Let's code the corrected function. We'll return a dict with key "1" since there's only one answer.

Also, ensure we import math. The function should be self-contained.

Let's write the corrected solve():

```python
import math

def solve():
    # Constants
    T = 273.15               # K
    p = 80000.0              # Pa
    e_s = 611.2              # Pa, saturation vapor pressure at 0°C
    L_v = 2.5e6              # J/kg, latent heat of vaporization
    c_p = 1005.0             # J/(kg K), specific heat of dry air
    R_d = 287.0              # J/(kg K), gas constant dry air
    R_v = 461.5              # J/(kg K), gas constant water vapor
    g = 9.81                 # m/s^2
    rho_l = 1000.0           # kg/m^3, density of liquid water
    K = 0.0243               # W/(m K), thermal conductivity of air at 0°C
    D_v_1atm = 2.26e-5       # m^2/s, diffusivity of water vapor at 0°C, 1 atm
    p_1atm = 101325.0        # Pa
    w = 8.0                  # m/s, updraft speed
    LWC = 0.2e-3             # kg/m^3, liquid water content (0.2 g/m^3)
    r0 = 4.0e-6              # m, mean radius
    sigma = 0.6e-6           # m, standard deviation

    # Adjust diffusivity for pressure
    D_v = D_v_1atm * (p_1atm / p)

    # Saturation mixing ratio
    epsilon = R_d / R_v
    q_vs = epsilon * e_s / (p - e_s)

    # Air density
    rho_a = p / (R_d * T)

    # Coefficient alpha (supersaturation production)
    term1 = L_v / (c_p * R_v * T**2)
    term2 = 1.0 / (R_d * T)
    alpha = g * (term1 - term2)

    # Coefficient beta (supersaturation depletion)
    beta = 1.0 / q_vs + L_v**2 / (c_p * R_v * T**2)

    # Condensation rate at steady state
    C = (alpha / beta) * w

    # Growth parameter G (full expression)
    # F_k = (L_v/(R_v*T) - 1) * (L_v * rho_l) / (K * T)
    # F_d = (rho_l * R_v * T) / (D_v * e_s)
    F_k = (L_v/(R_v*T) - 1.0) * (L_v * rho_l) / (K * T)
    F_d = (rho_l * R_v * T) / (D_v * e_s)
    G = 1.0 / (F_k + F_d)

    # Droplet number concentration N from LWC and spectrum
    # For Gaussian, <r^3> = r0^3 + 3*r0*sigma^2
    mean_r3 = r0**3 + 3.0 * r0 * sigma**2
    N = LWC / (rho_l * (4.0/3.0 * math.pi * mean_r3))

    # Integral of r * n(r) dr = N * r0
    integral_r = N * r0

    # Steady-state supersaturation s
    s = C * rho_a / (4.0 * math.pi * rho_l * G * integral_r)

    # Express as percentage
    s_percent = s * 100.0

    return {"1": {"value": s_percent, "unit": "%"}}
```

But wait, is the steady-state supersaturation formula exactly as above? Let's double-check the derivation. The supersaturation equation: ds/dt = alpha w - beta * (dq_l/dt). At steady state, dq_l/dt = (alpha/beta) w. The condensation rate per unit mass of air is dq_l/dt. The total condensation rate per unit volume is rho_a * dq_l/dt. This must equal the integral of dm/dt * n(r) dr. dm/dt = 4 pi r rho_l G s. So rho_a * (alpha/beta) w = 4 pi rho_l G s * integral_r. So s = (alpha/beta) w * rho_a / (4 pi rho_l G integral_r). That's what we have.

Now, check if there's any other missing factor. Some derivations use the supersaturation in % as s*100. That's fine.

Let's test the code mentally with approximate values to see if s_percent is reasonable. Typical supersaturations in cumulus clouds are on the order of 0.1-1%. Let's compute roughly.

Compute epsilon = 287/461.5 ≈ 0.622. e_s = 611.2, p=80000, p-e_s ≈ 79388.8. q_vs = 0.622 * 611.2 / 79388.8 ≈ 0.622 * 0.00770 ≈ 0.00479 kg/kg. rho_a = 80000/(287*273.15) ≈ 80000/78400 ≈ 1.02 kg/m^3.

alpha: term1 = L_v/(c_p R_v T^2) = 2.5e6/(1005*461.5*273.15^2). T^2 ≈ 74600. c_p R_v T^2 ≈ 1005*461.5*74600 ≈ 1005*34,400,000 ≈ 3.46e10. term1 ≈ 2.5e6/3.46e10 ≈ 7.23e-5. term2 = 1/(R_d T) = 1/(287*273.15) ≈ 1/78400 ≈ 1.275e-5. term1 - term2 ≈ 5.955e-5. alpha = 9.81 * 5.955e-5 ≈ 5.84e-4 m^-1? Actually units: term1 and term2 have units 1/K? Let's check: L_v/(c_p R_v T^2): L_v J/kg, c_p J/(kg K), R_v J/(kg K), T^2 K^2 => units: (J/kg) / (J/(kg K) * J/(kg K) * K^2) = (J/kg) / (J^2/(kg^2 K^2) * K^2) = (J/kg) / (J^2/(kg^2)) = kg/J. That's not 1/K. Wait, I need to be careful. The standard alpha is derived from dq_vs/dz. The formula is alpha = (g/(R_d T)) * ( (L_v R_d)/(c_p R_v T) - 1 ). Let's check units: g/(R_d T) has units (m/s^2) / (J/(kg K) * K) = (m/s^2) / (J/kg) = (m/s^2) / (m^2/s^2) = 1/m. So alpha has units 1/m. The code's alpha = g*(term1 - term2). term1 = L_v/(c_p R_v T^2). Units: L_v J/kg, c_p J/(kg K), R_v J/(kg K), T^2 K^2. So L_v/(c_p R_v T^2) = (J/kg) / (J^2/(kg^2 K^2) * K^2) = (J/kg) / (J^2/(kg^2)) = kg/J. term2 = 1/(R_d T) = 1/(J/(kg K) * K) = kg/J. So both have units kg/J. Then g*(kg/J) has units (m/s^2)*(kg/J) = (m/s^2)*(kg/(kg m^2/s^2)) = 1/m. Yes, alpha has units 1/m. So that's correct.

Now beta: 1/q_vs is dimensionless? q_vs is kg/kg, so 1/q_vs is dimensionless. L_v^2/(c_p R_v T^2): L_v^2 J^2/kg^2, c_p J/(kg K), R_v J/(kg K), T^2 K^2 => J^2/kg^2 / (J^2/(kg^2 K^2) * K^2) = dimensionless. So beta dimensionless. Good.

C = (alpha/beta)*w: alpha 1/m, beta dimensionless, w m/s => C has units 1/s. That's dq_l/dt? dq_l/dt is kg/kg/s, which is 1/s. Good.

Now G: F_k = (L_v/(R_v T) - 1) * (L_v rho_l)/(K T). L_v/(R_v T) dimensionless. L_v rho_l/(K T): L_v J/kg, rho_l kg/m^3, K J/(s m K), T K. So L_v rho_l = J/m^3. K T = J/(s m). So L_v rho_l/(K T) = (J/m^3) / (J/(s m)) = s/m^2. So F_k s/m^2. F_d = rho_l R_v T/(D_v e_s): rho_l R_v T = J/m^3, D_v e_s = (m^2/s)*(J/m^3) = J/(m s). So F_d = (J/m^3)/(J/(m s)) = s/m^2. G = 1/(F_k+F_d) m^2/s. Good.

Now compute approximate values: L_v/(R_v T) = 2.5e6/(461.5*273.15) ≈ 2.5e6/126000 ≈ 19.84. So L_v/(R_v T) - 1 ≈ 18.84. L_v rho_l/(K T) = 2.5e6 * 1000 / (0.0243 * 273.15) = 2.5e9 / (6.637) ≈ 3.77e8 s/m^2? Let's compute: 0.0243*273.15 ≈ 6.637. 2.5e9/6.637 ≈ 3.767e8 s/m^2. Then F_k = 18.84 * 3.767e8 ≈ 7.10e9 s/m^2. F_d: rho_l R_v T = 1000 * 461.5 * 273.15 ≈ 1000 * 126000 ≈ 1.26e8 J/m^3. D_v = D_v_1atm * (101325/80000) = 2.26e-5 * 1.2666 ≈ 2.86e-5 m^2/s. e_s = 611.2 Pa. D_v e_s = 2.86e-5 * 611.2 ≈ 0.0175 J/(m s). F_d = 1.26e8 / 0.0175 ≈ 7.20e9 s/m^2. So F_k + F_d ≈ 1.43e10 s/m^2. G = 1/1.43e10 ≈ 7.0e-11 m^2/s.

Now integral_r = N * r0. N = LWC / (rho_l * (4/3 pi mean_r3)). mean_r3 = r0^3 + 3 r0 sigma^2 = (4e-6)^3 + 3*4e-6*(0.6e-6)^2 = 64e-18 + 12e-6*0.36e-12 = 64e-18 + 4.32e-18 = 68.32e-18 = 6.832e-17 m^3. Volume = 4/3 pi * 6.832e-17 ≈ 2.86e-16 m^3. Mass = 1000 * 2.86e-16 = 2.86e-13 kg. LWC = 0.2e-3 = 2e-4 kg/m^3. N = 2e-4 / 2.86e-13 ≈ 7.0e8 m^-3. integral_r = 7e8 * 4e-6 = 2800 m^-2.

Now C = (alpha/beta)*w. Compute alpha: term1 = L_v/(c_p R_v T^2) = 2.5e6/(1005*461.5*74600) ≈ 2.5e6/(1005*461.5*74600). 461.5*74600 ≈ 34,400,000. 1005*34,400,000 ≈ 3.46e10. term1 ≈ 7.23e-5 kg/J? Actually units kg/J. term2 = 1/(R_d T) = 1/(287*273.15) ≈ 1/78400 ≈ 1.275e-5 kg/J. alpha = 9.81*(7.23e-5 - 1.275e-5) = 9.81*5.955e-5 ≈ 5.84e-4 1/m. beta = 1/q_vs + L_v^2/(c_p R_v T^2). q_vs ≈ 0.00479, 1/q_vs ≈ 208.7. L_v^2 = 6.25e12. c_p R_v T^2 = 1005*461.5*74600 ≈ 3.46e10. L_v^2/(c_p R_v T^2) ≈ 6.25e12/3.46e10 ≈ 180.6. beta ≈ 208.7+180.6 = 389.3. alpha/beta ≈ 5.84e-4/389.3 ≈ 1.5e-6 1/m. C = 1.5e-6 * 8 = 1.2e-5 1/s.

Now s = C * rho_a / (4 pi rho_l G integral_r) = 1.2e-5 * 1.02 / (4*3.1416*1000*7e-11*2800). Denominator: 4*3.1416 ≈ 12.566. 12.566*1000=12566. 12566*7e-11=8.8e-7. 8.8e-7*2800=0.002464. So s ≈ 1.224e-5 / 0.002464 ≈ 0.00497. s_percent ≈ 0.497%. That's about 0.5%, which is a reasonable supersaturation for a cumulus cloud. So the code with the full G gives ~0.5%. If we used the simplified G (missing -1), F_k would be L_v^2 rho_l/(K R_v T^2) = (L_v/(R_v T)) * (L_v rho_l/(K T)) = 19.84 * 3.77e8 ≈ 7.48e9. Then F_k + F_d ≈ 7.48e9 + 7.20e9 = 1.468e10, G ≈ 6.81e-11, slightly larger G, so s would be slightly smaller: s_percent ≈ 0.497 * (7.0/6.81) ≈ 0.51%? Actually G in denominator, so larger G gives smaller s. Wait, G = 1/(F_k+F_d). Simplified F_k is larger (19.84 vs 18.84 factor), so F_k+F_d larger, G smaller, s larger. Let's compute: simplified F_k = 19.84*3.77e8 = 7.48e9, F_d=7.20e9, sum=1.468e10, G=6.81e-11. Full F_k=18.84*3.77e8=7.10e9, sum=1.43e10, G=7.0e-11. So simplified G is slightly smaller (6.81e-11 vs 7.0e-11), so s would be larger by factor 7.0/6.81 ≈ 1.028, so s_percent ~0.51%. The difference is small (~3%). Both are plausible. The problem likely expects the full expression, but many textbooks use the simplified one. Since the original code used the simplified termA (missing -1), maybe that was intentional? But the original code had termA = L_v^2 rho_l/(K R_v T^2) and termB = rho_l R_v T/(D_v e_s). That's exactly the simplified G. However, the original code also had a bug in the return type. The user might have written that code and it failed due to return type. The instruction: "Your solve() function failed to run. Fix the bug and return the corrected function." The bug that caused the failure is the return type. But there might be other bugs. The problem says "Fix the bug and return the corrected function." It doesn't say to improve the physics. However, the original code's G expression is a common approximation. I'll keep the original G expression but fix the return type. But wait, the original code had termA and termB as described, and G = 1/(termA + termB). That is the simplified G. It's not necessarily a bug; it's a valid approximation. The error message only mentioned the return type. So I'll just fix the return type. However, I should also check if there are any other runtime errors. The code uses math.pi, so it imports math. That's fine. The only runtime error is returning a list instead of a dict. So I'll change the return statement to return a dict with key "1".

But let's double-check the original code's termA: L_v**2 * rho_l / (K * R_v * T**2). That's exactly what I computed as the first part of F_k. So it's the simplified G. I'll leave it as is, because the problem might expect that. However, to be safe, I could include the full expression, but the original code didn't have it. The user might have written it that way. The instruction is to fix the bug that caused the failure. The failure is the return type. So I'll just fix that.

But wait: The problem statement says "Your solve() function failed to run. Fix the bug and return the corrected function." It might be that the only bug is the return type. I'll provide the corrected function with the return type fixed. I'll also ensure the code is clean.

Let's review the original code for any other potential issues: 
- It uses `O.6` in the problem statement but `0.6` in code. That's fine.
- It uses `0 . 2 \mathrm { g }
~~~~

#### `deepseek-v4-pro-reasoning` · core_code · run 3 · **PASS**

Source: `experiments/core_code/deepseek-v4-pro-reasoning.run3.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `0.5288263945568786` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    # Given parameters
    mean_radius=4e-6,          # m (4 μm)
    std_radius=0.6e-6,         # m (0.6 μm)
    LWC=0.2e-3,                # kg/m^3 (0.2 g/m^3)
    w=8.0,                     # m/s updraft
    T=273.15,                  # K (0°C)
    p=80e3,                    # Pa (80 kPa)
    # Physical constants
    R_d=287.04,                # J/(kg K)
    R_v=461.5,                 # J/(kg K)
    c_p=1005.0,                # J/(kg K)
    L_v=2.5e6,                 # J/kg
    g=9.81,                    # m/s^2
    rho_l=1000.0,              # kg/m^3
    e_s_0C=611.2,              # Pa
    D_v0=2.11e-5,              # m^2/s at 0°C, 101325 Pa
    p0=101325.0,               # Pa
    K=0.0243,                  # J/(s m K) thermal conductivity of air
):
    # Air density
    rho_a = p / (R_d * T)
    
    # Saturation vapor pressure and mixing ratio
    e_s = e_s_0C
    epsilon = R_d / R_v
    q_vs = epsilon * e_s / (p - e_s)
    
    # Diffusivity adjusted for pressure (same temperature)
    D_v = D_v0 * (p0 / p)
    
    # a1 and a2
    term1_a1 = (L_v * g) / (c_p * R_v * T**2)
    term2_a1 = g / (R_d * T)
    a1 = term1_a1 - term2_a1
    
    a2 = 1.0 / q_vs + (L_v**2) / (c_p * R_v * T**2)
    
    # F factor for droplet growth
    F = (rho_l * L_v**2) / (K * R_v * T**2) + (rho_l * R_v * T) / (D_v * e_s)
    
    # Moments of the Gaussian droplet spectrum
    # M_3 = integral of r^3 n(r) dr = (3/(4π)) * (LWC / rho_l)
    M3 = (3.0 / (4.0 * math.pi)) * (LWC / rho_l)
    # For Gaussian: E[r] = mean, E[r^3] = mean^3 + 3*mean*var
    mu = mean_radius
    sigma = std_radius
    moment_ratio = mu / (mu**3 + 3.0 * mu * sigma**2)
    M1 = M3 * moment_ratio
    
    # Steady-state supersaturation (fraction)
    s = (a1 * w * rho_a * F) / (4.0 * math.pi * a2 * rho_l * M1)
    
    # Express as percentage
    s_percent = s * 100.0
    
    return {"1": {"value": s_percent, "unit": "%"}}
```
~~~~

### Mid/low-tier failures (Qwen-3.6-27B spans orders of magnitude across its three runs)

#### `qwen3.6-27b` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/qwen3.6-27b.run1.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `5.566051868782093e+20` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
To solve this problem, we need to estimate the supersaturation in a developing cumulus cloud. The supersaturation is determined by the balance between the production of water vapor (due to adiabatic cooling in the updraft) and the consumption of water vapor (due to condensation onto cloud droplets).

### 1. Physical Principles

The rate of change of supersaturation $S$ (expressed as a fraction, e.g., 0.01 for 1%) with time $t$ is given by the equation:
$$ \frac{dS}{dt} = \frac{L^2 \rho_d}{R_v T^2 P} w \frac{dT_{ad}}{dz} - \pi \rho_w \int_0^\infty r^2 K(T, P, S) n(r) dr $$
However, a more common and simplified approach for estimating the *equilibrium* or *peak* supersaturation in a developing cloud involves balancing the vapor supply from the updraft against the condensation sink.

A widely used approximation for the supersaturation $S$ (in percent) in a cloud with a given droplet spectrum is derived from the Bergeron-Findeisen or Köhler theory considerations, but specifically for the *growth* phase, we often look at the time scale of condensation.

Let's use the standard formulation for the rate of change of supersaturation:
$$ \frac{dS}{dt} = \frac{L^2 \rho_v}{R_v T^2 P} w \Gamma_d - \pi \rho_w \int_0^\infty r^2 K S n(r) dr $$
Where:
- $S$ is supersaturation (fraction).
- $w$ is updraft velocity.
- $\Gamma_d$ is the dry adiabatic lapse rate ($\approx 9.8 \, \text{K/km}$).
- $L$ is latent heat of vaporization.
- $\rho_v$ is vapor density.
- $R_v$ is gas constant for water vapor.
- $T$ is temperature.
- $P$ is pressure.
- $\rho_w$ is density of liquid water.
- $K$ is the condensation coefficient (kinetic growth rate factor).
- $n(r)$ is the droplet size distribution.

At the peak supersaturation, $\frac{dS}{dt} \approx 0$. Thus:
$$ S_{peak} \approx \frac{\frac{L^2 \rho_v}{R_v T^2 P} w \Gamma_d}{\pi \rho_w K \int_0^\infty r^2 n(r) dr} $$

Let's break down the terms:

**1. Vapor Supply Term (Numerator):**
The term $A = \frac{L^2 \rho_v}{R_v T^2 P} w \Gamma_d$ represents the rate of supersaturation generation.
Note: $\rho_v \approx \frac{e_s}{R_v T}$ where $e_s$ is saturation vapor pressure.
So, $A = \frac{L^2 e_s}{R_v^2 T^3 P} w \Gamma_d$.

**2. Condensation Sink Term (Denominator):**
The term $B = \pi \rho_w K \int_0^\infty r^2 n(r) dr$ represents the condensation sink.
The integral $\int_0^\infty r^2 n(r) dr$ is related to the surface area concentration of the droplets.
Let $N$ be the total droplet concentration and $\bar{r^2}$ be the mean square radius.
$\int_0^\infty r^2 n(r) dr = N \langle r^2 \rangle$.

For a Gaussian distribution $n(r) = N \frac{1}{\sqrt{2\pi}\sigma} \exp\left(-\frac{(r-\mu)^2}{2\sigma^2}\right)$:
- Mean radius $\mu = 4 \, \mu\text{m}$.
- Standard deviation $\sigma = 0.6 \, \mu\text{m}$.
- $\langle r^2 \rangle = \mu^2 + \sigma^2$.

We need to find $N$ (total droplet concentration). We are given the cloud water content $W$ (liquid water content, LWC).
$W = \rho_w \int_0^\infty \frac{4}{3} \pi r^3 n(r) dr = \rho_w \frac{4}{3} \pi N \langle r^3 \rangle$.
For a Gaussian distribution, $\langle r^3 \rangle = \mu^3 + 3\mu\sigma^2$.
So, $N = \frac{W}{\rho_w \frac{4}{3} \pi (\mu^3 + 3\mu\sigma^2)}$.

**3. Condensation Coefficient $K$:**
The kinetic growth rate of a droplet is given by:
$$ \frac{dr}{dt} = \frac{K S}{r} $$
Where $K$ is defined as:
$$ K = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}} $$
Wait, the standard form for the condensation current is often simplified. Let's use the explicit formula for the condensation sink coefficient $K_{cond}$ in the equation $\frac{dS}{dt} = \dots - S \cdot \pi \rho_w K_{eff} \int r^2 n(r) dr$.
Actually, the term in the denominator is often written as $K \pi \rho_w \int r^2 n(r) dr$ where $K$ is the "condensation coefficient" with units of $m^2/s$.
The standard expression for the condensation rate constant $K$ (often denoted as $\beta$ or similar in different texts) for a single droplet of radius $r$ is:
$$ \frac{dm}{dt} = 4 \pi r D_v \rho_v \frac{L}{R_v T^2} \frac{S}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}} $$
This is complex because $K$ depends on $r$. However, for small droplets (micron scale), the thermal resistance term is often significant.
Let's use the approximation for the condensation sink $CS$:
$$ CS = \pi \rho_w \int_0^\infty r^2 K(r) n(r) dr $$
Where $K(r) = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}}$.
Let $K_0 = \frac{D_v \rho_v L}{\rho_w R_v T^2}$. This is the kinetic limit.
Then $K(r) = \frac{K_0}{1 + \frac{r_c}{r}}$ where $r_c = \frac{L^2 \rho_v}{4 \pi k T^2}$.
Note: $\rho_v$ here is the vapor density. $\rho_v = \frac{e_s}{R_v T}$.

So, $S_{peak} = \frac{A}{CS}$.

### 2. Constants and Parameters

- $w = 8 \, \text{m/s}$
- $T = 0^\circ \text{C} = 273.15 \, \text{K}$
- $P = 80 \, \text{kPa} = 80,000 \, \text{Pa}$
- $W = 0.2 \, \text{g/m}^3 = 0.2 \times 10^{-3} \, \text{kg/m}^3$
- $\mu = 4 \, \mu\text{m} = 4 \times 10^{-6} \, \text{m}$
- $\sigma = 0.6 \, \mu\text{m} = 0.6 \times 10^{-6} \, \text{m}$
- $\rho_w = 1000 \, \text{kg/m}^3$
- $L = 2.5 \times 10^6 \, \text{J/kg}$ (Latent heat of vaporization at 0°C)
- $R_v = 461.5 \, \text{J/(kg K)}$
- $R_d = 287.05 \, \text{J/(kg K)}$
- $\Gamma_d = 9.8 \, \text{K/km} = 0.0098 \, \text{K/m}$
- $D_v = 2.2 \times 10^{-5} \, \text{m}^2/\text{s}$ (Diffusivity of water vapor in air at 0°C, 1 atm. Adjust for pressure? $D_v \propto P^{-1}$. At 80 kPa, $D_v \approx 2.2 \times 10^{-5} \times \frac{101.3}{80} \approx 2.78 \times 10^{-5} \, \text{m}^2/\text{s}$)
- $k = 0.024 \, \text{W/(m K)}$ (Thermal conductivity of air at 0°C)
- $e_s$: Saturation vapor pressure over water at 0°C. $e_s(0^\circ \text{C}) \approx 611 \, \text{Pa}$.

### 3. Step-by-Step Calculation

1.  **Calculate Saturation Vapor Pressure $e_s$**:
    Using Magnus formula or standard value. At 0°C, $e_s = 611.2 \, \text{Pa}$.

2.  **Calculate Vapor Density $\rho_v$**:
    $\rho_v = \frac{e_s}{R_v T}$

3.  **Calculate Total Droplet Concentration $N$**:
    $\langle r^3 \rangle = \mu^3 + 3\mu\sigma^2$
    $N = \frac{W}{\rho_w \frac{4}{3} \pi \langle r^3 \rangle}$

4.  **Calculate Mean Square Radius $\langle r^2 \rangle$**:
    $\langle r^2 \rangle = \mu^2 + \sigma^2$

5.  **Calculate Condensation Coefficient Parameters**:
    $K_0 = \frac{D_v \rho_v L}{\rho_w R_v T^2}$
    $r_c = \frac{L^2 \rho_v}{4 \pi k T^2}$

6.  **Calculate Condensation Sink $CS$**:
    We need to integrate $K(r) r^2 n(r)$.
    $CS = \pi \rho_w \int_0^\infty \frac{K_0}{1 + r_c/r} r^2 n(r) dr = \pi \rho_w K_0 \int_0^\infty \frac{r^3}{r + r_c} n(r) dr$.
    Since the distribution is narrow ($\sigma \ll \mu$), we can approximate the integral by evaluating the integrand at the mean radius $\mu$ or using the moments.
    Approximation: $\int \frac{r^3}{r+r_c} n(r) dr \approx \frac{\langle r^3 \rangle}{\mu + r_c}$? Or better, $\int r^2 K(r) n(r) dr \approx K(\mu) \langle r^2 \rangle N$?
    Let's check the variation. $K(r)$ varies with $r$.
    $K(r) = \frac{K_0 r}{r + r_c}$.
    Term in integral: $r^2 K(r) = \frac{K_0 r^3}{r + r_c}$.
    Let's approximate $\int \frac{r^3}{r+r_c} n(r) dr \approx \frac{\langle r^3 \rangle}{\mu + r_c}$ is a bit rough.
    A better approximation for narrow distributions is to expand around $\mu$.
    However, given the Gaussian shape, we can compute the integral numerically or use the approximation:
    $\int_0^\infty f(r) n(r) dr \approx f(\mu) N$ if $f$ is slowly varying.
    Let's evaluate $f(r) = \frac{r^3}{r+r_c}$.
    $CS \approx \pi \rho_w K_0 N \frac{\mu^3}{\mu + r_c}$.
    
    Let's refine the "Vapor Supply" term $A$.
    $A = \frac{L^2 \rho_v}{R_v T^2 P} w \Gamma_d$.
    Wait, the standard formula for supersaturation generation rate is:
    $\frac{dS}{dt} = \frac{L^2 \rho_d}{R_v T^2 P} w \Gamma_d$?
    Let's derive it.
    $S = \frac{e - e_s}{e_s}$.
    $\frac{dS}{dt} = \frac{1}{e_s} \frac{de}{dt} - \frac{e}{e_s^2} \frac{de_s}{dt}$.
    Assuming $e \approx e_s$ (near saturation), $\frac{dS}{dt} \approx \frac{1}{e_s} (\frac{de}{dt} - \frac{de_s}{dt})$.
    $\frac{de_s}{dt} = \frac{de_s}{dT} \frac{dT}{dt} = \frac{de_s}{dT} (-w \Gamma_d)$.
    $\frac{de}{dt}$ is the change in actual vapor pressure. In an adiabatic updraft, if no condensation occurred, $e$ would stay constant (relative to the parcel's mixing ratio), but $e_s$ drops.
    Actually, the standard term is:
    $\frac{dS}{dt} = \frac{L^2 \rho_v}{R_v T^2 P} w \Gamma_d$ is incorrect dimensionally or conceptually?
    Let's use the form:
    $\frac{dS}{dt} = \frac{L^2 \rho_d}{R_v T^2 P} w \Gamma_d$? No.
    
    Correct derivation:
    $\frac{dS}{dt} = \frac{1}{e_s} \frac{de}{dt} - \frac{1}{e_s} \frac{de_s}{dt}$ (assuming $e \approx e_s$).
    $\frac{de_s}{dt} = \frac{L e_s}{R_v T^2} \frac{dT}{dt} = \frac{L e_s}{R_v T^2} (-w \Gamma_d)$.
    So the source term is $-\frac{1}{e_s} \frac{de_s}{dt} = \frac{L w \Gamma_d}{R_v T^2}$.
    Wait, where does the density come in?
    The supersaturation $S$ is defined as $\frac{e - e_s}{e_s}$.
    The rate of change of vapor mixing ratio $q_v$ due to lifting is zero (conservation of mass).
    $e = \frac{q_v P}{\epsilon + q_v} \approx \frac{q_v P}{\epsilon}$.
    $\frac{de}{dt} = \frac{q_v}{\epsilon} \frac{dP}{dt} = \frac{e}{P} \frac{dP}{dt}$.
    $\frac{dP}{dt} = -\rho_d g w$.
    So $\frac{de}{dt} = -\frac{e \rho_d g w}{P}$.
    Using Ideal Gas Law for dry air: $\rho_d = \frac{P_d}{R_d T} \approx \frac{P}{R_d T}$.
    $\frac{de}{dt} = -\frac{e g w}{R_d T}$.
    
    So, $\frac{dS}{dt} = \frac{1}{e_s} (-\frac{e g w}{R_d T}) - \frac{1}{e_s} (\frac{L e_s}{R_v T^2} (-w \Gamma_d))$.
    At saturation $e \approx e_s$.
    $\frac{dS}{dt} = -\frac{g w}{R_d T} + \frac{L w \Gamma_d}{R_v T^2}$.
    Note that $\Gamma_d = \frac{g}{C_p}$. And $\frac{L}{R_v T^2}$ is related to Clausius-Clapeyron.
    Usually, the second term dominates.
    Let's check the magnitude.
    Term 1: $\frac{9.8 \times 8}{287 \times 273} \approx \frac{78.4}{78351} \approx 0.001$.
    Term 2: $\frac{2.5 \times 10^6 \times 8 \times 0.0098}{461.5 \times 273^2} \approx \frac{196000}{34400000} \approx 0.0057$.
    
    Actually, there is a more standard form found in cloud physics textbooks (e.g., Pruppacher & Klett):
    $\frac{dS}{dt} = \frac{L^2 \rho_d}{R_v T^2 P} w \Gamma_d$?
    Let's re-evaluate $\frac{de_s}{dt}$.
    $\frac{de_s}{dT} = \frac{L e_s}{R_v T^2}$.
    $\frac{de_s}{dt} = \frac{L e_s}{R_v T^2} (-w \Gamma_d)$.
    Source term for S: $-\frac{1}{e_s} \frac{de_s}{dt} = \frac{L w \Gamma_d}{R_v T^2}$.
    
    Is there a $\rho_d$ term?
    Some formulations use $S$ as mixing ratio supersaturation.
    Let's stick to $S = (e-e_s)/e_s$.
    Source $A = \frac{L w \Gamma_d}{R_v T^2}$.
    
    Let's check units:
    $L$: J/kg. $w$: m/s. $\Gamma_d$: K/m. $R_v$: J/kg/K. $T$: K.
    $A$: $\frac{(J/kg) (m/s) (K/m)}{(J/kg/K) K^2} = \frac{J/kg \cdot 1/s}{J/kg \cdot K} = \frac{1}{s \cdot K}$? No.
    $\frac{L w \Gamma_d}{R_v T^2} \rightarrow \frac{(J/kg) (m/s) (K/m)}{(J/kg/K) K^2} = \frac{J/kg \cdot 1/s}{J/kg \cdot K} = \frac{1}{s \cdot K}$?
    Wait. $R_v T^2$ has units $(J/kg/K) K^2 = J \cdot K / kg$.
    Numerator: $J/kg \cdot m/s \cdot K/m = J \cdot K / (kg \cdot s)$.
    Result: $1/s$. Correct.

    So, $A = \frac{L w \Gamma_d}{R_v T^2}$.

    Now for the Sink $B$.
    $\frac{dS}{dt} = - S \cdot \pi \rho_w \int r^2 K(r) n(r) dr$.
    $B = \pi \rho_w \int r^2 K(r) n(r) dr$.
    
    $S_{peak} = A / B$.

### 4. Implementation Details

- **Constants**:
  - $L = 2.501 \times 10^6$ J/kg
  - $R_v = 461.5$ J/kg/K
  - $R_d = 287.05$ J/kg/K
  - $\rho_w = 1000$ kg/m³
  - $k = 0.024$ W/m/K
  - $D_v$: At 0°C and 1013 hPa, $D_v \approx 2.2 \times 10^{-5}$ m²/s.
    At 80 kPa, $D_v = 2.2 \times 10^{-5} \times \frac{101325}{80000}$.
  - $e_s = 611.2$ Pa.
  - $\Gamma_d = 0.0098$ K/m.

- **Distribution**:
  - $\mu = 4 \times 10^{-6}$ m.
  - $\sigma = 0.6 \times 10^{-6}$ m.
  - $W = 0.2 \times 10^{-3}$ kg/m³.

- **Calculations**:
  1. $\rho_v = e_s / (R_v T)$.
  2. $N = W / (\rho_w \frac{4}{3} \pi (\mu^3 + 3\mu\sigma^2))$.
  3. $K_0 = D_v \rho_v L / (\rho_w R_v T^2)$.
  4. $r_c = L^2 \rho_v / (4 \pi k T^2)$.
  5. Approximate Integral $I = \int r^2 K(r) n(r) dr$.
     Using $K(r) = K_0 \frac{r}{r+r_c}$.
     $I \approx N \frac{\mu^3}{\mu + r_c} K_0$?
     Let's use a slightly more accurate approximation for the integral of $r^2 \frac{r}{r+r_c} n(r)$.
     Since the distribution is narrow, we can evaluate the function $f(r) = \frac{r^3}{r+r_c}$ at $\mu$.
     $I \approx N K_0 \frac{\mu^3}{\mu + r_c}$.
  6. $B = \pi \rho_w I$.
  7. $A = L w \Gamma_d / (R_v T^2)$.
  8. $S_{frac} = A / B$.
  9. $S_{percent} = S_{frac} \times 100$.

Let's double check the $A$ term.
Some sources define $A = \frac{L^2 \rho_d w \Gamma_d}{R_v T^2 P}$.
Let's check if $\frac{L w \Gamma_d}{R_v T^2}$ is equivalent to $\frac{L^2 \rho_d w \Gamma_d}{R_v T^2 P}$.
$\rho_d = P / (R_d T)$.
$\frac{L^2 (P/R_d T) w \Gamma_d}{R_v T^2 P} = \frac{L^2 w \Gamma_d}{R_v R_d T^3}$.
This is different from $\frac{L w \Gamma_d}{R_v T^2}$.
Which one is correct?
The term $\frac{de_s}{dt} = \frac{L e_s}{R_v T^2} \frac{dT}{dt}$.
$\frac{dS}{dt} = -\frac{1}{e_s} \frac{de_s}{dt} = \frac{L}{R_v T^2} (-\frac{dT}{dt}) = \frac{L w \Gamma_d}{R_v T^2}$.
This derivation assumes $S = (e-e_s)/e_s$.
The other form might be for mixing ratio supersaturation $S_q = (q-q_s)/q_s$.
$q_s = 0.622 e_s / P$.
$\frac{dS_q}{dt} \approx \frac{1}{q_s} \frac{dq_s}{dt}$.
$\frac{dq_s}{dt} = \frac{0.622}{P} \frac{de_s}{dt} - \frac{0.622 e_s}{P^2} \frac{dP}{dt}$.
This gets complicated. The standard "supersaturation" in cloud physics problems usually refers to relative humidity excess, i.e., $S = (e-e_s)/e_s$.
I will use $A = \frac{L w \Gamma_d}{R_v T^2}$.

One correction: The condensation sink term $B$ has units of $1/s$.
$K_0$ units:
$D_v$: m²/s. $\rho_v$: kg/m³. $L$: J/kg. $\rho_w$: kg/m³. $R_v$: J/kg/K. $T$: K.
$K_0 = \frac{(m^2/s)(kg/m^3)(J/kg)}{(kg/m^3)(J/kg/K)K^2} = \frac{m^2/s \cdot J/m^3}{J/m^3 \cdot K} = \frac{m^2}{s \cdot K}$?
Wait. $K(r)$ in $\frac{dr}{dt} = \frac{K S}{r}$ has units of m²/s.
My $K_0$ definition:
$\frac{dr}{dt} = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{S}{r} \frac{1}{1 + \dots}$.
So the coefficient in front of $S/r$ is $K_{kin}$.
$K_{kin} = \frac{D_v \rho_v L}{\rho_w R_v T^2}$.
Units: $\frac{(m^2/s)(kg/m^3)(J/kg)}{(kg/m^3)(J/kg/K)K^2} = \frac{m^2/s \cdot J/m^3}{J/m^3 \cdot K} = \frac{m^2}{s \cdot K}$?
No. $R_v T^2$ is $J \cdot K / kg$.
Numerator: $m^2/s \cdot kg/m^3 \cdot J/kg = J \cdot m^2 / (s \cdot m^3) = J / (s \cdot m)$.
Denominator: $kg/m^3 \cdot J \cdot K / kg = J \cdot K / m^3$.
Result: $\frac{J / (s \cdot m)}{J \cdot K / m^3} = \frac{m^2}{s \cdot K}$.
So $K_{kin}$ has units $m^2/(s \cdot K)$?
But $\frac{dr}{dt}$ is m/s. $S$ is dimensionless. $r$ is m.
$\frac{K S}{r} \rightarrow \frac{[K]}{m}$.
So $[K]$ must be $m^2/s$.
Where did the K go?
Ah, $L$ is J/kg. $R_v$ is J/kg/K.
$\frac{L}{R_v T^2}$ has units $\frac{J/kg}{(J/kg/K) K^2} = \frac{1}{K}$.
So $K_{kin} = D_v \frac{\rho_v}{\rho_w} \frac{L}{R_v T^2}$.
Units: $m^2/s \cdot 1 \cdot 1/K = m^2/(s \cdot K)$.
This implies $\frac{dr}{dt} = \frac{K_{kin} S}{r}$ is wrong dimensionally if $K_{kin}$ has $1/K$.
The formula is $\frac{dr}{dt} = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{S}{r}$.
Let's check the Clausius Clapeyron factor.
$\frac{de_s}{dT} = \frac{L e_s}{R_v T^2}$.
The driving force is $\frac{e - e_s}{e_s} = S$.
The flux is proportional to $\nabla e$.
The standard result is $\frac{dr}{dt} = \frac{K S}{r}$ where $K = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \dots}$.
Let's re-verify units of $K$.
$D_v$: m²/s.
$\rho_v$: kg/m³.
$L$: J/kg.
$\rho_w$: kg/m³.
$R_v$: J/kg/K.
$T$: K.
$\frac{D_v \rho_v L}{\rho_w R_v T^2} = \frac{(m^2/s)(kg/m^3)(J/kg)}{(kg/m^3)(J/kg/K)K^2} = \frac{m^2/s \cdot J/m^3}{J/m^3 \cdot K} = \frac{m^2}{s \cdot K}$.
There is a missing $T$ or something?
Actually, the term is often written as $\frac{D_v \rho_v L}{\rho_w R_v T^2}$.
If $S$ is defined as $\frac{e-e_s}{e_s}$, then the gradient is $\frac{e_s S}{r}$.
Flux $J = -D_v \nabla \rho_v \approx -D_v \frac{\rho_v}{e_s} \nabla e$.
$\nabla e \approx \frac{e_s S}{r}$.
$J = -D_v \frac{\rho_v}{e_s} \frac{e_s S}{r} = -D_v \frac{\rho_v S}{r}$.
Mass accretion $\frac{dm}{dt} = 4 \pi r^2 J = -4 \pi r D_v \rho_v S$.
$\frac{dm}{dt} = 4 \pi r^2 \rho_w \frac{dr}{dt}$.
$4 \pi r^2 \rho_w \frac{dr}{dt} = 4 \pi r D_v \rho_v S$.
$\frac{dr}{dt} = \frac{D_v \rho_v}{\rho_w r} S$.
This is the purely diffusive limit.
The thermal resistance adds the factor $\frac{L}{R_v T^2}$?
No, the thermal resistance modifies the effective diffusivity.
The combined coefficient is $K = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}}$?
Let's check the units of the thermal term.
$\frac{L^2 \rho_v}{4 \pi k T^2 r}$.
$L^2$: J²/kg². $\rho_v$: kg/m³. $k$: W/m/K = J/s/m/K. $T^2$: K². $r$: m.
Num: $J^2/kg^2 \cdot kg/m^3 = J^2/(kg \cdot m^3)$.
Den: $J/s/m/K \cdot K^2 \cdot m = J \cdot K / s$.
Ratio: $\frac{J^2/(kg \cdot m^3)}{J \cdot K / s} = \frac{J \cdot s}{kg \cdot m^3 \cdot K}$.
This doesn't look dimensionless.
The standard formula is:
$\frac{dr}{dt} = \frac{S}{r} \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r} \frac{R_v T^2}{L}}$?
Actually, the term is $\frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r} \frac{1}{\dots}}$.
Let's use the explicit $K$ value from literature.
At 0°C, $K \approx 1.5 \times 10^{-10} \, \text{m}^2/\text{s}$?
Let's calculate $K_{diff} = \frac{D_v \rho_v}{\rho_w}$.
$\rho_v = 611 / (461.5 \times 273) \approx 0.00485$ kg/m³.
$D_v \approx 2.8 \times 10^{-5}$.
$K_{diff} = \frac{2.8 \times 10^{-5} \times 0.00485}{1000} \approx 1.36 \times 10^{-10}$ m²/s.
This matches the order of magnitude.
The thermal correction factor is $\frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r} \frac{R_v T^2}{L}}$?
The term in the denominator is $\frac{L \rho_v}{4 \pi k T r}$?
Let's use the formula:
$K = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}}$.
Wait, if I use $K_{diff} = \frac{D_v \rho_v}{\rho_w}$, then the factor $\frac{L}{R_v T^2}$ is extra.
The correct formula for $\frac{dr}{dt}$ is:
$\frac{dr}{dt} = \frac{S}{r} \frac{D_v \rho_v}{\rho_w} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r} \frac{R_v T^2}{L}}$?
No, the standard form is:
$\frac{dr}{dt} = \frac{S}{r} K_{eff}$.
$K_{eff} = \frac{D_v \rho_v L}{\rho_w R_v T^2} \frac{1}{1 + \frac{L^2 \rho_v}{4 \pi k T^2 r}}$.
Let's assume this form and compute.

```python
import math

def solve():
    # Given values
    w = 8.0          # m/s
    T = 273.15       # K (0 C)
    P = 80000.0      # Pa (80 kPa)
    W = 0.2e-3       # kg/m^3 (0.2 g/m^3)
    mu = 4e-6        # m (4 um)
    sigma = 0.6e-6   # m (0.6 um)
    
    # Constants
    L = 2.501e6      # J/kg
    R_v = 461.5      # J/(kg K)
    R_d = 287.05     # J/(kg K)
    rho_w = 1000.0   # kg/m^3
    k = 0.024        # W/(m K)
    D_v_1atm = 2.2e-5 # m^2/s at 1 atm, 0 C
    P_1atm = 101325.0 # Pa
    e_s = 611.2      # Pa (saturation vapor pressure at 0 C)
    Gamma_d = 0.0098 # K/m (dry adiabatic lapse rate)
    
    # Adjust D_v for pressure
    D_v = D_v_1atm * (P_1atm / P)
    
    # Vapor density
    rho_v = e_s / (R_v * T)
    
    # Droplet concentration N
    # <r^3> for Gaussian
    r3_mean = mu**3 + 3 * mu * sigma**2
    N = W / (rho_w * (4/3) * math.pi * r3_mean)
    
    # Condensation coefficient parameters
    # K_0 is the kinetic limit coefficient for dr/dt = K_0 * S / r
    # Using the form K = (D_v * rho_v * L) / (rho_w * R_v * T^2) * 1 / (1 + r_c/r)
    K_0 = (D_v * rho_v * L) / (rho_w * R_v * T**2)
    r_c = (L**2 * rho_v) / (4 * math.pi * k * T**2)
    
    # Condensation Sink B
    # B = pi * rho_w * Integral(r^2 * K(r) * n(r) dr)
    # Approximate Integral ~ N * K(mu) * mu^2 ?
    # More accurately: Integral(r^2 * K(r) * n(r) dr) = N * <r^2 * K(r)>
    # K(r) = K_0 * r / (r + r_c)
    # Term = r^2 * K_0 * r / (r + r_c) = K_0 * r^3 / (r + r_c)
    # Approximate <r^3 / (r + r_c)> ~ mu^3 / (mu + r_c)
    
    K_mu = K_0 * mu / (mu + r_c)
    # Integral approx
    I = N * K_mu * mu**2 
    
    B = math.pi * rho_w * I
    
    # Supersaturation Generation Rate A
    # A = L * w * Gamma_d / (R_v * T^2)
    A = (L * w * Gamma_d) / (R_v * T**2)
    
    # Peak Supersaturation
    S_frac = A / B
    S_percent = S_frac * 100
    
    return {
        "1": {"value": S_percent, "unit": "%"}
    }
```
~~~~

#### `qwen3.6-27b` · core_code · run 2 · **FAIL**

Source: `experiments/core_code/qwen3.6-27b.run2.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `7143.4` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    mean_radius_um=4.0,
    std_dev_um=0.6,
    cloud_water_content_g_m3=0.2,
    updraft_speed_m_s=8.0,
    temperature_C=0.0,
    pressure_kPa=80.0
):
    """
    Estimate the supersaturation in a developing cumulus cloud.
    
    Parameters:
    -----------
    mean_radius_um : float
        Mean droplet radius in micrometers
    std_dev_um : float
        Standard deviation of droplet radius in micrometers
    cloud_water_content_g_m3 : float
        Cloud water content in g/m^3
    updraft_speed_m_s : float
        Updraft speed in m/s
    temperature_C : float
        Temperature in degrees Celsius
    pressure_kPa : float
        Pressure in kPa
    
    Returns:
    --------
    dict : Supersaturation as a percentage
    """
    
    # Constants
    rho_water = 1000.0  # kg/m^3, density of water
    R_d = 287.05  # J/(kg·K), gas constant for dry air
    R_v = 461.5  # J/(kg·K), gas constant for water vapor
    L_v = 2.501e6  # J/kg, latent heat of vaporization at 0°C
    T_K = temperature_C + 273.15  # Temperature in Kelvin
    P_Pa = pressure_kPa * 1000.0  # Pressure in Pascals
    
    # Convert units
    mean_radius_m = mean_radius_um * 1e-6  # m
    std_dev_m = std_dev_um * 1e-6  # m
    w_c_kg_m3 = cloud_water_content_g_m3 / 1000.0  # kg/m^3
    
    # Calculate the number concentration of droplets
    # For a Gaussian distribution, the total water content is:
    # w_c = rho_water * integral( (4/3)*pi*r^3 * n(r) dr )
    # where n(r) is the number concentration distribution
    # For a Gaussian: n(r) = N_total * (1/(sqrt(2*pi)*sigma)) * exp(-(r-r_mean)^2/(2*sigma^2))
    # 
    # The integral of r^3 * Gaussian can be computed analytically.
    # Let's compute the mean of r^3 for a Gaussian distribution centered at r_mean with std dev sigma.
    # E[r^3] = integral r^3 * (1/(sqrt(2*pi)*sigma)) * exp(-(r-r_mean)^2/(2*sigma^2)) dr
    # This equals: r_mean^3 + 3*r_mean*sigma^2
    # (Using the moments of a Gaussian distribution)
    
    mean_r_cubed = mean_radius_m**3 + 3 * mean_radius_m * std_dev_m**2
    
    # Total water content: w_c = rho_water * N_total * (4/3)*pi * E[r^3]
    # So: N_total = w_c / (rho_water * (4/3)*pi * E[r^3])
    
    N_total = w_c_kg_m3 / (rho_water * (4/3) * math.pi * mean_r_cubed)
    
    # Now estimate supersaturation using the growth rate equation.
    # The supersaturation S is related to the updraft velocity and droplet properties.
    # Using the simplified approach from cloud microphysics:
    # 
    # The maximum supersaturation in an updraft can be estimated using:
    # S_max ≈ (w * L_v) / (rho_air * c_p * T) * (some factor related to droplet growth)
    # 
    # A more detailed approach uses the competition between condensation and adiabatic cooling.
    # The supersaturation can be estimated from the balance between vapor supply (from updraft)
    # and vapor sink (condensation on droplets).
    #
    # Using the formula from Pruppacher and Klett (1978) or similar texts:
    # The supersaturation S (as a fraction) can be estimated as:
    # S = (w * L_v^2 * N_total) / (4 * pi * rho_air * c_p * T^2 * A)
    # where A is a coefficient related to droplet growth.
    #
    # A simpler empirical/semi-empirical approach:
    # For typical cumulus clouds, the supersaturation can be estimated using:
    # S (%) ≈ 0.1 * w (m/s) * sqrt(N_total (cm^-3)) / T(K)^0.5
    # But let's use a more physically-based approach.
    #
    # Using the approach from Rogers and Yau (1989):
    # The supersaturation at which droplet growth balances adiabatic cooling is:
    # S = (w * L_v) / (rho_air * c_p * T) * (1 / (1 + beta))
    # where beta accounts for the condensation sink.
    #
    # Let's use a standard formula for maximum supersaturation:
    # S_max = (w * L_v) / (rho_air * c_p * T) * sqrt( (pi * N_total) / (4 * A * rho_water) )
    # where A is the accommodation coefficient times some diffusivity terms.
    #
    # For simplicity, let's use the formula from Seifert and Beheng (2001) or similar:
    # S (%) = 100 * (w * L_v^2 * N_total) / (4 * pi * rho_air * c_p * T^2 * D_v * rho_water * r_mean)
    # where D_v is the diffusivity of water vapor.
    
    # Calculate air density
    rho_air = P_Pa / (R_d * T_K)  # kg/m^3
    
    # Specific heat of dry air at constant pressure
    c_p = 1005.0  # J/(kg·K)
    
    # Diffusivity of water vapor in air at 0°C and 80 kPa
    # D_v at 0°C and 101.3 kPa is approximately 2.1e-5 m^2/s
    # Adjust for pressure: D_v ∝ 1/P
    D_v_ref = 2.1e-5  # m^2/s at 101.3 kPa and 0°C
    D_v = D_v_ref * (101.3 / (pressure_kPa))  # Adjust for pressure
    
    # Accommodation coefficient (typically ~1 for water vapor)
    alpha = 1.0
    
    # Calculate supersaturation using a simplified growth rate balance
    # The supersaturation S (as a fraction) is given by:
    # S = (w * L_v) / (rho_air * c_p * T) * (1 / sqrt( (4 * pi * N_total * D_v * alpha * r_mean) / (rho_water * L_v^2 / (R_v * T^2)) ))
    #
    # Simplifying, we get:
    # S = (w * L_v) / (rho_air * c_p * T) * sqrt( (rho_water * L_v^2 / (R_v * T^2)) / (4 * pi * N_total * D_v * alpha * r_mean) )
    
    # Let's use a more direct formula from cloud physics literature:
    # S (%) = 100 * w * L_v / (rho_air * c_p * T) * sqrt( (rho_water * R_v * T^2) / (4 * pi * N_total * D_v * alpha * r_mean * L_v^2) )
    #
    # Actually, let me use the standard formula for maximum supersaturation in an updraft:
    # S_max = (w * L_v) / (rho_air * c_p * T) * (1 / (1 + (4 * pi * N_total * D_v * alpha * r_mean * rho_air * c_p * T) / (w * L_v^2)))
    #
    # For small supersaturations, this simplifies to:
    # S_max ≈ (w * L_v) / (rho_air * c_p * T) * sqrt( (rho_water) / (4 * pi * N_total * D_v * alpha * r_mean * (L_v^2 / (R_v * T^2))) )
    
    # Let me use a cleaner formulation. The supersaturation can be estimated as:
    # S = (w * L_v) / (rho_air * c_p * T) * (1 / sqrt(1 + (4 * pi * N_total * D_v * alpha * r_mean * rho_air * c_p * T * R_v * T^2) / (w * L_v^3 * rho_water)))
    #
    # For typical cumulus clouds, the second term in the denominator is often small, so:
    # S ≈ (w * L_v) / (rho_air * c_p * T)
    #
    # But this doesn't account for droplet number concentration. Let's use the full expression.
    
    # Calculate the adiabatic supersaturation (without condensation)
    S_adiabatic = (updraft_speed_m_s * L_v) / (rho_air * c_p * T_K)
    
    # Calculate the condensation sink term
    # The condensation rate per unit volume is proportional to N_total * r_mean * S
    # The balance gives: S = S_adiabatic / (1 + beta)
    # where beta = (4 * pi * N_total * D_v * alpha * r_mean * rho_air * c_p * T_K * R_v * T_K^2) / (updraft_speed_m_s * L_v^3 * rho_water)
    
    beta = (4 * math.pi * N_total * D_v * alpha * mean_radius_m * rho_air * c_p * T_K * R_v * T_K**2) / (updraft_speed_m_s * L_v**3 * rho_water)
    
    S_fraction = S_adiabatic / (1 + beta)
    
    # Convert to percentage
    S_percentage = S_fraction * 100
    
    return {
        "1": {"value": round(S_percentage, 2), "unit": "%"}
    }
```
~~~~

#### `qwen3.6-27b` · core_code · run 3 · **FAIL**

Source: `experiments/core_code/qwen3.6-27b.run3.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `1396059.942420474` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
To solve this problem, we need to estimate the supersaturation in a developing cumulus cloud. The supersaturation is determined by the balance between the production of water vapor (due to adiabatic ascent) and the consumption of water vapor (due to condensation onto cloud droplets).

### 1. Physical Principles and Equations

The rate of change of supersaturation $S$ with time $t$ is given by:
$$ \frac{dS}{dt} = \frac{dS_{adiabatic}}{dt} - \frac{dS_{condensation}}{dt} $$

In a steady state or for an estimate of the peak supersaturation, we often look at the point where the condensation sink balances the adiabatic cooling production, or we integrate the growth equation. However, a common approximation for the *peak* supersaturation $S_{max}$ in a developing cloud, before the droplet concentration stabilizes, involves the competition between the updraft velocity and the droplet growth rate.

A more rigorous approach for "estimating" supersaturation given a specific droplet spectrum and water content is to use the **Köhler theory** and the **diffusional growth equation**.

The rate of change of the radius of a droplet $r$ is given by:
$$ \frac{dr}{dt} = \frac{L^2 S \rho_v}{\rho_l R_v T^2} \left( \frac{1}{k + D \frac{\rho_l L}{R_v T^2}} \right)^{-1} $$
Wait, the standard form for the growth rate of a droplet radius $r$ due to condensation is:
$$ \frac{dr}{dt} = \frac{S}{r} \cdot \frac{D \rho_v L}{\rho_l R_v T} \cdot \frac{1}{1 + \frac{L \rho_v D}{k T}} $$
Let's simplify using the standard coefficient $K$:
$$ \frac{dr}{dt} = \frac{S}{r} K $$
where $K$ is a constant depending on temperature and pressure.

However, the problem asks for the supersaturation *given* the cloud water content and the spectrum. This implies we are looking for the supersaturation required to sustain the observed water content growth rate or the equilibrium supersaturation associated with the mean droplet size.

Actually, a standard method to estimate the supersaturation $S$ in a cloud with a known droplet concentration $N$ and updraft velocity $w$ is derived from the balance of vapor production and consumption. But here, $N$ is not directly given; instead, we have the water content $W$ and the spectrum parameters.

Let's calculate the droplet concentration $N$ from the water content $W$ and the mean radius $r_m$.
The mass of a single droplet is $m = \frac{4}{3} \pi r^3 \rho_l$.
If we assume the spectrum is narrow (Gaussian with $\sigma = 0.6$ vs $r_m = 4$), we can approximate the total water content as:
$$ W \approx N \cdot \frac{4}{3} \pi r_m^3 \rho_l $$
From this, we can find $N$:
$$ N = \frac{W}{\frac{4}{3} \pi r_m^3 \rho_l} $$

Once we have $N$, we can estimate the supersaturation. In many textbook problems of this type (e.g., from Pruppacher & Klett or similar atmospheric physics texts), the supersaturation is estimated using the relationship between the updraft velocity $w$, the droplet concentration $N$, and the diffusional growth properties.

The peak supersaturation $S_{max}$ is often approximated by:
$$ S_{max} \approx \left( \frac{w \cdot \Gamma \cdot \rho_d \cdot L}{N \cdot K \cdot T} \right)^{1/2} $$
This formula is complex and depends on specific derivations. Let's look for a simpler, more direct relationship often used in such estimation problems.

Another common approximation relates the supersaturation to the mean radius and the growth time.
$$ r^2 = 2 K S t $$
And the height $z = w t$.
So $r^2 = \frac{2 K S z}{w}$.
This requires knowing the height $z$, which is not given.

Let's reconsider the "steady state" or "quasi-equilibrium" assumption. If the cloud is "developing", the supersaturation might be determined by the balance between the adiabatic production of supersaturation and the condensation sink.
The rate of change of supersaturation due to adiabatic expansion is:
$$ \frac{dS}{dt} \approx \frac{w \cdot \Gamma_d \cdot \rho_d \cdot L}{\rho_l \cdot R_v \cdot T^2} $$
Let's call this production rate $P$.
The rate of consumption of supersaturation by condensation onto $N$ droplets of mean radius $r$ is:
$$ \frac{dS}{dt} \approx - N \cdot 4 \pi r \cdot \frac{D \rho_v}{R_v T} \cdot S \cdot (\text{correction for heat}) $$
Actually, the condensation sink $A$ is defined such that $\frac{dS}{dt} = - A S$.
The coefficient $A$ for a population of droplets is:
$$ A = N \cdot 4 \pi r \cdot \frac{D \rho_v L}{\rho_l R_v T^2} \cdot \frac{1}{1 + \frac{L \rho_v D}{k T}} $$
Wait, the standard growth equation is $\frac{dr}{dt} = \frac{S}{r} K_{eff}$.
The mass condensation rate per droplet is $\frac{dm}{dt} = 4 \pi r \rho_l \frac{dr}{dt} = 4 \pi r \rho_l \frac{S}{r} K_{eff} = 4 \pi \rho_l K_{eff} S$.
The total mass condensation rate per unit volume is $N \cdot 4 \pi \rho_l K_{eff} S$.
The rate of change of water content $W$ is $\frac{dW}{dt} = N \cdot 4 \pi \rho_l K_{eff} S$.
Also, $\frac{dW}{dt} = \rho_l \frac{dV_{liq}}{dt}$.

In a steady updraft, the water content increases as the air rises. The rate of increase of water content due to adiabatic cooling is:
$$ \frac{dW}{dt} = \frac{w \cdot \Gamma_d \cdot \rho_d \cdot L}{R_v \cdot T^2} \cdot \frac{1}{\text{something?}} $$
Actually, the adiabatic lapse rate $\Gamma_d$ is defined for potential temperature. The rate of change of saturation mixing ratio $q_s$ with pressure is $\frac{dq_s}{dp}$.
The production rate of liquid water (and thus supersaturation if not condensed) is:
$$ \frac{dW}{dt} = \rho_d \cdot w \cdot \frac{dq_s}{dz} \approx \rho_d \cdot w \cdot \frac{dq_s}{dp} \frac{dp}{dz} $$
Using hydrostatic balance $\frac{dp}{dz} = -\rho_d g$.
So, $\frac{dW}{dt} = -\rho_d^2 g w \frac{dq_s}{dp}$.
Since $q_s$ increases as pressure decreases (altitude increases), $\frac{dq_s}{dp}$ is negative, so the rate is positive.

Let's equate the production rate to the condensation rate:
$$ \rho_d^2 g w \left| \frac{dq_s}{dp} \right| = N \cdot 4 \pi \rho_l K_{eff} S $$
Solving for $S$:
$$ S = \frac{\rho_d^2 g w \left| \frac{dq_s}{dp} \right|}{N \cdot 4 \pi \rho_l K_{eff}} $$

We need to calculate:
1.  **Droplet Concentration $N$**: From $W$ and $r_m$.
2.  **Air Density $\rho_d$**: From $P$ and $T$.
3.  **Saturation Vapor Pressure $e_s$** and its derivative $\frac{de_s}{dT}$: To find $\frac{dq_s}{dp}$ or directly use the formula for supersaturation production.
    Alternatively, the rate of change of supersaturation $S$ (dimensionless) due to adiabatic ascent is:
    $$ \frac{dS}{dt} = \frac{w \cdot \Gamma_d \cdot \rho_d \cdot L}{\rho_l \cdot R_v \cdot T^2} \cdot \frac{1}{\text{correction?}} $$
    Actually, a more precise expression for the production rate of supersaturation $P_S$ is:
    $$ P_S = \frac{w \cdot \rho_d \cdot L \cdot \Gamma_d}{\rho_l \cdot R_v \cdot T^2} $$
    Wait, $\Gamma_d$ is the dry adiabatic lapse rate ($\approx 9.8$ K/km). But in a moist environment, we should use the moist adiabatic lapse rate or just the rate of change of saturation vapor pressure.
    Let's use the fundamental definition:
    $$ \frac{dS}{dt} = \frac{1}{e_s} \frac{de_s}{dt} - \frac{1}{e} \frac{de}{dt} $$
    Assuming the air is near saturation ($e \approx e_s$), and the vapor mixing ratio is conserved (no condensation yet, or looking at the production term):
    $$ \frac{dS}{dt} \approx \frac{1}{e_s} \frac{de_s}{dT} \frac{dT}{dt} $$
    With $\frac{dT}{dt} = -w \Gamma_d$ (dry adiabatic cooling is the initial driver, or moist if saturated). Since it's a "developing" cloud, let's assume dry adiabatic cooling until saturation is reached, but here we are *in* the cloud. The cooling rate is the moist adiabatic lapse rate $\Gamma_m$. However, often in these problems, $\Gamma_d$ is used as an approximation for the cooling rate if the water content is small, or we calculate $\Gamma_m$. Given $T=0^\circ C$, $\Gamma_m \approx 6-7$ K/km. Let's stick to the standard approximation $\Gamma \approx 9.8$ K/km for simplicity unless specified, or better, calculate the exact rate of change of saturation vapor pressure with height.
    
    Actually, the standard formula for the supersaturation production rate $P$ is:
    $$ P = \frac{w \cdot \rho_d \cdot L \cdot \Gamma}{\rho_l \cdot R_v \cdot T^2} \cdot \frac{1}{\text{something}} $$
    Let's derive it carefully.
    $S = \frac{e - e_s}{e_s}$.
    $\frac{dS}{dt} = \frac{1}{e_s} \frac{de}{dt} - \frac{e}{e_s^2} \frac{de_s}{dt}$.
    If we assume the vapor mixing ratio $q_v$ is constant (no condensation), then $e$ changes only due to pressure change. $e = q_v \frac{P}{\epsilon + q_v} \approx q_v \frac{P}{\epsilon}$.
    $\frac{de}{dt} = \frac{e}{P} \frac{dP}{dt} = \frac{e}{P} (-\rho_d g w)$.
    $\frac{de_s}{dt} = \frac{de_s}{dT} \frac{dT}{dt} = \frac{de_s}{dT} (-w \Gamma)$.
    So, $\frac{dS}{dt} = -\frac{e}{e_s} \frac{\rho_d g w}{P} + \frac{e}{e_s^2} \frac{de_s}{dT} w \Gamma$.
    Near saturation $e \approx e_s$, so:
    $\frac{dS}{dt} \approx w \left( \frac{e_s}{e_s^2} \frac{de_s}{dT} \Gamma - \frac{\rho_d g}{P} \right) = w \left( \frac{1}{e_s} \frac{de_s}{dT} \Gamma - \frac{\rho_d g}{P} \right)$.
    Using Clausius-Clapeyron: $\frac{1}{e_s} \frac{de_s}{dT} = \frac{L}{R_v T^2}$.
    So, $\frac{dS}{dt} = w \left( \frac{L \Gamma}{R_v T^2} - \frac{\rho_d g}{P} \right)$.
    The term $\frac{\rho_d g}{P}$ is small compared to the first term for typical clouds?
    $\frac{L \Gamma}{R_v T^2} \approx \frac{2.5 \times 10^6 \cdot 0.01}{461.5 \cdot 273^2} \approx \frac{25000}{3.4 \times 10^7} \approx 7 \times 10^{-4}$ K$^{-1}$.
    $\frac{\rho_d g}{P} \approx \frac{1 \cdot 9.8}{80000} \approx 1.2 \times 10^{-4}$ Pa$^{-1}$? No, units.
    $\rho_d \approx P / (R_d T) = 80000 / (287 \cdot 273) \approx 1.02$ kg/m$^3$.
    $\frac{\rho_d g}{P} = \frac{1.02 \cdot 9.8}{80000} \approx 1.25 \times 10^{-4}$ m$^{-1}$.
    The first term has units K$^{-1}$. We need to multiply by $\Gamma$ (K/m).
    $\Gamma \approx 0.01$ K/m.
    Term 1: $7 \times 10^{-4} \cdot 0.01 = 7 \times 10^{-6}$ m$^{-1}$.
    Term 2: $1.25 \times 10^{-4}$ m$^{-1}$.
    Wait, the signs.
    $\frac{dS}{dt} = w [ \frac{L \Gamma}{R_v T^2} - \frac{g}{R_d T} ]$.
    $\frac{g}{R_d T} = \frac{9.8}{287 \cdot 273} \approx 1.25 \times 10^{-4}$.
    $\frac{L \Gamma}{R_v T^2} = \frac{2.5 \cdot 10^6 \cdot 0.01}{461.5 \cdot 273^2} \approx 1.17 \times 10^{-4}$.
    They are comparable. The net production rate is small.
    However, usually, the "supersaturation" in these problems refers to the peak value reached during droplet activation, which is often estimated by:
    $$ S_{max} \approx \left( \frac{w \cdot \Gamma \cdot \rho_d \cdot L}{N \cdot K \cdot R_v \cdot T^2} \right)^{1/2} $$
    This is the classic Pruppacher & Klett result for the maximum supersaturation.
    Let's use this formula. It balances the adiabatic production of supersaturation with the condensation sink.

    **Formula:**
    $$ S_{max} = \sqrt{ \frac{w \cdot \Gamma \cdot \rho_d \cdot L}{N \cdot K_{eff} \cdot R_v \cdot T^2} } $$
    Wait, let's check the units and constants.
    The condensation sink coefficient $A$ in $\frac{dS}{dt} = -A S$ is $A = N \cdot 4 \pi r \cdot \frac{D \rho_v L}{\rho_l R_v T^2 (1 + \dots)}$.
    The production rate $P = w \cdot \frac{L \Gamma}{R_v T^2} \cdot \rho_d$? No.
    Let's stick to the derived balance:
    Production Rate $P_S = w \left( \frac{L \Gamma}{R_v T^2} - \frac{g}{R_d T} \right)$.
    Consumption Rate $C_S = S \cdot N \cdot 4 \pi r \cdot \frac{D \rho_v L}{\rho_l R_v T^2} \cdot \frac{1}{1 + \frac{L \rho_v D}{k T}}$.
    Let $K_{diff} = \frac{D \rho_v L}{\rho_l R_v T^2 (1 + \frac{L \rho_v D}{k T})}$.
    Then $C_S = S \cdot N \cdot 4 \pi r \cdot K_{diff}$.
    Equating $P_S = C_S$:
    $$ S = \frac{w \left( \frac{L \Gamma}{R_v T^2} - \frac{g}{R_d T} \right)}{N \cdot 4 \pi r \cdot K_{diff}} $$

    Let's calculate the values.

    **Parameters:**
    *   $r_m = 4 \times 10^{-6}$ m
    *   $\sigma = 0.6 \times 10^{-6}$ m (not needed for mean approx)
    *   $W = 0.2$ g/m$^3$ = $0.2 \times 10^{-3}$ kg/m$^3$
    *   $w = 8$ m/s
    *   $T = 0^\circ$C = 273.15 K
    *   $P = 80$ kPa = $80,000$ Pa

    **Constants:**
    *   $R_v = 461.5$ J/(kg K)
    *   $R_d = 287.05$ J/(kg K)
    *   $L = 2.501 \times 10^6$ J/kg (Latent heat of vaporization at 0°C)
    *   $k = 0.024$ W/(m K) (Thermal conductivity of air)
    *   $D = 2.2 \times 10^{-5}$ m$^2$/s (Diffusivity of water vapor in air) - *Need to adjust for P and T*.
        $D \propto T^{1.81} / P$.
        Standard $D_0$ at 273 K, 101325 Pa is approx $2.11 \times 10^{-5}$ m$^2$/s.
        $D = D_0 \cdot \left(\frac{T}{273.15}\right)^{1.81} \cdot \left(\frac{101325}{P}\right)$.
    *   $\rho_l = 1000$ kg/m$^3$
    *   $g = 9.81$ m/s$^2$
    *   $\Gamma$: Dry adiabatic lapse rate $\Gamma_d = g / C_p \approx 9.8$ K/km = $0.0098$ K/m. Or Moist? At 0°C, moist is lower. Let's use $\Gamma_d$ as it's the standard "updraft" cooling assumption unless "moist adiabatic" is specified. However, the term $\frac{g}{R_d T}$ accounts for pressure expansion. The term $\frac{L \Gamma}{R_v T^2}$ accounts for cooling. If we use $\Gamma_d$, we are assuming dry cooling. If the air is saturated, it cools at $\Gamma_m$. But the *production* of supersaturation is driven by the difference between the actual cooling and the saturation vapor pressure change.
    Actually, the standard formula for $S_{max}$ uses $\Gamma_d$. Let's use $\Gamma = 0.0098$ K/m.

    **Step 1: Calculate Air Density $\rho_d$**
    $$ \rho_d = \frac{P}{R_d T} $$

    **Step 2: Calculate Droplet Concentration $N$**
    $$ N = \frac{W}{\frac{4}{3} \pi r_m^3 \rho_l} $$

    **Step 3: Calculate Saturation Vapor Pressure $e_s$ and $\rho_v$**
    Using Magnus formula or Clausius-Clapeyron.
    $e_s(T) = 611 \exp\left(\frac{L}{R_v} \left(\frac{1}{273.15} - \frac{1}{T}\right)\right)$ Pa.
    $\rho_v = \frac{e_s}{R_v T}$ kg/m$^3$.

    **Step 4: Calculate Diffusivity $D$ and Thermal Conductivity $k$**
    $D = 2.11 \times 10^{-5} \cdot \left(\frac{T}{273.15}\right)^{1.81} \cdot \left(\frac{101325}{P}\right)$ m$^2$/s.
    $k \approx 0.024$ W/(m K) (weak dependence on T, P).

    **Step 5: Calculate the Condensation Coefficient $K_{diff}$**
    $$ K_{diff} = \frac{D \rho_v L}{\rho_l R_v T^2 \left(1 + \frac{L \rho_v D}{k T}\right)} $$

    **Step 6: Calculate Production Rate $P_S$**
    $$ P_S = w \left( \frac{L \Gamma}{R_v T^2} - \frac{g}{R_d T} \right) $$

    **Step 7: Calculate Supersaturation $S$**
    $$ S = \frac{P_S}{N \cdot 4 \pi r_m \cdot K_{diff}} $$

    **Step 8: Convert to Percentage**
    $$ S_{\%} = S \times 100 $$

Let's write the code.

```python
import math

def solve():
    # Given values
    r_m = 4e-6       # Mean radius in meters
    sigma = 0.6e-6   # Standard deviation in meters (not used in mean approx)
    W = 0.2e-3       # Cloud water content in kg/m^3 (0.2 g/m^3)
    w = 8.0          # Updraft velocity in m/s
    T = 273.15       # Temperature in Kelvin (0 C)
    P = 80e3         # Pressure in Pa (80 kPa)
    
    # Constants
    R_v = 461.5      # Gas constant for water vapor J/(kg K)
    R_d = 287.05     # Gas constant for dry air J/(kg K)
    L = 2.501e6      # Latent heat of vaporization J/kg
    k_air = 0.024    # Thermal conductivity of air W/(m K)
    D_0 = 2.11e-5    # Diffusivity of water vapor at 273.15 K, 101325 Pa m^2/s
    rho_l = 1000.0   # Density of liquid water kg/m^3
    g = 9.81         # Gravity m/s^2
    Gamma = 0.0098   # Dry adiabatic lapse rate K/m
    
    # 1. Air Density
    rho_d = P / (R_d * T)
    
    # 2. Droplet Concentration N
    # W = N * (4/3) * pi * r_m^3 * rho_l
    volume_droplet = (4.0/3.0) * math.pi * r_m**3
    N = W / (volume_droplet * rho_l)
    
    # 3. Saturation Vapor Pressure e_s and Vapor Density rho_v
    # Clausius-Clapeyron approximation
    # e_s = 611 * exp( (L/R_v) * (1/273.15 - 1/T) )
    e_s = 611.0 * math.exp((L / R_v) * (1.0/273.15 - 1.0/T))
    rho_v = e_s / (R_v * T)
    
    # 4. Diffusivity D at given P and T
    # D = D_0 * (T/273.15)^1.81 * (101325/P)
    D = D_0 * (T / 273.15)**1.81 * (101325.0 / P)
    
    # 5. Condensation Coefficient K_diff
    # Term in denominator: 1 + (L * rho_v * D) / (k * T)
    heat_term = (L * rho_v * D) / (k_air * T)
    K_diff = (D * rho_v * L) / (rho_l * R_v * T**2 * (1.0 + heat_term))
    
    # 6. Production Rate of Supersaturation P_S
    # P_S = w * ( (L * Gamma) / (R_v * T^2) - g / (R_d * T) )
    term_cooling = (L * Gamma) / (R_v * T**2)
    term_expansion = g / (R_d * T)
    P_S = w * (term_cooling - term_expansion)
    
    # 7. Supersaturation S
    # S = P_S / (N * 4 * pi * r_m * K_diff)
    sink_coeff = N * 4.0 * math.pi * r_m * K_diff
    S = P_S / sink_coeff
    
    # 8. Convert to percentage
    S_percent = S * 100.0
    
    return {
        "1": {"value": S_percent, "unit": "%"}
    }
```

Double check the logic.
The formula $S = \frac{P_S}{Sink}$ assumes steady state where production equals consumption. This is a standard estimate for the supersaturation in a cloud with a fixed droplet concentration.
The value of $N$ is derived from the water content and mean radius. This assumes the water content is entirely in droplets of mean radius $r_m$. Given the Gaussian spectrum, this is a reasonable first-order approximation.
The lapse rate $\Gamma$ is taken as dry adiabatic. If moist adiabatic were intended, $\Gamma$ would be smaller (~0.006 K/m), reducing the production term and thus $S$. However, "updraft of 8 m/s" in a "developing" cloud often implies the initial stage where dry cooling dominates or the standard dry lapse rate is used for the potential temperature gradient. Given the ambiguity, dry adiabatic is the standard default in such textbook problems unless "moist adiabatic" is specified.

Let's do a quick sanity check on the numbers.
$T=273.15$, $P=80000$.
$\rho_d \approx 1.02$ kg/m$^3$.
$e_s \approx 611$ Pa.
$\rho_v \approx 611 / (461.5 \cdot 273.15) \approx 0.0048$ kg/m$^3$.
$D \approx 2.11e-5 \cdot 1 \cdot (101325/80000) \approx 2.66e-5$ m$^2$/s.
$heat\_term \approx (2.5e6 \cdot 0.0048 \cdot 2.66e-5) / (0.024 \cdot 273) \approx 0.32 / 6.55 \approx 0.05$.
$K\_diff \approx (2.66e-5 \cdot 0.0048 \cdot 2.5e6) / (1000 \cdot 461.5 \cdot 273^2 \cdot 1.05) \approx 0.32 / (3.4e7 \cdot 1.05) \approx 9e-9$ m$^2$/s?
Wait, units of $K\_diff$:
Numerator: $m^2/s \cdot kg/m^3 \cdot J/kg = J/(m s)$.
Denominator: $kg/m^3 \cdot J/(kg K) \cdot K^2 = J \cdot K / m^3$.
Result: $m^2 / (s K)$.
$K\_diff \approx 9 \times 10^{-9}$ m$^2$/(s K).

$N$:
$Vol \approx 4/3 \pi (4e-6)^3 \approx 2.7e-16$ m$^3$.
$N \approx 0.2e-3 / (2.7e-16 \cdot 1000) \approx 0.2e-3 / 2.7e-13 \approx 7.4e8$ droplets/m$^3$.

$Sink$:
$N \cdot 4 \pi r K \approx 7.4e8 \cdot 4 \pi \cdot 4e-6 \cdot 9e-9 \approx 7.4e8 \cdot 50e-6 \cdot 9e-9 \approx 3.3e-4$ 1/s.

$P_S$:
$term\_cooling \approx (2.5e6 \cdot 0.0098) / (461.5 \cdot 273^2) \approx 24500 / 3.4e7 \approx 7.2e-4$ K$^{-1}$.
$term\_expansion \approx 9.81 / (287 \cdot 273) \approx 1.25e-4$ K$^{-1}$.
$P_S = 8 \cdot (7.2e-4 - 1.25e-4) \approx 8 \cdot 6e-4 \approx 4.8e-3$ 1/s.

$S = 4.8e-3 / 3.3e-4 \approx 14.5$.
$S \% = 1450 \%$.
This is extremely high. Typical supersaturations are 0.1% - 1%.
Where is the error?
Ah, $N$ is very high? $7.4 \times 10^8$ is 740,000 per cm$^3$. Typical cloud droplet concentrations are 100-1000 per cm$^3$.
$W = 0.2$ g/m$^3$ is very low. Typical is 0.5-1 g/m$^3$.
$r = 4$ $\mu$m is small.
If $N$ is high, $S$ is low.
Wait, $N \approx 7.4 \times 10^8$ m$^{-3}$ = 740 cm$^{-3}$. This is a reasonable concentration.
Why is $S$ so high?
Let's re-evaluate $K\_diff$.
$K\_diff \approx 9 \times 10^{-9}$.
$Sink = N \cdot 4 \pi r K \approx 7.4e8 \cdot 5e-5 \cdot 9e-9 \approx 3.3e-4$.
$P_S \approx 4.8e-3$.
$S \approx 14$.
Is $P_S$ correct?
$w=8$ m/s is a strong updraft.
$\Gamma = 0.0098$ K/m.
$dT/dt = -0.08$ K/s.
$de_s/dt = e_s \cdot (L/R_v T^2) \cdot dT/dt \approx 611 \cdot 7.2e-4 \cdot (-0.08) \approx -0.035$ Pa/s.
$dS/dt \approx (1/e_s) de_s/dt \dots$
Actually, $P_S$ is the rate of change of *supersaturation*.
If $S$ is dimensionless, $P_S$ is 1/s.
$S = 14$ means 1400%.
This suggests that with such a strong updraft and relatively low droplet concentration (for the water content), the condensation cannot keep up with the vapor production, leading to high supersaturation.
However, in reality, droplets would grow larger, reducing $N$ (if coalescence) or increasing $r$ (increasing sink).
But the problem asks to *estimate* based on the given spectrum.
Perhaps the "mean radius" is the *current* radius, and we are to find the $S$ that sustains it?
No, the balance equation gives the $S$ required to maintain the growth rate implied by the updraft.
If the calculated $S$ is unphysically high, it might imply the assumptions (dry lapse rate, steady state) are breaking down, or the "developing" nature means we are looking at the peak $S$ before droplets grow.
Actually, the formula $S_{max} \propto w^{1/2}$ is for the peak. The steady state $S$ is what I calculated.
Let's check the units of $K\_diff$ again.
$\frac{dr}{dt} = \frac{S}{r} K$.
$K$ has units $m^2/s$.
My $K\_diff$ calculation:
Numerator: $D \rho_v L$. Units: $m^2/s \cdot kg/m^3 \cdot J/kg = J/(m s)$.
Denominator: $\rho_l R_v T^2$. Units: $kg/m^3 \cdot J/(kg K) \cdot K^2 = J K / m^3$.
Result: $m^2 / (s K)$.
So $\frac{dr}{dt} = \frac{S}{r} K\_diff$.
Units: $1/m \cdot m^2/s = m/s$. Correct.
So $K\_diff \approx 9 \times 10^{-9}$ m$^2$/s.
At $S=0.01$ (1%), $r=4 \mu m$:
$dr/dt = 0.01 / 4e-6 \cdot 9e-9 = 2.5e-6 \cdot 9e-9 = 2.25e-14$ m/s.
This growth rate is tiny.
In 1 second, radius grows $2e-14$ m.
To grow from 0 to 4 $\mu$m, it would take forever.
This implies that for $r=4 \mu$m, the supersaturation must be much higher to sustain the growth required by the updraft?
Or, the droplets are already grown, and the supersaturation is low?
If the cloud is "developing", the droplets are growing.
The balance $P_S = Sink \cdot S$ gives the $S$ that exists *given* the current $N$ and $r$.
If $S$ is high, it means the condensation is inefficient.
With $w=8$ m/s, the air rises 8 meters in 1 second.
The cooling is significant.
The result $S \approx 1400\%$ is likely the mathematical answer to the posed problem, even if physically unrealistic for a stable cloud. It indicates that the given parameters (high w, low W, small r) are inconsistent with a low-supersaturation equilibrium.

However, often in these problems, the "supersaturation" asked is the **peak supersaturation** $S_{max}$ which occurs *before* the droplets reach this size.
But the problem gives the spectrum *centered at 4 $\mu$m*. This implies the droplets are already this size.
If they are this size, and the water content is 0.2 g/m$^3$, then $N$ is fixed.
The supersaturation *now* is determined by the balance.
I will provide the calculated value.

One correction: The term $\frac{g}{R_d T}$ in $P_S$ might be subtracted or added depending on sign conventions.
$\frac{dS}{dt} = w (\frac{L \Gamma}{R_v T^2} - \frac{g}{R_d T})$.
Since $\frac{L \Gamma}{R_v T^2} > \frac{g}{R_d T}$, the term is positive.
The calculation holds.

Final Answer seems to be ~1450%.

```python
import math

def solve():
    # Given values
    r_m = 4e-6       # Mean radius in meters
    W = 0.2e-3       # Cloud water content in kg/m^3 (0.2 g/m^3)
    w = 8.0          # Updraft velocity in m/s
    T = 273.15       # Temperature in Kelvin (0 C)
    P = 80e3         # Pressure in Pa (80 kPa)
    
    # Constants
    R_v = 461.5      # Gas constant for water vapor J/(kg K)
    R_d = 287.05     # Gas constant for dry air J/(kg K)
    L = 2.501e6      # Latent heat of vaporization J/kg
    k_air = 0.024    # Thermal conductivity of air W/(m K)
    D_0 = 2.11e-5    # Diffusivity of water vapor at 273.15 K, 101325 Pa m^2/s
    rho_l = 1000.0   # Density of liquid water kg/m^3
    g = 9.81         # Gravity m/s^2
    Gamma = 0.0098   # Dry adiabatic lapse rate K/m
    
    # 1. Air Density
    rho_d = P / (R_d * T)
    
    # 2. Droplet Concentration N
    volume_droplet = (4.0/3.0) * math.pi * r_m**3
    N = W / (volume_droplet * rho_l)
    
    # 3. Saturation Vapor Pressure e_s and Vapor Density rho_v
    e_s = 611.0 * math.exp((L / R_v) * (1.0/273.15 - 1.0/T))
    rho_v = e_s / (R_v * T)
    
    # 4. Diffusivity D at given P and T
    D = D_0 * (T / 273.15)**1.81 * (101325.0 / P)
    
    # 5. Condensation Coefficient K_diff
    heat_term = (L * rho_v * D) / (k_air * T)
    K_diff = (D * rho_v * L) / (rho_l * R_v * T**2 * (1.0 + heat_term))
    
    # 6. Production Rate of Supersaturation P_S
    term_cooling = (L * Gamma) / (R_v * T**2)
    term_expansion = g / (R_d * T)
    P_S = w * (term_cooling - term_expansion)
    
    # 7. Supersaturation S
    sink_coeff = N * 4.0 * math.pi * r_m * K_diff
    S = P_S / sink_coeff
    
    # 8. Convert to percentage
    S_percent = S * 100.0
    
    return {
        "1": {"value": S_percent, "unit": "%"}
    }
```
~~~~

#### `qwen-2.5-72b` · core_code · run 1 · **FAIL**

Source: `experiments/core_code/qwen-2.5-72b.run1.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `12988.791086533269` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(mean_radius=4, std_dev=0.6, cloud_water_content=0.2, updraft_speed=8, temperature=0, pressure=80):
    # Constants
    R = 8.314  # Gas constant (J/(mol*K))
    M_w = 0.018  # Molar mass of water (kg/mol)
    rho_w = 1000  # Density of water (kg/m^3)
    T = temperature + 273.15  # Convert temperature to Kelvin
    P = pressure * 1000  # Convert pressure to Pascals
    g = 9.81  # Acceleration due to gravity (m/s^2)
    k_B = 1.380649e-23  # Boltzmann constant (J/K)
    m_w = M_w / (6.02214076e23)  # Mass of a water molecule (kg)
    
    # Saturation vapor pressure over ice at 0°C
    P_sat_ice = 611.21 * math.exp(22.587 * (1 / 273.15 - 1 / T))  # Pa
    
    # Calculate the number concentration of droplets
    N = cloud_water_content * rho_w / (math.sqrt(2 * math.pi) * std_dev * 1e-6 * M_w)
    
    # Calculate the mean droplet radius in meters
    r_mean = mean_radius * 1e-6
    
    # Calculate the diffusivity of water vapor in air
    D_v = 2.11e-5 * (T / 273.15)**1.94 * (101325 / P)
    
    # Calculate the accommodation coefficient
    alpha = 1.0
    
    # Calculate the growth rate of droplets
    dr_dt = (D_v * alpha * (P - P_sat_ice) / (r_mean * P)) * (1 + (2 * m_w * g * r_mean / (3 * k_B * T)))
    
    # Calculate the supersaturation
    S = (P - P_sat_ice) / P_sat_ice
    
    # Convert supersaturation to percentage
    S_percent = S * 100
    
    return {
        "1": {"value": S_percent, "unit": "%"}
    }

# Example usage
result = solve()
print(result)
```

This function `solve()` computes the supersaturation in a developing cumulus cloud given the specified parameters. The result is returned as a dictionary with the supersaturation expressed as a percentage.
~~~~

#### `qwen-2.5-72b` · core_code · run 2 · **FAIL**

Source: `experiments/core_code/qwen-2.5-72b.run2.json` → `ry_7.7` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0.52` | `0.02382861156294707` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(mean_radius=4, std_dev=0.6, cloud_water_content=0.2, updraft_speed=8, temperature=0, pressure=80):
    # Constants
    R = 8.314  # Universal gas constant (J/mol*K)
    M_w = 0.018  # Molar mass of water (kg/mol)
    rho_w = 1000  # Density of water (kg/m^3)
    T = temperature + 273.15  # Convert temperature to Kelvin
    P = pressure * 1000  # Convert pressure to Pascals
    g = 9.81  # Acceleration due to gravity (m/s^2)
    
    # Saturation vapor pressure over water at 0°C
    e_s = 611  # Pa (saturation vapor pressure at 0°C)
    
    # Calculate the number concentration of droplets (N)
    # Using the formula for the volume of a sphere and the cloud water content
    # cloud_water_content = N * (4/3) * pi * (mean_radius * 1e-6)^3
    N = (3 * cloud_water_content) / (4 * math.pi * (mean_radius * 1e-6)**3 * rho_w)
    
    # Calculate the terminal velocity of a droplet (v_t)
    # Using the Stokes' law for small droplets
    # v_t = (2 * g * (rho_w - rho_a) * (mean_radius * 1e-6)^2) / (9 * mu)
    # For simplicity, we assume the air density (rho_a) and viscosity (mu) at 0°C and 80 kPa
    rho_a = 1.293  # kg/m^3 (air density at 0°C and 101325 Pa)
    mu = 1.714e-5  # Pa*s (dynamic viscosity of air at 0°C)
    v_t = (2 * g * (rho_w - rho_a) * (mean_radius * 1e-6)**2) / (9 * mu)
    
    # Calculate the supersaturation (S)
    # Using the formula for the supersaturation in an updraft
    # S = (updraft_speed / v_t) * (M_w * e_s) / (R * T * P)
    S = (updraft_speed / v_t) * (M_w * e_s) / (R * T * P)
    
    # Convert the supersaturation to a percentage
    S_percent = S * 100
    
    return {"1": {"value": S_percent, "unit": "%"}}

# Example usage
result = solve()
print(result)
```

This function `solve()` computes the supersaturation in a developing cumulus cloud given the specified parameters. The result is returned as a dictionary with the supersaturation value in percentage.
~~~~

