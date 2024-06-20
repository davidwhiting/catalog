import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

drop_table('program_descriptions',c)
c.execute('''
    CREATE TABLE program_descriptions (
        id INTEGER PRIMARY KEY,
        program_id INTEGER,
        info TEXT DEFAULT '',
        description TEXT DEFAULT '',
        learn TEXT DEFAULT '',
        certification TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        FOREIGN KEY(program_id) REFERENCES programs(id)
    )
''')

#####################################################################

############################################################
##                  ASSOCIATE DEGREE                      ##
############################################################



############################################################
##              BACHELOR'S MAJOR PROGRAMS                 ##
############################################################

# The title of the paragraph in description will be
#   "Major in [programs.name where program.id=program_id]"
# The title of the paragraph in 'learn' will be "What You'll Learn" and the first sentence will be 
#   "Through your coursework, you will learn how to"

majors = []

#• Accounting

program_id = 2
description = '''
The major in accounting combines theory and practice to help prepare you to analyze and report on the economic activities of organizations. You’ll develop skills in managerial accounting, budgeting, accounting systems, internal controls, financial analysis, financial reporting, internal and external auditing, taxation, and international accounting.
'''
learn='''
• Communicate with financial and nonfinancial audiences in a concise manner to facilitate financial decisions

• Create financial and business reports based on research and data analysis

• Apply accounting and business management principles to inform decision-making and risk management

• Evaluate current business technology designed to help personnel work collaboratively and to facilitate the decision-making process

• Exercise professional skepticism in the application of analytical, critical-thinking, and problem-solving skills

• Employ standards to identify, test, and validate processes, systems, and financial data

• Illustrate ethical decision-making models for addressing current and emerging business issues

• Present a framework and plan for fraud detection and deterrence analysis, implementation, and evaluation

• Perform a range of functions, including budgeting, reporting, and auditing, to manage federal agency finances

• Propose a plan for improved use of business intelligence, data management, and analytics
'''
certification='''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• Certified Fraud Examiner (CFE)

• Certified Government Auditing Professional (CGAP)

• Certified Government Financial Manager (CGFM)

• Certified Information Systems Auditor (CISA)

• Certified Internal Auditor (CIA)

• Certified Management Accountant/Certified Financial Manager (CMA/CFM)

• Certified Public Accountant (CPA)
'''

majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Applied Technology

program_id = 3
description = '''
The major in applied technology is designed to allow you to actively develop skills across different types of computing technologies. It offers great flexibility in credit options and course choices, allowing you to apply knowledge from prior work experience, as well as existing skills and abilities in multiple areas of technology. In this program, you are encouraged to cross-fertilize ideas, leading to a multidimensional and enriched approach to solving problems. You’ll learn foundational skills in computer technology and be able to customize your learning plan based on your individual interests and market-aligned career needs.
'''
learn='''
• Apply critical thinking and quantitative reasoning skills while using computing technologies and methodologies

• Combine concepts and practices in modern information technology (IT) and information systems (IS) with fundamental concepts in other fields to develop computing-based multidimensional approaches to problem-solving

• Develop oral and written communication skills to present computing-based solutions to complex problems

• Analyze insights about personal and professional goals
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Biotechnology

program_id = 4
info='''
The bachelor’s degree program in biotechnology has program-specific admission requirements that you must meet before enrolling in any program courses.

You must have completed 11 credits of approved coursework in genetics and biotechnology applications and techniques—within an Associate of Applied Science degree program at a community college with which UMGC has an articulation agreement or within another appropriate transfer program—to pursue an academic major in biotechnology. Consult an advisor or a success coach before choosing this major.
'''
description = '''
The major in biotechnology combines laboratory skills and applied coursework with a biotechnology internship experience and upper-level study.

For this program, you are required to have already gained technical and scientific knowledge of biotechnology through coursework and direct experience in the field. Contact an advisor or a success coach to confirm your eligibility.
'''
learn='''
• Practice ethical standards of integrity, honesty, and fairness in scientific practices and professional conduct

• Communicate orally and in writing in a clear, well-organized manner that effectively informs and clarifies scientific principles and lab techniques

• Offer technical support, customer assistance, and cost-benefit analyses regarding biotechnical approaches to the development of products and services

• Use scientific procedures and current and emerging technologies to conduct safe and hygienic laboratory experiments and collect validated and documented data

• Comply with and adhere to national, state, and local standards, policies, protocols, and regulations for laboratory and manufacturing activity

• Apply scientific knowledge and principles, quantitative methods, and technology to think critically and solve complex problems in biotechnology
'''
majors.append({ 'program_id': program_id, 'info': info, 'description': description, 'learn': learn, 'certification': '' })


#• Business Administration

program_id = 5
description = '''
In the business administration major, you’ll gain a well-rounded education that provides foundational, workplace-relevant management skills, organizational theory, and operational knowledge.

UMGC’s career-focused bachelor’s degree program in business administration is designed to help you compete for the jobs of today and tomorrow by building a comprehensive base of knowledge. This major will help you prepare for a variety of positions in for-profit, nonprofit, and public-sector organizations.'''
learn='''
• Plan and communicate a shared vision for the organization that will drive strategy, assist with decision-making, and position the organization competitively

• Design and create management and leadership plans

• Evaluate qualitative and quantitative data

• Communicate effectively across all levels of an organization

• Develop, communicate, and implement policies and procedures to reduce cost and organizational risk and promote ethical practices

• Manage people, time, and resources by using effective employment practices, encouraging team building, and mentoring junior members of the staff

• Design and execute personal and employee development systems to enhance job performance and leadership skills
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Communication Studies

program_id = 6
description = '''
Whether you’re interested in journalism, public relations, business, or digital communications, you can build a firm base of knowledge while you earn a bachelor’s degree in communication studies at UMGC. In this major, you’ll learn about and apply communication theories and best practices to communicate about events and ideas to various populations. In addition, you’ll learn to work with individuals and groups professionally and manage communications within ethical, legal, and financial parameters.
'''
learn='''

• Interpret, evaluate, and apply conventions of communication scholarship

• Apply critical reasoning skills to finding, evaluating, interpreting, using, and delivering information

• Apply ethical communication principles and practices to finding, evaluating, interpreting, creating, and delivering messages

• Create written messages tailored to specific audiences, purposes, and contexts

• Create oral and multimedia presentations tailored to specific audiences, purposes, and contexts

• Access, analyze, evaluate, design, create, and act on messages in a variety of media contexts

• Demonstrate techniques for mindful hearing, attending, understanding, responding, and remembering in a variety of contexts

• Observe, analyze, and adapt cognitive, affective, and behavioral communication in a variety of contexts

• Leverage the principles of small-group communication to complete tasks

• Apply organizational communication frameworks to the management of upward, downward, and horizontal oral, visual, and written communication in workplace contexts
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Computer Science

program_id = 7
description = '''
With a bachelor’s degree in computer science, you’ll be able to plan, design, and optimize computer software and hardware systems for commercial and government environments. This versatile major provides you with a foundation in programming languages, software development, complex algorithms, and graphics and visualization.
'''
learn='''
• Develop the analytical and problem-solving skills necessary to design, implement, test, and debug computer programs

• Apply mathematical principles, computer science theory, and software development fundamentals to design and build effective computing-based solutions

• Design and implement a computing-based solution to meet a given set of requirements, standards, and guidelines

• Evaluate alternative computing architectures, algorithms, and systems to make informed decisions that optimize system performance

• Communicate effectively with a range of audiences in a variety of professional contexts

• Recognize local, national, and international technical standards and legal, ethical, and intellectual property regulations in computing practice
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Criminal Justice

program_id = 8
description = '''
The criminal justice curriculum at UMGC is uniquely designed to provide you with an understanding of crime and criminal behavior, the roles of practitioners within the criminal justice system, and the critical-thinking and ethical decision-making strategies necessary to meet the professional demands of the field of criminal justice.
'''
learn='''
• Evaluate the roles and responsibilities of police, courts, and corrections within the American criminal justice system

• Utilize ethical reasoning, analytical skills, and professional knowledge to investigate the implications of criminal justice policies or procedures on diverse social groups

• Articulate the importance of research in the social sciences

• Evaluate criminal justice public policies using analytical competencies

• Apply the principles of the various criminal bodies of law (i.e., substantive, procedural, and evidentiary) that currently regulate the American criminal justice system
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Cybersecurity Management and Policy

program_id = 9
description = '''
In UMGC’s bachelor’s degree program in cybersecurity management and policy, you can prepare to become a leader in the protection of data. This innovative, world-class program uses a multidisciplinary approach—drawing from fields such as management, law, science, business, technology, and psychology—to provide you with the most current knowledge and skills for protecting critical cyber infrastructure and assets.

UMGC was named a National Center of Academic Excellence in Cyber Defense Education (CAE-CDE) by the National Security Agency and the Department of Homeland Security.
'''
learn='''
• Integrate cybersecurity best practices and guidance to formulate protection strategies for an organization’s critical information and assets

• Apply ethical principles to the development of cybersecurity plans, policies, and programs in industry and government organizations

• Evaluate the applicability of laws, regulations, standards, and frameworks to improve organizational resilience and governance of cybersecurity capabilities

• Apply business analysis principles to identify, assess, and mitigate organizational risk, including acquisition and supply chain risk, arising from diverse sources

• Apply risk management frameworks to identify cybersecurity needs and integrate best practices to improve cybersecurity positions for municipal, state, federal, and international government agencies and organizations

• Integrate continuous monitoring and real-time security solutions to improve situational awareness and deployment of countermeasures within an organization

• Evaluate technology applications to support the cybersecurity goals and objectives of an organization

• Investigate the effects (good or bad) of emerging technology applications on cybersecurity

• Participate in the incident response and recovery process for an organization

• Apply the principles of professional communications and technical writing to effectively communicate about cybersecurity in organizational settings
'''

certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• CompTIA Network+

• CompTIA Security+

• EC-Council Certified Chief Information Security Officer (CCISO)

• EC-Council Certified Incident Handler (ECIH)

• EC-Council Certified Secure Computer User (CSCU)

• EC-Council Certified Threat Intelligence Analyst (CTIA)

• EC-Council Information Security Manager (EISM)

• IAPP Certified Information Privacy Professional/US (CIPP/US)

• (ISC)2 Certified Authorization Professional (CAP)

• (ISC)2 Certified Information Systems Security Professional (CISSP)

• Professional Business Analyst (PMI-PBA)
'''

majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• Cybersecurity Technology

program_id = 10
description = '''
In UMGC’s award-winning program in cybersecurity technology, you’ll learn the operational procedures and technologies to design, implement, administer, secure, and troubleshoot corporate networks while applying cybersecurity principles operationally.

Designed to combine the benefits of a traditional college education with hands-on training in state-of-the-art computer technology, the cybersecurity technology curriculum integrates technical skills with communication skills and superior general education knowledge.

UMGC was named a National Center of Academic Excellence in Cyber Defense Education (CAE-CDE) by the National Security Agency and the Department of Homeland Security. UMGC is also a designated National Center of Digital Forensics Academic Excellence (CDFAE) institution.
'''
learn='''
• Design, implement, and administer local-area and wide-area networks to satisfy organizational goals

• Resolve IT system problems and meet the needs of end users by applying troubleshooting methodologies

• Apply relevant policies and procedures to effectively secure and monitor IT systems

• Communicate IT knowledge effectively using a wide range of presentation styles

• Meet organizational goals using effective workforce skills, best practices, and ethical principles
'''
certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• AWS Certified Cloud Practitioner—Foundational • AWS Certified Solutions Architect—Associate

• CERT Computer Security Incident Handler (CSIH) • Cisco Certified Network Associate (CCNAv7)

• Cisco Certified Network Professional (CCNP-ENARSI) • Cisco Certified Network Professional (CCNP-ENCOR) • CompTIA A+

• CompTIA Cloud+

• CompTIA Cybersecurity Analyst (CySA+) • CompTIA Linux+ and LPIC-1

• CompTIA Network+

• CompTIA PenTest+

• CompTIA Security+

• EC-Council Certified Ethical Hacker (CEH)

• (ISC)2 Certified Cloud Security Professional (CCSP)

• (ISC)2 Certified Information Systems Security Professional (CISSP)

• ISFCE Certified Computer Examiner (CCE)

• Microsoft 365 Certified: Enterprise Administrator Expert

• Microsoft 365 Certified: Modern Desktop Administrator Associate

• Microsoft Certified: Azure Fundamentals (AZ-900)

The cybersecurity technology curriculum is closely aligned to industry standards and certifications. Changes related to leading industry certifications may lead to adjustments in course offerings. Visit the program web page for updates.
'''

majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• Data Science

program_id = 11
description = '''
The major in data science is designed to meet the growing need for highly skilled professionals who can transform increasing amounts of data into actionable insights. The program provides hands-on experience with a number of the most frequently used analytical tools and methods, offering opportunities to manage and manipulate data; create data visualizations; build predictive models using different machine learning techniques; apply artificial intelligence (AI) and natural language processing techniques to gain insights from free text, images, and videos; and make strategic data-driven recommendations that directly affect business outcomes. You’ll acquire fundamental knowledge and skills in data science that will help you adapt to future changes in tools, technology, and the marketplace.'''
learn='''
• Communicate effectively orally and in writing, meeting expectations for content, purpose, organization, audience, and format

• Implement all stages of data science methodology, including data extraction, data cleaning, data load, and transformation

• Execute best practices, using diverse technologies, in data science, business intelligence, machine learning, and artificial intelligence

• Analyze social, global, and ethical issues and their implications as they relate to the use of existing and emerging data science, machine learning, and AI technologies

• Evaluate a business problem or opportunity to determine the extent data science can provide a viable solution, and translate the business problem into a viable project to meet organizational strategic and operational needs

• Incorporate data security, data privacy, and risk management best practices in the planning, development, and implementation of data science solutions

• Build and deploy the machine learning process throughout its life cycle in full compliance with best practices for tool evaluation, model selection, and model validation

• Leverage big data analytics and AI technology to create solutions for stream analytics, text processing, natural language understanding, AI, and cognitive applications
'''
certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• AWS Certified Machine Learning

• Microsoft Certified: Data Analyst Associate

• Tableau Desktop Certified Associate

• Tableau Desktop Specialist
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• East Asian Studies

program_id = 12
description = '''
UMGC’s East Asian studies major provides an overview of the history, economics, politics, culture, and languages of the East Asian region, including China, Korea, and Japan. In this program, you’ll examine East Asia’s rich past and continuing contributions to the global community.

This program is ideal for those who live or work in East Asia, know East Asian languages, or regularly interact with people from East Asian countries.
'''
learn='''
• Interpret, communicate, educate, and advise others based on your understanding, research, and analysis of the social, historical, and cultural contexts of East Asia

• Use your knowledge of East Asia to identify, create, facilitate, and promote opportunities for interaction and cooperation between East Asia and the global community

• Apply your knowledge of East Asian diversity, values, and expectations to perform in a culturally appropriate way in personal and professional settings

• Write and speak an East Asian language, integrating interpersonal skills and cultural knowledge
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• English

program_id = 13
description = '''
Like other liberal arts majors, a major in English at UMGC offers a solid base of critical thinking on which to build a career or further graduate study. In-demand skills in research and writing that have a wide application in the job market are also honed. If you are intrigued by literature, the English major may be right for you.
'''
learn='''
• Demonstrate knowledge of a range of English-language literary texts, genres, and terms

• Analyze literary texts to explain stylistic, historical, sociocultural, and ethical significance

• Apply critical theory to literary texts to enhance interpretation and analysis

• Conduct effective research across a range of media

• Create writing that effectively argues, persuades, illuminates, and/or informs

• Create presentations in various media to demonstrate the results of academic inquiry
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Environmental Health and Safety

program_id = 14
description = '''
In UMGC’s environmental health and safety program, you’ll learn to implement evidence-based professional practices to support a safe and healthy work environment.
'''
learn='''
• Use information-gathering skills and professional judgment to recommend solutions for broadly defined technical or scientific problems in environmental health and safety

• Apply cognitive and technical skills to anticipate, recognize, and critically evaluate hazards and risk factors

• Select effective control methods to generate practical evidence-based solutions while following legislative and industry standards

• Develop strategies for ongoing professional development and learning to inform evidence-based practice in a continually changing global environment

• Model a range of written and oral communication formats to explain technical information and concepts to various audiences

• Choose collaborative and ethical practices to build the relationships necessary to address contemporary environmental health and safety issues
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Finance

program_id = 15
description = '''
In UMGC’s bachelor’s degree program in finance, you’ll develop the expertise to apply finance theory to real-world situations. Our program combines a foundation in the principles of business, economics, and accounting with an in-depth focus on the details of finance and financial management via intensive case studies. It can also serve as a significant first step toward earning important certifications in the field.
'''
learn='''
• Examine and describe the impact of the legal, regulatory, and environmental influences on the monetary system on planning, forecasting, and making financial decisions

• Evaluate financial information such as financial statements, financial ratios, and cash flows and apply that information to the analysis of business problems

• Analyze and interpret financial concepts to make basic institutional and functional business decisions

• Apply the basic principles of security markets to create, evaluate, and manage security portfolios

• Demonstrate the ability to communicate business concepts professionally

• Recognize the inherent conflict of interest in many business decisions

• Synthesize financial data by applying appropriate technology tools to solve business problems
'''
certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• Certified Financial Planner (CFP)

• Certified Management Accountant (CMA)
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• General Studies

program_id = 16
description = '''
The bachelor’s degree program in general studies allows you to take an active role in designing your educational experience through a flexible curriculum while maximizing your ability to transfer previously earned credit. This personalized learning path, coupled with a focus on your specific interests and areas of study, provides a solid, well-rounded foundation in preparation for a variety of careers.
'''
learn='''
• Improve oral and written communication skills

• Apply critical-thinking and problem-solving skills

• Analyze insights about personal and professional goals

• Apply skills and knowledge from different academic disciplines

• Synthesize concepts and theories in core content courses and focus areas
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Gerontology and Aging Services

program_id = 17
description = '''
In the gerontology and aging services program at UMGC, you’ll gain a foundation in the physiological, psychological, social, and health aspects of aging, coupled with an understanding of programs, services, and policies that affect how we age and live as older adults. You’ll gain hands-on experiences in the aging services sector in preparation for a career that improves quality of life for this important and growing segment of the population.
'''
learn='''
• Access, interpret, and apply research findings related to biological, psychological, and social processes in the context of aging

• Analyze the impact of factors such as race, ethnicity, gender, and social class on the aging process

• Analyze the development of policies related to aging and their impact on services and organizations for older adults, both locally and nationally

• Apply knowledge to work with older adults in a chosen area of practice

• Practice within the legal and ethical standards of the aging services field
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Graphic Communication

program_id = 18
description = '''
UMGC’s graphic communication major is a portfolio-intensive program that can help you master the skills and technology needed to compete in today’s rapidly changing visual arts and communication environment. With a graphic communication degree, along with an updated portfolio aimed toward your ideal clients, you can apply your creative streak toward a career in business, government, or industry as a graphic designer, manager, or communications specialist.
'''
learn='''
• Produce effective visual communications by applying principles of composition, layout, color theory, and context

• Plan, design, and create interactive solutions, such as user interfaces, motion graphics, mobile applications, and web designs

• Use professional, analytical, collaborative, and technical design skills to support team goals, roles, and responsibilities

• Define and direct creative strategy in a business environment by combining scope, messaging, and evaluation of success in an overarching design campaign
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Health Services Management

program_id = 19
description = '''
A major in health services management can provide you with grounding in the core knowledge and competencies for effective management in the dynamic healthcare environment, teaching you to think comprehensively and strategically about healthcare trends so you can lead innovation. It is ideal for entry-level and midcareer professionals.
'''
learn='''
• Exercise sound business and financial management principles in healthcare settings through process mapping and strategic planning

• Apply technological advances and emerging trends in the U.S. healthcare system to achieve organizational goals and practices

• Identify, analyze, and evaluate quantitative and qualitative healthcare data and information for effective decision-making in various healthcare settings

• Evaluate legal and ethical issues associated with the planning and delivery of healthcare services

• Analyze policies related to healthcare management
'''
certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the Certified Health Data Analyst (CHDA) exam.
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• History

program_id = 20
description = '''
Like other liberal arts majors, a major in history offers a solid base of critical thinking on which to build a career or further graduate study.

One of the very first schools to offer a degree program in history online, UMGC brings you nearly two decades of experience in teaching history in an online environment. Plus, if you’re based in the Washington, D.C., area, you’ll have myriad opportunities to find internships and part-time and full-time jobs in the field via public institutions and federal positions. Our alumni have gone on to work at such agencies as the National Archives and the National Park Service.
'''
learn='''
What You’ll Learn

• Research, interpret, and present historical knowledge

• Write and speak clearly and appropriately about historical information for diverse audiences

• Engage in history as a moral and ethical practice, recognizing a wide range of backgrounds and perspectives

• Apply historical precedents to contemporary life and develop self-reflection

• Achieve a deep understanding of the different peoples, events, and cultures that have shaped human civilization
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Homeland Security

program_id = 21
description = '''
The UMGC homeland security program is uniquely designed to provide you with an understanding of the homeland security sector. The curriculum covers international and domestic terrorism, emerging technologies, cyber threats, infrastructure protection, emergency preparedness and response, private-sector partnerships, global pandemics, natural disasters, strategic planning, policies, intelligence operations, and international engagement. In this program, you’ll develop the necessary critical-thinking, ethical decision-making, risk analysis, and communication skills to meet the professional demands of leadership and management in the homeland security profession.
'''
learn='''
• Distinguish policies and procedures in the homeland security sector that demonstrate leadership and management

• Apply professional and ethical decision-making skills to increase knowledge of strategic and operational homeland security goals and interface with internal and external stakeholders

• Assess the critical technologies essential for the protection and recovery of critical infrastructure and for ensuring the nation’s cybersecurity against all hostile threats

• Assess terrorist threats, cyber and insider threats, critical infrastructure vulnerabilities, and emerging asymmetric threats to U.S. national security

• Evaluate the roles and relationships of homeland security partners and stakeholders supporting homeland security operations
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Humanities

program_id = 22
description = '''
Like other liberal arts majors, a major in humanities offers a solid base of critical thinking on which to build a career or further study. This major will broaden your understanding of yourself and your interaction with the world and provide a perspective on cultural and intellectual heritage while offering tools to use that knowledge in the real world.

You’ll explore how individuals and groups understand their existence, their place within their cultures, and their responsibility to others and the physical world.
'''
learn='''
• Integrate theories, methods, and concepts from multiple humanities disciplines, such as philosophy, history, art, literature, music, and religious studies

• Evaluate the adequacy and justifiability of propositions, theories, assumptions, and arguments

• Communicate the results of critical reflection into personal positions on social, cultural, and ethical issues

• Apply sound ethical reasoning in contemporary contexts

• Develop cultural understanding by exploring the cultural heritage of sites, events, people, and communities
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Human Resource Management

program_id = 23
description = '''
With a degree in human resource management from UMGC, you’ll find employment opportunities in nearly every industry. Our bachelor’s degree program is ideal for those who have some experience in HR, as well as those who want to transition into the HR profession.

You’ll gain a comprehensive understanding of human resource functions—such as resource planning; recruitment, selection, placement, and orientation of employees; training and career development; labor relations; performance appraisal and rewards programs; and development of personnel policies and procedures—in private- and public-sector settings. Additionally, you’ll explore the ways that human behavior, laws, labor relations, and diversity issues can intersect and affect a company’s culture and ultimately its progress.
'''
learn='''
• Apply business knowledge, best practices, and ethical leadership skills to make effective business decisions

• Apply knowledge of human behavior, labor relations, and current laws and regulations to evaluate whether a working environment is safe, fair, and compliant with regulations

• Develop a plan to create and implement a total rewards program that aligns employee and organizational goals and objectives

• Create, implement, and assess training, development, and rewards programs that foster employee and organizational learning and development

• Recognize the diversity of cultures and worldviews that inform human behavior and respond constructively to differences in workplaces, communities, and organizations

• Use technology to research, collect, analyze, and interpret data and effectively communicate information in a professional manner

• Evaluate current issues in talent acquisition, selection, strategic planning, and performance-appraisal systems
'''
certification = '''
This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• Global Professional in Human Resources (GPHR)

• Professional in Human Resources (PHR)

• SHRM-Certified Professional (SHRM-CP)
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• Laboratory Management

program_id = 24
info = '''
The bachelor’s degree program in laboratory management has program-specific admission requirements that you must meet before enrolling in any program courses.

If you have completed virtually all the required lower-level coursework for the laboratory management major—within an Associate of Applied Science degree program at a community college with which UMGC has an articulation agreement or within another appropriate transfer program—you may seek an academic major in laboratory management. Consult an advisor or a success coach before electing this major.
'''
description = '''
UMGC’s program in laboratory management is unique in Maryland: no other university in the state offers a bachelor’s degree program in laboratory management. Yet the need within the biotechnology industry for employees with both scientific and management skills is great.

The laboratory management major will help you prepare to coordinate the activities that contribute to a well-ordered laboratory by combining an in-depth study of scientific concepts and procedures with hands-on laboratory management practice.
'''
learn='''
• Create a healthy, safe, and productive workplace by appropriately hiring, training, supporting, and evaluating laboratory personnel

• Plan, organize, and direct the daily work activities of a laboratory setting by working independently and as a member of a team

• Communicate in a clear, well-organized manner that effectively persuades, informs, and clarifies ideas, information, and laboratory techniques/procedures to staff, the scientific community, and the public

• Practice ethical standards of integrity, honesty, and fairness as a laboratory manager

• Monitor and maintain laboratory-related documentation, equipment, and supplies necessary for conducting efficient, safe, cost-effective, and hygienic laboratory operations

• Manage scientific and laboratory practices and procedures by complying with and adhering to national, state, and local standards, policies, protocols, and regulations
'''
majors.append({ 'program_id': program_id, 'info': info, 'description': description, 'learn': learn, 'certification': '' })

#• Legal Studies

program_id = 25
description = '''
The legal studies curriculum at UMGC is designed to provide you with a background in contemporary American civil and criminal law, legal systems and institutions, and legal theory and practice. In this major, you’ll be able to develop the knowledge and skills necessary in the legal workplace, including fact identification and analysis, legal research and writing, and field-related digital competence.
'''
learn='''
• Determine how the application of the American civil and criminal justice systems can further social justice

• Research appropriate standard and internet-based legal resources to identify relevant, current, and presiding legal authority

• Develop legal documents that incorporate critical thinking and legal reasoning to inform, evaluate, and advocate with respect to specific legal issues

• Analyze the relevant legal concepts, authorities, regulations, and ethical codes required to support the resolution of legal disputes
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Management Information Systems


program_id = 26
description = '''
Management information systems are a critical part of the strategic decision-making process in virtually all of today’s public and private organizations. Managers who can lead the teams that integrate information systems with general business processes are in high demand.

Developed by chief information officers and other high-level IT professionals, the bachelor’s degree program in management information systems at UMGC is well suited for those looking to move into a management position in information systems and bridge the gap between an organization’s functional users and technical developers.
'''
learn='''
• Communicate effectively, orally and in writing, meeting expectations for content, purpose, organization, audience, and format

• Utilize diverse technologies to achieve project-level or organizational information systems objectives, within diverse areas, including cybersecurity, project management, software development, data analytics, and business process analysis

• Apply appropriate management, analysis, and measurement methods and tools for information systems and technology to meet organizational strategic and operational needs

• Utilize business intelligence and data analytics tools and techniques to generate actionable insights that support achievement of strategic or operational objectives

• Analyze recent and projected developments, implications, and applications of existing and emerging technologies, taking into account ethical issues and global and multinational corporate perspectives

• Incorporate cybersecurity and risk management best practices in the planning, development, and use of information systems

• Develop clear and concise technical and functional requirements, including the use of data and process models, for information systems development and implementation

• Create information technology strategic and implementation plans that support organizational strategies and activities and improve processes and outcomes

• Develop organizational policies, standards, and communications to inform end users about relevant IT operations issues, including ethical issues and accountabilities

• Collaborate with team members to plan, evaluate, and document technology solutions
'''
certification = '''
INDUSTRY CERTIFICATION

This program is designed to help prepare you for the following certification exams, listed in alphabetical order:

• Agile Certified Practitioner (PMI-ACP)®

• Certified Associate in Project Management (CAPM)®

• Project Management Professional (PMP)®
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': certification })

#• Management Studies

program_id = 27
description = '''
Today, many business, government, public service, and technical environments require knowledge of management principles from multiple disciplines. UMGC’s program in management studies can help you gain that expertise through a course of study focused on decision-making, problem-solving, and leadership.
'''
learn='''
• Apply leadership skills to promote communication, ethical behavior, and quality performance

• Implement employment practices, encourage team building, and mentor staff members

• Communicate effectively with culturally diverse audiences using a variety of formats and technologies

• Assess and develop performance measures, feedback, and coaching that facilitate employee development

• Employ self-reflection and mindfulness of individual and cultural differences when interacting with others

• Research, plan, and develop processes and procedures that ensure organizational performance
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })


#• Marketing

program_id = 28
description = '''
The major in marketing offers an introduction to the fundamental concepts and strategies that constitute successful marketing management. It is designed to provide a thorough understanding of how to identify, retain, and grow profitable customer segments; create effective promotional programs; and develop integrated marketing communication tools, both in domestic and global markets. The program incorporates digital marketing strategies to meet the requirements of the modern marketplace.
'''
learn='''
• Apply strategic marketing skills, such as scenario planning, market intelligence, customer profiles, and digital planning, to successfully market products or services

• Develop marketing insights with data derived from internal and external sources

• Design effective integrated marketing communication plans using traditional, digital, and social media channels

• Develop multichannel campaigns for nonprofit organizations through fundraising, recruiting volunteers, and promoting alliances using traditional and digital marketing channels

• Create consumer-driven marketing strategies for a consistent consumer experience across multiple marketing channels

• Develop successful customer relationships and enhance customer loyalty using appropriate marketing technologies

• Create marketing strategies to meet the challenges of a competitive global market
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Nursing for Registered Nurses

program_id = 29
info = '''
The nursing for registered nurses program has specific admission requirements (listed on p. 9) that you must meet before enrolling in any required major courses.

If you have an associate degree in nursing or have completed a registered nursing education program that is recognized by the appropriate state board of nursing and you reside in and have an active, unencumbered nursing license in an approved state, you may seek an academic major in nursing for registered nurses. This program is not intended to prepare you for initial professional licensure.
'''
description = '''
UMGC’s bachelor’s degree program in nursing for registered nurses provides a pathway for career advancement in clinical management and leadership or public health nursing, as well as preparation for graduate study, by building on your established clinical and practical experiences. Accredited by the Commission on Collegiate Nursing Education (CCNE), this program will help equip you to assume the role of the professional nurse in diverse and challenging settings, take on responsibility for client care, and provide exceptional evidence-based nursing care to patients.
'''
learn='''
• Demonstrate clinical reasoning in selecting and applying healthcare approaches for individuals, families, and communities

• Evaluate and apply research to promote evidence-based nursing practice

• Apply management and leadership concepts in various settings to promote health

• Evaluate and communicate the effects of health policy and healthcare systems on the nursing profession and the delivery of care

• Demonstrate an understanding of the value of continuous personal and professional development as healthcare evolves
'''
majors.append({ 'program_id': program_id, 'info': info, 'description': description, 'learn': learn, 'certification': '' })

#• Political Science

program_id = 30
description = '''
With a major in political science, you’ll develop a comprehensive understanding of U.S. government and global politics. By analyzing political structures, theory, and problems, you’ll learn to interpret complex political problems in both the public and private sectors and propose potential solutions. You’ll also have an opportunity to enhance your professionalism and fine-tune your communication and organizational skills.
'''
learn='''
• Identify the characteristics of political science and its subfields

• Distinguish between major concepts, theories, and research methods in political science

• Explain key domestic and international systems, institutions, and organizations, including their purposes, functions, and impacts on domestic and global politics and policies

• Describe ethical issues in political science that inform a commitment to integrity in personal, professional, and political practice

• Explain the importance of diversity, equity, and identity within sociopolitical, economic, and cultural contexts, both domestically and internationally

• Apply new information, terminology, and research in political science and other relevant fields

• Analyze qualitatively and quantitatively based reports and articles for validity, methodology, applicability, and conclusions

• Produce well-reasoned research within the major theoretical/ conceptual frameworks of political science, using appropriate research skills, including statistical methods as needed

• Express oneself clearly, accurately, logically, cohesively, and critically, in the language of political science, about international and domestic political issues

• Demonstrate strong critical thinking and analytical writing skills
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Psychology

program_id = 31
description = '''
UMGC’s bachelor’s degree program in psychology will help prepare you for graduate study or a multitude of careers in the field. While acquiring a knowledge base of theory, research, and practice in psychological sciences, you’ll hone your quantitative skills, written and oral communication proficiencies, analytical and scientific reasoning, and ability to analyze human behavior.
'''
learn='''
• Apply relevant concepts, theories, empirical findings, and historical trends to personal, organizational, and social issues

• Model scientific reasoning by designing, participating in, and evaluating psychological research

• Implement critical and creative thinking, skeptical inquiry, technology-based information literacy, and the scientific approach to solve problems related to current and emerging trends in psychology

• Use ethical principles of psychology to evaluate psychological science and practice within professional and personal settings

• Communicate ideas, concepts, arguments, and perspectives during effective interactions with diverse groups in a variety of contexts

• Analyze the complexity of human diversity and how it influences our understanding of behavior

• Apply psychology content and skills to career readiness, lifetime learning goals, and workforce contributions
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Public Safety Administration

program_id = 32
description = '''
The public safety administration curriculum at UMGC is designed to provide you with a foundation of knowledge and expand your understanding of the unique aspects of administration in the field of public safety. In this program, you’ll study public safety’s professional and legal frameworks as well as administrators’ responsibilities related to risk management, mitigation, and liability. You’ll also examine ethical decision-making processes and distinguish the attributes of exceptional public safety leaders.
'''
learn='''
• Analyze the unique aspects and best professional practices associated with the field of public safety administration within the United States

• Analyze the legal framework within the United States that outlines the obligations and limitations of public safety entities with respect to their employees, constituents, and the public at large

• Evaluate the challenges associated with the professional obligation to address concurrent public safety emergencies and the challenges associated with the development of effective corresponding mitigation plans

• Evaluate the unique ethical framework associated with the field of public safety administration and the corresponding decision-making process required of public safety professionals

• Assess the leadership attributes most commonly associated with exceptional professionals within the field of public safety administration
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Social Science

program_id = 33
description = '''
In UMGC’s bachelor’s degree program in social science, you’ll gain a breadth of knowledge through interdisciplinary study that encompasses perspectives from the fields of anthropology, behavioral sciences, gerontology, psychology, and sociology. You’ll also have the opportunity to drill down and focus closely on one of these fields.
'''
learn='''
• Analyze how quantitative and qualitative methods are used in social science research

• Communicate social science concepts and research findings effectively to a variety of audiences

• Examine how micro- and macro-level factors are linked in the social lives of individuals, communities, and societies

• Analyze complex social issues using theoretical approaches, critical-thinking skills, information literacy, technology, or interdisciplinary perspectives

• Evaluate social science research using ethical principles and standards for professional conduct

• Apply concepts of diversity, social factors, and global multicultural perspectives to examine practical problems in the workplace and society
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Software Development and Security

program_id = 34
description = '''
The major in software development and security at UMGC is designed to teach you programming languages and best practices in software development that are in demand today in the workplace. Study also focuses on the critical element of software security, providing skills in how to find and address possible vulnerabilities.

UMGC was named a National Center of Academic Excellence in Cyber Defense Education (CAE-CDE) by the National Security Agency and the Department of Homeland Security.
'''
learn='''
• Work individually or in a team to design, develop, implement, and test secure software using leading industry practices and standards to meet user requirements

• Plan, manage, document, and communicate all phases of a secure software development project as part of a software development team

• Use appropriate tools to assess and analyze existing applications for weaknesses and vulnerabilities and implement techniques for mitigating security threats and risks

• Identify and respond to threats and attacks to minimize risk and protect privacy
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

#• Web and Digital Design

program_id = 35
description = '''
You can follow your interests and prepare for a career in digital design with UMGC’s bachelor’s degree program in web and digital design, which allows you to explore design using various digital media and web technologies. In this major, you’ll learn how to create digital works using industry-standard software and incorporating design theory and efficient workflows. Through your coursework, you can gain hands-on experience in web design, virtual reality, augmented reality, electronic publishing, motion graphics, multimedia, animation, and graphic design.
'''
learn='''
• Create digital products, such as graphics, interactive digital media, and web applications, that utilize current or emerging technologies to meet customer requirements and usability standards

• Apply sound business principles and project management techniques to manage a digital media or web design project from conceptualization to deployment

• Utilize scripting and programming languages to develop interactive digital media or web applications that meet technical specifications and quality standards

• Assess the cultural, ethical, and legal implications of producing and distributing interactive digital media, products, or platforms

• Communicate clearly and effectively with diverse stakeholders about technology and digital media
'''
majors.append({ 'program_id': program_id, 'info': '', 'description': description, 'learn': learn, 'certification': '' })

c.executemany('''
    INSERT INTO program_descriptions (program_id, info, description, learn, certification)
    VALUES (:program_id, :info, :description, :learn, :certification)
''', majors )
conn.commit()

############################################################
##              BACHELOR'S MINOR PROGRAMS                 ##
############################################################

minors = []

#• Accounting

program_id = 36
description = '''
The accounting minor complements the skills you gain in your major discipline by providing a study of how the accounting environment measures and communicates the economic activities of organizations to enable stakeholders to make informed decisions regarding the allocation of limited resources.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• African American Studies

program_id = 37
description = '''
The African American studies minor complements the skills you gain in your major discipline by offering an interdisciplinary approach to the study of the contemporary life, history, and culture of African Americans.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Art

program_id = 38
description = '''
The art minor complements the skills you gain in your major discipline by offering an aesthetic and personal exploration of imagery, media, and composition through a balance of art theory and practice.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Art History

program_id = 39
description = '''
The art history minor complements the skills you gain in your major discipline by helping to develop skills in historical and cultural interpretation and critical analysis of works of architecture, sculpture, painting, and the applied arts.
'''
minors.append({ 'program_id': program_id, 'description': description })

### check program_id from here:

#• Biology

program_id = 40
description = '''
The biology minor complements the skills you gain in your major discipline by helping to provide an underlying scientific base on which to build a career in the life sciences, allied health fields, bioinformatics, environmental management, science journalism, or science education.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Business Administration

program_id = 41
description = '''
The business administration minor complements the skills you gain in your major discipline by providing a study of principles and techniques used in organizing, planning, managing, and leading within various organizations.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Communication Studies

program_id = 42
description = '''
The communication studies minor complements the skills you gain in your major discipline by helping you develop specialized skills in workplace communication, including visual, written, and oral communication skills and a greater understanding of human interaction.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Computer Science

program_id = 43
description = '''
The computer science minor complements the skills you gain in your major discipline by providing the foundations for designing and programming computer applications in support of many occupations and developing a process for solving challenging computer problems.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Criminal Justice

program_id = 44
description = '''
The criminal justice minor complements the skills you gain in your major discipline by providing a study of crime, law enforcement, courts, corrections, security, and investigative forensics.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Cybersecurity

program_id = 45
description = '''
The cybersecurity minor complements the skills you gain in your major discipline by providing a study of the principles, issues, and technologies pertinent to the cybersecurity field.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Data Science

program_id = 46
description = '''
The data science minor complements the skills you gain in your major discipline by helping you develop specialized skills in data science, business intelligence, machine learning, and artificial intelligence.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Diversity Awareness

program_id = 47
description = '''
The diversity awareness minor complements the skills you gain in your major discipline by providing an interdisciplinary perspective on diversity in contemporary society, conceptually grounded in social science, to promote and cultivate the intercultural awareness and effective communication skills that are necessary in today’s professional and social settings.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• East Asian Studies

program_id = 48
description = '''
The East Asian studies minor complements the skills you gain in your major discipline by providing an interdisciplinary study of the cultural, historical, political, and contemporary business realities of the Asian/Pacific world.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Economics

program_id = 49
description = '''
The economics minor complements the skills you gain in your major discipline by providing a study of the forces that determine production and distribution, price levels, and income distribution, as well as other economic factors that influence the quality of life.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Emergency Management

program_id = 50
description = '''
The emergency management minor complements the skills you gain in your major discipline by providing knowledge of emergency management, including disaster planning and operations, continuity of operations, risk management, and allocation of limited resources.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• English

program_id = 51
description = '''
The English minor complements the skills you gain in your major discipline by providing exposure to literary analysis, critical thinking and reading, and the study of the relationship of literature to contemporary intellectual issues.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Environmental Health and Safety

program_id = 52
description = '''
The environmental health and safety minor complements the skills you gain in your major discipline by providing an interdisciplinary study of techniques and practices to support a safe and healthy work environment.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Finance

program_id = 53
description = '''
The finance minor complements the skills you gain in your major discipline by providing a study of the institutions, theory, and practice associated with the allocation of financial resources within the private sector.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Fire Service Administration

program_id = 54
description = '''
The fire service administration minor complements the skills you gain in your major discipline by providing knowledge of disaster planning and the administration of fire-protection services, including organization, planning, operating procedures, management, and allocation of limited resources.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Forensics

program_id = 55
description = '''
The minor in forensics complements the skills you gain in your major discipline by providing interdisciplinary study in selected areas of criminal justice, natural science, social science, investigation and security, information and computer systems, psychology, and sociology. It combines laboratory and field skills in the collection and analysis of physical evidence with further study in the various subfields of forensics.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Gerontology and Aging Services

program_id = 56
description = '''
The gerontology and aging services minor complements the skills you gain in your major discipline by examining aging from a multidisciplinary perspective that integrates biological, sociological, psychological, and historical perspectives. It provides you with the opportunity to study complex processes and aspects of aging and the field of gerontology.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Health Services Management

program_id = 57
description = '''
The minor in health services management complements the skills you gain in your major discipline by enhancing the knowledge, skills, and competencies required by the changing health services environment. The minor covers a wide range of topics designed to help you deal with the challenges of management and leadership in this dynamic field.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• History

program_id = 58
description = '''
The history minor complements the skills you gain in your major discipline by offering a historical perspective and by helping you develop critical-thinking skills and an appreciation of the major contributions of various events and individuals to human civilization.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Homeland Security

program_id = 59
description = '''
The homeland security minor complements the skills you gain in your major discipline by providing knowledge of infrastructure protection, cyber threats, international and domestic terrorism, emergency preparedness and response, and strategic planning and policies.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Human Resource Management

program_id = 60
description = '''
The human resource management minor complements the skills you gain in your major discipline by examining the human resource functions in a private- or public-sector organizational setting. These functions include human resource planning; recruitment, selection, and placement; employee appraisal and compensation; employee training and career development; management of labor relations; and development of a human resource department implementation plan.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Law for Business

program_id = 61
description = '''
The law for business minor complements the knowledge and skills you gain in your major discipline by providing opportunities to achieve substantive knowledge and practical skill competencies in selected areas of law relevant to business.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Management Information Systems

program_id = 62
description = '''
The management information systems minor complements the skills you gain in your major discipline by helping you develop your abilities to conceptualize and manage the design and implementation of high-quality information systems.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Marketing

program_id = 63
description = '''
The marketing minor complements the skills you gain in your major discipline by enhancing the knowledge and skills related to marketing situations and processes and the emerging global marketplace.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Mathematical Sciences

program_id = 64
description = '''
The mathematical sciences minor complements the skills you gain in your major discipline by helping you develop skills in solving mathematical problems and addressing complex and technical materials and by providing a mathematical background to support study in other areas, such as business and management, computer and information technology, and the biological and social sciences.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Natural Science

program_id = 65
description = '''
The natural science minor complements the skills you gain in your major by providing an underlying scientific basis on which to build a career in natural science, life science, physical science, and the allied health fields, as well as bioinformatics, environmental management, science journalism, and science education.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Personal Financial Planning

program_id = 66
description = '''
The personal financial planning minor complements the skills you gain in your major discipline by providing a study of financial management and planning designed to help prepare you for the Certified Financial Planner (CFP) exam.

This minor is designed primarily for students majoring in finance. If you are majoring in another field, you may need to take several courses to fulfill prerequisites. Consult an advisor or a success coach for more information.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Philosophy

program_id = 67
description = '''
The philosophy minor complements the skills you gain in your major discipline by providing a study of the relationships between personal opinions and real-world issues faced by members of a pluralistic, open society.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Political Science

program_id = 68
description = '''
The political science minor complements the skills you gain in your major discipline by providing a systematic study of politics and government. It exposes you to the basic concepts, theories, policies, and roles of government at local, state, and national levels in domestic and foreign settings.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Psychology

program_id = 69
description = '''
The psychology minor complements the skills you gain in your major discipline by investigating the nature of the mind and behavior, including the biological basis of behavior; perception, memory, and cognition; the influence of environmental and social forces on the individual, personality, and lifespan development and adjustment; research methods; and statistical analysis.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Public Safety Administration

program_id = 70
description = '''
The public safety administration minor complements the skills you gain in your major discipline by providing a background in the field of public safety. The minor exposes you to the principles of strategic planning, risk management, public policy, and ethics as related to public safety administration.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Small Business Management and Entrepreneurship

program_id = 71
description = '''
The small business management and entrepreneurship minor complements the skills you gain in your major discipline by helping you develop your ability to start and operate a successful small business and look for opportunities to create patterns of innovation within your organization. If you are planning to start or manage a small business, such as a family-owned business, a franchise, a virtual business, or a home enterprise, you’ll find this minor helpful.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Sociology

program_id = 72
description = '''
The sociology minor complements the skills you gain in your major discipline by providing a study of contemporary sociological theory and research and applying it to social issues, including globalization, social inequality, diversity, healthcare, education, family, work, and religion.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Speech Communication

program_id = 73
description = '''
The minor in speech communication complements the skills you gain in your major discipline by helping you develop communication skills, particularly oral communication, as well as providing a greater understanding of human interaction in a variety of personal and professional contexts.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Terrorism and Critical Infrastructure

program_id = 74
description = '''
The terrorism and critical infrastructure minor complements the knowledge and skills you develop in your major discipline by offering you an understanding of the principal components of protecting both public and private critical infrastructure from acts of terrorism.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Web and Digital Design

program_id = 75
description = '''
The web and digital design minor complements the skills you gain in your major discipline by providing a study of the principles, best practices, and technologies that govern the design of digital media.
'''
minors.append({ 'program_id': program_id, 'description': description })

#• Women, Gender, and Sexuality Studies

program_id = 76
description = '''
The women, gender, and sexuality studies minor complements the skills you gain in your major discipline by providing an interdisciplinary study of the history, status, and experiences of women.
'''
minors.append({ 'program_id': program_id, 'description': description })

c.executemany('''
    INSERT INTO program_descriptions ( program_id, description )
    VALUES (:program_id, :description)
''', minors )
conn.commit()

############################################################
##            UNDERGRADUATE CERTIFICATIONS                ##
############################################################

ucert = []

#• Accounting Foundations
program_id = 121
description = '''
The undergraduate certificate program in accounting foundations can help you develop the skills and knowledge needed for business transactions, including critical-thinking skills for analysis and reporting of the economic activities of an organization. It can also supplement an associate or bachelor’s degree program.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Advanced Management
program_id = 122
description = '''
Successful managers today require a strong balance of managerial skills and the relationship-building soft skills to manage those who are completing the work. The certificate program in advanced management is designed to help you build expertise by applying best practices to decision-making, problem-solving, and relationship building in real workplace scenarios. The curriculum covers management principles and organizational dynamics for today’s global, multicultural, and virtual organizations.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• American Government and Political Processes
program_id = 123
description = '''
The certificate program in American government and political processes provides an in-depth study and analysis of the U.S. government, including its history, structure, and political culture. In this program, you’ll analyze the vertical and horizontal structures of the American government and its federal and republican foundations. You’ll examine the three federal branches, bureaucracies, and state governments in the context of the development of the American political system and their impact on the political landscape. In addition, the program introduces relevant political theory and compares American government and political economy to those of other nations for a comprehensive overview of political forces.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Applied Social Sciences
program_id = 124
description = '''
The certificate program in applied social sciences helps prepare you to apply social science tools and concepts to practical problems. The program helps equip you with updated knowledge and skills for identifying and solving social problems in communities, families, and the workplace. You’ll develop a deep understanding of social science concepts and learn to identify stakeholders, apply expert knowledge, communicate evidence, and present and defend solutions to relevant parties.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Augmented and Virtual Reality Design
program_id = 125
description = '''
The augmented and virtual reality design certificate program helps provide you with entry-level skills for a career in these immersive technologies. In this project-centric program, you’ll be exposed to virtual reality design and augmented reality design, 3D game engines, user experience and interface design, and immersive design techniques.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Clinical Mental Health Care
program_id = 126
description = '''
The certificate in clinical mental health care is designed to
help prepare you for mental health service jobs that do not require licensure or credentialing. It supports work in direct and indirect client care activities performed under the supervision of a licensed professional (e.g., psychologist, medical doctor, social worker, or rehabilitation therapist) across multiple clinical settings (e.g., hospitals, behavioral health agencies, government agencies, and nonprofit organizations). The curriculum provides foundational theoretical and practical coverage of human behavior, mental health, ethics, and current research in the field.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Computer Networking
program_id = 127
description = '''
A certificate in computer networking can supplement a bachelor’s degree or help you build knowledge and experience in this in-demand field. Ideal for those who want to work as network administrators for business, government, or nonprofit organizations, the undergraduate certificate program in computer networking at UMGC can provide you with hands-on training in state-of-the-art computer technology.

Through the computer networking certificate program, you’ll learn about the fundamental aspects of computer troubleshooting, networking, network security, interconnected Cisco devices, and cloud technologies. Plus, you’ll get a chance to choose from upper-level courses so you can tailor your degree to your career goals.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Cyber Threat Hunting
program_id = 128
description = '''
Organizations today must continuously hunt for cyber threats, since the threat scenario is constantly shifting and no software environment is secure from all threats. This certificate program provides an introduction to the concept of cyber threat hunting. In this program, you’ll learn fundamental techniques and methods for uncovering threats.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Data Analytics
program_id = 129
description = '''
Today, employers are looking to hire professionals who possess data analytics skills and can inform and enhance decision-making within corporations, nonprofit organizations, government agencies, or the military. The certificate program in data analytics provides a valuable introduction to data science and can enhance your career opportunities, regardless of your major. In this program, you learn how to manage and manipulate data, create data visualizations, and use cutting-edge technology to gain insights from traditional and emerging data sources to make strategic data-driven recommendations that influence managerial decision making and organizational outcomes.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Decision Support for Business
program_id = 130
description = '''
The certificate program in decision support for business focuses on building leadership skills in thinking creatively and strategically about both business administration and information systems in the workplace to achieve organizational success. In this program, you’ll explore the foundations of business administration, leadership, management, marketing, finance/accounting, and information systems to gain appropriate insights, improve operations, make on-target predictions, and achieve a competitive advantage in today’s global business environment.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Digital Design
program_id = 131
description = '''
The digital design certificate program provides you with entry-level skills for a career in digital and computer graphics design. The project-centric program exposes you to elements of design, electronic publishing, image editing, illustration graphics, motion graphics, ethical and legal considerations, digital design applications, theories, industry best practices, and design techniques, as well as to various career paths.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Digital Marketing
program_id = 132
description = '''
The digital marketing certificate integrates a foundational understanding of marketing principles with practical applications of digital techniques. In this program, you’ll learn how to create effective online content and use data visualization techniques to gain better insight into the customer experience.

In addition, you’ll learn the skills to create an ad on Facebook that contributes to a social media campaign on that platform and understand the key metrics of optimization. You’ll examine the role of marketing in specific business contexts; use consumer behavior and psychology in the design of marketing strategies; employ best practices in simulating cost-effective marketing designs and selecting delivery modalities; and analyze how to use social media, email, and other digital-based platforms for optimum marketing results.
'''
info = '''
All courses required for the digital marketing certificate can be applied to major course requirements for the BS in Marketing. Prior-learning portfolio credit, internship/Workplace Learning credit, course challenge, or transfer credit from other schools cannot be applied to this certificate.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': info })

#• Health Information Management and Data Analytics
program_id = 133
description = '''
The certificate program in health information management and data analytics is designed to help equip you with knowledge of the U.S. healthcare system and the skills needed for healthcare organizational management. In this program, you’ll learn methods of health information management and technologies for collecting, storing, retrieving, and processing healthcare data. In addition, you’ll learn how to analyze, interpret, and present that data using appropriate statistical tools and techniques for healthcare decision-making. You’ll apply managerial epidemiology tools and evidence in decision-making and acquire skills in planning and resolving diverse healthcare issues.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• HR People Analytics
program_id = 134
description = '''
The HR people analytics certificate program is designed to provide a comprehensive understanding of human resource functions—such as resource planning; recruitment, selection, placement, and orientation of employees; training and career development; labor relations; performance appraisal and rewards programs; and development of personnel policies and procedures—in private- and public-sector settings.

The program provides a data-driven approach toward human resource management that involves collecting, analyzing, and reporting HR data. In this program, you’ll learn the skills you need to measure the impact of a range of HR metrics on overall business performance and make effective business decisions based on HR-related data.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Human Resource Management
program_id = 135
description = '''
The human resource management certificate program at UMGC can help provide the theoretical and practical knowledge you need to advance and skills you can apply on the job right away.

In your HR management certificate program, you’ll learn how to resolve problems in the workplace via conflict management, approach the workplace and employees with a sensitivity to cultural diversity, develop programs for rewarding employees, and help employees reach their full potential.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Leadership and Ethics
program_id = 136
description = '''
The certificate program in leadership and ethics is designed for business managers, organizational leaders, entrepreneurs, legal professionals, and individuals seeking to become effective leaders in public and private global organizations, both for-profit and not-for-profit. The program examines the elements of thoughtful and responsible leadership and allows you to explore issues of ethics related to business administration, leadership, and organizations. In this program, you’ll learn how to practice ethical leadership, executive decision-making, and corporate social responsibility. You'll also learn about leadership theory and practice, conflicts of interest, and organizational culture.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Machine Learning
program_id = 137
description = '''
Machine learning affects all industry sectors that generate significant amounts of data. The certificate program in machine learning combines study of methods and software tools to develop predictive models and artificial intelligence solutions. It can help prepare you for in-demand positions, such as machine learning engineer, applied machine learning scientist, artificial intelligence engineer, artificial intelligence specialist, and data scientist, among others.

The program can serve as an excellent supplement to a wide range of majors—including cybersecurity, environmental health and safety, computer science, and biotechnology— beyond data science.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Management
program_id = 138
description = '''
Today, many workplaces require knowledge of management principles from multiple disciplines. The certificate in management can help you gain knowledge and skills by focusing on fundamental concepts of business management and leadership, problem-solving, and effective data communication strategies.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Management Information Systems
program_id = 139
description = '''
The management information systems certificate program provides you with entry-level skills for a career in information systems. It is especially helpful if you are looking to move into a management position in information systems and bridge the gap between an organization’s functional users and technical developers.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Project Management
program_id = 140
description = '''
The undergraduate project management certificate program at UMGC can help prepare you for supervisory and midlevel management positions involving project management and team management. If you’re a project manager, project team member, or otherwise assigned to project teams within a private- or public-sector organization, this certificate program can help you upgrade your skills with theoretical and practical knowledge to advance to a higher level.

In your project management courses, you’ll learn to bring a project full cycle from development to completion. You’ll also work with a variety of tools designed specifically for project management and work hands-on with federal contracts to become familiar with processes and issues.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Public Safety Executive Leadership
program_id = 141
description = '''
Develop the executive leadership skills needed to succeed in the public safety professional environment. There is currently a high demand for leadership education for public safety officials at the federal, state, and local government levels, as well as throughout the private sector. This certificate should be of professional benefit to both current and future public safety officials employed in public safety planning, public safety legal issues, public policy, public safety research and technology, and public safety leadership.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Spanish for Business and the Professions
program_id = 142
description = '''
Through the certificate program in Spanish for business and the professions at UMGC, you’ll benefit from a combination of language and professional study that will build a foundation to enhance your résumé and prepare you to work and communicate in a variety of Spanish-speaking environments.

This program is ideal for those who are in a professional or social setting where Spanish is often spoken.

In your online Spanish classes, you’ll not only learn the language but also explore contexts and practices specific to the Spanish-speaking world. You’ll use your knowledge of diverse business cultures to communicate and interact effectively in a business environment.
'''
info = '''
This certificate is not intended for students who already have native or near-native ability in Spanish. If you have prior experience in the Spanish language, you should contact the department at languages@umgc.edu about a placement test.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': info })

#• Vulnerability Assessment
program_id = 143
description = '''
The vulnerability assessment certificate program is designed to provide you with the knowledge and skills to examine software for embedded vulnerabilities—whether they are accidental or malicious—that create weaknesses that may be exploited by hackers. In this program, you’ll learn techniques to identify such flaws in software.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Watershed Management
program_id = 144
description = '''
Watershed management plays a crucial role in protecting water quality and aquatic ecosystems, preventing water pollution, decreasing flood risk, and minimizing other human and environmental health impacts related to polluted runoff. The certificate program in watershed management is designed to help prepare you for careers with local, state, and federal government, industry, consulting, and nongovernmental organizations implementing watershed and stormwater management programs with a focus on design principles. You’ll learn about geospatial analyses and the biophysical and social impacts of human activities on watersheds. The program offers you an opportunity to practice designing best management practices, including collaborative and community-based approaches, to reduce stormwater impacts to watersheds. Activities emphasize how to effectively manage watersheds to reduce the impact of land development, industrial processes, and everyday human activities.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Web Design
program_id = 145
description = '''
The web design certificate program provides you with entry-level skills for a career in web design. This project-centric program exposes you to responsive web design, industry best practices, cascading style sheets (CSS), HTML5 coding, extensible markup language (XML), and JavaScript technologies, as well as ethical and legal considerations. Career paths are also explored.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Women, Gender, and Sexuality Studies
program_id = 146
description = '''
The certificate program in women, gender, and sexuality studies provides an interdisciplinary study of gender and sexuality. You’ll examine how these concepts differ across cultures and through time, with an eye toward understanding the diversity of expressions of gender and sexuality in contemporary society and applying that understanding to your personal, professional, and educational contexts.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

c.executemany('''
    INSERT INTO program_descriptions ( program_id, description, info )
    VALUES (:program_id, :description, :info)
''', ucert )
conn.commit()

############################################################
##                 MASTERS PROGRAMS                       ##
############################################################


############################################################
##                  PH.D. PROGRAMS                        ##
############################################################


############################################################
##               GRADUATE CERTIFICATIONS                  ##
############################################################



# Close the connection
conn.close()
