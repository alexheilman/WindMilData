# WindMil Data

## Description

Data wrangling program.

## Problem

WindMil is a software that leverages GIS databases to create flowable electric models to simulate the power flow of utility-scale electric networks.  These models are used to simulate system voltages, available fault current, energy losses, and the impact of distributed solar generation.  The calculated engineering data from these simulations can be exported into various formats.  The deliverable for these utility clients includes a set of printed system maps which displays data from these simulations.  A solution was needed to automate the transfer of WindMil simulated data into the AutoCAD mapping software.

Additionally, one technical issue within the exported data needed to be rectified.  "Voltage Drop" is a term used to describe the reduction in system voltage due to conductor impedance.  Consider a source of 100 volts followed by a conductor with a resistance of 2 ohms.  If 5 amps of current were to flow through this conductor, Ohm's Law tells us that 10 volts of voltage drop will occur by the end of the conductor.  WindMil contains an attribute field which calculates this voltage drop at every element in the electric network.  This number is useful, but does not give us the full picture.  Voltage regulators are commonly installed on electric systems to boost the line voltage back up to the nominal voltage, essentially counteracting the effects of voltage drop.  WindMil will calculate the voltage drop from nominal voltage, but will not calculate the total voltage drop accumulated in the presence of regulators. An example: 10 volts of voltage drop occur, a voltage regulator boosts the line voltage back to nominal, and an additional 2 volts of voltage drop occur further down the network.  At this point in the system, WindMil will display 2 volts of voltage drop (the element is 2 volts below nominal), even though an accumulated voltage drop of 12 volts has occured since the source (10 volts before the regulator and 2 volts after).
