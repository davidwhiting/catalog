---------------------------------------------------
-- Get Skill Categories
---------------------------------------------------
SELECT * 
FROM skill_category

---------------------------------------------------
-- Get Skills for each Skill Category
---------------------------------------------------

SELECT scsm.id, 
    sk.id AS category_id, sk.name AS category,
    scsm.skill AS skill_id, s.name AS skill 
FROM 
    skill_category sk 
JOIN
    skill_category_skill_map scsm on scsm.skill_category = sk.id
JOIN Skills s on scsm.skill = s.id
ORDER BY category_id, skill_id

---------------------------------------------------
-- FIND MAJORS THAT MOST RELATE TO SELECTED SKILLS
---------------------------------------------------

select p.name, sum(pss.score) AS TotalScore from program_skill_score pss
join programs p on pss.program_id = p.id
join Skills s on s.id = pss.skill_id
--where s.name in ('Technology Design', 'Monitoring')
where s.name in ('Mathematics')
GROUP BY p.name
order by sum(pss.score) desc

---------------------------------------------------
-- FIND MAJORS THAT MOST RELATE TO SELECTED SKILLS
---------------------------------------------------

SELECT program, sum(score) AS TotalScore 
FROM program_skill_score_view
WHERE skill IN ('Mathematics', 'Negotiation')
GROUP BY program
ORDER BY TotalScore DESC 
LIMIT 10


SELECT program, sum(score) AS TotalScore 
FROM program_skill_score_view
WHERE skill IN ('Mathematics')
GROUP BY program
ORDER BY TotalScore DESC 
LIMIT 10
