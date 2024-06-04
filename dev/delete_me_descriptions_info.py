'''
    CREATE TABLE student_progress (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        seq INTEGER,
        name TEXT,
        course_type TEXT,
        type TEXT,
        credits INTEGER,
        title TEXT,
        completed INTEGER DEFAULT 0,
        term INTEGER DEFAULT 0,
        session INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0,
        pre TEXT DEFAULT '',
        pre_credits TEXT DEFAULT '',
        substitutions TEXT DEFAULT '',
        prerequisites TEXT DEFAULT '',
        description TEXT DEFAULT '',
        FOREIGN KEY(user_id) REFERENCES users(id)
'''

'''
    CREATE TABLE student_progress_d3 (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        seq INTEGER,
        name TEXT,
        credits INTEGER,
        type TEXT,
        completed INTEGER DEFAULT 0,
        term INTEGER DEFAULT 0,
        session INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0,
        prerequisites TEXT,
        pre TEXT DEFAULT NULL,
        pre_credits TEXT DEFAULT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')
#MINORS

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


###############################################
## Undergraduate Certifications

ucert = []

#• Accounting Foundations
program_id = 121
description = '''
The undergraduate certificate program in accounting founda- tions can help you develop the skills and knowledge needed for business transactions, including critical-thinking skills for analy- sis and reporting of the economic activities of an organization. It can also supplement an associate or bachelor’s degree program.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Advanced Management
program_id = 122
description = '''
Successful managers today require a strong balance of mana- gerial skills and the relationship-building soft skills to manage those who are completing the work. The certificate program in advanced management is designed to help you build expertise by applying best practices to decision-making, problem-solving, and relationship building in real workplace scenarios. The curriculum covers management principles and organizational dynamics for today’s global, multicultural, and virtual organizations.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• American Government and Political Processes
program_id = 123
description = '''
The certificate program in American government and political processes provides an in-depth study and analysis of the U.S. government, including its history, structure, and political culture. In this program, you’ll analyze the vertical and horizontal struc- tures of the American government and its federal and repub- lican foundations. You’ll examine the three federal branches, bureaucracies, and state governments in the context of the development of the American political system and their impact on the political landscape. In addition, the program introduces relevant political theory and compares American government and political economy to those of other nations for a compre- hensive overview of political forces.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Applied Social Sciences
program_id = 124
description = '''
The certificate program in applied social sciences helps prepare you to apply social science tools and concepts to practical problems. The program helps equip you with updated knowl- edge and skills for identifying and solving social problems in communities, families, and the workplace. You’ll develop a deep understanding of social science concepts and learn to identify stakeholders, apply expert knowledge, communicate evidence, and present and defend solutions to relevant parties.
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
help prepare you for mental health service jobs that do not require licensure or credentialing. It supports work in direct and indirect client care activities performed under the supervision of a licensed professional (e.g., psychologist, medical doctor, social worker, or rehabilitation therapist) across multiple clinical settings (e.g., hospitals, behavioral health agencies, government agencies, and nonprofit organizations). The curriculum provides foundational theoretical and practical coverage of human behav- ior, mental health, ethics, and current research in the field.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Computer Networking
program_id = 127
description = '''
A certificate in computer networking can supplement a bachelor’s degree or help you build knowledge and experience in this in-demand field. Ideal for those who want to work as network administrators for business, government, or non- profit organizations, the undergraduate certificate program in computer networking at UMGC can provide you with hands-on training in state-of-the-art computer technology.

Through the computer networking certificate program, you’ll learn about the fundamental aspects of computer troubleshoot- ing, networking, network security, interconnected Cisco devices, and cloud technologies. Plus, you’ll get a chance to choose from upper-level courses so you can tailor your degree to your career goals.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Cyber Threat Hunting
program_id = 128
description = '''
Organizations today must continuously hunt for cyber threats, since the threat scenario is constantly shifting and no software environment is secure from all threats. This certificate program provides an introduction to the concept of cyber threat hunting. In this program, you’ll learn fundamental techniques and meth- ods for uncovering threats.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Data Analytics
program_id = 129
description = '''
Today, employers are looking to hire professionals who possess data analytics skills and can inform and enhance decision-making within corporations, nonprofit organizations, government agen- cies, or the military. The certificate program in data analytics provides a valuable introduction to data science and can enhance your career opportunities, regardless of your major. In this pro- gram, you learn how to manage and manipulate data, create data visualizations, and use cutting-edge technology to gain insights from traditional and emerging data sources to make strategic data-driven recommendations that influence managerial decision- making and organizational outcomes.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Decision Support for Business
program_id = 130
description = '''
The certificate program in decision support for business focuses on building leadership skills in thinking creatively and strate- gically about both business administration and information systems in the workplace to achieve organizational success. In this program, you’ll explore the foundations of business adminis- tration, leadership, management, marketing, finance/accounting, and information systems to gain appropriate insights, improve operations, make on-target predictions, and achieve a competi- tive advantage in today’s global business environment.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Digital Design
program_id = 131
description = '''
The digital design certificate program provides you with entry- level skills for a career in digital and computer graphics design. The project-centric program exposes you to elements of design, electronic publishing, image editing, illustration graphics, motion graphics, ethical and legal considerations, digital design applications, theories, industry best practices, and design techniques, as well as to various career paths.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• Digital Marketing
program_id = 132
description = '''
The digital marketing certificate integrates a foundational understanding of marketing principles with practical applica- tions of digital techniques. In this program, you’ll learn how to create effective online content and use data visualization tech- niques to gain better insight into the customer experience.

In addition, you’ll learn the skills to create an ad on Facebook that contributes to a social media campaign on that platform and understand the key metrics of optimization. You’ll exam- ine the role of marketing in specific business contexts; use consumer behavior and psychology in the design of marketing strategies; employ best practices in simulating cost-effective marketing designs and selecting delivery modalities; and analyze how to use social media, email, and other digital-based platforms for optimum marketing results.
'''
info = '''
All courses required for the digital marketing certificate can be applied to major course requirements for the BS in Marketing. Prior-learning portfolio credit, internship/Workplace Learning credit, course challenge, or transfer credit from other schools cannot be applied to this certificate.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': info })

#• Health Information Management and Data Analytics
program_id = 133
description = '''
The certificate program in health information management and data analytics is designed to help equip you with knowledge of the U.S. healthcare system and the skills needed for healthcare organizational management. In this program, you’ll learn meth- ods of health information management and technologies for collecting, storing, retrieving, and processing healthcare data. In addition, you’ll learn how to analyze, interpret, and present that data using appropriate statistical tools and techniques for healthcare decision-making. You’ll apply managerial epidemiol- ogy tools and evidence in decision-making and acquire skills in planning and resolving diverse healthcare issues.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

#• HR People Analytics
program_id = 134
description = '''
The HR people analytics certificate program is designed to provide a comprehensive understanding of human resource functions—such as resource planning; recruitment, selection, placement, and orientation of employees; training and career development; labor relations; performance appraisal and rewards programs; and development of personnel policies and proce- dures—in private- and public-sector settings.

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
The certificate program in leadership and ethics is designed for business managers, organizational leaders, entrepreneurs, legal professionals, and individuals seeking to become effective leaders in public and private global organizations, both for- profit and not-for-profit. The program examines the elements of thoughtful and responsible leadership and allows you to explore issues of ethics related to business administration, leadership, and organizations. In this program, you’ll learn how to practice ethical leadership, executive decision-making, and corporate social responsibility. You'll also learn about leadership theory and practice, conflicts of interest, and organizational culture.
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
Today, many workplaces require knowledge of management principles from multiple disciplines. The certificate in manage- ment can help you gain knowledge and skills by focusing on fundamental concepts of business management and leadership, problem-solving, and effective data communication strategies.
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
The undergraduate project management certificate program at UMGC can help prepare you for supervisory and midlevel management positions involving project management and team management. If you’re a project manager, project team mem- ber, or otherwise assigned to project teams within a private- or public-sector organization, this certificate program can help you upgrade your skills with theoretical and practical knowledge to advance to a higher level.

In your project management courses, you’ll learn to bring a project full cycle from development to completion. You’ll also work with a variety of tools designed specifically for project man- agement and work hands-on with federal contracts to become familiar with processes and issues.
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
Through the certificate program in Spanish for business and the professions at UMGC, you’ll benefit from a combination of language and professional study that will build a foundation to enhance your résumé and prepare you to work and communi- cate in a variety of Spanish-speaking environments.

This program is ideal for those who are in a professional or social setting where Spanish is often spoken.

In your online Spanish classes, you’ll not only learn the lan- guage but also explore contexts and practices specific to the Spanish-speaking world. You’ll use your knowledge of diverse business cultures to communicate and interact effectively in a business environment.
'''
info = '''
This certificate is not intended for students who already have native or near- native ability in Spanish. If you have prior experience in the Spanish language, you should contact the department at languages@umgc.edu about a placement test.
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
Watershed management plays a crucial role in protecting water quality and aquatic ecosystems, preventing water pollution, decreasing flood risk, and minimizing other human and environ- mental health impacts related to polluted runoff. The certificate program in watershed management is designed to help prepare you for careers with local, state, and federal government, indus- try, consulting, and nongovernmental organizations implement- ing watershed and stormwater management programs with a focus on design principles. You’ll learn about geospatial analyses and the biophysical and social impacts of human activities on watersheds. The program offers you an opportunity to practice designing best management practices, including collabora- tive and community-based approaches, to reduce stormwater impacts to watersheds. Activities emphasize how to effectively manage watersheds to reduce the impact of land development, industrial processes, and everyday human activities.
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
The certificate program in women, gender, and sexuality stud- ies provides an interdisciplinary study of gender and sexuality. You’ll examine how these concepts differ across cultures and through time, with an eye toward understanding the diversity of expressions of gender and sexuality in contemporary society and applying that understanding to your personal, professional, and educational contexts.
'''
ucert.append({ 'program_id': program_id, 'description': description, 'info': '' })

##### COURSES FOR CERTIFICATES ########

ucert = []


#The following undergraduate certificate programs are available:

certification_courses = [
    { 'program_id': 121, 'required': 1, 'course': 'ACCT 220' },
    { 'program_id': 121, 'required': 1, 'course': 'ACCT 221' },
    { 'program_id': 121, 'required': 0, 'course': 'ACCT 100+' },
    { 'program_id': 121, 'required': 0, 'course': 'FINC 100+' },
    { 'program_id': 121, 'required': 0, 'course': 'BMGT 110' },
    { 'program_id': 121, 'required': 0, 'course': 'CMSC 105' },
    { 'program_id': 121, 'required': 0, 'course': 'DATA 200' },
    { 'program_id': 121, 'required': 0, 'course': 'ECON 201' },
    { 'program_id': 121, 'required': 0, 'course': 'ECON 203' },
    { 'program_id': 121, 'required': 0, 'course': 'IFSM 201' },
    { 'program_id': 121, 'required': 0, 'course': 'STAT 200' },
    { 'program_id': 121, 'required': 0, 'course': 'WRTG 112' },
    { 'program_id': 122, 'required': 1, 'course': 'BMGT 160' },
    { 'program_id': 122, 'required': 1, 'course': 'BMGT 364' },
    { 'program_id': 122, 'required': 1, 'course': 'BMGT 484' },
    { 'program_id': 122, 'required': 1, 'course': 'BMGT 317' },
    { 'program_id': 122, 'required': 0, 'course': 'ACCT 301' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 305' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 335' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 365' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 380' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 464' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 465' },
    { 'program_id': 122, 'required': 0, 'course': 'BMGT 496' },
    { 'program_id': 122, 'required': 0, 'course': 'DATA 200' },
    { 'program_id': 122, 'required': 0, 'course': 'FINC 330' },
    { 'program_id': 122, 'required': 0, 'course': 'FINC 331' },
    { 'program_id': 122, 'required': 0, 'course': 'HRMN 300' },
    { 'program_id': 122, 'required': 0, 'course': 'HRMN 302' },
    { 'program_id': 122, 'required': 0, 'course': 'HRMN 367' },
    { 'program_id': 122, 'required': 0, 'course': 'IFSM 300' },
    { 'program_id': 122, 'required': 0, 'course': 'MRKT 310' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 170' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 280' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 306' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 444' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 457' },
    { 'program_id': 123, 'required': 1, 'course': 'GVPT 475' },
    { 'program_id': 124, 'required': 1, 'course': 'PSYC 100' },
    { 'program_id': 124, 'required': 1, 'course': 'SOCY 100' },
    { 'program_id': 124, 'required': 0, 'course': 'ANTH 350' },
    { 'program_id': 124, 'required': 0, 'course': 'ANTH 351' },
    { 'program_id': 124, 'required': 0, 'course': 'GERO 427' },
    { 'program_id': 124, 'required': 0, 'course': 'PSYC 354' },
    { 'program_id': 124, 'required': 0, 'course': 'PSYC 386' },
    { 'program_id': 124, 'required': 0, 'course': 'SOCY 350' },
    { 'program_id': 125, 'required': 1, 'course': 'CMST 290' }, 
    { 'program_id': 125, 'required': 1, 'course': 'CMST 295' }, 
    { 'program_id': 125, 'required': 1, 'course': 'CMST 308' }, 
    { 'program_id': 125, 'required': 1, 'course': 'CMST 315' }, 
    { 'program_id': 125, 'required': 1, 'course': 'CMST 330' }, 
    { 'program_id': 125, 'required': 1, 'course': 'CMST 331' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 100' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 300' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 301' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 335' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 353' },
    { 'program_id': 126, 'required': 1, 'course': 'PSYC 436' },
    { 'program_id': 127, 'required': 1, 'course': 'CMIT 202' }, 
    { 'program_id': 127, 'required': 1, 'course': 'CMIT 265' },
    { 'program_id': 127, 'required': 1, 'course': 'CMIT 320' },
    { 'program_id': 127, 'required': 1, 'course': 'CMIT 326' },
    { 'program_id': 127, 'required': 1, 'course': 'CMIT 351' },
    { 'program_id': 127, 'required': 0, 'course': 'CMIT 300+' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 202' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 265' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 320' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 321' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 386' },
    { 'program_id': 128, 'required': 1, 'course': 'CMIT 421' },
    { 'program_id': 129, 'required': 1, 'course': 'STAT 200' },
    { 'program_id': 129, 'required': 1, 'course': 'DATA 200' },
    { 'program_id': 129, 'required': 1, 'course': 'DATA 320' },
    { 'program_id': 129, 'required': 1, 'course': 'IFSM 330' },
    { 'program_id': 129, 'required': 1, 'course': 'DATA 335' },
    { 'program_id': 129, 'required': 0, 'course': 'CSIA 300' },
    { 'program_id': 129, 'required': 0, 'course': 'DATA 300' },

Total credits for certificate in Data Analytics: 18


• Decision Support for Business
rogram_id = 130
ONE COURSE CHOSEN FROM THE FOLLOWING:
IFSM 300
DATA 200

FIVE REQUIRED COURSES:
BMGT 364 
BMGT 365 
BMGT 495 
FINC 330 
MRKT 310

Total credits for certificate in Decision Support for Business: 18
• Digital Design
rogram_id = 131
SIX REQUIRED COURSES:
CMST 295 
CMST 310 
CMST 311 
CMST 320 
CMST 325 
CMST 341

Total credits for certificate in Digital Design: 18
• Digital Marketing
rogram_id = 132
SIX REQUIRED COURSES:
MRKT 311 
MRKT 354 
MRKT 356 
MRKT 394 
MRKT 411 
MRKT 458

Total credits for certificate in Digital Marketing: 18
• Health Information Management and Data Analytics
rogram_id = 133
SIX REQUIRED COURSES:
HMGT 300 
IFSM 305
STAT 200 
HMGT 307
HMGT 320 
HMGT 400

Total credits for certificate in Health Information Management and Data Analytics: 18
• HR People Analytics
rogram_id = 134
SIX REQUIRED COURSES:
BMGT 364 
FINC 331 
HRMN 300 
HRMN 400 
HRMN 410 
IFSM 300
Total credits for certificate in HR People Analytics: 18
• Human Resource Management
rogram_id = 135
FOUR REQUIRED COURSES:
BMGT 364 
HRMN 300 
HRMN 362 
HRMN 400

TWO SUPPORTING ELECTIVES CHOSEN FROM THE FOLLOWING:
BMGT 365 
BMGT 464 
BMGT 465
HRMN 302 
HRMN 367 
HRMN 395
HRMN 406 
HRMN 495

Total credits for certificate in Human Resource Management: 18
• Leadership and Ethics
rogram_id = 136
SIX REQUIRED COURSES:
BMGT 364 
BMGT 365 
BMGT 496 
HRMN 300 
BMGT 110 
BMGT 380

Total credits for certificate in Leadership and Ethics: 18
• Machine Learning
rogram_id = 137
SIX REQUIRED COURSES:
STAT 200 
DATA 220 
DATA 300 
DATA 430 
DATA 450 
DATA 460

Total credits for certificate in Machine Learning: 18
• Management
rogram_id = 138
TWO REQUIRED COURSES:
BMGT 160 
BMGT 110

FOUR COURSES CHOSEN FROM THE FOLLOWING:
ACCT 220 
ACCT 221 
ECON 201 
ECON 203 
IFSM 201
STAT 200

Total credits for certificate in Management: 18
• Management Information Systems
rogram_id = 139
SIX REQUIRED COURSES:
CSIA 300 
IFSM 300 
IFSM 301
IFSM 310
IFSM 370 
IFSM 330

Total credits for certificate in Management Information Systems: 18
• Project Management
rogram_id = 140
FOUR REQUIRED COURSES:
BMGT 487 
BMGT 488 
IFSM 438 
IFSM 441

TWO SUPPORTING ELECTIVES CHOSEN FROM THE FOLLOWING:
BMGT 317
BMGT 339 
BMGT 365 
BMGT 484 
IFSM 300


• Public Safety Executive Leadership
rogram_id = 141
SIX REQUIRED COURSES:
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 304' }, 
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 306' }, 
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 408' }, 
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 410' }, 
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 416' }, 
    { 'program_id': 141, 'required': 1, 'course': 'PSAD 414' },
    { 'program_id': 142, 'required': 1, 'course': 'SPAN 211' },
    { 'program_id': 142, 'required': 1, 'course': 'SPAN 212' },
    { 'program_id': 142, 'required': 1, 'course': 'SPAN 300+' },
    { 'program_id': 142, 'required': 0, 'course': 'SPAN 418' },
    { 'program_id': 142, 'required': 0, 'course': 'SPAN 419' },
    { 'program_id': 143, 'required': 1, 'course': 'CMSC 105' },
    { 'program_id': 143, 'required': 1, 'course': 'CMSC 115' }, 
    { 'program_id': 143, 'required': 1, 'course': 'CMSC 215' }, 
    { 'program_id': 143, 'required': 1, 'course': 'CMSC 320' }, 
    { 'program_id': 143, 'required': 1, 'course': 'SDEV 300' }, 
    { 'program_id': 143, 'required': 1, 'course': 'SDEV 325' }, 
    { 'program_id': 143, 'required': 1, 'course': 'SDEV 360' },
    { 'program_id': 144, 'required': 1, 'course': 'ENHS 300' },
    { 'program_id': 144, 'required': 1, 'course': 'ENHS 305' },
    { 'program_id': 144, 'required': 1, 'course': 'EHNS 340' },
    { 'program_id': 144, 'required': 1, 'course': 'ENHS 350' },
    { 'program_id': 144, 'required': 1, 'course': 'ENMT 360' },
    { 'program_id': 144, 'required': 1, 'course': 'ENHS 405' },
    { 'program_id': 145, 'required': 1, 'course': 'CMST 290' }, 
    { 'program_id': 145, 'required': 1, 'course': 'CMST 295' }, 
    { 'program_id': 145, 'required': 1, 'course': 'CMST 385' }, 
    { 'program_id': 145, 'required': 1, 'course': 'CMST 386' }, 
    { 'program_id': 145, 'required': 1, 'course': 'CMST 388' }, 
    { 'program_id': 145, 'required': 1, 'course': 'CMST 355' },
    { 'program_id': 146, 'required': 1, 'course': 'WMST 200' },
    { 'program_id': 146, 'required': 0, 'course': 'BEHS 220' },
    { 'program_id': 146, 'required': 0, 'course': 'BEHS 250' },
    { 'program_id': 146, 'required': 0, 'course': 'BEHS 343' },
    { 'program_id': 146, 'required': 0, 'course': 'BEHS 453' },
    { 'program_id': 146, 'required': 0, 'course': 'ENGL 250' },
    { 'program_id': 146, 'required': 0, 'course': 'GERO 311' },
    { 'program_id': 146, 'required': 0, 'course': 'HIST 377' },
    { 'program_id': 146, 'required': 0, 'course': 'PSYC 332' },
    { 'program_id': 146, 'required': 0, 'course': 'SOCY 325' },
    { 'program_id': 146, 'required': 0, 'course': 'SOCY 443' },
    { 'program_id': 146, 'required': 0, 'course': 'SOCY 462' },
    { 'program_id': 146, 'required': 0, 'course': 'SPCH 324' }
]