import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import gurobipy as gp 
from gurobipy import Model, GRB, quicksum

#Data import 
filename   = pd.ExcelFile(r'/Users/niloysmac/Documents/708 Project/demanddata.xlsx')
dataDemand = filename.parse('Demand')  
dataDistance = filename.parse('Distance')

#Demand Scaling
D = dataDistance.to_numpy();
Demand = dataDemand.to_numpy()
Demand =  Demand*.15 

#Set definition
n = 303                        #Number of potentital mobile pantries
m = 303                         #Number of demand nodes

I=[i for i in range(0,n)];
J=[j for j in range(0,m)];
#K=[k for k in range(0,m)];

A=[(i,j) for i in I for j in J]
#B=[(j,k) for j in J for k in K if j!=k]

#Model definition
mdl=Model('Project')

#Decision Variables
x = mdl.addVars(A, vtype=GRB.BINARY)      #wheter i supplies to j
y = mdl.addVars(J, vtype=GRB.BINARY)        #whether i is selected
s = {}
for i in range(n):
  for j in range(m):
    s[i,j] = mdl.addVar(vtype=GRB.INTEGER)  #supply from i to j
    
Amat = np.zeros((303,303)) #distnace matrix
d= 15                      #distance threshold (15mi)
M=100000000

for i in I: 
    for j in J: 
        if (D[i][j] <=d):
            Amat[i][j]=1
        else:
            Amat[i][j]=0

#Equity percentage
r=.05

##CONSTRAINTS

#all demand points are served
mdl.addConstrs((quicksum(x[i,j] for i in I) >= 1) for j in J)
#Strong formulation constraint
mdl.addConstrs((x[i,j] <= y[i]) for i in I for j in J)

#Distance constraints
mdl.addConstrs((x[i,j] <=  Amat[i][j]) for i in I for j in J)

#Supply can't be more than demand
mdl.addConstrs(sum(s[i,j] for i in I) <= Demand[j][0] for j in J)

#supply minimum
mdl.addConstrs(sum(s[i,j] for i in I) >= .1 * Demand[j][0] for j in J)

mdl.addConstrs((s[i,j]  <= 1000000000 * x[i,j]) for i in I for j in J) #supply criteria

mdl.addConstrs(x[i,i] >=x[i,k] for i in I for k in J if k!=i ) #serves its location first

#Linearized equity
mdl.addConstrs((sum(s[i, j] for i in I) * sum(Demand[k][0] for k in J) - (Demand[j][0] * quicksum(s[i, k] for (i, k) in A))) <= r * (quicksum(s[i, k] for (i, k) in A)) * sum(Demand[k][0] for k in J) for j in J)

mdl.addConstrs((sum(s[i, j] for i in I) * sum(Demand[k][0] for k in J) - (Demand[j][0] * quicksum(s[i, k] for (i, k) in A))) >= - r * (quicksum(s[i, k] for (i, k) in A)) * sum(Demand[k][0] for k in J) for j in J)

#Objective function
mdl.setObjective((quicksum(y[j] for j in J)), GRB.MINIMIZE) 

#Solve
mdl.optimize()

#locations
if mdl.status == GRB.OPTIMAL:
    count=0
    for i in range(303):
        if y[i].x == 1:
                print(f"({i+1})\n")
                count=count+1     
else:
    print("Optimal not found.")

##Arcs
if mdl.status == GRB.OPTIMAL:
    count=0
    for i in range(303):
        for j in range(303):
            if x[i, j].x == 1:
                print(f"({i+1},{j+1})\n")
                count=count+1
else:
    print("Optimal not found.")
    


