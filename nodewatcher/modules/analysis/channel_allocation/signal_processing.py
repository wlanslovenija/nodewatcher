import math


def amplify_interference(signal, factor):
    """
    Returns the new signal strength in dB if the power is multiplied by factor

    :param signal: Original signal in dB
    :param factor: Multiplication factor
    :return: dB signal given that the original power was multiplied by the multiplication factor.
    """

    return 10 * math.log(factor * math.pow(10, signal / 10), 10)


def combine_power(signal1, signal2):
    """
    Calculates the combined signal (in db) from two signals. It assumes that the output power equals the sum
    of powers of signal1 and signal2.

    :param signal1: First signal strength in dB.
    :param signal2: Second signal strength in dB.
    :return: signal strength in dB.
    """

    return 10 * math.log(math.pow(10, signal1 / 10) + math.pow(10, signal2 / 10), 10)
