
class ObjectiveTracker:
    """
    This class tracks the objective value of a vehicle.
    Instead of computing the objective value every time from scratch,
    this class makes use of delta evaluation and recomputes only necessary parts.
    """

    def __init__(self, vehicles, rho):
        """
        Initializes the objective tracker by computing the objective value and storing intermediate values.

        vehicles: contains a list of vehicle objects
        rho: the fairness weight
        """

        self.rho = rho
        self.N = len(vehicles)

        self.total = sum(v.path_length for v in vehicles)
        self.squares = sum(v.path_length ** 2 for v in vehicles)

        self.objective_value = self.compute_objective()


    def compute_objective(self):
        """
        Computes and returns the objective value.
        """

        fairness = (self.total ** 2) / (self.N * self.squares)
        return self.total + self.rho * (1 - fairness)


    def update(self, old_length, new_length):
        """
        Updates the objective value by using delta evaluation.

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
        """
        Returns the resulting objective value, if the path lengths of some vehicles are replaced by new ones.

        old_lengths: set of old lengths of different vehicle paths
        new_lengths: set of new lengths of the same vehicle paths
        """

        delta_total = sum(n - o for o, n in zip(old_lengths, new_lengths))
        delta_squares = sum(n ** 2 - o ** 2 for o, n in zip(old_lengths, new_lengths))

        new_total = self.total + delta_total
        new_squares = self.squares + delta_squares

        new_fairness = (new_total ** 2) / (self.N * new_squares)
        return new_total + self.rho * (1 - new_fairness)
