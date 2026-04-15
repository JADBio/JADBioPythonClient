
class SVM:
    def to_dict(self):
        return {'type': 'SVMModelTrainer', 'param_str': self.to_svm_str()}

    @staticmethod
    def linearSVM(cost: float, constant: bool=True, probabilities: bool=False):
        return LinearSVM(cost, constant, probabilities)

    @staticmethod
    def linearSVR(cost: float, epsilon: float, constant: bool=True):
        return LinearSVR(cost, epsilon, constant)

    @staticmethod
    def polynomialSVM(degrees: int, cost: float, gamma: float, constant: bool=True, probabilities: bool=False):
        return PolynomialSVM(cost, gamma, degrees, constant, probabilities)

    @staticmethod
    def RBFSVM(cost: float, gamma: float, constant: bool=True, probabilities: bool=False):
        return RBFSVM(cost, gamma, constant, probabilities)

    @staticmethod
    def sigmoidSVR(cost: float, gamma: float, epsilon: float, constant: bool=True):
        return SigmoidSVR(gamma, cost, epsilon, constant)

    @staticmethod
    def RBFSVR(cost: float, gamma: float, epsilon: float, constant: bool=True):
        return RBFSVR(cost, gamma, epsilon, constant)

    @staticmethod
    def polynomialSVR(cost: float, gamma: float, degrees: int, epsilon: float, constant: bool=True):
        return PolynomialSVR(cost, gamma, degrees, epsilon, constant)


class LinearSVM(SVM):
    cost = 0
    constant = True
    probabilities = False

    def __init__(self, cost, constant=True, probabilities=False):
        self.cost = cost
        self.constant = constant
        self.probabilities = probabilities

    def to_svm_str(self):
        return " -s 0 -t 0 -c {} -r {} -b {}".format(
            self.cost,
            '1' if self.constant else '0',
            '1' if self.probabilities else '0'
        )

class LinearSVR(SVM):
    cost = 0
    epsilon = 0
    constant = False

    def __init__(self, cost, epsilon, constant=True):
        self.cost = cost
        self.epsilon = epsilon
        self.constant = constant

    def to_svm_str(self):
        return " -s 3 -t 0 -c {} -p {} -r {}".format(
            self.cost,
            self.epsilon,
            '1' if self.constant else '0',
        )

class SigmoidSVR(SVM):
    cost = 0
    gamma = 0
    epsilon = 0
    constant = False
    probabilities = False

    def __init__(self, gamma, cost, epsilon, constant=True, probabilities=False):
        self.cost = cost
        self.gamma = gamma
        self.epsilon = epsilon
        self.constant = constant
        self.probabilities = probabilities

    def to_svm_str(self):
        return " -s 3 -t 3 -g {} -c {} -p {} -r {}".format(
            self.gamma,
            self.cost,
            self.epsilon,
            '1' if self.constant else '0',
        )

class RBFSVR(SVM):
    cost = 0
    gamma = 0
    epsilon = 0
    constant = False

    def __init__(self, cost, gamma, epsilon, constant=True):
        self.cost = cost
        self.gamma = gamma
        self.epsilon = epsilon
        self.constant = constant

    def to_svm_str(self):
        return " -s 3 -t 2 -g {} -c {} -p {} -r {}".format(
            self.gamma,
            self.cost,
            self.epsilon,
            '1' if self.constant else '0',
        )

class RBFSVM(SVM):
    cost = 0
    gamma = 0
    constant = False
    probabilities = False

    def __init__(self, cost, gamma, constant=True, probabilities=False):
        self.cost = cost
        self.gamma = gamma
        self.constant = constant
        self.probabilities = probabilities

    def to_svm_str(self):
        return " -s 0 -t 2 -g {} -c {} -r {} -b {}".format(
            self.gamma,
            self.cost,
            '1' if self.constant else '0',
            '1' if self.probabilities else '0'
        )

class PolynomialSVM(SVM):
    cost = 0
    gamma = 0
    degrees = 1
    constant = False
    probabilities = False

    def __init__(self, cost, gamma, degrees, constant=True, probabilities=False):
        self.cost = cost
        self.gamma = gamma
        self.degrees = degrees
        self.constant = constant
        self.probabilities = probabilities

    def to_svm_str(self):
        return " -s 0 -t 1 -d {} -g {} -c {} -r {} -b {}".format(
            self.degrees,
            self.gamma,
            self.cost,
            '1' if self.constant else '0',
            '1' if self.probabilities else '0'
        )

class PolynomialSVR(SVM):
    cost = 0
    gamma = 0
    degrees = 0
    epsilon = 0
    constant = False

    def __init__(self, cost, gamma, degrees, epsilon, constant=True):
        self.cost = cost
        self.degrees = degrees
        self.gamma = gamma
        self.epsilon = epsilon
        self.constant = constant

    def to_svm_str(self):
        return " -s 3 -t 1 -d {} -g {} -c {} -p {} -r {}".format(
            self.degrees,
            self.gamma,
            self.cost,
            self.epsilon,
            '1' if self.constant else '0',
        )


class LaplaceSVM(SVM):
    cost = 0
    gamma = 0
    constant = False
    probabilities = False

    def __init__(self, cost, gamma, constant=True, probabilities=False):
        self.cost = cost
        self.gamma = gamma
        self.constant = constant
        self.probabilities = probabilities

    def to_svm_str(self):
        return " -s 0 -t 5 -g {} -c {} -r {} -b {}".format(
            self.gamma,
            self.cost,
            '1' if self.constant else '0',
            '1' if self.probabilities else '0'
        )

class LaplaceSVR(SVM):
    cost = 0
    gamma = 0
    epsilon = 0
    constant = False

    def __init__(self, cost, gamma, epsilon, constant=True):
        self.cost = cost
        self.gamma = gamma
        self.constant = constant
        self.epsilon = epsilon

    def to_svm_str(self):
        return " -s 3 -t 5 -g {} -c {} -p {} -r {}".format(
            self.gamma,
            self.cost,
            self.epsilon,
            '1' if self.constant else '0'
        )

# class