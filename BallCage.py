
import adsk.core
import adsk.fusion
import traceback


L = 100.0          
H = 75.0          
D = 50.0           

BALL_DIA = 40.0    

SIDE_RAIL = 6.0    
FACE_RAIL = 6.0   
TOP_BOTTOM_RAIL = 20.0  

def mm(v):
    """Convert millimetres to Fusion internal centimetres."""
    return v / 10.0


def make_box(temp_mgr, x0, y0, z0, sx, sy, sz):
    """Create a temporary axis-aligned box."""
    center = adsk.core.Point3D.create(
        mm(x0 + sx / 2.0),
        mm(y0 + sy / 2.0),
        mm(z0 + sz / 2.0)
    )

    x_dir = adsk.core.Vector3D.create(1, 0, 0)
    y_dir = adsk.core.Vector3D.create(0, 1, 0)

    obb = adsk.core.OrientedBoundingBox3D.create(
        center,
        x_dir,
        y_dir,
        mm(sx),
        mm(sy),
        mm(sz)
    )

    return temp_mgr.createBox(obb)


def validate():
    if min(L, H, D, BALL_DIA, SIDE_RAIL, FACE_RAIL, TOP_BOTTOM_RAIL) <= 0:
        raise ValueError('All dimensions must be positive.')

    if BALL_DIA >= min(L, H, D):       
        raise ValueError('BALL_DIA must be smaller than L, H, and D.')

    front_clear_x = L - 2 * SIDE_RAIL
    front_clear_y = H - 2 * TOP_BOTTOM_RAIL

    top_clear_x = L - 2 * SIDE_RAIL
    top_clear_z = D - 2 * FACE_RAIL

    side_clear_y = H - 2 * TOP_BOTTOM_RAIL
    side_clear_z = D - 2 * FACE_RAIL

    if min(front_clear_x, front_clear_y) >= BALL_DIA:
        raise ValueError(
            'Front/back opening is large enough for the ball to escape. '
            'Increase rail thickness or increase BALL_DIA.'
        )

    if min(top_clear_x, top_clear_z) >= BALL_DIA:
        raise ValueError(
            'Top/bottom opening is large enough for the ball to escape. '
            'Increase rail thickness or increase BALL_DIA.'
        )

    if min(side_clear_y, side_clear_z) >= BALL_DIA:
        raise ValueError(
            'Left/right opening is large enough for the ball to escape. '
            'Increase rail thickness or increase BALL_DIA.'
        )


def run(context):
    ui = None

    try:
        validate()

        app = adsk.core.Application.get()
        ui = app.userInterface

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Please open a Fusion 360 Design workspace first.')
            return

        root = design.rootComponent

        # Create a new component so the generated model is easy to remove/rebuild.
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = 'Captive Ball Cage'

        temp_mgr = adsk.fusion.TemporaryBRepManager.get()

        cage_bodies = []

       
        # FOUR X-DIRECTION RAILS
        # Located at top/bottom + front/back edges.
     
        for y0 in (0.0, H - TOP_BOTTOM_RAIL):
            for z0 in (0.0, D - FACE_RAIL):
                body = make_box(
                    temp_mgr,
                    0.0, y0, z0,
                    L, TOP_BOTTOM_RAIL, FACE_RAIL
                )
                cage_bodies.append(comp.bRepBodies.add(body))

      
        # FOUR Y-DIRECTION RAILS
        # Located at left/right + front/back edges.
      
        for x0 in (0.0, L - SIDE_RAIL):
            for z0 in (0.0, D - FACE_RAIL):
                body = make_box(
                    temp_mgr,
                    x0, 0.0, z0,
                    SIDE_RAIL, H, FACE_RAIL
                )
                cage_bodies.append(comp.bRepBodies.add(body))

       
        # FOUR Z-DIRECTION RAILS
        # Located at left/right + top/bottom corners.
       
        for x0 in (0.0, L - SIDE_RAIL):
            for y0 in (0.0, H - TOP_BOTTOM_RAIL):
                body = make_box(
                    temp_mgr,
                    x0, y0, 0.0,
                    SIDE_RAIL, TOP_BOTTOM_RAIL, D
                )
                cage_bodies.append(comp.bRepBodies.add(body))

        # Join all rails into one cage body.
        combine_features = comp.features.combineFeatures
        target = cage_bodies[0]

        tools = adsk.core.ObjectCollection.create()
        for b in cage_bodies[1:]:
            tools.add(b)

        combine_input = combine_features.createInput(target, tools)
        combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combine_input.isKeepToolBodies = False
        combine_feature = combine_features.add(combine_input)

        cage = combine_feature.bodies.item(0)
        cage.name = 'One Piece Cage'

     
        # CAPTIVE BALL
       
        ball_center = adsk.core.Point3D.create(
            mm(L / 2.0),
            mm(H / 2.0),
            mm(D / 2.0)
        )

        sphere = temp_mgr.createSphere(ball_center, mm(BALL_DIA / 2.0))
        ball = comp.bRepBodies.add(sphere)
        ball.name = 'Free Captive Ball'

      
        # Add informational user parameters      
        params = design.userParameters

        def add_param(name, value_mm, comment):
            existing = params.itemByName(name)
            if existing:
                return
            val = adsk.core.ValueInput.createByString(f'{value_mm} mm')
            params.add(name, val, 'mm', comment)

        add_param('Cage_Length', L, 'Overall cage length')
        add_param('Cage_Height', H, 'Overall cage height')
        add_param('Cage_Depth', D, 'Overall cage depth')
        add_param('Ball_Diameter', BALL_DIA, 'Captive ball diameter')
        add_param('Side_Rail', SIDE_RAIL, 'Left/right rail thickness')
        add_param('Face_Rail', FACE_RAIL, 'Front/back rail thickness')
        add_param('Top_Bottom_Rail', TOP_BOTTOM_RAIL, 'Top/bottom rail thickness')

        # calculated values in message.
        front_clear_y = H - 2 * TOP_BOTTOM_RAIL
        top_clear_z = D - 2 * FACE_RAIL

        ui.messageBox(
            'Captive-ball cage created successfully.\n\n'
            f'Ball diameter: {BALL_DIA:.1f} mm\n'
            f'Front/back smallest opening: {front_clear_y:.1f} mm\n'
            f'Top/bottom smallest opening: {top_clear_z:.1f} mm\n\n'
            'The ball is a separate body and is not connected to the cage.\n'
            'The openings are smaller than the ball diameter, so the ball is captive.\n\n'
            'Next step: create CAM setups/toolpaths after choosing the actual CNC machine and saw.'
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    pass
