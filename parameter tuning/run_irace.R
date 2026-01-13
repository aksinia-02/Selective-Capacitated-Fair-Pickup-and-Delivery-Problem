library(irace)

scenario <- readScenario("scenario_50.txt")
parameters <- readParameters("parameters.txt")

irace(scenario = scenario)

scenario <- readScenario("scenario_100.txt")

irace(scenario = scenario)

