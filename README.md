# paraInduced
paraInduced is a ParaView-Pythong script meant for extracting circulation and calculating the induced drag of a wing or airplane. It has so far only been used with OpenFOAM cases, but other formats can be analyzed with some modification. 

The theoretical basis for the procedure is *Munk's stagger theorem*, according to which any lift producing object will have the same induced drag as a lifting line with the same spanwise distribution of circulation.

This script was written for use in a research work. Before use, it needs to be readjusted to the studied case, but it is not long or complex

### How to use

1. Input all the necessary parameters in the SETTINGS section of the code.

2. Load only the wing or airplane patch/patches into ParaView and switch to the correct time.

3. In the Python shell, select Run Script, choose the correctly adjusted script and wait.

The output file *paraInduced.log* contains the induced drag coefficient and the span-wise distributions of circulation and downwash in dimensionless form in gnuplot-ready format.

Currently, the script works only for symmetric, half-domain cases. As is, the script is set for the left half-domain (looking in the direction of flight). The currently assumed, body-centered, right handed coordinate system, is oriented so that the *x* axis is colinear with the airplane chord and pointing "back", with the *y* axis pointing "up" and the *z* axis pointing left along the span. To use the script either the case has to be transformed to this coordinate system or the script has to be modified. 






