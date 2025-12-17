# -*- coding: mbcs -*-
from rsg.rsgGui import *

dialogBox = RsgDialog(
    title='Steel-RO v1',
    kernelModule='steel_ro_kernel',
    kernelFunction='runSteelRO',
    includeApplyBtn=False,
    includeSeparator=True,
    okBtnText='Create',
    applyBtnText='Apply',
    execDir=thisDir
)

# Targets
RsgTextField(
    p='DialogBox', fieldType='String', ncols=24,
    labelText='Model Name', keyword='model', default='Model-1'
)
RsgTextField(
    p='DialogBox', fieldType='String', ncols=24,
    labelText='Material Name', keyword='matname', default='Steel-RO'
)

# Elastic & density
RsgGroupBox(
    name='grpED', p='DialogBox',
    text='Elastic & density', layout='LAYOUT_FILL_X'
)
RsgTextField(
    p='grpED', fieldType='Float', ncols=12,
    labelText='E (MPa)', keyword='E', default='200000.0'
)
RsgTextField(
    p='grpED', fieldType='Float', ncols=12,
    labelText='nu (0-0.5)', keyword='nu', default='0.30'
)
RsgTextField(
    p='grpED', fieldType='Float', ncols=12,
    labelText='Density (tonne/mm^3)', keyword='rho_tonmm3', default='7.85e-9'
)

# Ramberg-Osgood
RsgGroupBox(
    name='grpRO', p='DialogBox',
    text='Ramberg-Osgood parameters', layout='LAYOUT_FILL_X'
)
RsgTextField(
    p='grpRO', fieldType='Float', ncols=12,
    labelText='Fy (MPa)', keyword='Fy', default='250.0'
)
RsgTextField(
    p='grpRO', fieldType='Float', ncols=12,
    labelText='n (hardening)', keyword='n', default='6.0'
)
RsgTextField(
    p='grpRO', fieldType='Float', ncols=12,
    labelText='Max engineering strain', keyword='max_strain', default='0.03'
)
RsgTextField(
    p='grpRO', fieldType='Integer', ncols=12,
    labelText='Plastic points (N)', keyword='npoints', default='50'
)

# Ductile damage
RsgGroupBox(
    name='grpDam', p='DialogBox',
    text='Ductile damage (metal)', layout='LAYOUT_FILL_X'
)
RsgCheckButton(
    p='grpDam',
    text='Enable ductile damage with evolution',
    keyword='useDamage',
    default=False
)
RsgTextField(
    p='grpDam', fieldType='Float', ncols=12,
    labelText='Failure eq. plastic strain', keyword='eps_f', default='0.0'
)
RsgTextField(
    p='grpDam', fieldType='Float', ncols=12,
    labelText='Damage evolution disp (mm)', keyword='u_f', default='0.0'
)

RsgTextField(
    p='grpDam', fieldType='Float', ncols=12,
    labelText='Char. length Lc for damage (mm)', keyword='Lc_mm', default='5.0'
)
RsgTextField(
    p='grpDam', fieldType='Float', ncols=12,
    labelText='Stress triaxiality eta (0 = auto uniaxial)', keyword='triax', default='0.0'
)
RsgLabel(
    p='grpDam',
    text='Initiation: (eps_f, eta, rate=0). If eta=0, plug-in uses eta~1/3 (uniaxial tension). Evolution: DISPLACEMENT-based.',
    useBoldFont=False
)

# Options
RsgGroupBox(
    name='grpOpt', p='DialogBox',
    text='Output options', layout='LAYOUT_FILL_X'
)
RsgCheckButton(
    p='grpOpt',
    text='Preview plot only (no material changes)',
    keyword='previewOnly',
    default=False
)
RsgCheckButton(
    p='grpOpt',
    text='Add small pre-yield row at epl=0',
    keyword='addAnchor',
    default=True
)
RsgTextField(
    p='grpOpt', fieldType='Float', ncols=12,
    labelText='Anchor stress (MPa)', keyword='anchorMPa', default='0.5'
)

dialogBox.show()
