# Fusion 360 Captive Ball Cage

This project creates a rectangular aluminum cage with a completely free captive ball inside. The ball is not connected to the frame. It can move inside the cage, while every exit opening has a limiting dimension smaller than the ball diameter.

## Files

- `BallCage.py` - Fusion 360 Python script.
- `ReadMe.md` - This guide.

## Default dimensions

| Parameter | Value |
|---|---:|
| Cage length | 100 mm |
| Cage height | 75 mm |
| Cage depth | 50 mm |
| Ball diameter | 40 mm |
| Side rail | 6 mm |
| Front/back rail | 6 mm |
| Top/bottom rail | 20 mm |

Default openings:
- Front/back: 88 x 35 mm
- Top/bottom: 88 x 38 mm
- Left/right: 35 x 38 mm

The ball is 40 mm diameter, so each opening has at least one dimension smaller than the ball.

## Run in Fusion 360

1. Open Autodesk Fusion 360 and enter the Design workspace.
2. Go to **Utilities > Scripts and Add-Ins**.
3. Select the **Scripts** tab.
4. Add or create a script location if required.
5. Place `BallCage.py` in the script folder.
6. Select the script and click **Run**.
7. Fusion creates a component named `Ball Cage`.

The model contains:
- `One Piece Cage`
- `Free Captive Ball`

## Change dimensions

Edit the settings near the top of the Python file:

```python
L = 100.0
H = 75.0
D = 50.0
BALL_DIA = 40.0
SIDE_RAIL = 6.0
FACE_RAIL = 6.0
TOP_BOTTOM_RAIL = 20.0
```

All values are millimetres. The script checks whether an opening becomes large enough for the ball to escape.

## Captive-ball rule

For a sphere, every possible exit must have a limiting dimension smaller than the sphere diameter.

Example:

```text
Ball diameter = 40 mm
Opening = 88 x 35 mm
35 mm < 40 mm
```

Also account for machining tolerance, chamfers, corner radii, and other features that may enlarge the effective opening.

## Important manufacturing note

The current script creates the desired CAD geometry. It does not yet define the actual sequence of saw cuts required to manufacture both the cage and captive ball from one solid aluminum block.

A manufacturing version must account for:
- CNC machine and number of axes
- Slitting-saw diameter and kerf
- Arbor/holder clearance
- Maximum cutting depth
- Workholding and re-fixturing
- Tool accessibility
- Remaining stock during each operation

Use Fusion 360 Manufacture simulation and collision checking before machining.

## CAM and G-code

The current script does not generate G-code.

Recommended workflow:

```text
CAD geometry
    |
Choose CNC machine
    |
Choose saw/cutters
    |
Create Manufacture setups
    |
Create toolpaths
    |
Simulate and check collisions
    |
Select the correct post-processor
    |
Generate NC/G-code
```

Machine-specific G-code should only be generated after the exact CNC machine, controller, tooling, workholding, and setup are known.

## Information needed for the CAM version

1. CNC machine make/model
2. Controller type
3. 3-axis, 4-axis, or 5-axis
4. Slitting-saw diameter
5. Slitting-saw thickness/kerf
6. Maximum usable cutting depth
7. Arbor/holder dimensions
