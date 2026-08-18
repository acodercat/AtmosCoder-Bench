# Trap problems — transcripts of convergence on a shared shortcut

**Backs**: Supplementary Tables S22 / S23. **Verbatim.**

> ⚠️ **Two of the four named traps do not hold**: `air_89` is solved in all 27 measurements; `air_121` is solved 25/27 and no model returns its shortcut value.
> The traps that genuinely converge are `holton_28` (18/27) and `air_215` (12/27). All four originals are kept here, plus three replacement candidates.
> (Adjudicated against the stored runs; see `docs/results/TRAP_RESULTS.md`.)
>
> **Capture rule**: the run failed *and* every sub-answer it returned matches the full `shortcut_values` vector within 2% (the count is insensitive to that tolerance).
> **Control selection**: controls are drawn only from fallers whose parent problem the model solves — otherwise "solved the parent, tripped on the trigger" does not hold.
>
> **Sampling (this file is not exhaustive)**: each of the five traps with fallers contributes 4 transcripts, 2 of them paired with the same-run parent control;
> `air_89` and `air_121` have no fallers and contribute 2 transcripts each with no control. The `Shortcut capture x/27` in each heading is a **whole-corpus count**
> (`holton_28`, for instance, has 17 qualifying fallers; only 2 are shown here). For any other (model, run), pull it from `experiments/` using the `Source:` path.

---

## Trap `trap_holton_28_gen` (parent `holton_28`, family: regime boundary)

**shortcut output vector** = `{'1': 3.978568868148536e-06}` · **correct answer** = `[('1', 2.984e-06)]` · `shortcut`：the base small-deflection calculation, assuming the centers would meet at the midpoint and setting the combined Coriolis deflection over half the separation equal to one diameter

**Shortcut capture 18/27** (7 configurations) · **solved 5/27** · **fallers whose parent also passed: 17/18**

### Problem `trap_holton_28_gen`

Source: `synthesized` · category `atmospheric_dynamics` · difficulty `medium`

**problem (verbatim)**

~~~~
Two balls 4 cm in diameter are placed with their centers 8 cm apart on a frictionless horizontal plane at 43°N. If the balls are impulsively propelled directly at each other with equal speeds, at what speed must they travel so that they just miss each other?
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `2.984e-06` | m/s |

**reference solve()**

~~~~python
def solve(diameter_cm=4.0, center_separation_cm=8.0, latitude_deg=43.0):
    import math

    Omega = 7.2921159e-5  # Earth's rotation rate, rad/s

    d = diameter_cm / 100.0
    S = center_separation_cm / 100.0
    lat = math.radians(latitude_deg)
    f = 2.0 * Omega * math.sin(lat)

    # Exact f-plane inertial-motion geometry for the relative separation of the two centers:
    # r(t) = (S - 2(v/f) sin(ft), -2(v/f)(1 - cos(ft))).
    # This is a circle with center distance sqrt(S^2 + (2v/f)^2) from the origin
    # and radius 2v/f, so its minimum distance from the origin is
    # sqrt(S^2 + (2v/f)^2) - 2v/f.  Just missing requires this minimum to equal d.
    # Solving gives v = f * (S^2 - d^2) / (4d).
    v = f * (S*S - d*d) / (4.0 * d)

    return {"1": {"value": v, "unit": "m/s"}}
~~~~

### Representative shortcut-capture transcripts (all from configurations that solve the parent)

#### `gemini-3.1-pro` · trap · run 1 · **FAIL**

Source: `experiments/trap/gemini-3.1-pro.run1.json` → `trap_holton_28_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.984e-06` | `3.978560193129396e-06` | ✗ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
Two balls 4 cm in diameter are placed with their centers 8 cm apart on a frictionless horizontal plane at 43°N. If the balls are impulsively propelled directly at each other with equal speeds, at what speed must they travel so that they just miss each other?

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(D_cm=4.0, L_cm=8.0, lat_deg=43.0, omega=7.2921e-5):
    """
    Calculates the speed at which two balls must be propelled to just miss each other
    due to the Coriolis effect.
    """
    # Convert units to meters and radians
    D = D_cm / 100.0
    L = L_cm / 100.0
    lat_rad = math.radians(lat_deg)
    
    # Calculate the Coriolis parameter
    f = 2 * omega * math.sin(lat_rad)
    
    # The balls meet at the midpoint, so each travels a distance of L/2 in the x-direction.
    # Time to reach the midpoint: t = (L/2) / V
    # The Coriolis acceleration is a = f * V (perpendicular to motion).
    # The deflection for each ball is y = 1/2 * a * t^2 = 1/2 * f * V * (L / (2*V))^2 = f * L^2 / (8 * V)
    # Since they are traveling in opposite directions, they deflect in opposite directions.
    # The total distance between their centers at the midpoint is 2 * y = f * L^2 / (4 * V).
    # For the balls to just miss each other, this distance must equal their diameter D.
    # Therefore, D = f * L^2 / (4 * V)  =>  V = f * L^2 / (4 * D)
    
    V = (f * L**2) / (4 * D)
    
    return {
        "1": {"value": V, "unit": "m/s"}
    }
```
~~~~

#### `gemini-3.1-pro` · trap · run 2 · **FAIL**

Source: `experiments/trap/gemini-3.1-pro.run2.json` → `trap_holton_28_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.984e-06` | `3.978560193129396e-06` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(D_cm=8.0, d_cm=4.0, lat_deg=43.0, omega=7.2921e-5):
    """
    Calculates the speed at which two balls must be propelled to just miss each other
    due to the Coriolis effect.
    """
    # Convert units to meters
    D = D_cm / 100.0
    d = d_cm / 100.0
    
    # Calculate the Coriolis parameter (f)
    lat_rad = math.radians(lat_deg)
    f = 2 * omega * math.sin(lat_rad)
    
    # The balls meet at the midpoint, so each travels a distance of D/2 in the x-direction.
    # Time to reach the midpoint is t = (D/2) / V.
    # Transverse deflection for each ball is y = 0.5 * f * V * t^2.
    # Since they travel in opposite directions, they both deflect to their right, 
    # meaning they deflect in opposite directions in the transverse axis.
    # Total relative transverse displacement is 2 * y = f * V * t^2.
    # For them to just miss each other, this relative displacement must equal the diameter of one ball (d).
    # d = f * V * (D / (2 * V))^2 = f * D^2 / (4 * V)
    # Solving for V:
    V = (f * D**2) / (4 * d)
    
    return {
        "1": {"value": V, "unit": "m/s"}
    }
```
~~~~

#### `gemini-3.1-pro` · trap · run 3 · **FAIL**

Source: `experiments/trap/gemini-3.1-pro.run3.json` → `trap_holton_28_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.984e-06` | `3.978560193129396e-06` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(diameter_cm=4.0, distance_cm=8.0, lat_deg=43.0, omega=7.2921e-5):
    """
    Calculates the speed at which two balls must travel to just miss each other
    due to the Coriolis effect.
    """
    # Convert units to meters
    D = diameter_cm / 100.0
    L = distance_cm / 100.0
    
    # Distance each ball travels along the x-axis to the midpoint
    d = L / 2.0
    
    # Coriolis parameter
    lat_rad = math.radians(lat_deg)
    f = 2 * omega * math.sin(lat_rad)
    
    # The transverse deflection y for each ball after time t is approximately 0.5 * f * U * t^2.
    # The time to reach the midpoint is t = d / U.
    # So the deflection of one ball is y = 0.5 * f * d^2 / U.
    # Since they deflect in opposite directions, the total separation is 2 * y = f * d^2 / U.
    # For the balls to just miss each other, this separation must equal the diameter D.
    # D = f * d^2 / U  =>  U = f * d^2 / D
    
    U = f * (d ** 2) / D
    
    return {
        "1": {"value": U, "unit": "m/s"}
    }
```
~~~~

### The same models on the parent problem (control) — all PASS

#### `gemini-3.1-pro` · core_code · run 1 · **PASS**

Source: `experiments/core_code/gemini-3.1-pro.run1.json` → `holton_28` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `6.216513856482088` | `6.216500301764682` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(D=0.04, L=100.0, lat=43.0, omega=7.2921e-5):
    """
    Calculates the speed at which two balls must travel to just miss each other
    due to the Coriolis effect.
    
    Parameters:
    D : float : Diameter of the balls in meters (default 4 cm = 0.04 m)
    L : float : Initial distance between the balls in meters (default 100 m)
    lat : float : Latitude in degrees (default 43.0)
    omega : float : Earth's angular velocity in rad/s (default 7.2921e-5)
    """
    # Calculate the Coriolis parameter
    f = 2 * omega * math.sin(math.radians(lat))
    
    # The balls meet at L/2. 
    # Time to meet is t = (L/2) / V
    # Transverse deflection for each ball is y = 0.5 * a_c * t^2 = 0.5 * (f * V) * ((L/2)/V)^2 = f * L^2 / (8 * V)
    # Since they travel in opposite directions, they deflect to opposite transverse sides.
    # Total transverse separation is 2 * y = f * L^2 / (4 * V)
    # For them to just miss, this separation must equal the diameter of one ball, D.
    # Therefore, D = f * L^2 / (4 * V)  =>  V = f * L^2 / (4 * D)
    
    V = (f * L**2) / (4 * D)
    
    return {
        "1": {"value": V, "unit": "m/s"}
    }
```
~~~~

#### `gemini-3.1-pro` · core_code · run 2 · **PASS**

Source: `experiments/core_code/gemini-3.1-pro.run2.json` → `holton_28` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `6.216513856482088` | `6.216500301764682` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(D=0.04, L=100.0, lat=43.0, omega=7.2921e-5):
    """
    Calculates the speed at which two balls must travel to just miss each other
    due to the Coriolis effect.
    
    Parameters:
    D : float : Diameter of the balls in meters (default 4 cm = 0.04 m)
    L : float : Initial distance between the balls in meters (default 100 m)
    lat : float : Latitude in degrees (default 43.0)
    omega : float : Earth's angular velocity in rad/s (default 7.2921e-5)
    """
    # Calculate the Coriolis parameter
    f = 2 * omega * math.sin(math.radians(lat))
    
    # The balls meet at the midpoint, L/2. 
    # The time taken to reach the midpoint is t = L / (2 * V).
    # The transverse deflection for each ball is x = 0.5 * f * V * t^2.
    # Since they are traveling in opposite directions, they deflect in opposite 
    # absolute directions, so their total separation is 2 * x.
    # For them to just miss each other, their center-to-center separation must be D.
    # Therefore, 2 * (0.5 * f * V * (L / (2 * V))^2) = D
    # f * L^2 / (4 * V) = D  =>  V = f * L^2 / (4 * D)
    
    V = (f * L**2) / (4 * D)
    
    return {
        "1": {"value": V, "unit": "m/s"}
    }
```
~~~~

### Contrast: transcripts that get the trap right

#### `deepseek-v4-flash-reasoning` · trap · run 2 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run2.json` → `trap_holton_28_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.984e-06` | `2.983926282832288e-06` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(ball_diameter=4, center_distance=8, latitude=43, earth_rotation_rate=7.2921150e-5):
    """
    Compute the speed at which two balls must be propelled toward each other
    so that they just miss due to the Coriolis effect.

    Parameters
    ----------
    ball_diameter : float, optional
        Diameter of each ball in cm (default 4).
    center_distance : float, optional
        Initial distance between centers in cm (default 8).
    latitude : float, optional
        Latitude in degrees north (default 43).
    earth_rotation_rate : float, optional
        Earth's angular velocity in rad/s (default 7.2921150e-5).

    Returns
    -------
    dict
        A dictionary with key "1" mapping to {"value": speed, "unit": "m/s"}.
    """
    # Convert lengths from cm to m
    d = center_distance / 100.0          # initial center separation [m]
    r_min = ball_diameter / 100.0        # minimum center distance for just miss [m]

    # Coriolis parameter
    phi = math.radians(latitude)
    f = 2.0 * earth_rotation_rate * math.sin(phi)   # [rad/s]

    # Speed derived from the condition that the minimum distance equals r_min
    # V = f * (d^2 - r_min^2) / (4 * r_min)
    V = f * (d**2 - r_min**2) / (4.0 * r_min)       # [m/s]

    return {"1": {"value": V, "unit": "m/s"}}
```
~~~~

---

## Trap `trap_air_215_gen` (parent `air_215`, family: formula selection)

**shortcut output vector** = `{'1': 0.0, '2': 10.0, '3': 10.0}` · **correct answer** = `[('1', -17.8), ('2', 27.8), ('3', 19.44)]` · `shortcut`：the base Cartesian formulas for divergence, vorticity, and deformation, which ignore the spherical-coordinate curvature terms proportional to U tan(phi)/R and V tan(phi)/R

**Shortcut capture 12/27** (6 configurations) · **solved 6/27** · **fallers whose parent also passed: 11/12**

### Problem `trap_air_215_gen`

Source: `synthesized` · category `atmospheric_dynamics` · difficulty `medium`

**problem (verbatim)**

~~~~
At latitude 80°N on a spherical Earth of radius 6371 km, the local wind components are U = 40 m s^-1 eastward and V = 40 m s^-1 northward. Given local horizontal wind gradients ΔU / Δx = ΔV / Δx = 5 units, and ΔU / Δy = -5 units, ΔV / Δy = -5 units, where x is local eastward arc-distance, y is local northward arc-distance, and 1 unit = (1 m s^-1) / (500 km), find the horizontal divergence, the vertical component of relative vorticity, and the total deformation of the wind field, in the same units. Express your answers: (1) in units, (2) in units, (3) in units.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `-17.8` | units |
| `2` | `27.8` | units |
| `3` | `19.44` | units |

**reference solve()**

~~~~python
def solve(dU_dx_units=5.0, dV_dx_units=5.0, dU_dy_units=-5.0, dV_dy_units=-5.0, U_ms=40.0, V_ms=40.0, lat_deg=80.0, earth_radius_km=6371.0):
    import math

    # Convert the given gradient unit: (1 m/s) / (500 km) to s^-1.
    unit_s_inv = 1.0 / (500.0 * 1000.0)
    dU_dx = dU_dx_units * unit_s_inv
    dV_dx = dV_dx_units * unit_s_inv
    dU_dy = dU_dy_units * unit_s_inv
    dV_dy = dV_dy_units * unit_s_inv

    # Spherical Earth metric/curvature terms for local eastward U and northward V.
    R = earth_radius_km * 1000.0
    phi = math.radians(lat_deg)
    tan_over_R = math.tan(phi) / R

    # Exact local spherical-coordinate horizontal kinematics:
    # divergence = dU/dx + dV/dy - V tan(phi)/R
    # vorticity  = dV/dx - dU/dy + U tan(phi)/R
    # stretching deformation = dU/dx - dV/dy - V tan(phi)/R
    # shearing deformation   = dV/dx + dU/dy + U tan(phi)/R
    divergence = dU_dx + dV_dy - V_ms * tan_over_R
    vorticity = dV_dx - dU_dy + U_ms * tan_over_R
    stretching = dU_dx - dV_dy - V_ms * tan_over_R
    shearing = dV_dx + dU_dy + U_ms * tan_over_R
    total_deformation = math.sqrt(stretching**2 + shearing**2)

    return {
        "1": {"value": divergence / unit_s_inv, "unit": "units"},
        "2": {"value": vorticity / unit_s_inv, "unit": "units"},
        "3": {"value": total_deformation / unit_s_inv, "unit": "units"}
    }
~~~~

### Representative shortcut-capture transcripts (all from configurations that solve the parent)

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air_215_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-17.8` | `0.0` | ✗ |
| `2` | `27.8` | `10.0` | ✗ |
| `3` | `19.44` | `10.0` | ✗ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
At latitude 80°N on a spherical Earth of radius 6371 km, the local wind components are U = 40 m s^-1 eastward and V = 40 m s^-1 northward. Given local horizontal wind gradients ΔU / Δx = ΔV / Δx = 5 units, and ΔU / Δy = -5 units, ΔV / Δy = -5 units, where x is local eastward arc-distance, y is local northward arc-distance, and 1 unit = (1 m s^-1) / (500 km), find the horizontal divergence, the vertical component of relative vorticity, and the total deformation of the wind field, in the same units. Express your answers: (1) in units, (2) in units, (3) in units.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(lat=80, R=6371, U=40, V=40,
          dUdx=5, dVdx=5, dUdy=-5, dVdy=-5):
    """
    Compute horizontal divergence, vertical component of relative vorticity,
    and total deformation from given wind gradients in specified units.
    
    Parameters are all given in the problem statement; defaults match the values.
    lat and R are provided but not needed for the computation because the
    gradients are already given in the required units.
    
    Returns:
        dict with keys "1", "2", "3" mapping to {"value": number, "unit": "units"}
    """
    # Horizontal divergence: ∂U/∂x + ∂V/∂y
    divergence = dUdx + dVdy
    
    # Vertical component of relative vorticity: ∂V/∂x - ∂U/∂y
    vorticity = dVdx - dUdy
    
    # Deformation components
    stretching = dUdx - dVdy
    shearing = dVdx + dUdy
    total_deformation = math.sqrt(stretching**2 + shearing**2)
    
    return {
        "1": {"value": divergence, "unit": "units"},
        "2": {"value": vorticity, "unit": "units"},
        "3": {"value": total_deformation, "unit": "units"}
    }
```
~~~~

#### `deepseek-v4-flash-reasoning` · trap · run 2 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run2.json` → `trap_air_215_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-17.8` | `0.0` | ✗ |
| `2` | `27.8` | `10.0` | ✗ |
| `3` | `19.44` | `10.0` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(lat=80, R=6371e3, U=40, V=40,
          dUdx=5, dVdx=5, dUdy=-5, dVdy=-5):
    """
    Compute horizontal divergence, relative vorticity, and total deformation
    from given wind gradients (in units of (m/s)/(500 km)).
    """
    # Divergence = ∂U/∂x + ∂V/∂y
    divergence = dUdx + dVdy
    # Relative vorticity = ∂V/∂x - ∂U/∂y
    vorticity = dVdx - dUdy
    # Total deformation = sqrt( (∂U/∂x - ∂V/∂y)^2 + (∂V/∂x + ∂U/∂y)^2 )
    deformation = math.sqrt((dUdx - dVdy)**2 + (dVdx + dUdy)**2)

    return {
        "1": {"value": divergence, "unit": "units"},
        "2": {"value": vorticity, "unit": "units"},
        "3": {"value": deformation, "unit": "units"}
    }
```
~~~~

#### `deepseek-v4-flash-reasoning` · trap · run 3 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run3.json` → `trap_air_215_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-17.8` | `0.0` | ✗ |
| `2` | `27.8` | `10.0` | ✗ |
| `3` | `19.44` | `10.0` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(lat=80, R=6371, U=40, V=40, dUdx=5, dVdx=5, dUdy=-5, dVdy=-5):
    """
    Compute horizontal divergence, vertical component of relative vorticity,
    and total deformation of the wind field from given gradients.

    Parameters are provided with defaults as per problem statement.
    Returns a dictionary with keys "1", "2", "3" for the three quantities.
    """
    # Horizontal divergence: ∂U/∂x + ∂V/∂y
    divergence = dUdx + dVdy

    # Vertical component of relative vorticity: ∂V/∂x - ∂U/∂y
    vorticity = dVdx - dUdy

    # Stretching deformation: ∂U/∂x - ∂V/∂y
    stretching = dUdx - dVdy

    # Shearing deformation: ∂V/∂x + ∂U/∂y
    shearing = dVdx + dUdy

    # Total deformation: sqrt(stretching^2 + shearing^2)
    deformation = math.sqrt(stretching**2 + shearing**2)

    return {
        "1": {"value": divergence, "unit": "units"},
        "2": {"value": vorticity, "unit": "units"},
        "3": {"value": deformation, "unit": "units"}
    }
```
~~~~

### The same models on the parent problem (control) — all PASS

#### `deepseek-v4-flash-reasoning` · core_code · run 1 · **PASS**

Source: `experiments/core_code/deepseek-v4-flash-reasoning.run1.json` → `air_215` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0` | `0.0` | ✓ |
| `2` | `10` | `10.0` | ✓ |
| `3` | `10` | `10.0` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(dudx=5, dvdx=5, dudy=-5, dvdy=-5):
    """
    Compute horizontal divergence, vertical component of relative vorticity,
    and total deformation from given wind gradients.

    Parameters are in units where 1 unit = (1 m/s) / (500 km).
    Returns dict with keys "1", "2", "3" each containing value and unit.
    """
    # Horizontal divergence = ∂u/∂x + ∂v/∂y
    divergence = dudx + dvdy

    # Vertical component of relative vorticity = ∂v/∂x - ∂u/∂y
    vorticity = dvdx - dudy

    # Stretching deformation = ∂u/∂x - ∂v/∂y
    stretching = dudx - dvdy

    # Shearing deformation = ∂v/∂x + ∂u/∂y
    shearing = dvdx + dudy

    # Total deformation = sqrt(stretching^2 + shearing^2)
    deformation = math.sqrt(stretching**2 + shearing**2)

    return {
        "1": {"value": divergence, "unit": "units"},
        "2": {"value": vorticity, "unit": "units"},
        "3": {"value": deformation, "unit": "units"}
    }
```
~~~~

#### `deepseek-v4-flash-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/deepseek-v4-flash-reasoning.run2.json` → `air_215` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `0` | `0.0` | ✓ |
| `2` | `10` | `10.0` | ✓ |
| `3` | `10` | `10.0` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    dUdx: float = 5.0,
    dVdx: float = 5.0,
    dUdy: float = -5.0,
    dVdy: float = -5.0
) -> dict:
    """
    Compute horizontal divergence, vertical component of relative vorticity,
    and total deformation from given wind gradients.

    Parameters are in "units" where 1 unit = (1 m/s)/(500 km).
    Returns a dict with keys "1", "2", "3" for the three quantities.
    """
    # Horizontal divergence = ∂U/∂x + ∂V/∂y
    divergence = dUdx + dVdy

    # Vertical component of relative vorticity = ∂V/∂x - ∂U/∂y
    vorticity = dVdx - dUdy

    # Stretching deformation = ∂U/∂x - ∂V/∂y
    stretching = dUdx - dVdy
    # Shearing deformation = ∂V/∂x + ∂U/∂y
    shearing = dVdx + dUdy
    # Total deformation = sqrt(stretching^2 + shearing^2)
    total_deformation = math.sqrt(stretching**2 + shearing**2)

    return {
        "1": {"value": divergence, "unit": "units"},
        "2": {"value": vorticity, "unit": "units"},
        "3": {"value": total_deformation, "unit": "units"}
    }
```
~~~~

### Contrast: transcripts that get the trap right

#### `gemini-3.1-pro` · trap · run 1 · **PASS**

Source: `experiments/trap/gemini-3.1-pro.run1.json` → `trap_air_215_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-17.8` | `-17.803427467015247` | ✓ |
| `2` | `27.8` | `27.803427467015247` | ✓ |
| `3` | `19.44` | `19.438505853234734` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(lat_deg=80.0, R_km=6371.0, U=40.0, V=40.0, 
          dU_dx=5.0, dV_dx=5.0, dU_dy=-5.0, dV_dy=-5.0, 
          unit_dx_km=500.0):
    
    # Convert radius and unit scale to meters
    R_m = R_km * 1000.0
    unit_s_inv = 1.0 / (unit_dx_km * 1000.0)
    
    # Latitude in radians and its tangent
    lat_rad = math.radians(lat_deg)
    tan_lat = math.tan(lat_rad)
    
    # Metric terms in s^-1 due to the spherical Earth
    metric_V = (V / R_m) * tan_lat
    metric_U = (U / R_m) * tan_lat
    
    # Convert metric terms to the given "units"
    M_V = metric_V / unit_s_inv
    M_U = metric_U / unit_s_inv
    
    # 1. Horizontal divergence
    D = dU_dx + dV_dy - M_V
    
    # 2. Vertical component of relative vorticity
    zeta = dV_dx - dU_dy + M_U
    
    # 3. Total deformation
    # Stretching deformation
    E_st = dU_dx - dV_dy - M_V
    # Shearing deformation
    E_sh = dV_dx + dU_dy + M_U
    # Total deformation magnitude
    E = math.sqrt(E_st**2 + E_sh**2)
    
    return {
        "1": {"value": D, "unit": "units"},
        "2": {"value": zeta, "unit": "units"},
        "3": {"value": E, "unit": "units"}
    }
```
~~~~

---

## Trap `trap_air_89_gen` (parent `air_89`, family: formula selection)

**shortcut output vector** = `{'1': 680.5}` · **correct answer** = `[('1', 456.2)]` · `shortcut`：the base transparent-atmosphere projection formula F = S_o sin(Ψ), ignoring atmospheric attenuation

**Shortcut capture 0/27** (0 configurations) · **solved 27/27**

### Problem `trap_air_89_gen`

Source: `synthesized` · category `atmospheric_radiation` · difficulty `medium`

**problem (verbatim)**

~~~~
During the equinox at noon at latitude Φ = 60°, the solar elevation angle is Ψ = 90° - 60° = 30°. The top-of-atmosphere solar irradiance normal to the Sun's rays is S_o = 1361 W·m^-2. The atmosphere attenuates the direct solar beam according to Beer-Lambert law with vertical optical depth τ = 0.20, so the slant optical depth is τ/sin(Ψ), and diffuse radiation is negligible. How much direct radiative flux is absorbed into a perfectly black asphalt parking lot? The asphalt is a flat horizontal surface that absorbs all incident radiation. Express your answer in W·m^-2.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `456.2` | W·m^-2 |

**reference solve()**

~~~~python
def solve(S_o=1361.0, psi_deg=30.0, tau_vertical=0.20):
    import math
    psi_rad = math.radians(psi_deg)
    sin_psi = math.sin(psi_rad)
    transmittance = math.exp(-tau_vertical / sin_psi)
    F_rad = S_o * transmittance * sin_psi
    return {"1": {"value": round(F_rad, 1), "unit": "W·m^-2"}}
~~~~

### No captures (solved 27/27 — trapped no model) — two representative transcripts

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air_89_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `456.2` | `456.15279132725243` | ✓ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
During the equinox at noon at latitude Φ = 60°, the solar elevation angle is Ψ = 90° - 60° = 30°. The top-of-atmosphere solar irradiance normal to the Sun's rays is S_o = 1361 W·m^-2. The atmosphere attenuates the direct solar beam according to Beer-Lambert law with vertical optical depth τ = 0.20, so the slant optical depth is τ/sin(Ψ), and diffuse radiation is negligible. How much direct radiative flux is absorbed into a perfectly black asphalt parking lot? The asphalt is a flat horizontal surface that absorbs all incident radiation. Express your answer in W·m^-2.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(phi: float = 60.0, S_o: float = 1361.0, tau: float = 0.20) -> dict:
    """
    Compute the direct radiative flux absorbed by a perfectly black horizontal surface
    at the equinox noon at a given latitude.

    Parameters:
        phi (float): Latitude in degrees (default 60°).
        S_o (float): Top-of-atmosphere solar irradiance normal to Sun's rays in W·m^-2 (default 1361).
        tau (float): Vertical optical depth (default 0.20).

    Returns:
        dict: A dictionary with a single entry "1" containing the absorbed flux in W·m^-2.
    """
    # Solar elevation angle at equinox noon: psi = 90° - phi
    psi_deg = 90.0 - phi
    psi_rad = math.radians(psi_deg)
    sin_psi = math.sin(psi_rad)

    # Slant optical depth
    slant_od = tau / sin_psi

    # Direct normal irradiance at surface
    I_direct_normal = S_o * math.exp(-slant_od)

    # Flux on horizontal surface (projection factor sin(psi))
    flux_horizontal = I_direct_normal * sin_psi

    return {
        "1": {
            "value": flux_horizontal,
            "unit": "W·m^-2"
        }
    }
```
~~~~

#### `deepseek-v4-flash-reasoning` · trap · run 2 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run2.json` → `trap_air_89_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `456.2` | `456.15279132725243` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    latitude_deg: float = 60.0,
    solar_elevation_deg: float = 30.0,  # given as 90 - latitude
    S_o: float = 1361.0,  # W/m^2
    tau: float = 0.20
) -> dict:
    """
    Compute the direct radiative flux absorbed by a perfectly black horizontal surface
    at noon during equinox at given latitude.

    Parameters:
        latitude_deg: latitude in degrees (default 60)
        solar_elevation_deg: solar elevation angle in degrees (default 30)
        S_o: top-of-atmosphere solar irradiance normal to Sun's rays (W/m^2)
        tau: vertical optical depth (dimensionless)

    Returns:
        dict with key "1" mapping to {"value": computed flux, "unit": "W·m^-2"}
    """
    # Convert elevation to radians for math.sin
    psi_rad = math.radians(solar_elevation_deg)
    sin_psi = math.sin(psi_rad)

    # Slant optical depth
    slant_tau = tau / sin_psi

    # Direct normal irradiance at surface
    S_normal = S_o * math.exp(-slant_tau)

    # Horizontal irradiance (projection factor sin(psi))
    S_horizontal = S_normal * sin_psi

    return {
        "1": {
            "value": S_horizontal,
            "unit": "W·m^-2"
        }
    }
```
~~~~

---

## Trap `trap_air121_moist_adiabat` (parent `air_121`, family: formula selection)

**shortcut output vector** = `{'1': 10.1}` · **correct answer** = `[('1', 12.74)]` · `shortcut`：dry adiabatic lapse (base air_121's method) applied to an already-saturated parcel; should be the moist lapse

**Shortcut capture 0/27** (0 configurations) · **solved 25/27**

### Problem `trap_air121_moist_adiabat`

Source: `synthesized` · category `atmospheric_thermodynamics` · difficulty `medium`

**problem (verbatim)**

~~~~
An already-SATURATED air parcel at 15 °C and 900 hPa rises adiabatically through a height change of 0.5 km. Find its final temperature. Express your answer in °C.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `12.74` | °C |

**reference solve()**

~~~~python
def solve(T_i_C=15.0, delta_z_km=0.5, P_hPa=900.0):
    import math
    g=9.81; cp=1004.0; Lv=2.5e6; Rd=287.0; Rv=461.5
    T=T_i_C+273.15
    es=6.112*math.exp(17.62*T_i_C/(243.12+T_i_C))
    rs=0.622*es/(P_hPa-es)
    gs=(g/cp)*(1+Lv*rs/(Rd*T))/(1+Lv**2*rs/(cp*Rv*T**2))*1000.0   # moist lapse, K/km
    return {"1":{"value": T_i_C - gs*delta_z_km, "unit":"°C"}}
~~~~

### No captures (solved 25/27 — trapped no model) — two representative transcripts

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air121_moist_adiabat` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `12.74` | `12.745445804342374` | ✓ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
An already-SATURATED air parcel at 15 °C and 900 hPa rises adiabatically through a height change of 0.5 km. Find its final temperature. Express your answer in °C.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(T_initial=15.0, P_initial=900.0, delta_z=0.5):
    """
    Compute the final temperature of a saturated air parcel rising adiabatically.

    Parameters:
        T_initial : float  initial temperature in °C (default 15)
        P_initial : float  initial pressure in hPa (default 900)
        delta_z   : float  height change in km (default 0.5)

    Returns:
        dict with key "1" mapping to {"value": final_temp, "unit": "°C"}
    """
    # Convert to SI units
    T_K = T_initial + 273.15          # K
    P_Pa = P_initial * 100.0          # Pa
    dz = delta_z * 1000.0             # m

    # Saturation vapour pressure (Magnus formula) in Pa
    es_hPa = 6.112 * math.exp(17.67 * T_initial / (T_initial + 243.5))
    es_Pa = es_hPa * 100.0

    # Saturation mixing ratio (kg/kg)
    rs = 0.622 * es_Pa / (P_Pa - es_Pa)

    # Constants
    g = 9.80665      # m/s^2
    cp = 1004.0      # J/(kg·K)
    Lv = 2.5e6       # J/kg
    R_d = 287.0      # J/(kg·K)
    R_v = 461.0      # J/(kg·K)

    # Saturated adiabatic lapse rate (K/m)
    numerator = 1.0 + (Lv * rs) / (R_d * T_K)
    denominator = 1.0 + (Lv**2 * rs) / (cp * R_v * T_K**2)
    gamma_s = (g / cp) * numerator / denominator

    # Temperature change
    delta_T = -gamma_s * dz   # K (same as °C difference)
    final_T_C = T_initial + delta_T

    return {"1": {"value": final_T_C, "unit": "°C"}}
```
~~~~

#### `deepseek-v4-flash-reasoning` · trap · run 2 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run2.json` → `trap_air121_moist_adiabat` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `12.74` | `12.745436266200091` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(initial_temperature=15.0, initial_pressure=900.0, height_change=0.5):
    """
    Compute the final temperature of a saturated air parcel rising adiabatically.

    Parameters:
        initial_temperature (float): Initial temperature in °C.
        initial_pressure (float): Initial pressure in hPa.
        height_change (float): Height change in km (positive upward).

    Returns:
        dict: {"1": {"value": final_temperature, "unit": "°C"}}
    """
    # Constants
    g = 9.81          # m/s^2
    cp = 1005.0       # J/(kg·K)
    Lv = 2.5e6        # J/kg
    Rd = 287.0        # J/(kg·K)
    Rv = 461.0        # J/(kg·K)

    # Convert height change to meters
    dz = height_change * 1000.0  # m

    # Saturation vapor pressure (Tetens formula) in hPa
    T_C = initial_temperature
    e_s = 6.112 * math.exp(17.67 * T_C / (T_C + 243.5))  # hPa

    # Saturation mixing ratio (kg/kg)
    p = initial_pressure  # hPa
    r_s = 0.622 * e_s / (p - e_s)

    # Temperature in Kelvin
    T_K = T_C + 273.15

    # Saturated adiabatic lapse rate (K/m)
    numerator = (g / cp) * (1 + Lv * r_s / (Rd * T_K))
    denominator = 1 + (Lv**2 * r_s) / (cp * Rv * T_K**2)
    Gamma_s = numerator / denominator

    # Temperature change
    delta_T = -Gamma_s * dz  # K

    # Final temperature in °C
    final_temperature = T_C + delta_T

    return {"1": {"value": final_temperature, "unit": "°C"}}
```
~~~~

---

# Replacement candidates — three further traps that do show shortcut convergence

The remaining three rows of Table 4 in `TRAP_RESULTS.md`.

---

## Trap `trap_air_205_gen` (parent `air_205`, family: formula selection) **(replacement candidate)**

**shortcut output vector** = `{'1': 8.541019662496845, '2': 0.2}` · **correct answer** = `[('1', 13.82), ('2', 0.2)]` · `shortcut`：uses the low-pressure/cyclonic gradient-wind formula from the base problem despite the pressure center now being a high

**Shortcut capture 9/27** (4 configurations) · **solved 17/27** · **fallers whose parent also passed: 9/9**

### Problem `trap_air_205_gen`

Source: `synthesized` · category `atmospheric_dynamics` · difficulty `medium`

**problem (verbatim)**

~~~~
If the geostrophic wind is G = 10 m s⁻¹, find the normal gradient wind speed (M_tan) around a high-pressure center and the curvature Rossby number (Ro_c), given a Coriolis parameter of f_c = 10⁻⁴ s⁻¹ and a radius of curvature of R = 500 km. Use the appropriate gradient-wind balance for this pressure center, and compute Ro_c = G / (f_c R). Express your answers in m s⁻¹ and dimensionless, respectively.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `13.82` | m s^-1 |
| `2` | `0.2` | dimensionless |

**reference solve()**

~~~~python
def solve(G=10.0, f_c=1e-4, R_km=500.0):
    import math
    R = R_km * 1000.0
    Ro_c = G / (f_c * R)
    disc = 1.0 - 4.0 * G / (f_c * R)
    M_tan = 0.5 * f_c * R * (1.0 - math.sqrt(disc))
    return {
        "1": {"value": M_tan, "unit": "m s^-1"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
~~~~

### Representative shortcut-capture transcripts (all from configurations that solve the parent)

#### `deepseek-v4-flash` · trap · run 1 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash.run1.json` → `trap_air_205_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `13.82` | `8.541019662496845` | ✗ |
| `2` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
If the geostrophic wind is G = 10 m s⁻¹, find the normal gradient wind speed (M_tan) around a high-pressure center and the curvature Rossby number (Ro_c), given a Coriolis parameter of f_c = 10⁻⁴ s⁻¹ and a radius of curvature of R = 500 km. Use the appropriate gradient-wind balance for this pressure center, and compute Ro_c = G / (f_c R). Express your answers in m s⁻¹ and dimensionless, respectively.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G=10.0, f_c=1e-4, R=500e3):
    """
    Compute the normal gradient wind speed around a high-pressure center
    and the curvature Rossby number.
    
    Parameters:
    G  : geostrophic wind speed (m/s)
    f_c: Coriolis parameter (1/s)
    R  : radius of curvature (m)
    
    Returns:
    dict with keys "1" for gradient wind speed (m/s) and "2" for Ro_c (dimensionless)
    """
    
    # For a high-pressure center in gradient wind balance:
    # The gradient wind equation for an anticyclone is:
    # M_tan^2 / R + f_c * M_tan - f_c * G = 0
    # Solve quadratic: a = 1/R, b = f_c, c = -f_c * G
    a = 1.0 / R
    b = f_c
    c = -f_c * G
    
    discriminant = b**2 - 4 * a * c
    # Two roots: one positive (physical) and one negative
    # For high pressure, the physical root is the smaller positive one
    M_tan1 = (-b + math.sqrt(discriminant)) / (2 * a)
    M_tan2 = (-b - math.sqrt(discriminant)) / (2 * a)
    
    # Choose the positive root that is less than G (typical for high pressure)
    if M_tan1 > 0 and M_tan1 < G:
        M_tan = M_tan1
    else:
        M_tan = M_tan2
    
    # Curvature Rossby number
    Ro_c = G / (f_c * R)
    
    return {
        "1": {"value": M_tan, "unit": "m s⁻¹"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
~~~~

#### `deepseek-v4-flash` · trap · run 2 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash.run2.json` → `trap_air_205_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `13.82` | `8.541019662496845` | ✗ |
| `2` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G=10.0, f_c=1e-4, R=500e3):
    """
    Compute the normal gradient wind speed around a high-pressure center
    and the curvature Rossby number.
    
    Parameters:
    G  : geostrophic wind speed (m/s)
    f_c: Coriolis parameter (1/s)
    R  : radius of curvature (m)
    
    Returns:
    dict with keys "1" and "2" for M_tan and Ro_c.
    """
    # For a high-pressure center, the gradient wind balance is:
    # M_tan^2 / R + f_c * M_tan - f_c * G = 0
    # Solve quadratic: a = 1/R, b = f_c, c = -f_c * G
    a = 1.0 / R
    b = f_c
    c = -f_c * G
    
    discriminant = b**2 - 4 * a * c
    # Two roots: one positive (physical) and one negative
    # For high pressure, the physical root is the smaller positive one
    M_tan1 = (-b + math.sqrt(discriminant)) / (2 * a)
    M_tan2 = (-b - math.sqrt(discriminant)) / (2 * a)
    
    # Choose the positive root that is less than G (subgeostrophic for high pressure)
    if M_tan1 > 0 and M_tan1 < G:
        M_tan = M_tan1
    else:
        M_tan = M_tan2
    
    # Curvature Rossby number
    Ro_c = G / (f_c * R)
    
    return {
        "1": {"value": M_tan, "unit": "m s⁻¹"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
~~~~

#### `deepseek-v4-flash` · trap · run 3 · **FAIL**

Source: `experiments/trap/deepseek-v4-flash.run3.json` → `trap_air_205_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `13.82` | `8.541019662496845` | ✗ |
| `2` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G=10.0, f_c=1e-4, R=500e3):
    # G: geostrophic wind speed (m/s)
    # f_c: Coriolis parameter (1/s)
    # R: radius of curvature (m)
    
    # For a high-pressure center (anticyclone), the gradient wind balance is:
    # M_tan^2 / R + f_c * M_tan - f_c * G = 0
    # Solve quadratic: a = 1/R, b = f_c, c = -f_c * G
    a = 1.0 / R
    b = f_c
    c = -f_c * G
    
    # Discriminant
    disc = b*b - 4*a*c
    # Two roots: one positive, one negative; for anticyclonic flow, take the positive root
    M_tan = (-b + math.sqrt(disc)) / (2*a)
    
    # Curvature Rossby number
    Ro_c = G / (f_c * R)
    
    return {
        "1": {"value": M_tan, "unit": "m s⁻¹"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
~~~~

### The same models on the parent problem (control) — all PASS

#### `deepseek-v4-flash` · core_code · run 1 · **PASS**

Source: `experiments/core_code/deepseek-v4-flash.run1.json` → `air_205` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `M_tan` | `8.541019662496845` | `8.541019662496845` | ✓ |
| `Ro_c` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G=10.0, f_c=1e-4, R=500e3):
    # Compute gradient wind speed M_tan
    M_tan = 0.5 * f_c * R * (-1 + math.sqrt(1 + 4 * G / (f_c * R)))
    
    # Compute curvature Rossby number Ro_c
    Ro_c = G / (f_c * R)
    
    return {
        "1": {"value": M_tan, "unit": "m s^{-1}"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
```
~~~~

#### `deepseek-v4-flash` · core_code · run 2 · **PASS**

Source: `experiments/core_code/deepseek-v4-flash.run2.json` → `air_205` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `M_tan` | `8.541019662496845` | `8.541019662496845` | ✓ |
| `Ro_c` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G=10.0, f_c=1e-4, R=500e3):
    # Compute gradient wind speed M_tan
    M_tan = 0.5 * f_c * R * (-1 + math.sqrt(1 + (4 * G) / (f_c * R)))
    
    # Compute curvature Rossby number Ro_c
    Ro_c = G / (f_c * R)
    
    return {
        "1": {"value": M_tan, "unit": "m s^{-1}"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
```
~~~~

### Contrast: transcripts that get the trap right

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air_205_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `13.82` | `13.819660112501051` | ✓ |
| `2` | `0.2` | `0.2` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(G: float = 10.0, f_c: float = 1e-4, R: float = 500e3) -> dict:
    """
    Compute the normal gradient wind speed around a high-pressure center
    and the curvature Rossby number.

    Parameters
    ----------
    G : float
        Geostrophic wind speed (m/s)
    f_c : float
        Coriolis parameter (1/s)
    R : float
        Radius of curvature (m), positive magnitude

    Returns
    -------
    dict
        Keys "1" and "2" with values and units for M_tan and Ro_c.
    """
    # Gradient wind speed for a high (anticyclone)
    # Equation: V^2/R - f_c * V + f_c * G = 0
    # Solve for V (positive magnitude), take the smaller root
    discriminant = (f_c * R) ** 2 - 4 * f_c * R * G
    # discriminant is non-negative for physically possible flow
    sqrt_disc = math.sqrt(discriminant)
    M_tan = (f_c * R - sqrt_disc) / 2.0

    # Curvature Rossby number
    Ro_c = G / (f_c * R)

    return {
        "1": {"value": M_tan, "unit": "m s⁻¹"},
        "2": {"value": Ro_c, "unit": "dimensionless"}
    }
```
~~~~

---

## Trap `trap_air_108_gen` (parent `air_108`, family: sign direction) **(replacement candidate)**

**shortcut output vector** = `{'1': 0.001}` · **correct answer** = `[('1', -0.001)]` · `shortcut`：uses the base problem's convention for an 'east wind' as wind from the east, incorrectly applying U = -20 m/s to an eastward wind

**Shortcut capture 8/27** (4 configurations) · **solved 19/27** · **fallers whose parent also passed: 7/8**

### Problem `trap_air_108_gen`

Source: `synthesized` · category `atmospheric_dynamics` · difficulty `medium`

**problem (verbatim)**

~~~~
The potential temperature of the air increases 5°C per 100 km distance east. If an eastward wind of 20 m s^-1 is blowing, find the temperature change associated with this advection. Express your answer in °C s^-1.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `-0.001` | °C s^-1 |

**reference solve()**

~~~~python
def solve(delta_theta_C=5.0, delta_x_km=100.0, wind_speed=20.0):
    # Convert the potential-temperature gradient to °C/m.
    dtheta_dx = delta_theta_C / (delta_x_km * 1000.0)
    # An eastward wind is toward the east, so the zonal wind component U is positive.
    U = wind_speed
    # Local temperature tendency due to horizontal advection is -U * dtheta/dx.
    temperature_change = -U * dtheta_dx
    return {"1": {"value": temperature_change, "unit": "°C s^-1"}}
~~~~

### Representative shortcut-capture transcripts (all from configurations that solve the parent)

#### `qwen3.5-9b-reasoning` · trap · run 2 · **FAIL**

Source: `experiments/trap/qwen3.5-9b-reasoning.run2.json` → `trap_air_108_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-0.001` | `0.001` | ✗ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
The potential temperature of the air increases 5°C per 100 km distance east. If an eastward wind of 20 m s^-1 is blowing, find the temperature change associated with this advection. Express your answer in °C s^-1.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(potential_temp_gradient_degC_per_100km=5, wind_speed_ms=20):
    """
    Calculates the temperature change associated with advection.
    
    Parameters:
    potential_temp_gradient_degC_per_100km (float): The gradient of potential temperature in °C per 100 km.
    wind_speed_ms (float): The wind speed in m/s.
    
    Returns:
    dict: A dictionary with the calculated temperature change rate.
    """
    # Convert the gradient from °C per 100 km to °C per meter
    # 100 km = 100,000 meters
    gradient_degC_per_m = potential_temp_gradient_degC_per_100km / 100000.0
    
    # Calculate the advection rate (temperature change per unit time)
    # Formula: Rate = Wind Speed * Gradient
    # Units: (m/s) * (°C/m) = °C/s
    temperature_change_rate = wind_speed_ms * gradient_degC_per_m
    
    return {
        "1": {
            "value": temperature_change_rate,
            "unit": "°C s^-1"
        }
    }
```
~~~~

#### `qwen3.5-9b-reasoning` · trap · run 3 · **FAIL**

Source: `experiments/trap/qwen3.5-9b-reasoning.run3.json` → `trap_air_108_gen` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-0.001` | `0.001` | ✗ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 3
    def solv`

RESPONSE (verbatim, untruncated):

~~~~
Thinking Process:

1.  **Analyze the Request:**
    *   Role: Expert in atmospheric science.
    *   Task: Solve a specific atmospheric science problem and provide a Python `solve()` function.
    *   Rules:
        1.  Put given values as function parameters with defaults.
        2.  Return a dict with keys "1", "2", ..., "N" corresponding to the quantities asked, mapping to `{"value": <number>, "unit": "<unit>"}`.
        3.  Use only standard library. Compute answers from parameters (no hardcoding).
        4.  Output format: Single ```python code block.
    *   Problem Statement:
        *   Potential temperature gradient ($\partial \theta / \partial x$) = 5°C per 100 km east.
        *   Wind speed ($u$) = 20 m s$^{-1}$ eastward.
        *   Find the temperature change associated with this advection.
        *   Units required: °C s$^{-1}$.

2.  **Physics/Mathematical Formulation:**
    *   The problem asks for the rate of temperature change due to advection.
    *   Advection term in the thermodynamic equation (or simply the material derivative of temperature due to horizontal transport) is given by $u \cdot \nabla T$ or $u \cdot \nabla \theta$ depending on context.
    *   The problem specifically mentions "potential temperature" ($\theta$) gradient, but asks for "temperature change". Usually, in atmospheric dynamics contexts involving potential temperature gradients and wind, the advection of potential temperature is calculated. However, the question asks for "temperature change associated with this advection".
    *   Let's look closely at the wording: "The potential temperature of the air increases 5°C per 100 km distance east." -> $\frac{\partial \theta}{\partial x} = \frac{5^\circ\text{C}}{100 \text{ km}}$.
    *   "If an eastward wind of 20 m s^-1 is blowing" -> $u = 20 \text{ m s}^{-1}$.
    *   "find the temperature change associated with this advection."
    *   Strictly speaking, advection of potential temperature is $\frac{D\theta}{Dt} = u \frac{\partial \theta}{\partial x}$.
    *   Does "temperature change" mean potential temperature change ($\frac{D\theta}{Dt}$) or actual temperature change ($\frac{DT}{Dt}$)?
    *   In many introductory atmospheric dynamics contexts, if potential temperature gradient is given, the advection term calculated is usually the advection of potential temperature. However, the unit requested is °C s$^{-1}$. Potential temperature and temperature have the same units (Kelvin or Celsius).
    *   Let's assume the question implies the advection of the scalar field described (potential temperature) or that the gradient given is effectively the temperature gradient for the purpose of the calculation (since $\theta \approx T$ in isentropic coordinates or small lapse rate approximations, but here the units are explicitly Celsius).
    *   Actually, usually "temperature advection" refers to $u \frac{\partial T}{\partial x}$. If the problem gives the potential temperature gradient, it might be a trick or a simplification where we treat the given gradient as the relevant gradient for the advection calculation. Given the phrasing "potential temperature... increases... find the temperature change", it implies we calculate the advection rate based on the given gradient.
    *   Calculation: Rate = Speed $\times$ Gradient.
    *   Gradient magnitude: $5^\circ\text{C} / 100 \text{ km}$.
    *   Speed: $20 \text{ m s}^{-1}$.
    *   Direction: Wind is East, Gradient is East. So advection is positive (or negative depending on sign convention, but usually magnitude is asked or sign is implied by "change"). The gradient "increases... east", so $\partial \theta / \partial x > 0$. Wind is East ($u > 0$). So advection is $u \frac{\partial \theta}{\partial x} > 0$.
    *   Conversion needed: km to m.
    *   $100 \text{ km} = 100,000 \text{ m} = 10^5 \text{ m}$.
    *   Gradient = $5 / 100,000 \, ^\circ\text{C m}^{-1} = 5 \times 10^{-5} \, ^\circ\text{C m}^{-1}$.
    *   Advection Rate = $20 \, \text{m s}^{-1} \times (5 \times 10^{-5} \, ^\circ\text{C m}^{-1})$.
    *   Rate = $100 \times 10^{-5} \, ^\circ\text{C s}^{-1} = 10^{-3} \, ^\circ\text{C s}^{-1} = 0.001 \, ^\circ\text{C s}^{-1}$.

3.  **Python Function Design:**
    *   Parameters: `theta_gradient_deg_per_km` (5), `distance_km` (100), `wind_speed_ms` (20).
    *   Wait, the problem says "increases 5°C per 100 km". It's better to parameterize the gradient directly or the components. Let's parameterize the gradient magnitude and wind speed to be explicit.
    *   Let's define parameters: `gradient_deg_per_100km` = 5, `distance_100km` = 100 (or just `gradient_deg_per_km` = 5/100).
    *   To follow Rule 1 ("Put every given value in as a function parameter with a default"), I should extract the numbers from the text.
    *   Values:
        *   Gradient: 5 °C per 100 km.
        *   Wind: 20 m s^-1.
    *   I will create parameters `potential_temp_gradient_deg_per_100km` (default 5) and `wind_speed_ms` (default 20).
    *   Actually, to be more precise about the "100 km" part, I can pass `gradient_per_100km` and `distance_per_unit`? No, simpler is better.
    *   Let's pass `gradient_deg_per_100km` = 5.0 and `wind_speed_ms` = 20.0.
    *   Wait, I need to make sure I don't hardcode the conversion logic inside the function if it's not derived from parameters. The conversion logic is standard math.
    *   The output needs to be a dict with keys "1", "2", ...
    *   The question asks for "the temperature change". There is only one quantity asked. So key "1".
    *   Unit: °C s^-1.

4.  **Refining the Logic:**
    *   Input: `gradient_deg_per_100km` (default 5), `wind_speed_ms` (default 20).
    *   Step 1: Convert gradient to °C per meter.
        *   $100 \text{ km} = 100 \times 1000 \text{ m} = 100,000 \text{ m}$.
        *   `gradient_per_m` = `gradient_deg_per_100km` / 100000.
    *   Step 2: Calculate advection rate.
        *   `rate` = `wind_speed_ms` * `gradient_per_m`.
    *   Step 3: Return dict.
    *   Key: "1".
    *   Value: `rate`.
    *   Unit: "°C s^-1".

5.  **Reviewing Constraints:**
    *   "Return a dict with one entry per quantity asked... exactly that many entries".
    *   "Compute each answer from its parameters".
    *   "Use only standard library".
    *   "Put every given value in as a function parameter with a default".
    *   The problem statement gives specific numbers. I should use those as defaults.
    *   The question asks for "the temperature change". Singular. So one entry.

6.  **Drafting the Code:**
    ```python
    import math

    def solve(potential_temp_gradient_deg_per_100km=5, wind_speed_ms=20):
        # Convert gradient to degrees Celsius per meter
        # 100 km = 100,000 meters
        gradient_per_meter = potential_temp_gradient_deg_per_100km / 100000.0
        
        # Calculate advection rate: u * (dT/dx)
        # Units: (m/s) * (°C/m) = °C/s
        temperature_change_rate = wind_speed_ms * gradient_per_meter
        
        return {
            "1": {"value": temperature_change_rate, "unit": "°C s^-1"}
        }
    ```
    Wait, check the unit string format. The prompt asks for "°C s^-1". I should match that exactly.
    Check the math again.
    $5 / 100,000 = 0.00005$.
    $20 * 0.00005 = 0.001$.
    Correct.

    Is there any ambiguity about "temperature change"?
    In meteorology, "temperature advection" usually refers to $u \frac{\partial T}{\partial x}$.
    The problem gives $\frac{\partial \theta}{\partial x}$.
    Since $\theta$ is potential temperature, and the question asks for "temperature change", there is a slight technical distinction. However, without information about the lapse rate or vertical motion, we cannot convert $\theta$ advection to $T$ advection accurately ($\frac{D\theta}{Dt} = \frac{DT}{Dt} + \dots$).
    Given the simplicity of the problem statement (likely a textbook exercise), it implies calculating the advection of the scalar field provided (potential temperature) and reporting it as the "temperature change" (or assuming $\theta \approx T$ for the sake of the exercise). The units requested (°C s^-1) apply to both.
    I will proceed with calculating $u \cdot \nabla \theta$.

    One detail: "Put every given value in as a function parameter with a default."
    Given values: 5, 100 (km), 20 (m s^-1).
    Should I parameterize the 100 km separately?
    "increases 5°C per 100 km".
    I can parameterize `gradient_value` (5) and `distance_unit` (100).
    Or just `gradient_deg_per_100km` (5).
    The prompt says "Put every given value in as a function parameter".
    Values explicitly mentioned: "5°C", "100 km", "20 m s^-1".
    I should probably make `distance_per_gradient` a parameter or just combine them into a gradient parameter.
    Usually, in these coding tasks, grouping the gradient into a single parameter is acceptable if the text implies a rate. However, to be safe regarding "every given value", I could separate them.
    But "5°C per 100 km" is a single physical quantity (the gradient).
    Let's look at the instruction: "Put every given value in as a function parameter with a default."
    If I define `gradient_deg_per_100km = 5`, I am capturing the "5".
    If I define `wind_speed_ms = 20`, I am capturing the "20".
    The "100 km" is part of the definition of the gradient.
    I will define `potential_temp_gradient_deg_per_100km` and `wind_speed_ms`.
    Wait, strictly speaking, "100" is a given value.
    Maybe `gradient_deg` = 5, `distance_km` = 100.
    Let's check the wording: "increases 5°C per 100 km".
    If I pass `gradient_deg_per_100km=5`, I am hardcoding the "100" into the parameter name logic.
    To be most compliant with "every given value", I should probably pass the numbers 5, 100, 20.
    Let's try: `gradient_deg` (5), `distance_km` (100), `wind_speed_ms` (20).
    Then calculate `gradient_per_m = gradient_deg / (distance_km * 1000)`.
    This ensures all numbers from the text are parameters.

    Revised Plan:
    Parameters: `gradient_deg` (5), `distance_km` (100), `wind_speed_ms` (20).
    Calculation: `rate = wind_speed_ms * (gradient_deg / (distance_km * 1000))`.
    Return dict with key "1".

    Wait, is there any other quantity asked? "find the temperature change associated with this advection."
    Just one quantity.

    Wait, checking the "unit" string.
    Prompt: "Express your answer in °C s^-1."
    Return dict value: `{"value": <number>, "unit": "<unit>"}`.
    So unit string should be "°C s^-1".

    Let's double check the "every given value" rule.
    "Put every given value in as a function parameter with a default."
    Given values in text: 5, 100, 20.
    So I need 3 parameters.
    `gradient_deg_celsius` = 5
    `distance_km` = 100
    `wind_speed_ms` = 20

    Wait, "100 km" is the distance over which the change occurs.
    So `gradient_deg_celsius` is the change, `distance_km` is the distance.
    This seems robust.

    Wait, one more check. "The potential temperature of the air increases 5°C per 100 km distance east."
    Is "100 km" a given value or a unit definition? It's a specific number in the problem statement.
    So yes, parameterize it.

    Wait, is there any ambiguity on the sign?
    "increases... east". Gradient is positive East.
    "eastward wind". Velocity is positive East.
    Advection = $u \frac{\partial \theta}{\partial x}$.
    Both positive. Result positive.
    The question asks for "temperature change". Usually implies magnitude or signed value. I will provide the signed value (positive).

    Final check on constraints:
    - Single code block.
    - `solve()` function.
    - Dict return format `{"1": {"value": ..., "unit": ...}}`.
    - Standard library only.
    - Compute from parameters.

    One detail: The prompt says "Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked".
    Since there is only one quantity ("find the temperature change"), key is "1".

    Let's write the code.

```python
import math

def solve(gradient_deg_celsius=5, distance_km=100, wind_speed_ms=20):
    """
    Calculates the temperature change associated with advection.
    
    Parameters:
    gradient_deg_celsius (float): The change in potential temperature over the given distance (default 5).
    distance_km (float): The distance over which the gradient is defined (default 100).
    wind_speed_ms (float): The speed of the eastward wind (default 20).
    
    Returns:
    dict: A dictionary with the calculated temperature change rate.
    """
    # Convert distance from km to meters
    distance_m = distance_km * 1000.0
    
    # Calculate gradient in degrees Celsius per meter
    gradient_per_m = gradient_deg_celsius / distance_m
    
    # Calculate advection rate: u * (dT/dx)
    # Units: (m/s) * (°C/m) = °C/s
    temperature_change_rate = wind_speed_ms * gradient_per_m
    
    return {
        "1": {
            "value": temperature_change_rate,
            "unit": "°C s^-1"
        }
    }
```
    Wait, I should check if I need to import `math`. I am not using any math functions that require import (basic arithmetic). But the rule says "Use only the standard library (math, etc.)". It's safer to include `import math` if I were using `math`, but I'm not. I'll include it just in case or leave it out. The prompt says "Use only the standard library". It doesn't mandate importing `math` if not used. I will omit `import math` to keep it clean, as I am not using `math` functions. Wait, actually, I'll check if I need `math` for anything. No.
    However, often these templates expect `import math` if it's a "science" problem. I'll leave it out to avoid clutter unless I use it.
    Wait, I should check the "unit" format again. "°C s^-1".
    In Python strings, `°` is a unicode character. It should be fine.
    The prompt asks for `°C s^-1`. I will copy that exactly.

    One more check on the "given value" rule.
    "Put every given value in as a function parameter with a default."
    Does "100 km" count as a value? Yes.
    Does "5°C" count? Yes.
    Does "20 m s^-1" count? Yes.
    So `gradient_deg_celsius=5`, `distance_km=100`, `wind_speed_ms=20`.
    This satisfies the rule.

    Wait, is there any ambiguity on "temperature change"?
    If the wind is blowing East, and temperature increases East, the air moving East is moving into warmer air.
    Advection term $u \frac{\partial T}{\partial x}$.
    $u > 0$ (East). $\frac{\partial T}{\partial x} > 0$ (Increases East).
    Product is positive.
    So the temperature change rate is positive.
    The question asks for "temperature change".
    I will return the positive value.

    Wait, I need to make sure I don't hardcode the conversion factor 1000.
    "100 km" is a parameter.
    `distance_m = distance_km * 1000.0`.
    Is 1000 a hardcode? It is a physical constant (km to m).
    The rule says "do not hard-code a precomputed number".
    Usually, unit conversion constants (like 1000 m/km) are allowed as they are definitions, not problem-specific precomputed answers.
    However, to be extremely safe, I could define `km_to_m = 1000` as a constant or just use the literal.
    Given "do not hard-code a precomputed number" usually refers to the *answer* (e.g. don't return 0.001 directly).
    Using 1000 for unit conversion is standard practice.
    I will use `1000.0`.

    Wait, looking at the instruction "Return a dict... exactly that many entries".
    I have 1 entry.
    Key "1".
    Value `{"value": ..., "unit": ...}`.
    Looks correct.

    One nuance: "The potential temperature... increases 5°C per 100 km".
    Is it possible the user wants `gradient_deg_per_km` as a parameter?
    If I pass `gradient_deg_per_100km = 5`, I am combining the 5 and 100.
    If I pass `gradient_deg = 5` and `distance = 100`, I am separating them.
    Separating them is safer for the "every given value" rule.
    I will stick with `gradient_deg_celsius`, `distance_km`, `wind_speed_ms`.

    Wait, I need to check if the problem implies a specific sign convention.
    "find the temperature change associated with this advection."
    Usually, advection is defined as $u \frac{\partial T}{\partial x}$.
    If $u$ is East and $\partial T/\partial x$ is East (positive), advection is positive.
    If the wind was West, it would be negative.
    I will assume the standard definition.

    Final check on the code structure.
    Function name `solve`.
    Parameters with defaults.
    Return dict.
    Single code block.

    One detail: "The graded answer is whatever solve() returns".
    So the function must be callable.
    I will ensure the function is defined at the top level.

    Wait, I should check if `math` is needed for anything. No.
    I will remove `import math` to avoid unused imports, although it's allowed.
    Wait, I'll add `import math` just to be safe with "standard library" context, but it's not used. I'll omit it.

    Wait, one more check on the unit string.
    "°C s^-1".
    In the return dict, `unit` must be a string.
    I will use `"°C s^-1"`.

    Wait, I need to make sure I don't use `math` if I don't need it.
    Okay, ready to write.

    Wait, I should check if there are multiple quantities asked.
    "find the temperature change associated with this advection."
    Singular.
    So only "1".

    Wait, is there any possibility that "temperature change" implies the change over a specific time or distance?
    "Express your answer in °C s^-1."
    This is a rate. So it is the derivative $dT/dt$.
    This matches $u \cdot \nabla T$.
    Okay.

    One final check on the "given value" rule.
    "Put every given value in as a function parameter with a default."
    Values: 5, 100, 20.
    My parameters: `gradient_deg_celsius=5`, `distance_km=100`, `wind_speed_ms=20`.
    This covers all numbers.
    The unit conversions (km->m, m/s * C/m -> C/s) are physical operations, not "precomputed answers".
    The 1000 factor is a unit definition.
    Okay.

    Wait, I should check if I need to handle the sign of the wind.
    "eastward wind".
    "increases... east".
    Both positive.
    Result positive.

    Wait, I'll check if I should use `float` explicitly. Python handles division as float in Python 3.
    I will use `1000.0` to ensure float division.

    Wait, I need to make sure I don't output anything else. Just the code block.
    The prompt says "Give your solve() in a single ```python code block."
    I will provide just the function definition.

    Wait, I should check if I need to handle the case where parameters are not provided (using defaults).
    Yes, defaults are provided.
    Okay.

    Wait, one detail in the prompt: "The graded answer is whatever solve() returns".
    This implies the testing harness will call `solve()`.
    So I must ensure `solve` is the entry point.
    Okay.

    Wait, I'll check the unit string again. "°C s^-1".
    Sometimes superscripts are tricky in strings.
    I will use the exact characters provided in the prompt: `°C s^-1`.
    Wait, the prompt says "Express your answer in °C s^-1."
    I will use that string.

    Wait, I need to make sure I don't use `math` if I don't need it, but I'll add `import math` at the top just in case the environment expects it for "standard library" compliance in a generic sense, though it's not used. Actually, better not to import unused modules. I'll skip it.

    Wait, I'll check the "100 km" part again.
    "increases 5°C per 100 km".
    Is "100 km" a value or a unit?
    It's a value "100" with unit "km".
    So `distance_km=100` is correct.

    Okay, writing the solution.

    Wait, I need to check if I should calculate the value or just return the formula.
    "The function must COMPUTE each answer from its parameters".
    So `temperature_change_rate = ...` is required.

    Okay, final check.
    Problem: Potential temp gradient = 5 C / 100 km. Wind = 20 m/s.
    Find advection rate in C/s.
    Math: 20 * (5 / (100 * 1000)) = 20 * (5 / 100000) = 100 / 100000 = 0.001.
    Code implements this.
    Returns dict with key "1".
    Unit "°C s^-1".

    One nuance: "The potential temperature...".
    Does advection of potential temperature equal advection of temperature?
    In the absence of vertical motion and diabatic heating, $\frac{D\theta}{Dt} = 0$ for adiabatic processes.
    But here we are calculating the *advection term* specifically.
    The advection term for potential temperature is $u \frac{\partial \theta}{\partial x}$.
    The advection term for temperature is $u \frac{\partial T}{\partial x}$.
    Since the problem gives $\frac{\partial \theta}{\partial x}$ and asks for "temperature change associated with this advection", and asks for the answer in °C s^-1, it implies we treat the given gradient as the relevant gradient for the calculation.
    In many simplified problems, $\theta$ and $T$ are treated interchangeably regarding advection rates unless vertical terms are involved.
    Given the constraints, I will calculate $u \frac{\partial \theta}{\partial x}$.

    Wait, I should check if I need to handle the sign of the wind direction explicitly.
    "eastward wind".
    "increases... east".
    So $u > 0$, $\partial/\partial x > 0$.
    Result positive.
    Okay.

    One last check on the "given value" rule.
    "Put every given value in as a function parameter with a default."
    Does "5°C" count as value 5? Yes.
    Does "100 km" count as value 100? Yes.
    Does "20 m s^-1" count as value 20? Yes.
    My parameters: `gradient_deg_celsius=5`, `distance_km=100`, `wind_speed_ms=20`.
    This is compliant.

    Wait, I'll check if I should name the parameters more descriptively.
    `gradient_deg_celsius` is good.
    `distance_km` is good.
    `wind_speed_ms` is good.

    Okay, ready.

    Wait, one detail. "Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked".
    Since there is only one quantity, key is "1".
    Okay.

    Wait, I need to make sure I don't include any docstrings that might be considered "intermediate or unit-converted extras" if they are printed? No, docstrings are in the code, not the return value.
    The return value is the dict.
    Okay.

    Wait, I'll check if I need to handle the `solve` function being inside a class or something. No, "Give your solve() in a single ```python code block."
    So just the function.

    Wait, I'll check if I need to handle the case where the user passes different values.
    Yes, defaults allow that.
    Okay.

    Wait, I'll check the unit string again.
    "°C s^-1".
    I will ensure the string matches exactly.
    In Python: `"°C s^-1"`.
    Okay.

    Wait, I'll check if I need to use `float()` explicitly.
    Python 3 division `/` returns float.
    So `20 * (5 / 100000)` is float.
    Okay.

    Wait, I'll check if I need to handle the "100 km" as a string or number.
    It's a number.
    Okay.

    Wait, I'll check if I need to handle the "5°C" as a number.
    It's a number.
    Okay.

    Wait, I'll check if I need to handle the "20 m s^-1" as a number.
    It's a number.
    Okay.

    Wait, I'll check if I need to handle the "eastward" direction.
    It implies sign.
    I will assume positive.
    Okay.

    Wait, I'll check if I need to handle the "potential temperature" vs "temperature".
    I will assume they are equivalent for the purpose of the calculation as per the problem context.
    Okay.

    Wait, I'll check if I need to handle the "advection" term.
    Advection = $u \cdot \nabla T$.
    Okay.

    Wait, I'll check if I need to handle the "change" vs "rate".
    "Express your answer in °C s^-1."
    This is a rate.
    Okay.

    Wait, I'll check if I need to handle the "associated with this advection".
    This confirms we calculate the advection term.
    Okay.

    Wait, I'll check if I need to handle the "100 km" as 100.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "5°C" as 5.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "20 m s^-1" as 20.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "east" direction.
    Yes, implies sign.
    Okay.

    Wait, I'll check if I need to handle the "increase".
    Yes, implies positive gradient.
    Okay.

    Wait, I'll check if I need to handle the "wind of 20".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solve()" function name.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "single ```python code block".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "Return a dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value" and "unit" keys.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "1" key.
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate or unit-converted extras".
    Yes, return dict directly.
    Okay.

    Wait, I'll check if I need to handle the "standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code a precomputed number".
    Yes, compute from params.
    Okay.

    Wait, I'll check if I need to handle the "put every given value in as a function parameter with a default".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "express it as a Python solve() function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "Work out the solution".
    Yes, I did the math.
    Okay.

    Wait, I'll check if I need to handle the "atmospheric science problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "expert in atmospheric science".
    Yes, context.
    Okay.

    Wait, I'll check if I need to handle the "graded answer is whatever solve() returns".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "Give your solve() in a single ```python code block".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "rules".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "value".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "exactly that many entries".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "no intermediate".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "unit-converted extras".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "use only the standard library".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do unit conversions explicitly".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function must COMPUTE".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "do not hard-code".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "problem".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "solution".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "function".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "parameters".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "defaults".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "dict".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "entry".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "keyed".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "order asked".
    Yes.
    Okay.

    Wait, I'll check if I need to handle the "quantity".
    Yes.
    Okay.

    Wait, I'll
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(potential_temp_gradient_deg_per_100km=5, wind_speed_ms=20):
    # Convert gradient to degrees Celsius per meter
    # 100 km = 100,000 meters
    gradient_per_meter = potential_temp_gradient_deg_per_100km / 100000.0
    
    # Calculate advection rate: u * (dT/dx)
    # Units: (m/s) * (°C/m) = °C/s
    temperature_change_rate = wind_speed_ms * gradient_per_meter
    
    return {
        "1": {"value": temperature_change_rate, "unit": "°C s^-1"}
    }
```
~~~~

#### `qwen3.5-9b` · trap · run 1 · **FAIL**

Source: `experiments/trap/qwen3.5-9b.run1.json` → `trap_air_108_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-0.001` | `0.001` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    potential_temp_gradient_c_per_km=5.0,  # °C per 100 km
    wind_speed_m_s=20.0                     # m s^-1
):
    """
    Calculates the temperature change associated with advection.
    
    Parameters:
    - potential_temp_gradient_c_per_km: The rate of change of potential temperature 
      with respect to distance east. Given as °C per 100 km in the problem statement.
    - wind_speed_m_s: The speed of the eastward wind in m/s.
    
    Returns:
    - A dictionary with the key "1" mapping to the temperature change rate in °C/s.
    """
    
    # The problem states the gradient is 5°C per 100 km.
    # We need to convert this to °C per meter to match the wind speed unit (m/s).
    # 100 km = 100,000 meters.
    # Gradient in °C/m = (potential_temp_gradient_c_per_km) / 100,000
    
    gradient_c_per_m = potential_temp_gradient_c_per_km / 100000.0
    
    # The temperature change rate (dT/dt) is the dot product of the wind vector and the temperature gradient vector.
    # Since the wind is blowing eastward and the gradient is given as "increases ... east", 
    # the vectors are aligned.
    # dT/dt = (Wind Speed) * (Gradient)
    # Units: (m/s) * (°C/m) = °C/s
    
    temp_change_rate_c_per_s = wind_speed_m_s * gradient_c_per_m
    
    return {
        "1": {"value": temp_change_rate_c_per_s, "unit": "°C s^-1"}
    }
```
~~~~

### The same models on the parent problem (control) — all PASS

#### `qwen3.5-9b-reasoning` · core_code · run 2 · **PASS**

Source: `experiments/core_code/qwen3.5-9b-reasoning.run2.json` → `air_108` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `2` | `0.001` | `0.001` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(theta_gradient_C_per_100km=5, distance_km=100, wind_speed_ms=20):
    """
    Calculates the temperature change associated with advection.
    
    Parameters:
    theta_gradient_C_per_100km (float): Magnitude of potential temperature increase in degrees Celsius.
    distance_km (float): Distance over which the increase occurs in kilometers.
    wind_speed_ms (float): Wind speed in meters per second.
    
    Returns:
    dict: {"1": {"value": float, "unit": str}}
    """
    # Convert the gradient distance from km to m for consistent SI units
    gradient_distance_m = distance_km * 1000.0
    
    # Calculate the potential temperature gradient in C/m
    # Gradient = Change in Temp / Change in Distance
    theta_gradient_C_per_m = theta_gradient_C_per_100km / gradient_distance_m
    
    # Calculate the advective temperature change rate
    # Advection = Wind Speed * Gradient
    # Units: (m/s) * (C/m) = C/s
    advection_rate = wind_speed_ms * theta_gradient_C_per_m
    
    return {
        "1": {
            "value": advection_rate,
            "unit": "°C s⁻¹"
        }
    }
```
~~~~

#### `qwen3.5-9b-reasoning` · core_code · run 3 · **PASS**

Source: `experiments/core_code/qwen3.5-9b-reasoning.run3.json` → `air_108` · `num_attempts` = 2 · 2 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `2` | `0.001` | `0.001` | ✓ |

**attempt 0** — `outcome` = `ungradable: Runtime error in solve():
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    exec(sys.stdin.read(), ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 4
    - Potent`

RESPONSE (verbatim, untruncated):

~~~~
The problem is asking me to find the temperature change associated with advection of air.

Given:
- Potential temperature gradient: 5°C per 100 km east
- Wind speed: 20 m/s east

I need to find the temperature change rate (°C/s) due to this advection.

The formula for advection is:
Temperature change rate = - (temperature gradient) × (wind velocity)

The temperature gradient is given as 5°C per 100 km east.
The wind is blowing east at 20 m/s.

So the temperature change rate = - (5°C / 100 km) × (20 m/s)

First, I need to convert units to be consistent:
- 100 km = 100,000 m = 10^5 m

So the gradient = 5°C / 100,000 m = 5 × 10^(-5) °C/m

The temperature change rate = - (5 × 10^(-5) °C/m) × (20 m/s)
= - 100 × 10^(-5) °C/s
= - 0.001 °C/s

Wait, let me think about the sign. The problem asks for "temperature change associated with this advection". 

If the potential temperature increases 5°C per 100 km east, and the wind is blowing east, then air is being advected from west to east. As air moves eastward, it encounters higher potential temperatures. So the temperature at a fixed point would increase due to this advection.

Actually, the advection term in the temperature equation is:
dT/dt = -v · ∇T

Where v is the wind velocity vector and ∇T is the temperature gradient vector.

If the gradient is positive in the east direction (temperature increases eastward), and the wind is blowing eastward, then:
dT/dt = - (positive gradient) × (positive velocity) = negative

But wait, this is the rate of change at a fixed point due to advection. Let me think more carefully.

If air is moving eastward and the temperature increases eastward, then at a fixed location, the air that arrives from the west (cooler) will be replaced by air from the east (warmer). So the temperature at a fixed point should increase.


 
Actually, I need to reconsider the sign convention. The advection term in the material derivative is:
DT/Dt = ∂T/∂t + v · ∇T

For the local rate of change due to advection at a fixed point, we have:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be positive since warmer air is advecting into the location.

Actually, I need to reconsider the sign convention more carefully. The advection term in the temperature equation is:
∂T/∂t = -v · ∇T

With a positive eastward gradient and eastward wind, this gives a negative value. But physically, if warmer air is moving into a location, the temperature should rise.

The potential temperature gradient is 5°C per 100 km east, meaning temperature increases toward the east. With an eastward wind of 20 m/s, air from the west (cooler) is moving eastward, but at a fixed point, air from the east (warmer) is arriving. This means the temperature at that point increases.

So the magnitude is 0.001 °C/s, and the sign should be
~~~~

**attempt 1** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve():
    # Potential temperature gradient: 5°C per 100 km east
    gradient_c_per_km = 5 / 100  # °C/km
    
    # Convert to °C/m
    gradient_c_per_m = gradient_c_per_km / 1000  # °C/m
    
    # Wind speed: 20 m/s east
    wind_speed = 20  # m/s
    
    # Temperature change rate due to advection
    # Rate = wind speed × temperature gradient
    # Since warmer air is advecting into the location, temperature increases
    temperature_change_rate = wind_speed * gradient_c_per_m  # °C/s
    
    return {"value": temperature_change_rate, "unit": "°C s^{-1}"}
```
~~~~

### Contrast: transcripts that get the trap right

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air_108_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `-0.001` | `-0.001` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(gradient_degC_per_100km=5, distance_km=100, wind_speed_m_s=20):
    """
    Compute the temperature change due to advection given a potential temperature
    gradient and eastward wind speed.

    Parameters:
        gradient_degC_per_100km (float): Potential temperature increase per 100 km east (in °C).
        distance_km (float): Distance over which the gradient is given (in km).
        wind_speed_m_s (float): Eastward wind speed (in m/s).

    Returns:
        dict: A dictionary with one entry "1" containing the advective temperature
              change rate in °C/s.
    """
    # Convert gradient to per meter
    gradient_per_m = gradient_degC_per_100km / (distance_km * 1000)  # °C/m
    # Advection: -u * dθ/dx
    advection = -wind_speed_m_s * gradient_per_m  # °C/s
    return {"1": {"value": advection, "unit": "°C s^-1"}}
```
~~~~

---

## Trap `trap_air_111_gen` (parent `air_111`, family: averaging space) **(replacement candidate)**

**shortcut output vector** = `{'1': 2.80346327608325}` · **correct answer** = `[('1', 3.532)]` · `shortcut`：the base Deardorff calculation applied directly to the given 0.67 K m s^-1, incorrectly treating a layer-averaged flux as the surface flux

**Shortcut capture 6/27** (3 configurations) · **solved 18/27** · **fallers whose parent also passed: 6/6**

### Problem `trap_air_111_gen`

Source: `synthesized` · category `boundary_layer` · difficulty `medium`

**problem (verbatim)**

~~~~
Given an effective layer-averaged kinematic heat flux of F_H = 0.67 K \cdot m \cdot s^{-1}, where the vertical heat-flux profile decreases linearly from its surface value to zero at the top of the boundary layer, find the Deardorff convective velocity scale (w_*) for a dry, z_i = 1 km thick boundary layer of temperature T_v = 25^\circ C = 298 K. Express your answer in m \cdot s^{-1}.
~~~~

**sub_answers**

| sub | value | unit |
|---|---|---|
| `1` | `3.532` | m s^-1 |

**reference solve()**

~~~~python
def solve(F_H_bar=0.67, z_i_km=1.0, T_v=298.0) -> dict:
    g = 9.8

    # Unit conversions
    z_i = z_i_km * 1000.0  # km to m

    # For a linear profile that decreases from the surface value to zero at z_i,
    # the layer average is half the surface value.
    F_H_surface = 2.0 * F_H_bar

    # Deardorff velocity formula uses the surface kinematic heat flux.
    w_star = ((g / T_v) * z_i * F_H_surface) ** (1.0 / 3.0)

    return {
        "1": {"value": w_star, "unit": "m s^-1"}
    }
~~~~

### Representative shortcut-capture transcripts (all from configurations that solve the parent)

#### `gpt55-reasoning` · trap · run 3 · **FAIL**

Source: `experiments/trap/gpt55-reasoning.run3.json` → `trap_air_111_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `3.532` | `2.8044165108646597` | ✗ |

**attempt 0** — `outcome` = `graded`

<details><summary>PROMPT（逐字）</summary>

~~~~
You are given an atmospheric science problem. Work out the solution and express it as a Python `solve()` function that computes the numerical answer(s).

## Rules
1. Put every given value in as a function parameter with a default.
2. Return a dict with one entry per quantity asked, keyed "1", "2", ..., "N" in the order asked, each mapping to {"value": <number>, "unit": "<unit>"} — exactly that many entries, no intermediate or unit-converted extras.
3. Use only the standard library (math, etc.); do unit conversions explicitly. The function must COMPUTE each answer from its parameters — do not hard-code a precomputed number.

## Problem
Given an effective layer-averaged kinematic heat flux of F_H = 0.67 K \cdot m \cdot s^{-1}, where the vertical heat-flux profile decreases linearly from its surface value to zero at the top of the boundary layer, find the Deardorff convective velocity scale (w_*) for a dry, z_i = 1 km thick boundary layer of temperature T_v = 25^\circ C = 298 K. Express your answer in m \cdot s^{-1}.

The graded answer is whatever solve() returns, so let the function do the arithmetic. Give your solve() in a single ```python code block.
~~~~

</details>

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(F_H=0.67, z_i_km=1.0, T_v_K=298.0, g=9.81):
    z_i_m = z_i_km * 1000.0

    # F_H is the effective layer-averaged kinematic heat flux.
    w_star = ((g / T_v_K) * F_H * z_i_m) ** (1.0 / 3.0)

    return {
        "1": {"value": w_star, "unit": "m s^-1"}
    }
```
~~~~

#### `gpt55` · trap · run 2 · **FAIL**

Source: `experiments/trap/gpt55.run2.json` → `trap_air_111_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `3.532` | `2.8044165108646597` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    F_H=0.67,          # effective layer-averaged kinematic heat flux, K*m/s
    z_i_km=1.0,        # boundary-layer depth, km
    T_v=298.0,         # virtual temperature, K
    g=9.81             # gravitational acceleration, m/s^2
):
    z_i = z_i_km * 1000.0

    # Deardorff convective velocity scale:
    # w_* = [(g / T_v) * F_H * z_i]^(1/3)
    w_star = ((g / T_v) * F_H * z_i) ** (1.0 / 3.0)

    return {
        "1": {
            "value": w_star,
            "unit": "m s^-1"
        }
    }
```
~~~~

#### `gpt55` · trap · run 3 · **FAIL**

Source: `experiments/trap/gpt55.run3.json` → `trap_air_111_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `3.532` | `2.8044165108646597` | ✗ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(F_H=0.67, z_i_km=1.0, T_v_K=298.0, g=9.81):
    """
    Compute the Deardorff convective velocity scale w_*.

    Given F_H is the effective layer-averaged kinematic heat flux for a linear
    profile decreasing from the surface value to zero at the boundary-layer top.

    w_* = [ (g / T_v) * F_H * z_i ]^(1/3)

    Parameters:
        F_H: layer-averaged kinematic heat flux, K m s^-1
        z_i_km: boundary-layer depth, km
        T_v_K: virtual temperature, K
        g: gravitational acceleration, m s^-2

    Returns:
        dict: {"1": {"value": w_star, "unit": "m s^-1"}}
    """
    z_i_m = z_i_km * 1000.0
    w_star = ((g / T_v_K) * F_H * z_i_m) ** (1.0 / 3.0)

    return {
        "1": {
            "value": w_star,
            "unit": "m s^-1"
        }
    }
```
~~~~

### The same models on the parent problem (control) — all PASS

#### `gpt55-reasoning` · core_code · run 3 · **PASS**

Source: `experiments/core_code/gpt55-reasoning.run3.json` → `air_111` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.8` | `2.8044165108646597` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(F_H=0.67, z_i_km=1.0, T_v_K=298.0, g=9.81):
    z_i_m = z_i_km * 1000.0
    w_star = ((g / T_v_K) * F_H * z_i_m) ** (1.0 / 3.0)
    return {
        "1": {
            "value": w_star,
            "unit": "m s^-1"
        }
    }
```
~~~~

#### `gpt55` · core_code · run 2 · **PASS**

Source: `experiments/core_code/gpt55.run2.json` → `air_111` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `2.8` | `2.8044165108646597` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
import math

def solve(
    F_H=0.67,        # effective surface kinematic heat flux, K*m/s
    z_i_km=1.0,     # boundary layer depth, km
    T_v=298.0,      # virtual temperature, K
    g=9.81          # gravitational acceleration, m/s^2
):
    z_i = z_i_km * 1000.0  # convert km to m

    # Deardorff convective velocity scale:
    # w_* = [(g / T_v) * F_H * z_i]^(1/3)
    w_star = ((g / T_v) * F_H * z_i) ** (1.0 / 3.0)

    return {
        "1": {
            "value": w_star,
            "unit": "m s^-1"
        }
    }
```
~~~~

### Contrast: transcripts that get the trap right

#### `deepseek-v4-flash-reasoning` · trap · run 1 · **PASS**

Source: `experiments/trap/deepseek-v4-flash-reasoning.run1.json` → `trap_air_111_gen` · `num_attempts` = 1 · 1 stored call(s)

**details (expected vs. the value the interpreter actually returned)**

| sub | expected | actual | passed |
|---|---|---|---|
| `1` | `3.532` | `3.533343394711119` | ✓ |

**attempt 0** — `outcome` = `graded`

RESPONSE (verbatim, untruncated):

~~~~
```python
def solve(F_H=0.67, z_i=1000, T_v=298, g=9.81):
    """
    Compute the Deardorff convective velocity scale (w_*).

    Parameters:
        F_H : float – effective layer-averaged kinematic heat flux (K·m/s)
        z_i : float – boundary layer depth (m) (default 1000 m = 1 km)
        T_v : float – virtual temperature (K) (default 298 K = 25°C)
        g   : float – gravitational acceleration (m/s²) (default 9.81)

    Returns:
        dict with key "1" containing value and unit.
    """
    # Surface kinematic heat flux: linear profile from surface to zero at z_i,
    # so average = (surface + 0)/2 => surface = 2 * average
    Q0 = 2 * F_H
    w_star = ((g / T_v) * Q0 * z_i) ** (1/3)
    return {"1": {"value": w_star, "unit": "m/s"}}
```
~~~~

---

