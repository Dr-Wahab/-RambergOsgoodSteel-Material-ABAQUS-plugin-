# -*- coding: mbcs -*-
from __future__ import division
from abaqus import mdb, session
from abaqusConstants import *
import math
import material

_MIN_DEN = 1.0e-15     # tonne/mm^3 guard
_MIN_DPS = 1.0e-12     # minimum increment for plastic strain

def _sig(x, p=5):
    try:
        return float(('{0:.%dg}' % p).format(float(x)))
    except Exception:
        return float(x)

def _ramberg_osgood_strain(sig, Fy, E, n):
    return sig/float(E) + 0.002 * (sig/max(Fy,1e-12))**float(n)

def _gen_engineering(Fy, E, n, max_strain, n_raw=4000):
    s_max = 2.0*Fy
    s = [i*s_max/float(n_raw-1) for i in range(n_raw)]
    e = [_ramberg_osgood_strain(si, Fy, E, n) for si in s]
    ss, ee = [], []
    for si,ei in zip(s,e):
        if ei <= max_strain + 1e-12:
            ss.append(si); ee.append(ei)
        else:
            break
    if not ss or ss[0] != 0.0:
        ss.insert(0, 0.0); ee.insert(0, 0.0)
    sy = Fy; ey = _ramberg_osgood_strain(sy, Fy, E, n)
    if all(abs(si - sy) > 1e-6 for si in ss):
        for i in range(1, len(ss)):
            if ss[i] > sy:
                ss.insert(i, sy); ee.insert(i, ey); break
        else:
            ss.append(sy); ee.append(ey)
    return ss, ee, sy, ey

def _to_true(sig_eng, eps_eng, E):
    import math
    et = [math.log(1.0 + e) for e in eps_eng]
    st = [s*(1.0 + e) for s,e in zip(sig_eng, eps_eng)]
    epl = [et[i] - st[i]/float(E) for i in range(len(et))]
    return st, epl

def _resample_by_x(x, y, n):
    if n <= 2 or len(x) <= 2:
        return list(zip(x,y))
    x0, x1 = x[0], x[-1]
    if x1 <= x0: x1 = x0 + 1e-9
    step = (x1 - x0)/float(n-1)
    xn = [x0 + i*step for i in range(n)]
    out = []
    j = 0
    for xv in xn:
        while j < len(x)-2 and x[j+1] < xv: j += 1
        if xv <= x[0]: yv = y[0]
        elif xv >= x[-1]: yv = y[-1]
        else:
            denom = (x[j+1]-x[j])
            t = 0.0 if denom<=0.0 else (xv - x[j])/denom
            yv = y[j] + (y[j+1]-y[j])*t
        out.append((xv, yv))
    xe, ye = [], []
    for k,(xv,yv) in enumerate(out):
        if k and xv <= xe[-1]: xv = xe[-1] + _MIN_DPS
        xe.append(xv); ye.append(yv)
    return xe, ye

def _build_plastic(Fy, E, n, max_strain, npoints, addAnchor, anchorMPa):
    ss, ee, sy, ey = _gen_engineering(Fy, E, n, max_strain, n_raw=max(4000, 40*npoints))
    st, epl = _to_true(ss, ee, E)
    import math
    ey_t = math.log(1.0 + ey); sy_t = Fy*(1.0 + ey)
    epl_y = ey_t - sy_t/float(E)
    px = [max(0.0, ep - epl_y) for ep in epl]
    pairs = [(px[i], st[i]) for i in range(len(px)) if px[i] >= 0.0]
    pairs.sort(key=lambda p: p[0])
    # Default: first row = yield stress at 0.0 plastic strain
    first_x, first_y = 0.0, sy_t
    # Optional pre-yield anchor replaces the yield row
    if addAnchor:
        s_anchor = max( min(float(anchorMPa), sy_t*0.999), 1e-3 )  # MPa, small but not zero, < yield
        first_x, first_y = 0.0, s_anchor
    # enforce strict monotone plastic strain
    fixx = [first_x]; fixy = [first_y]
    for (x,y) in pairs:
        if x <= fixx[-1]: x = fixx[-1] + _MIN_DPS
        fixx.append(x); fixy.append(y)
    rx, ry = _resample_by_x(fixx, fixy, int(max(10, npoints)))
    table = tuple((_sig(ry[i],5), _sig(rx[i],5)) for i in range(len(rx)))
    return table, sy_t

def _preview_plot(plastic, matname):
    try:
        xy = session.XYData(name='RO_%s' % matname, data=[(p[1], p[0]) for p in plastic])
    except:
        base = 'RO_%s' % matname
        idx = 1
        while True:
            name = '%s_%d' % (base, idx)
            if name not in session.xyDataObjects.keys():
                xy = session.XYData(name=name, data=[(p[1], p[0]) for p in plastic])
                break
            idx += 1
    plot = session.XYPlot(name='RO_plot_%s' % matname)
    c = plot.charts.values()[0]
    curve = session.Curve(xyData=xy)
    c.setValues(curvesToPlot=(curve,), )
    vp = session.viewports.values()[0]
    vp.setValues(displayedObject=plot)


def runSteelRO(model='Model-1', matname='STEEL_RO',
               E=200000.0, nu=0.3, rho_tonmm3=7.85e-9,
               Fy=250.0, n=6.0, max_strain=0.03, npoints=50,
               previewOnly=False, addAnchor=True, anchorMPa=0.5,
               useDamage=False, eps_f=0.15, u_f=5.0, triax=0.0, **kwargs):

    E = float(E)
    nu = float(nu)
    Fy = float(Fy)
    n = float(n)
    max_strain = float(max_strain)
    npoints = int(npoints)
    rho = float(rho_tonmm3)
    addAnchor = bool(addAnchor)
    anchorMPa = float(anchorMPa)
    useDamage = bool(useDamage)
    eps_f = float(eps_f)
    u_f = float(u_f)
    triax = float(triax)

    if E <= 0.0 or Fy <= 0.0:
        raise RuntimeError('E and Fy must be > 0')
    if not (0.0 < nu < 0.5):
        raise RuntimeError('Poisson ratio must be in (0, 0.5)')
    if rho <= _MIN_DEN:
        raise RuntimeError('Density must be > %.1e tonne/mm^3' % _MIN_DEN)
    if npoints < 10:
        npoints = 10


    plastic, sy_t = _build_plastic(Fy, E, n, max_strain, npoints, addAnchor, anchorMPa)

    if useDamage:
        # Automatic estimate of ductile damage parameters from Ramberg–Osgood plastic curve
        # eps_f: equivalent plastic strain at damage initiation
        # u_f:   equivalent plastic displacement at failure (mm)
        epl_vals = [p[0] for p in plastic]
        eps_pl_max = max(epl_vals) if epl_vals else 0.0

        # If user did not provide eps_f (>0), set it as a fraction of the max plastic strain
        if eps_f <= 0.0 and eps_pl_max > 0.0:
            # Damage assumed to initiate at about 70% of the available plastic ductility
            eps_f = 0.7 * eps_pl_max

        # If user did not provide u_f (>0), estimate from element characteristic length
        if u_f <= 0.0 and eps_pl_max > 0.0:
            # Characteristic length (mm); can be overridden by keyword 'Lc_mm'
            Lc_mm = float(kwargs.get('Lc_mm', 5.0))
            if Lc_mm <= 0.0:
                Lc_mm = 5.0
            # Plastic strain interval between initiation and final failure
            delta_eps = max(eps_pl_max - eps_f, 0.1 * eps_pl_max)
            u_f = Lc_mm * delta_eps

        # If user did not specify stress triaxiality, assume uniaxial tension (η ≈ 1/3)
        if triax == 0.0:
            triax = 1.0/3.0

        if eps_f <= 0.0 or u_f <= 0.0:
            raise RuntimeError('Ductile damage auto-estimation failed; please check inputs or provide eps_f and u_f explicitly')


    if previewOnly:
        _preview_plot(plastic, matname)
        return

    m = mdb.models[str(model)]
    if matname in m.materials.keys():
        try:
            del m.materials[matname]
        except Exception:
            pass

    mat = m.Material(name=str(matname))
    mat.Density(table=((rho,),))
    mat.Elastic(table=((E, nu),))
    mat.Plastic(table=plastic)

    if useDamage:
        # Simple ductile metal damage:
        # Initiation: (equiv. plastic strain at failure, triaxiality=0, strain rate=0)
        mat.DuctileDamageInitiation(table=((eps_f, triax, 0.0),))
        # Damage evolution in terms of displacement at failure (mm), linear softening
        mat.ductileDamageInitiation.DamageEvolution(type=DISPLACEMENT, table=((u_f,),), softening=LINEAR)
        print('Steel RO material "%s" with ductile damage (eps_f=%.4g, u_f=%.4g mm)' %
              (matname, eps_f, u_f))
    else:
        print('Steel RO material "%s" created with %d plastic rows (first row: %.5g, %.5g)' %
              (matname, len(plastic), plastic[0][0], plastic[0][1]))


