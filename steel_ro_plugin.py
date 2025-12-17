# -*- coding: mbcs -*-
try:
    from abaqusGui import getAFXApp, Activator, AFXMode
    from abaqusConstants import ALL
    import os

    thisPath = os.path.abspath(__file__)
    thisDir = os.path.dirname(thisPath)

    toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
    toolset.registerGuiMenuButton(
        buttonText='Steel-RO v1',
        object=Activator(os.path.join(thisDir, 'steel_roDB.py')),
        kernelInitString='import steel_ro_kernel',
        messageId=AFXMode.ID_ACTIVATE,
        icon=None,
        applicableModules=ALL,
        version='1.2',
        author='RO Steel',
        description='Steel-RO v1: Elastic + Ramberg-Osgood plasticity with optional preview, pre-yield anchor, and ductile metal damage.'
    )
except Exception:
    pass
