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
    Task('MATH 99',  0, 3, []),
    Task('MATH 100', 0, 3, ['MATH 99']),
    Task('STAT 101', 0, 3, []),
    Task('MATH 115', 0, 3, ['STAT 101', 'MATH 100']),
    Task('MATH 107', 0, 3, []),
    Task('MATH 108', 0, 3, ['MATH 107']),
    Task('MATH 140', 0, 3, ['MATH 108', 'MATH 115']),
    Task('MATH 141', 0, 3, ['MATH 140']),
    Task('STAT 400', 0, 3, ['MATH 141'])
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
yticks = np.arange(len(filtered_tasks))
labels = [task.name for task in filtered_tasks]

# Generate bars for each task
for idx, task in enumerate(filtered_tasks):
    color = 'blue' if task.name in selected_tasks else 'red'
    ax.broken_barh([(task.start, task.duration)], (idx-0.4, 0.8), facecolors=color)
    ax.text(task.start + task.duration / 2, idx, task.name, ha='center', va='center', color='white', fontsize=8)  # Adjust fontsize here

# Add arrows for finish-to-start dependencies
for task in filtered_tasks:
    for dependency in task.dependencies:
        dep_task = next(t for t in tasks if t.name == dependency)
        arrow_color = 'black'
        arrow_start = dep_task.start + dep_task.duration
        arrow_end = task.start
        arrow_style = '<-'  # Arrow style for finish-to-start
        ax.annotate('', xy=(arrow_start, yticks[all_tasks.index(dependency)]), xytext=(arrow_end, yticks[all_tasks.index(task.name)]),
                    arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, arrowstyle=arrow_style))

# Format and show plot
ax.set_yticks(yticks)
ax.set_yticklabels(labels)
ax.set_xlabel('Time')

st.pyplot(fig)

