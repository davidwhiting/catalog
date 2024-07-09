# To Do Items

## I. Website (UI)

### 1. Pages

#### a) Login Page

- Navigation: Automatically send user to page of next step for student based on next task (e.g., select program, add courses, create schedule)

#### b) Home Page

- Update page for students with program not selected yet
  + Create two option cards
    + First is "Explore programs on your own"
      + Add button to take to Program page with pulldown menu
    + Second is "Let AI suggest programs for you"
      + Options: 'Based on your skills', 'Based on your interests', 'Shortest time to graduation' (for transfer students only)
      + Add links to Interest Assessment and Skills Assessment
- Until program is selected, disable 'Courses' and 'Schedule' links 

##### (Future)

- Add Pytorch or LLM-based recommendation engine for
  + Skills recommendations
  + Interests recommendations
- Add function that maximizes transfer credits into required coursework for program suggestions

#### c) Program Page

- Once degree program is selected, replace pulldown menu card with a "Program Title" card. Allow for `edit` button to change program. (This way someone can't accidentally change their program.)
- Change program functionality: Would have to erase schedule and everything downstream EXCEPT for possible electives and ge selected.
- Make description background light yellow (or nonwhite background) if possible

#### d) Courses Page

- Enable `Schedule` button
- Need button to `GE` selection page
- Need button to `Elective` selection page
- Course list table updates:
  + Add `Select Elective` menu option for non-required Elective courses only
  + Add `Select GE` menu option for non-required GE courses (that are empty) only.
  + Add `Change GE` menu option for non-required GE courses that have a selection.
- Add `Select Department Suggested` coursework functionality
- Add `Build my own coursework` functionality
  + Starts with major & required courses in the order of the suggested sequence
  + Requires unassigned GE to be filled in

##### (Future functions)
- `Select Minor` functionality to fill in GE and Electives
- `Select Certificate` functionality to fill in GE and Electives 

#### e) Schedule Page

- Connect D3 chart with Menu `Submit` button
- D3: Add lock icon to locked courses
- Table:
  + Change `Term` to actual term ("Spring 2024") instead of number
  + Create grouping by term in table
  + Add 'Lock/Unlock' functionality to menu
  + Add 'Move Class' functionality to menu
- Add option for 'Select department suggested schedule'
- Add functionality for "sanely" building schedule before optimization based on schedule template
- Create schedule template query from department suggested schedule (replace any chosen electives with "Elective" and any chosen GE with "General")

#### f) GE Page (not visible)

- Fill in more defaults in GE page based on program selected (e.g., Research & Computing Literacy 1.). 
- Fix `nopre` selection checkbox (connect to function for selecting electives with no prerequisites)
- Create `pre_done` function that will 
- Connect function that merges GE courses into coursework  

#### g) Electives Page (not visible)

- Build electives page, mirroring the GE page

### 2. Cards

#### a) Login Page

#### b) Home Page

- Add **edit** button to `Selected Student Information` card 

### 3. Connecting Cards

## II. Functions

## III. Database

### a) Login Page

- Add information for 
  + New student in
    + ~~Stage 1: No information~~
    + Stage 2: Demographics only
    + Stage 3: Program selected
    + ~~Stage 4: Schedule created~~
  + Transfer student in
    + Stage 1: No information
    + Stage 2: Demographics only
    + Stage 3: Program selected
    + Stage 4: Schedule created
  
##### (Future)

-  Update courses for 2024-2025 catalog
   + refactor new table for same course in multiple catalogs

## IV. Backend

- Matt & Michael

### a) Live Data Feeds

1. data feed 1
2. data feed 2
3. data feed 3

vs.

data feed 1 -> full integration

### b) API End Points

### c) Algorithms

#### 1. Requirements

- List out requirements (2023-2024 Catalog)

#### 2. Optimization (AI)

- Development / Adoption / Staging
- Intermediate optimization
- Firefly 

## V. Documentation
