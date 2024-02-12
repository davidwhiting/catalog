
# map sequence to database
# seq #, name, type are all that are needed
deptSequence = [
    { "seq":  1, "name": "PACE 111B", "type": "general" },
    { "seq":  2, "name": "LIBS 150",  "type": "general" },
    { "seq":  3, "name": "WRTG 111",  "type": "general" },
    { "seq":  4, "name": "WRTG 112",  "type": "general" },
    { "seq":  5, "name": "NUTR 100",  "type": "general" },
    { "seq":  6, "name": "BMGT 110",  "type": "major"   },
    { "seq":  7, "name": "SPCH 100",  "type": "general" },
    { "seq":  8, "name": "STAT 200",  "type": "required"},
    { "seq":  9, "name": "IFSM 300",  "type": "required"},
    { "seq": 10, "name": "ACCT 220",  "type": "major"   },
    { "seq": 11, "name": "HUMN 100",  "type": "general" },
    { "seq": 12, "name": "BIOL 103",  "type": "general" },
    { "seq": 13, "name": "ECON 201",  "type": "required"},
    { "seq": 14, "name": "ARTH 334",  "type": "general" },
    { "seq": 15, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 16, "name": "ECON 203",  "type": "required"},
    { "seq": 17, "name": "ACCT 221",  "type": "major"   },
    { "seq": 18, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 19, "name": "BMGT 364",  "type": "major"   },
    { "seq": 20, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 21, "name": "BMGT 365",  "type": "major"   },
    { "seq": 22, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 23, "name": "MRKT 310",  "type": "major"   },
    { "seq": 24, "name": "WRTG 394",  "type": "general" },
    { "seq": 25, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 26, "name": "BMGT 380",  "type": "major"   },
    { "seq": 27, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 28, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 29, "name": "HRMN 300",  "type": "major"   },
    { "seq": 30, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 31, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 32, "name": "FINC 330",  "type": "major"   },
    { "seq": 33, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 34, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 35, "name": "BMGT 496",  "type": "major"   },
    { "seq": 36, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 37, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 38, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 39, "name": "ELECTIVE",  "type": "elective"},
    { "seq": 40, "name": "BMGT 495",  "type": "major"   },
    { "seq": 41, "name": "CAPSTONE",  "type": "elective"}
]

]

deptRecommended = [
    { "seq":  1, "name": "PACE 111B", "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  2, "name": "LIBS 150",  "credits": 1, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  3, "name": "WRTG 111",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  4, "name": "WRTG 112",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  5, "name": "NUTR 100",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  6, "name": "BMGT 110",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq":  7, "name": "SPCH 100",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq":  8, "name": "STAT 200",  "credits": 3, "status": "incomplete", "type": 'required', "prerequisite": '' },
    { "seq":  9, "name": "IFSM 300",  "credits": 3, "status": "incomplete", "type": 'required', "prerequisite": '' },
    { "seq": 10, "name": "ACCT 220",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 11, "name": "HUMN 100",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq": 12, "name": "BIOL 103",  "credits": 4, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq": 13, "name": "ECON 201",  "credits": 3, "status": "incomplete", "type": 'required', "prerequisite": '' },
    { "seq": 14, "name": "ARTH 334",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": '' },
    { "seq": 15, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 16, "name": "ECON 203",  "credits": 3, "status": "incomplete", "type": 'required', "prerequisite": '' },
    { "seq": 17, "name": "ACCT 221",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": 'ACCT 220' },  
    { "seq": 18, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 19, "name": "BMGT 364",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 20, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 21, "name": "BMGT 365",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": 'BMGT 364' },
    { "seq": 22, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 23, "name": "MRKT 310",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 24, "name": "WRTG 394",  "credits": 3, "status": "incomplete", "type": 'general',  "prerequisite": 'WRTG 112' },
    { "seq": 25, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 26, "name": "BMGT 380",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 27, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 28, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 29, "name": "HRMN 300",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 30, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 31, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 32, "name": "FINC 330",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": 'ACCT 221 & STAT 200' },  
    { "seq": 33, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 34, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 35, "name": "BMGT 496",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": '' },
    { "seq": 36, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 37, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 38, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 39, "name": "ELECTIVE",  "credits": 3, "status": "incomplete", "type": 'elective', "prerequisite": '' },
    { "seq": 40, "name": "BMGT 495",  "credits": 3, "status": "incomplete", "type": 'major',    "prerequisite": 'BMGT 365 & MRKT 310 & FINC 330' },
    { "seq": 41, "name": "CAPSTONE",  "credits": 1, "status": "incomplete", "type": 'elective', "prerequisite": 'FINC 330' }
]
    
# complete: 2, 3, 8
# transfer: 5, 34, 36, 37, 38, 39
    
def assign_bins(data, max_credits=9):
    # Initialize a list to keep track of the total credits in each bin
    bin_credits = [0]

    # Initialize a dictionary to keep track of the bin of each course
    course_bin = {}

    for item in data:
        # If the course is complete, assign it to bin 0 and continue to the next course
        if item['status'] == 'complete':
            course_bin[item['name']] = 0
            item['period'] = 0
            item['color'] = 'black'
            item['textcolor'] = 'white'
        elif item['complete'] == 'transfer':
            course_bin[item['name']] = 0
            item['period'] = 0
            item['color'] = 'gray'
            item['textcolor'] = 'black'
        else:
            # Assign bins with prerequisites
            start_bin = 1

            # if prerequisite line non-empty
            if item['prerequisite']:
                # Split the prerequisites string into a list of prerequisites
                prerequisites = item['prerequisite'].split(' & ')

                # Get the bin of each prerequisite
                prerequisite_bins = [course_bin[prerequisite] for prerequisite in prerequisites]

                # Find the maximum bin among the prerequisites
                max_prerequisite_bin = max(prerequisite_bins)

                # Assign the minimum bin
                start_bin = max_prerequisite_bin + 1

            period = start_bin

            done = False
            while done == False:
                if period not in bin_credits:
                    bin_credits.append(item['credits'])
                    done = True
                elif bin_credits[period] + item['credits'] > max_credits:
                    period += 1
                else:
                    bin_credits[period] += item['credits']
                    done = True

            course_bin[item['name']] = period
            item['period'] = period
