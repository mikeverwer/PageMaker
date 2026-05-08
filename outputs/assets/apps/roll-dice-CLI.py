"""
This program is meant to showcase the Central Limit Theorem using the example of rolling 6-sided dice.
The user is able to input any valid probability distribution for a single die. They are also asked to input the number
of dice to roll per trial, and the number of trials to simulate.

The program shows that for any original probability distribution, if enough dice are rolled per trial, the sum of the
dice produces a Normal distribution whose mean and standard deviation are:
    Mean = N x (mean of single die)
    St. Dev. = (standard deviation of single die) x sqrt(N)
Where N is the number of dice rolled per trial.

The program also simulates rolling the dice as often as requested to really drive the point home.


Created by Mike Verwer, M.Sc. Mathematics. PT Professor of Mathematics & Statistics, Mohawk College
mike.verwer@mohawkcollege.ca
"""

import random
import matplotlib.pyplot as plt
import numpy as np


def get_valid_distribution():
    print("Enter the probability of each die face. \nFor fair dice, enter 'fair'. \nFor a random distribution, "
          "enter 'random'.")
    while True:
        inputs = []
        total = 0

        for i in range(5):
            while True:
                try:
                    value_input = input(f"Enter probability of {i + 1}: ")
                    if value_input == "fair":
                        return [float(1 / 6), float(1 / 6), float(1 / 6), float(1 / 6), float(1 / 6), 1 - float(5 / 6)]
                    if value_input == "set1":
                        return [float(60 / 128), float(30 / 128), float(20 / 128), float(10 / 128), float(5 / 128),
                                1 - float(125 / 128)]
                    if value_input == 'set2':
                        return [0.4, 0.08, 0.02, 0.03, 0.09, 0.38]
                    if value_input == 'random' or value_input == 'rdm' or value_input == 'rnd':
                        return generate_random_distribution()
                    if '/' in value_input:
                        numerator, denominator = map(float, value_input.split('/'))
                        value = numerator / denominator
                    else:
                        value = float(value_input)

                    if value < 0 or value > 1:
                        raise ValueError("Value must be between 0 and 1.")
                    break
                except ValueError as e:
                    print(e)
                except ZeroDivisionError as e:
                    print("Denominator cannot be zero.")

            inputs.append(value)
            total += value

        if total > 1:
            print(f"The sum of the first 5 inputs is already greater than 1. Please try again.")
            continue

        inputs.append(1 - total)

        return inputs


def generate_random_distribution():
    values = [random.random() for _ in range(6)]
    total = sum(values)
    normalized_values = [value / total for value in values]
    normalized_values[5] = (1 - sum(normalized_values[:5]))
    return normalized_values


def get_valid_ints(prompt):
    while True:
        try:
            user_input = int(input(prompt))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    return user_input


def get_valid_int_list(input_string):
    try:
        integers_list = [int(x) for x in input_string.split()]
        return integers_list
    except ValueError:
        return None


def roll_dice(k, n, distribution):
    # rolls k dice, n times; then counts the face outcomes of the k rolls for each trial and sums them
    # we then count the frequency of each face over all n trials

    # partition the closed set of reals [0,1] according to the input die distribution
    partition = [0]
    total = 0

    for l in range(len(distribution)):
        total += distribution[l]
        partition.append(total)
    formatted_partition = [f"{num:.2f}" for num in partition]
    print(formatted_partition)

    # roll the dice. The outcome is an n x 6 matrix whose rows are the frequency of each face in the k rolls performed
    outcomes = []
    sum_of_faces = []
    for a in range(n):
        one, two, three, four, five, six = 0, 0, 0, 0, 0, 0
        for b in range(k):
            roll = random.random()
            if partition[0] <= roll < partition[1]:
                one += 1
            if partition[1] <= roll < partition[2]:
                two += 1
            if partition[2] <= roll < partition[3]:
                three += 1
            if partition[3] <= roll < partition[4]:
                four += 1
            if partition[4] <= roll < partition[5]:
                five += 1
            if partition[5] <= roll < partition[6]:
                six += 1

        outcomes.append([one, two, three, four, five, six])
        sum_of_faces.append(np.dot(outcomes[a], [1, 2, 3, 4, 5, 6]))

    face_counts = [0] * 6

    for row in outcomes:
        for j in range(6):
            face_counts[j] += row[j]

    return outcomes, face_counts, sum_of_faces


def calculate_mean_and_deviation(distribution):
    # mean = sum(face * distribution[face] for face in distribution)

    mean = 0
    for x in range(6):
        mean += (x + 1) * distribution[x]

    variance = 0
    for x in range(1, 7):
        variance += distribution[x - 1] * ((x - mean) ** 2)

    # variance = sum((face - mean) ** 2 for face in distribution)
    deviation = variance ** .5

    return mean, deviation


def create_dice_distribution_plot(probabilities, counts, mean, deviation):
    outcomes = range(1, 7)

    plt.subplot2grid((2, 2), (0, 0))  # First subplot in a 2 x 2 grid
    plt.bar(outcomes, probabilities, width=0.97, align='center')
    plt.xlabel('Die Face\nThe number on each bar indicates the\nnumber of times that face got rolled')
    plt.ylabel('Probability')
    plt.title('Probability Distribution of a Single Die')
    plt.ylim(0, 1)

    # Annotate the frequency of each face rolled during the simulation
    for bar in range(7):
        height = probabilities[bar - 1]
        plt.annotate(f'{counts[bar - 1]}', xy=(bar, height),
                     xytext=(0, 3), textcoords='offset points',
                     ha='center', va='bottom')

    # Draw vertical line at the mean
    plt.axvline(x=mean, ymin=probabilities[round(mean) - 1] + 0.1, ymax=0.85, color='r', label="mu")
    plt.annotate(fr"$\mu$ = {mean:.2f}", xy=(mean, 0.9), xytext=(mean, 0.9), ha='center', va='bottom')

    # Draw Vertical lines one standard deviation from the mean
    # Find appropriate values for y_min
    if mean + deviation > 5.5:
        y_min_positive = probabilities[5]
        y_min_negative = probabilities[round(mean - deviation) - 1]
    elif mean - deviation < 0.5:
        y_min_positive = probabilities[round(mean + deviation) - 1]
        y_min_negative = probabilities[0]
    elif mean - deviation < 0.5 and mean + deviation > 5.5:
        y_min_positive = probabilities[5]
        y_min_negative = probabilities[0]
    else:
        y_min_positive = probabilities[round(mean + deviation) - 1]
        y_min_negative = probabilities[round(mean - deviation) - 1]

    plt.axvline(x=mean + deviation, ymin=y_min_positive + 0.1, ymax=0.95, color='g')
    plt.axvline(x=mean - deviation, ymin=y_min_negative + 0.1, ymax=0.95, color='g')

    # Draw arrows from the mean line to the standard deviation lines
    plt.axhline(y=0.5, xmin=mean + 0.1, xmax=(mean + deviation) - 0.1, color='g')
    plt.annotate(fr"$\sigma$ = {deviation:.2f}", xy=(((2 * mean) + deviation) / 2, 0.8),
                 xytext=(((2 * mean) + deviation) / 2, 0.8), ha='center', va='bottom', color='g')
    plt.annotate(fr"$\sigma$ = {deviation:.2f}", xy=(((2 * mean) - deviation) / 2, 0.8),
                 xytext=(((2 * mean) - deviation) / 2, 0.8), ha='center', va='bottom', color='g')


def create_histogram(outcomes, die_rolled, trials):
    if (0.015 * die_rolled) < 0.99:
        width = 1 - 0.015 * die_rolled
    else:
        width = 0.99

    plt.subplot2grid((2, 2), (0, 1))  # Second subplot in a 2 x 2 grid
    plt.hist(outcomes, bins=range(1, max(outcomes) + 1), align='left', rwidth=width)
    plt.xlabel('Sum of Dice Rolled')
    plt.ylabel('Frequency of Sum')
    plt.title(f'Results of Simulating Rolling {die_rolled} Dice, {trials} Times')
    plt.xlim(die_rolled - 1, 6 * die_rolled + 1)


def create_convoluted_distribution_plot(distribution, number_of_dice, mean, deviation):
    outcomes = list(range(number_of_dice, 6 * number_of_dice + 1))

    if (0.015 * number_of_dice) < 0.99:
        width = 1 - 0.015 * number_of_dice
    else:
        width = 0.99

    plt.subplot2grid((2, 2), (1, 0), colspan=2)  # Third subplot in a 2 x 2 grid
    plt.bar(outcomes, distribution, width=width, align='center')
    plt.xlabel(f'Sum of {number_of_dice} Dice')
    plt.ylabel('Probability')
    plt.title(f'Probability Distribution of the Sum of {number_of_dice} Dice')
    plt.ylim(0, max(distribution) + 0.2 * max(distribution))

    # Draw vertical line at the mean
    plt.axvline(x=mean, color='r', label="mu")
    plt.annotate(fr"    $\mu$ = {mean:.2f}", xy=(mean, max(distribution) + 0.1 * max(distribution)),
                 xytext=(mean, max(distribution) + 0.1 * max(distribution)), ha='center', va='bottom')

    # Draw vertical lines 1 standard deviation from the mean
    plt.axvline(x=mean + deviation, color='g')
    plt.axvline(x=mean - deviation, color='g')
    plt.annotate(fr"    $\sigma$ = {deviation:.2f}", xy=(mean + deviation, max(distribution) + 0.1 * max(distribution)),
                 xytext=(mean + deviation, max(distribution) + 0.1 * max(distribution)), ha='left', va='bottom')


def main():

    print('Made by: Mike Verwer, M.Sc. Mathematics')

    repeat_inputs = None

    while True:
        # Get the probability distribution of a single die
        if repeat_inputs is not None:
            if 0 in repeat_inputs or 1 in repeat_inputs:
                ProbabilityDistribution = get_valid_distribution()
        else:
            ProbabilityDistribution = get_valid_distribution()

        # Calculate the mean and st. dev of one die
        DieMean, DieStandardDeviation = calculate_mean_and_deviation(ProbabilityDistribution)

        FormattedDistribution = [f"{num:.4f}" for num in ProbabilityDistribution]
        print(FormattedDistribution)
        print(f'Mean = {DieMean:.2f}\nStandard Deviation = {DieStandardDeviation:.2f}')

        # Get info on trials and dice to roll
        if repeat_inputs is not None:
            if 0 in repeat_inputs or 2 in repeat_inputs:
                DiceToRoll = get_valid_ints('How many dice should be rolled per trial? ')
            if 0 in repeat_inputs or 3 in repeat_inputs:
                TrialsToRun = get_valid_ints('How many trials should be run? ')
        else:
            DiceToRoll = get_valid_ints('How many dice should be rolled per trial? ')
            TrialsToRun = get_valid_ints('How many trials should be run? ')

        # Convolve the single die distribution with itself 'DiceToRoll' times
        # to find the probability distribution of rolling all the desired dice
        ConvolutedDistribution = ProbabilityDistribution
        for _ in range(DiceToRoll - 1):
            ConvolutedDistribution = np.convolve(ConvolutedDistribution, ProbabilityDistribution)

        # Create a Normalized distribution
        NormalizedDistribution = []
        for _ in range(len(ConvolutedDistribution)):
            NormalizedDistribution.append(
                (ConvolutedDistribution[_] - (DieMean * DiceToRoll)) / (DieStandardDeviation * (DiceToRoll ** .5)))

        # Run the simulation
        FacesPerTrial, OverallFaces, Sums = roll_dice(DiceToRoll, TrialsToRun, ProbabilityDistribution)

        print(f"Results of rolling {DiceToRoll} dice {TrialsToRun} times: ")
        print(" 1  2  3  4  5  6")
        print("------------------")
        for row, i in zip(FacesPerTrial, range(TrialsToRun)):
            print(f"{row} : Sum = {Sums[i]}")
        print(f"Total frequency of each face: {OverallFaces}")

        plt.figure(figsize=(10, 8))  # Adjust the figure size as needed

        # Create plots
        create_dice_distribution_plot(ProbabilityDistribution, OverallFaces, DieMean, DieStandardDeviation)
        create_histogram(Sums, DiceToRoll, TrialsToRun)
        create_convoluted_distribution_plot(ConvolutedDistribution, DiceToRoll, DiceToRoll * DieMean,
                                            (DiceToRoll ** 0.5) * DieStandardDeviation)

        plt.tight_layout()  # To avoid overlapping labels

        plt.show()

        # Ask the user if they want to run again
        run_again = input("Do you want to run again? (yes/no): ")
        if run_again.lower() in ('yes', 'y'):
            repeat_input_string = input('Which input(s) would you like to change? (Enter numbers separated by spaces)\n'
                                        '0: All\n'
                                        '1: Die Distribution\n'
                                        '2: Number of dice to roll\n'
                                        '3: Number of trials to run\n'
                                        '4: None, keep all inputs\n')
            repeat_inputs = get_valid_int_list(repeat_input_string)

            if repeat_inputs is not None:
                continue
            else:
                print("Invalid input. Please enter integers separated by spaces.")
                repeat_inputs = get_valid_int_list(repeat_input_string)

        if run_again.lower() not in ('yes', 'y'):
            print('Made by: Mike Verwer, M.Sc. Mathematics')
            break


if __name__ == "__main__":
    main()
