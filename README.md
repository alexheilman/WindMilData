# WindMil Data

### Overview
WindMil is a software that leverages GIS databases to create flowable electric models to simulate the power flow of utility-scale electric networks.  These models are used to simulate system voltages, available fault current, energy losses, and the impact of distributed solar generation.  The calculated engineering data from these simulations can be exported into various formats.  The deliverable for these utility clients includes a set of system maps which display data from these simulations.  A solution was needed to automate the transfer of WindMil simulated data into the AutoCAD mapping software.

| WindMil Engineering Software |  AutoCAD Map Deliverable  |
| --- | --- |
| <img src="https://github.com/alexheilman/WindMilData/blob/master/Images/Electric%20System%20-%20WindMil.PNG?raw=true" width="402" height="451">  |  <img src="https://github.com/alexheilman/WindMilData/blob/master/Images/Electric%20System%20-%20Map%20Deliverable.PNG?raw=true" width="368" height="451"> |

### Description
The WindMil Data program pulls in the exported simulation data from an existing electric system model and also a proposed electric system model.  This enables the consultant to analyze the before and after effects of electric infrastructure upgrades for each individual element in the network. The program wrangles and calculates the following data for all n elements in both model exports into one OUTPUT DATA.csv file:
- Existing model minimum phase voltage
- Existing model accumulated voltage drop
- Proposed model accumulated voltage drop
- Proposed model element's distance from source node
- Proposed model maximum available fault current
- Proposed model minimum available fault current
- Existing model simulated load current for each phase

The program is buttoned up into an executable file for use by the drafting staff.  The drafter copies and pastes the WindMil Data.exe file into the directory of the exported data files.  Once launched, a simple GUI prompts the user to point to each of the export files, originating the user's file explorer in the current directory:
- Existing "Voltage and Fault Results" (.rsl file)
- Existing "Circuit Elements" (.std file)
- Proposed "Voltage and Fault Results" (.rsl file)
- Proposed "Circuit Elements" (.std file)

Different element information is contained within each file, so both exports were necessary from both models in order for the program to function.  As the program provides the user with brief updates and time stamps as it merges the four large data arrays, calculates the relevant data, and formats it into one output file.  This formatted output data can be utilized for a number of different mapping softwares, so it was necessary to handle the subsequent data import with a separate program.  The following section describes the program designed to import the previous output data file into the AutoCAD mapping software.

### Technical Challenges
Apart from wrangling and formatting the data, one technical issue within the export needed to be rectified.  "Voltage Drop" is a term used to describe the reduction in system voltage due to conductor impedance.  Consider a source of 100 volts followed by a conductor with a resistance of 2 ohms.  If 5 amps of current were to flow through this conductor, Ohm's Law tells us that 10 volts of voltage drop will occur by the end of the conductor.  WindMil contains a covariate which calculates this voltage drop at every element in the electric network.  Also, please note that the overall voltage drop at any point in the system (sans any series voltage sources) is simply a summation of each element's voltage drop from the source until the present element (Kirchhoff’s Voltage Law). This number is useful, but does not give us the full picture.  Voltage regulators are commonly installed on electric systems to boost the line voltage back up to the nominal voltage, essentially counteracting the effects of voltage drop.  WindMil will calculate the voltage drop from nominal voltage, but will not calculate the total voltage drop accumulated in the presence of regulators. An example: 10 volts of voltage drop occur, a voltage regulator boosts the line voltage back to nominal, and an additional 2 volts of voltage drop occur further down the network.  At this point in the system, WindMil will display 2 volts of voltage drop (the element is 2 volts below nominal), even though an accumulated voltage drop of 12 volts has occured since the source (10 volts before the regulator and 2 volts after).  For the client deliverable, a method of calculating this accumulated voltage drop was needed.

One unique property of the "Voltage and Fault Results" export file is that every network element's parent is an earlier entry it in the data.  Using this property, as we iterate down the array, we can simply store the present element's accumulated voltage drop in a dictionary. For every decendent of said element, the accumulated voltage drop would simply be the summation of its own voltage drop with the dictionary value of its parent.  Note that this is a summation of the entire accumulated voltage drop back to the source node because every time an element adds its parent's accumulated voltage drop, said parent has already accumulated all the voltage drop incurred by its antecedents as well.  This reduced the time-complexity from O(n^2) to O(n).

This method worked for nearly all network element types (capacitors, transformers, etc.) except for multi-parent nodes.  Multi-parent nodes are needed for connectivity of single-phase elements in some cases. Three-phase devices and power lines are actually represented as one element in the simulation software, even though each of the three-phases often has different calculated data. In the instances where the parent of a three-phase element is not another three-phase element, but rather three single-phase elements, a multiparent node must exist. Multi-parent nodes do not follow the property where all three parents of the element precede it in the data. This meant before calculating the accumulated voltage drop for all typical elements in the array, the multi-parent nodes had to be handled separately. The "Voltage and Fault Results" export is home to all simulated data, but does not identify the element type and only contains one covariate for "parent" (meaning two of the three parents for the multi-parent nodes are lost in the export).  To account for this, a second export file called "Circuit Elements" was merged into the data which contained the element types and parent information for all three phases of every element.  The before the accumulated voltage drop is calculated for most elements, a separate function looks for the unique identifier for multi-parent nodes in the element type covariate, and crawls all the way back to the source node for each of the three phases separately, calculating the accumulated voltage drop along each entire branch.  After completion, the program continues assuming one common parent for all three-phases and that the parent precedes the element in the array.

### Demonstration

[![Video](https://img.youtube.com/vi/enbYCP3dh7Q/0.jpg)](https://www.youtube.com/watch?v=enbYCP3dh7Q)
