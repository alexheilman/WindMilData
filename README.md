# WindMil Data

## Overview
WindMil is a software that leverages GIS databases to create flowable electric models to simulate the power flow of utility-scale electric networks.  These models are used to simulate system voltages, available fault current, energy losses, and the impact of distributed solar generation.  The calculated engineering data from these simulations can be exported into various formats.  The deliverable for these utility clients includes a set of system maps which display data from these simulations.  A solution was needed to automate the transfer of WindMil simulated data into the AutoCAD mapping software.

| WindMil Engineering Software |  AutoCAD Map Deliverable  |
| --- | --- |
| <img src="https://github.com/alexheilman/WindMilData/blob/master/Electric%20System%20-%20WindMil.PNG?raw=true" width="402" height="451">  |  <img src="https://github.com/alexheilman/WindMilData/blob/master/Electric%20System%20-%20Map%20Deliverable.PNG?raw=true" width="368" height="451"> |

## Challenges
Additionally, one technical issue within the exported data needed to be rectified.  "Voltage Drop" is a term used to describe the reduction in system voltage due to conductor impedance.  Consider a source of 100 volts followed by a conductor with a resistance of 2 ohms.  If 5 amps of current were to flow through this conductor, Ohm's Law tells us that 10 volts of voltage drop will occur by the end of the conductor.  WindMil contains a covariate which calculates this voltage drop at every element in the electric network.  Also, please note that the overall voltage drop at any point in the system (sans any series voltage sources) is simply a summation of each element's voltage drop from the source until the present element (Kirchhoff’s Voltage Law). This number is useful, but does not give us the full picture.  Voltage regulators are commonly installed on electric systems to boost the line voltage back up to the nominal voltage, essentially counteracting the effects of voltage drop.  WindMil will calculate the voltage drop from nominal voltage, but will not calculate the total voltage drop accumulated in the presence of regulators. An example: 10 volts of voltage drop occur, a voltage regulator boosts the line voltage back to nominal, and an additional 2 volts of voltage drop occur further down the network.  At this point in the system, WindMil will display 2 volts of voltage drop (the element is 2 volts below nominal), even though an accumulated voltage drop of 12 volts has occured since the source (10 volts before the regulator and 2 volts after).  For the client deliverable, a method of calculating this accumulated voltage drop was needed.

## Description
The WindMil Data program pulls in the exported simulation data from an existing electric system model and a proposed electric system model.  This enables the consultant to analyze the before and after effects of electric infrastructure upgrades. The program wrangles and calculates the following data for all n elements in each model into one output file:
- Minimum phase voltage
- Existing accumulated voltage drop
- Proposed accumulated voltage drop
- Element's distance from source
- Maximum available fault current
- Minimum available fault current
- Simulated load current for each phase

The program is buttoned up into an executable file for use by the drafting staff.  The drafter copies and pastes the .exe file into the directory of the exported data files.  Once launched, a simple GUI asks the user to point to each of the export files, originating the file explorer in the current directory:
- Existing system fault??? (.rsl file)
- Existing ??? (.std file)
- Proposed system fault??? (.rsl file)
- Proposed ??? (.std file)

Different element information is contained within each file, so both exports were necessary for the program to function. The .std file contains element device type and multi-parent node information. These two pieces of information were essential for the calculation of accumulated voltage drop. The device type enabled the identification voltage regulators through the system. The multi-parent node information allowed a work-around for a major obstacle in electric networks - nodes.  For most three-phase conductors and devices on the system, WindMil treats them as one element and therefore only one parent is assigned. For instances where each of the three phases has a different parent, the analysis software inserts multi-parent nodes to account for this.

## Pseudocode

