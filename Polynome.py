import sys
import itertools
import functools


def get_first_numbers(s):
    """
    Gets a string as argument and returns all numbers which are at the begin of the string until a non numeric char appears.
    :param s: String to search for the first numbers.
    :return: All numeric characters until the first non numeric.
    """
    return "".join(list(itertools.takewhile(lambda x: x.isdigit(), list(s))))


def get_degree(s):
    """
    Returns the next value in the string (if it starts with a number, the number is returned); used if string begin  with "("
    :param s: String to search for the value.
    :return: The next value of the string (number or content of brackets).
    """
    if s[0] != "(":
        return get_first_numbers(s)
    else:  # s should now start with "("
        bracket_count = 0
        degree_str = ""
        # copy the string until matching ")"
        for i in range(len(s)):
            degree_str += s[i]
            if s[i] == ")":
                bracket_count -= 1
            elif s[i] == "(":
                bracket_count += 1
            if bracket_count == 0:
                # check if ^ or ** is behind the closing bracket
                if len(s) >= i+2 and (s[i+1] == "^" or s[i+1:i+3] == "**"):
                    pre_str = "^" if s[i+1] == "^" else "**"
                    degree_str += pre_str + get_degree(s[i+1+len(pre_str):])
                break
        return degree_str


@functools.total_ordering
class PolynomialSummand:
    """
    One part of the polynomial (e.g.:"5*x^2")
    """

    def __init__(self, coefficient, degree):
        self.coefficient = coefficient
        self.degree = degree

    @classmethod
    def get_instance(cls, polynomPart):
        """
        Inits an object of class, matching the passed part of the polynomial(e.g.: polynomPart="3*x^(5/3)").
        :param polynomPart: String to create object from (e.g.: polynomPart="3*x^(5/3)").
        :return: Object of PolynomialSummand.
        """
        # get degree
        degree = 0
        splitted = polynomPart.split("x")
        # iterate, if x occurs more than once (e.g.: x^2*4*x)
        for i in range(1, len(splitted)):
            temp_degree = 1  # default value, if x got no explicit degree (degree = 1)
            if len(splitted[i]) >= 2 and (splitted[i][0] == "^" or splitted[i][:2] == "**"):  # check if x got an explicit degree
                beginning_index = (splitted[i][:2] == "**") + 1  # start of degree
                degr_str = get_degree(splitted[i][beginning_index:])
                temp_degree = eval(degr_str.replace("^", "**"))

                # remove degree from string (not used anymore)
                splitted[i] = splitted[i][beginning_index + len(degr_str):]
            if len(splitted[i - 1]) >= 1 and splitted[i - 1][-1] == "/":  # check for fraction bar before x
                temp_degree *= -1
            # check for brackets or divisor for other degrees
            opened_brackets = 0  # counts the closed and opened brackets before the current x
            # count how many brackets are still open:
            for j in range(i - 1, -1, -1):
                opened_brackets += splitted[j].count('(') - splitted[j].count(')')
            closed_brackets = opened_brackets  # closed_brackets after x must be the same as opened_brackets before x

            # find closing brackets and check for degrees
            for temp_i in range(i, len(splitted)):
                if opened_brackets <= 0:  # no brackets left -> stop outer loop
                    break
                after_brackets = splitted[temp_i].split(")")  # elements after 0 (1, 2, ...) are the potential degrees
                # iterate over potential degrees after brackets
                for bracket_index in range(1, len(after_brackets)):
                    if opened_brackets <= 0:  # no brackets left
                        break
                    # check if degree exist after bracket:
                    if len(after_brackets[bracket_index]) >= 2 and (
                            after_brackets[bracket_index][0] == "^" or after_brackets[bracket_index][:2] == "**"):
                        # exponential laws (a^b)^c = a^(b*c) -> multiply new degree to tamp_degree:
                        temp_degree *= eval(get_degree(after_brackets[bracket_index][(after_brackets[bracket_index][
                                            :2] == "**") + 1:] + ")").replace("^", "**"))  # + ")" because after_brackets is splited by ")"
                    opened_brackets -= 1

            # find opening brackets and check for fraction bars
            for temp_i in range(i - 1, -1, -1):
                if closed_brackets <= 0:  # no brackets left -> stop outer loop
                    break
                before_brackets = splitted[temp_i].split(
                    "(")  # elements before n (0, 1, ..., n-1) could contain a fraction bar
                # iterate over potential degrees after brackets
                for bracket_index in range(len(before_brackets) - 2, -1,
                                           -1):  # -2 because -1 would be the last element, a fraction bar is only important if it's before the "("...
                    if closed_brackets <= 0:  # no brackets left
                        break
                    # check if fraction_bar exist before bracket:
                    if len(before_brackets[bracket_index]) >= 1 and before_brackets[bracket_index][-1] == "/":
                        # x is in divisor -> change sign
                        temp_degree *= -1
                    closed_brackets -= 1

            # add temp_degree to degree
            degree += temp_degree
        # only int is valid for the degrees
        if degree != int(degree):
            print("Degree " + degr_str + " not valid, using " + str(degree) + ".")
        degree = int(degree)

        # get coefficient
        # degree removed, splitted by x -> only coefficient left after joining
        coefficient_str = "1".join(splitted)  # used 1 to join, because result should be a product
        coefficient = eval(coefficient_str.replace("^", "**"))

        # create PolynomialSummand object
        return PolynomialSummand(coefficient, degree)

    def __repr__(self):
        """
        Creates the string representation of the polynomial summand.
        :return: the string representation of the polynomial summand
        """
        if self.coefficient == 0:
            return "0"
        elif self.coefficient == 1 or self.coefficient == -1:  # because (-)1 * x^n = (-)x^n ...
            if self.degree == 0:  # only coefficient
                return str(int(self.coefficient))
            else:
                if self.coefficient == -1:  # for brackets and sign
                    return "(-x" + ("^" + str(self.degree)) * (self.degree != 1) + ")"
                else:  # self.coefficient == 1
                    return "x" + ("^" + str(self.degree)) * (self.degree != 1)
        # check if self.coefficient is an int or like 1.0, -3.0, ....
        if self.coefficient == int(self.coefficient):
            self.coefficient = int(self.coefficient)
        if self.coefficient < 0:
            str_builder = "(" + str(self.coefficient) + ")"
        else:
            str_builder = str(self.coefficient)
        if self.degree > 0:
            str_builder += "*x" + ("^" + str(self.degree)) * (self.degree != 1)
        return str_builder

    def __eq__(self, other):
        """
        Checks if degrees are equal.
        :param other: other object of PolynomialSummand.
        :return: True, if self and object got the same degree.
        """
        # check if both got the same degree
        return self.degree == other.degree

    def __lt__(self, other):
        """
        Checks if degree is lesser than the other.
        :param other: other object of PolynomialSummand.
        :return: True, if degree of self is lesser then degree of object.
        """
        return self.degree < other.degree

    def __add__(self, other):
        """
        Adds an other PolynomialSummand to the object.
        :param other: Object of type PolynomialSummand.
        :return: self.
        """
        self.coefficient += other.coefficient
        return self

    def __sub__(self, other):
        """
        Subtracts an other PolynomialSummand from the object.
        :param other: Object of type PolynomialSummand.
        :return: self
        """
        self.coefficient -= other.coefficient
        return self

    def __mul__(self, other):
        """
        Multiplies the coefficient with the passed scalar.
        :param other: Numeric scalar.
        :return: self
        """
        self.coefficient *= other
        return self

    def __truediv__(self, other):
        """
        Divides the coefficient with the passed scalar.
        :param other: Numeric scalar.
        :return: self
        """
        self.coefficient /= other
        return self

    def copy(self):
        """
        Creates a copy of self.
        :return: The copy of self.
        """
        return PolynomialSummand(self.coefficient, self.degree)


@functools.total_ordering
class Polynomial:
    """
    Represents a polynomial, contains an array of PolynomialSummand
    """
    def __init__(self, polynom_str):
        """
        Initialize object.
        :param polynom_str: String containing a polynomial.
        """
        self.summands = [PolynomialSummand(0, 0)]
        self.degree = 0
        # split polynom_str by + and -, exept for signs like "...(-..."
        final_polynom_parts = []

        opened_brackets = 0
        polynom_str_builder = ""
        # split without using the the method, to recognize (- or (a+b) ...
        for polynom_c in polynom_str:
            if (polynom_c == "-" or polynom_c == "+") and opened_brackets <= 0:
                # create new PolynomialSummand
                self.add_polynom_summand(polynom_str_builder)
                # reset str_builder
                polynom_str_builder = "-" if polynom_c == "-" else ""
            else:
                if polynom_c == "(":
                    opened_brackets += 1
                elif polynom_c == ")":
                    opened_brackets -= 1
                polynom_str_builder += polynom_c
        if polynom_str_builder != "":  # check if polynom_str_builder has changed (after initialization)
            self.add_polynom_summand(polynom_str_builder)  # for last element
        # check for maybe new degree
        self.check_degree()

    def add_polynom_summand(self, polynom_part_str):
        """
        Adds a PolynomialSummand object created from the argument to self.
        :param polynom_part_str: String to create PolynomialSummand out of.
        :return: self.
        """
        # method use, because summands with same degree should be existing only once
        new_summand = PolynomialSummand.get_instance(polynom_part_str)
        # initialize new PolynomialSummands
        for i in range(len(self.summands), new_summand.degree + 1):
            self.summands.append(PolynomialSummand(0, i))
        self.summands[new_summand.degree] += new_summand
        # check for maybe new degree
        self.check_degree()
        return self

    def check_degree(self):
        """
        Refreshes the current degree value.
        """
        if self.summands[-1].coefficient == 0 and len(self.summands) != 1:  # last summand is 0, so it can be removed
            self.summands = self.summands[:-1]
            self.degree = len(self.summands) - 1  # -1 because it starts with x^0
            self.check_degree()
        else:
            self.degree = len(self.summands) - 1  # -1 because it starts with x^0

    def __eq__(self, other):
        """
        Checks if max. degrees of summands are equal.
        :param other: other object of Polynomial.
        :return: True, if self and object got the same max. degree.
        """
        # check if both got the same degree
        return self.degree == other.degree

    def __lt__(self, other):
        """
        Checks if degree is lesser than the other.
        :param other: other object of PolynomialSummand.
        :return: True, if degree of self is lesser then degree of object.
        """
        return self.degree < other.degree

    def __add__(self, other):
        """
        Adds the other polynomial to self.
        :param other: Object of type Polynomial.
        :return: self.
        """
        # Check if degrees are matching:
        if self.degree < other.degree:
            for i in range(self.degree + 1, other.degree + 1):
                self.summands.append(PolynomialSummand(0, i))
            self.degree = other.degree
        # add other polynomial to self
        for i in range(self.degree + 1):
            self.summands[i] += other.summands[i]
        # check for maybe new degree
        self.check_degree()
        return self

    def __sub__(self, other):
        """
        Subtracts the other polynomial to self.
        :param other: Object of type polynomial.
        :return: self.
        """
        # Check if degrees are matching:
        if self.degree < other.degree:
            for i in range(self.degree + 1, other.degree + 1):
                self.summands.append(PolynomialSummand(0, i))
            self.degree = other.degree
        # subtract other polynomial from self
        for i in range(self.degree + 1):
            self.summands[i] -= other.summands[i]
        # check for maybe new degree
        self.check_degree()
        return self

    def __mul__(self, other):
        """
        Multiplies the scalar to self.
        :param other: Scalar to multiply with.
        :return self
        """
        # multiply scalar to summands
        for summand in self.summands:
            summand *= other
        # check for maybe new degree
        self.check_degree()
        return self

    def __truediv__(self, other):
        """
        Divides self by scalar.
        :param other: Scalar to divide by.
        :return self
        """
        # multiply scalar to summands
        for summand in self.summands:
            summand /= other
        return self

    def copy(self):
        """
        Creates an object of self.
        :return: The object of self.
        """
        cpy = Polynomial("")
        cpy.degree = self.degree
        cpy.summands = []
        for summand in self:
            cpy.summands.append(summand.copy())
        return cpy

    def __iter__(self):
        return iter(self.summands)

    def __repr__(self):
        """
        Creates a string representation of the polynomial.
        :return: the string representation
        """
        pol_repr = " + ".join(filter(lambda x: x != "0", list(map(lambda x: str(x), self.summands))))
        if pol_repr == "":
            return "0"
        return pol_repr

    def polinomial_division(self, other, print_formated = False):
        """
        Devides the self polynomial (dividend) by the other polynomial (divisor). After the division self is the rest of the division.
        :param other: An other Polynomial object, which is the divisor.
        :param print_formated: If true, division is printed to console (default: False).
        :return: The quotient of the division.
        """
        # refreshing degrees:
        self.check_degree()
        other.check_degree()
        # start division
        lines = ["(" + str(self) + ") / (" + str(other) + ") = "]
        indent = 0  # for visualisation
        quotient = Polynomial("")
        while self >= other:
            str_builder = " " * indent + "-("  # initialize with indent
            # TODO: this., . in str for summand building
            # create summand of quotient
            coefficient_quorient = self.summands[-1].coefficient / other.summands[-1].coefficient
            degree_differenz = self.degree - other.degree
            quotient.add_polynom_summand(str(coefficient_quorient) + "*x^" + str(degree_differenz))
            # create polynomial to subtract from self
            sub_polynomial = other.copy()
            for summand in sub_polynomial:
                summand.coefficient *= coefficient_quorient  # -> first coefficient match
                summand.degree += degree_differenz  # -> same max-degree
            str_builder += str(sub_polynomial)
            # fix summands array (add summands with coefficient 0 for the ):
            sub_polynomial.summands = [PolynomialSummand(0, i) for i in range(0, degree_differenz)] + sub_polynomial.summands
            sub_polynomial.degree += degree_differenz
            self -= sub_polynomial
            self.check_degree()
            if print_formated:
                # increase indent and append builded string to the maybe printed text
                str_builder += ")"
                lines.append(str_builder)
                lines.append(" " * indent + "-" * len(str_builder))  # for the line under the subtraction
                indent += 2
                lines.append(" " * indent + str(self))
        # print division if needed:
        if print_formated:
            lines[0] += str(quotient)
            print("\n".join(lines))
            # check for rest
            if str(self) != "0":
                print("Rest: " + str(self))

        return quotient


# if called by terminal:
# check if input is correct
if len(sys.argv) <= 2:
    print("Wrong arguments, add dividend and divisor as argument.")
else:
    # remove spaces
    sys.argv[1] = sys.argv[1].replace(" ", "")
    sys.argv[2] = sys.argv[2].replace(" ", "")

    # create Polynomial objects
    dividend = Polynomial(sys.argv[1])
    divisor = Polynomial(sys.argv[2])

    # print results
    dividend.polinomial_division(divisor, True)
