import collections
import itertools

from ortools.linear_solver import pywraplp

# create a variable for each user, slots, colour
def createVariables(solver, users, slots, colours):

  # variable for user and colour that does not exist are not necessary

  toReturn = collections.defaultdict(
      lambda: collections.defaultdict(
          lambda: dict()
      )
  )

  for (u, s, c) in itertools.product(users, slots, colours):
    toReturn[u][s][c] = solver.BoolVar(f"{u}-{s}-{c}")

  return (solver, toReturn)

# create slack variables
def createSlack(solver, users, slots, colours):
  toReturn = collections.defaultdict(
      lambda: dict()
  )

  for (s, c) in itertools.product(slots, colours):
    toReturn[s][c] = solver.BoolVar(f"slack-{s}-{c}")

  return toReturn

def retrieveUsers(graph):
  toReturn = set()

  for v in graph.values():
    for user in v:
      toReturn.add(user)

  return toReturn

def retrieveColour(graph):
  return set(graph.keys())

def invertGraph(graph):
  toReturn = collections.defaultdict(
      lambda: set()
  )

  for (k, v) in graph.items():
    for u in v:
      toReturn[u].add(k)

  return toReturn

def solve(colourToUser, slots):
  solver = pywraplp.Solver.CreateSolver('SCIP')

  users = retrieveUsers(colourToUser)
  colours = retrieveColour(colourToUser)
  userToColour = invertGraph(colourToUser)
  solver, variables = createVariables(solver, users, slots, colours)
  slack = createSlack(solver, users, slots, colours)

  # we must attend at the same time for a topic
  for (s, c) in itertools.product(slots, colours):
    for u in colourToUser[c]:
      constraint = solver.Constraint(0, 0)

      constraint.SetCoefficient(variables[u][s][c], 1)
      constraint.SetCoefficient(slack[s][c], -1)

  # we must meet exactly once for each topic
  for c in colours:
    constraint = solver.Constraint(1, 1)

    for s in slots:
      constraint.SetCoefficient(slack[s][c], 1)

  # you cannot attend two topics at the same time
  for s in slots:
    for u in users:
      constraint = solver.Constraint(-solver.infinity(), 1)

      for c in userToColour[u]:
        constraint.SetCoefficient(variables[u][s][c], 1)

  objective = solver.Objective()

  for u in users:
    slack = solver.IntVar(0.0, solver.infinity(), f'maximum_end_time_{u}')

    for s in slots:
        for c in colours:
            constraint = solver.Constraint(-solver.infinity(), 0)
            constraint.SetCoefficient(slack, -1)
            constraint.SetCoefficient(variables[u][s][c], s)

    objective.SetCoefficient(slack, 1)

  objective.SetMinimization()

  solver.Solve()

  toReturn = collections.defaultdict(lambda:list())

  for u in users:
    for s in slots:
      found = False
      for c in colours:
        if variables[u][s][c].solution_value() > 0.99:
          toReturn[u].append(c)
          found = True
          break
      if not found:
        toReturn[u].append(None)

  return toReturn