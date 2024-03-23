# Pathfinding

This repository contains an implementation of the A* algorithm for Emergency Pickup Coordination. The code is designed to coordinate the pickup of patients with the goal of minimizing energy usage.

## Rules

The rules for coordinating the pickup are as follows:

- There are two types of users: those with infectious diseases and those without. The service is provided using collective electric transport.
- The map provided contains the following information:
  - Cells marked with a **N**: Address of a patient without infectious diseases.
  - Cells marked with a **C**: Address of a patient with infectious diseases.
  - Cells marked with **CC**: Care center for patients with infectious diseases.
  - Cells marked with **CN**: Care center for patients without infectious diseases.
  - Cells marked with a number (1, 2, 3...): Time (energy cost) to travel through that location. The time/cost necessary to move through cells without a value (N, C, CC, CN, or P) will be one unit.
  - Cells marked with an **X**: Non-traversable positions.
- The collective vehicle has the following characteristics:
  - It must leave the parking and return there. 
  - It can pick up, without exceeding the vehicle’s capacity, as many patients as necessary in a single trip to take them to their respective care centers.
  - The vehicle has 10 seats in total, with 2 of them specially enabled for contagious patients. Non-contagious patients may also use these two seats as long as contagious patients are not transported on the same trip at any time.
  - The vehicle has 50 units of energy at maximum load. If a charge of 50 units is not enough to make all the necessary trips, it must go through the parking to recharge. This recharge action is immediate and has no additional cost.
  - Contagious patients are the last to be picked up from their homes and the first to be dropped off at their respective care centers on each journey.
  - Whenever the vehicle passes by a patient’s home, and the conditions allow for pick-up, the patient will board the vehicle.
  - The vehicle can only move either horizontally or vertically to adjacent cells.

## Test Case Format

The format of the test cases is a CSV file containing the value of every cell, whether a number or a letter.

## Result File

The result file details the emergency vehicle journey in the format of one line per cell traveled as follows:
`(x,y):value:load`, where:
- `x` is the row number in the map.
- `y` is the column number.
- `value` is the cost or type of cell (N, C, CC, CN, or P) depending on the case.
- `load` is the remaining charge value in the vehicle at that moment.
