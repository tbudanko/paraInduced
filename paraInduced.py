"""
                              paraInduced

extract circulation distribution and calculate induced drag for any wing
from finite volume method results (OpenFOAM)

author: Toma Budanko
"""


from math import *
import numpy as np
import os

"""---------------SETTINGS-------------------"""
# Angle of Attack
# Direction of lift
AoA = 2.0/180.0*pi
dirx = -np.sin(AoA)
diry = np.cos(AoA)

# Freestream velocity
V_inf = 22.3396226415094;

# Wing dimensions
S_ref = 0.30250;
span = 1.2;
halfSpan = span*0.5;

# Axis of Span
axis = 'z'

# Sampling
nPoints = 150
grading = 1
"""------------------------------------------"""


"""-------------------CODE-------------------"""
# Wing disretization
if grading == 1:
    sectionLen = halfSpan/nPoints*np.ones(nPoints)
else:
    rootCell = (1-simpleGrading**(1/(float(nPoints)-1)))/(1-simpleGrading**(float(nPoints)/(float(nPoints)-1)))
    tipCell = rootCell*simpleGrading
    sectionLen = np.geomspace(rootCell, tipCell, nPoints)

clipLoc = np.concatenate(([0], np.cumsum(sectionLen)))

sectionLoc = 0.5*(clipLoc[1:]+clipLoc[:-1])
clipLoc = clipLoc[1:]

cumulativeLift = np.zeros(nPoints)
sectionLift = np.zeros(nPoints)
circulationDiff = np.zeros(nPoints)

# OpenFOAM source
versa_unpowered = GetActiveSource()

# Surface normals
surfaceNormals = GenerateSurfaceNormals(Input=versa_unpowered)
surfaceNormals.FlipNormals = 1
#surfaceNormals.ComputeCellNormals = 1

# Lift differential field
calculator1 = Calculator(Input=surfaceNormals)
#calculator1.AttributeType = 'Cell Data'
calculator1.AttributeType = 'Point Data'
calculator1.ResultArrayName = 'Lift'
# only pressure taken into account because it is the dominant contributor to lift
calculator1.Function = '-p*(Normals_X*('+str(dirx)+')+Normals_Y*('+str(diry)+'))'#+'-(wallShearStress_X*('+str(dirx)+')+wallShearStress_Y*('+str(diry)+'))'

# Clip wing
clip = Clip(Input=calculator1)
clip.ClipType = 'Plane'
clip.Scalars = ['POINTS', 'p']
#clip.Value = -0.18846726417541504

# Integrated variables
integrateVariables = IntegrateVariables(Input=clip)

for i,ax in enumerate(clipLoc):
    # define clipping plane
    clip.ClipType.Origin = [0.0, 0.0, ax]
    clip.ClipType.Normal = [0.0, 0.0, 1.0]

    UpdatePipeline()

    data = servermanager.Fetch(integrateVariables)
    #cumulativeLift[i] = data.GetCellData().GetArray('Lift').GetValue(0)
    cumulativeLift[i] = data.GetPointData().GetArray('Lift').GetValue(0)

sectionLift[:] = cumulativeLift[:]
for i in range(1,nPoints):
    sectionLift[i] = cumulativeLift[i]-cumulativeLift[i-1]

# Circulation
circulation = np.divide(sectionLift, sectionLen)/V_inf

# Circulation delta along span
#circulationDiff[-1] = -circulation[-1]    # 2nd order (no winglets)

for i in range(1, nPoints-1):
    circulationDiff[i] = circulation[i]-circulation[i-1]

# Add other wing side for induced drag calculation
sectionLiftExt = np.concatenate((sectionLift[::-1], sectionLift[:]))
sectionLocExt = np.concatenate((-sectionLoc[::-1], sectionLoc[:]))
sectionLenExt = np.concatenate((sectionLen[::-1], sectionLen[:]))
vortexLocExt = np.concatenate((-clipLoc[::-1], clipLoc[:]))
circulationExt = np.concatenate((circulation[::-1], circulation[:]))
circulationDiffExt = np.concatenate((-circulationDiff[::-1], circulationDiff[:]))

# Downwash
downwashExt = np.array([sum([1.0/4.0/pi*circulationDiffExt[j]/(sectionLocExt[i]-vortexLocExt[j]) for j in range(2*nPoints)]) for i in range(2*nPoints)])
downwash = downwashExt[nPoints:2*nPoints]

# Induced drag coefficient
C_D_i = 2/V_inf**3/S_ref*sum([downwashExt[i]*sectionLiftExt[i] for i in range(2*nPoints)])
print('Induced drag coefficient: {}'.format(C_D_i))

# Output files
outputFile = open('paraInduced.log', 'w')

# Induced drag coefficient / Header
outputFile.write("# Induced Drag Coefficient: C_D_i = {}\n".format(C_D_i))
outputFile.write("#y\tG\tw\n")

# Span-wise distribution of nondimensional circulation
outputFile.writelines([str(sectionLoc[i]/halfSpan)+'\t'+str(circulation[i]/span/V_inf)+'\t'+str(downwash[i]/V_inf)+'\n' for i in range(nPoints)])

outputFile.close()
