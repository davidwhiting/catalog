import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

class Task:
    def __init__(self, name, start, duration, dependencies):
        self.name = name
        self.start = start
        self.duration = duration
        self.dependencies = dependencies

# Define your tasks. For example:
tasks = [
    Task('Task 1', 0, 3, []),
    Task('Task 2', 0, 2, ['Task 1']),
    Task('Task 3', 0, 4, ['Task 1', 'Task 2']),
    Task('Task 4', 0, 3, ['Task 3']),
    Task('Task 5', 0, 5, ['Task 4']),
    Task('Task 6', 0, 2, ['Task 4', 'Task 5']),
    Task('Task 7', 0, 2, ['Task 2', 'Task 5']),
    Task('Task 8', 0, 2, ['Task 5', 'Task 6']),
    Task('Task 9', 0, 2, ['Task 4', 'Task 8'])
]

# Calculate start times based on dependencies
for task in tasks:
    if task.dependencies:
        task.start = max([t.start + t.duration for t in tasks if t.name in task.dependencies])

# Function to recursively add dependencies
def add_dependencies(task_name, tasks, selected_tasks):
    task = next((t for t in tasks if t.name == task_name), None)
    if task:
        for dependency in task.dependencies:
            if dependency not in selected_tasks:
                selected_tasks.append(dependency)
                add_dependencies(dependency, tasks, selected_tasks)

# Streamlit code
st.title('Interactive Gantt Chart')

# Create a multiselect for the tasks
selected_tasks = st.multiselect('Select tasks', [task.name for task in tasks])

# Add dependencies of the selected tasks
all_tasks = selected_tasks.copy()
for task in selected_tasks:
    add_dependencies(task, tasks, all_tasks)

# Filter tasks based on selection
filtered_tasks = [task for task in tasks if task.name in all_tasks]

# Create Gantt chart
fig, ax = plt.subplots()

# Generate yticks and labels
#yticks = np.arange(len(filtered_tasks))
#labels = [task.name for task in filtered_tasks]

# Generate bars for each task
for idx, task in enumerate(filtered_tasks):
    color = 'blue' if task.name in selected_tasks else 'red'
    ax.broken_barh([(task.start, task.duration)], (idx-0.4, 0.8), facecolors=color)
    ax.text(task.start + task.duration / 2, idx, task.name, ha='center', va='center', color='white', fontsize=8)  # Adjust fontsize here

# Format and show plot
#ax.set_yticks(yticks)
#ax.set_yticklabels(labels)
ax.set_xlabel('Time')

st.pyplot(fig)
