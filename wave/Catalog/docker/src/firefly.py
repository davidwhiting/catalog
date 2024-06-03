## Initial use of firefly algorithm
## May not be very useful at the individual student level
## Will be a building block for later optimizations

import numpy as np
from pyfirefly import FireflyAlgorithm

# Define course scheduling problem parameters
num_courses = 50  # Maximum number of courses
num_periods = 10  # Maximum number of periods
max_credits_per_period = 15  # Maximum credits allowed per period
max_courses_per_period = 3  # Maximum courses allowed per period

# Define Firefly Algorithm parameters
num_fireflies = 50
max_iter = 100

# Define the objective function to evaluate a schedule
def evaluate_schedule(schedule):
    # Initialize fitness value
    fitness = 0
    
    # Check constraints for each period
    for period in schedule:
        total_credits = sum(course['credits'] for course in period)
        total_courses = len(period)
        
        # Penalize schedules that exceed credit constraints
        if total_credits > max_credits_per_period:
            fitness += total_credits - max_credits_per_period
        
        # Penalize schedules that exceed course constraints
        if total_courses > max_courses_per_period:
            fitness += total_courses - max_courses_per_period
            
    return fitness

# Initialize fireflies with random schedules
initial_fireflies = []
for _ in range(num_fireflies):
    schedule = [[] for _ in range(num_periods)]  # Initialize empty schedule
    for _ in range(num_courses):
        course = {}  # Initialize course with random attributes (e.g., id, credits)
        period_idx = np.random.randint(num_periods)  # Assign random period
        schedule[period_idx].append(course)
    initial_fireflies.append(schedule)

# Define the attractiveness function based on fitness values
def attractiveness(fitness_i, fitness_j):
    # Higher fitness value means better solution, so we want to minimize fitness
    if fitness_i <= fitness_j:
        return 1
    else:
        return np.exp(-0.1 * (fitness_i - fitness_j))

# Create FireflyAlgorithm object
fa = FireflyAlgorithm(evaluate_schedule, attractiveness)

# Run the Firefly Algorithm
best_schedule, best_fitness = fa.run(initial_fireflies, max_iter)

# Print the best schedule and its fitness value
print("Best Schedule:")
for period_idx, period in enumerate(best_schedule):
    print(f"Period {period_idx + 1}: {len(period)} courses, {sum(course['credits'] for course in period)} credits")
print("Fitness:", best_fitness)
