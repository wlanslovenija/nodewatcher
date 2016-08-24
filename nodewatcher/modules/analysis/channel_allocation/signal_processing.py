import math


def amplify_interference(signal, factor):
    """
    Converts signal strength from dB to power, then multiplies the power with the multiplication factor and returns
    new signal strength in dB.

    :param signal: Original signal in dB
    :param factor: Multiplication factor
    :return: dB signal given that the original power was multiplied by the multiplication factor.
    """

    return 10 * math.log(factor * math.pow(10, float(signal) / 10), 10)


def combine_power(signal1, signal2):
    """
    Calculates the combined signal (in dB) from two signals. It assumes that the output power equals the sum
    of powers of signal1 and signal2.

    :param signal1: First signal strength in dB.
    :param signal2: Second signal strength in dB.
    :return: Combined signal strength in dB.
    """

    return 10 * math.log(math.pow(10, float(signal1) / 10) + math.pow(10, float(signal2) / 10), 10)
