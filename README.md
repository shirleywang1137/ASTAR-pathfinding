# pathfinding
A* algorithm for Emergency Pickup Coordination
This code helps coordinate pickup of patients with the goal of minimizing energy usage.

The rules are as follows:
There are two types of users: with infectious diseases and without them. In order to design this transfer, we are provided with a schematic map, like the one shown in Figure 1. The service will be carried out in a collective electric transport.
The map shows the following information:
• Cell marked with a N: Address of patient without infectious diseases.
• Cell marked with a C: Address of a patient with infectious diseases. 3
• Cell marked with a CC: Care center of patients with infectious diseases.
• Cell marked with a CN: Care center of patients without infectious diseases.
• Cell marked with a P: Location of the parking.
• Cell marked with a number (1, 2, 3...): time (energy cost) to travel through that location. The time/cost necessary to move through cells without value (N, C, CC, CN or P) will be one unit.
• Cell marked with a X: non-traversable positions.
To carry out this task, there is a collective vehicle that, due to environmental commitment, is electric. The
transport can make as many trips as necessary and has the following characteristics:
• It must leave the parking and end there. It can pick up, without exceeding the vehicle’s capacity, as many patients as necessary in a single trip to take them to their respective care centers.
• The vehicle has 10 seats in total, with 2 of them specially enabled for contagious patients. Non- contagious patients may also use these two seats as long as contagious patients are not transported on the same trip at any time.
• The vehicle has 50 units of energy at maximum load. Use as many energy units as indicated in each cell on the map (as mentioned above) and, if a charge of 50 units is not enough to make all the necessary trips, you must go through the parking to recharge. This recharge action is immediate and has no additional cost.
• Contagious patients are the last to be picked up from their home and the first to be dropped off at their respective care centers on each journey in which they intervene.
• Whenever the vehicle passes by a patient’s home, and the conditions allow for pick-up, the patient will board the vehicle.
• The vehicle can only move either horizontally or vertically to adjacent cells.

Format of test cases:
N;1;1;1;1;1;1;1;N;1
           1;C;1;X;X;X;1;1;1;C
           1;1;X;2;2;1;N;1;2;2
           1;1;X;2;CC;1;1;1;CN;2
           1;1;X;2;2;2;2;2;2;2
           1;1;X;1;1;1;N;1;1;C
           N;X;X;X;X;X;1;N;1;1
           1;N;1;P;1;1;1;1;1;1
           1;N;1;1;1;1;N;1;N;1
           1;1;1;1;1;1;1;1;1;N

Result file details the emergency vehicle journey in the format of one line per cell traveled as follows:
(x,y):value:load, where x is the row number in the map, y is the column number, value the cost or type of cell (N, C, CC, CN or P) depending on the case and load the charge value remaining in the vehicle at that moment
