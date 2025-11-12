
class ObjectiveTracker:

    def __init__(self, vehicles, rho):
        self.rho = rho
        self.N = len(vehicles)

        self.total = sum(v.path_length for v in vehicles)
        self.squares = sum(v.path_length ** 2 for v in vehicles)

        self.objective_value = self.compute_objective()


    def compute_objective(self):
        fairness = (self.total ** 2) / (self.N * self.squares)
        return self.total + self.rho * (1 - fairness)


    def update(self, old_length, new_length):
        """
        updates the objective value.
        old_length: old length of a vehicle path
        new_length: new length of a vehicle path
        """

        delta = new_length - old_length
        delta_squares = new_length * new_length - old_length * old_length

        self.total += delta
        self.squares += delta_squares

        self.objective_value = self.compute_objective()

        return self.objective_value

    def predict_objective(self, old_lengths, new_lengths):
        delta_total = sum(n - o for o, n in zip(old_lengths, new_lengths))
        delta_squares = sum(n ** 2 - o ** 2 for o, n in zip(old_lengths, new_lengths))

        new_total = self.total + delta_total
        new_squares = self.squares + delta_squares

        new_fairness = (new_total ** 2) / (self.N * new_squares)
        return new_total + self.rho * (1 - new_fairness)
