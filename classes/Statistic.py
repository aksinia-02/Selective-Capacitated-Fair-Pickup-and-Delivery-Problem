from tools import objective_function_detailed

class Statistic:
    def __init__(self, solution=None, rho=None):
        self.iterations = 0
        self.objective_over_time = []
        self.fairness_over_time = []
        self.duration_over_time = []
        if solution is not None and rho is not None:
            objective, total_duration, fairness = objective_function_detailed(solution, rho)
            self.objective_over_time.append(objective)
            self.fairness_over_time.append(fairness)
            self.duration_over_time.append(total_duration)

    def update(self, solution, rho):
        self.iterations += 1
        objective, total_duration, fairness = objective_function_detailed(solution, rho)
        self.objective_over_time.append(objective)
        self.fairness_over_time.append(fairness)
        self.duration_over_time.append(total_duration)