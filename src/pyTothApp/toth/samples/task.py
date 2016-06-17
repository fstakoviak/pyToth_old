class Methods:

    def __init__(self):
        pass

    @staticmethod
    def sum(num1, num2):
        return num1 + num2

    @staticmethod
    def divide(num1, num2):

        if (num2 == 0):
            num2 = 1

        return float(num1) / float(num2)

    @staticmethod
    def power(base, exponent):

        if (exponent == 0):
            exponent = 1

        return math.pow(base, exponent)

    ###########################################################

    @staticmethod
    def replace_text(text, search_for, replace_to, size):
        return text.replace(search_for, replace_to)[:size]
    
    ###########################################################