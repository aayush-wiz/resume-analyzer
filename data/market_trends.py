# In a real app, this would come from a database, APIs, or scraped documents.
knowledge_base_data = [
    {
        "id": "skill-1",
        "content": "Cloud Engineering: In-demand skills include proficiency in AWS, Azure, or GCP. Core competencies involve Kubernetes for container orchestration and Terraform for Infrastructure as Code (IaC).",
        "metadata": {"type": "skill_trend", "field": "Software Development"},
    },
    {
        "id": "skill-2",
        "content": "Data Analysis career path often starts as a Data Analyst and progresses to a Senior Analyst or Analytics Manager. Advancing requires strong skills in data visualization tools like Tableau or Power BI.",
        "metadata": {"type": "career_path", "field": "Data Science"},
    },
    {
        "id": "skill-3",
        "content": "Full-Stack Development: A Junior Full-Stack Developer should master a frontend framework like React or Vue and a backend framework like Node.js/Express or Django. Skill gaps often appear in system design and database optimization.",
        "metadata": {"type": "role_description", "field": "Software Development"},
    },
    {
        "id": "skill-4",
        "content": "Popular certifications for data roles include the Google Professional Data Engineer certification and the Microsoft Certified: Azure Data Scientist Associate.",
        "metadata": {"type": "certification", "field": "Data Science"},
    },
    {
        "id": "skill-5",
        "content": "UI/UX Design: Figma is the industry-standard tool for collaborative design and prototyping. Knowledge of user research methodologies and usability testing is crucial for senior roles.",
        "metadata": {"type": "skill_trend", "field": "Design"},
    },
    # New Data Points
    {
        "id": "ats-1",
        "content": "ATS (Applicant Tracking Systems) readiness is crucial. Resumes should use standard section headers like 'Professional Experience', 'Skills', and 'Education'. Avoid using tables, columns, or images as they are often parsed incorrectly.",
        "metadata": {"type": "ats_tip", "field": "General"},
    },
    {
        "id": "ats-2",
        "content": "For maximum ATS compatibility, resumes should include specific keywords from the job description. For a data analyst role, keywords like 'SQL', 'Tableau', 'Power BI', 'Python', 'Data Visualization', and 'Statistical Analysis' are essential.",
        "metadata": {"type": "ats_tip", "field": "Data Science"},
    },
    {
        "id": "ats-3",
        "content": "For software development roles, ATS systems often scan for keywords related to programming languages (e.g., 'Java', 'Python', 'JavaScript'), frameworks ('React', 'Spring Boot', 'Django'), and methodologies ('Agile', 'Scrum').",
        "metadata": {"type": "ats_tip", "field": "Software Development"},
    },
    {
        "id": "roadmap-1",
        "content": "A typical career growth roadmap for a software engineer is: Junior Developer (0-2 years), Mid-Level Developer (2-5 years), and Senior Developer (5+ years). Specializations can lead to roles like Cloud Architect, DevOps Engineer, or Tech Lead.",
        "metadata": {"type": "career_roadmap", "field": "Software Development"},
    },
    {
        "id": "roadmap-2",
        "content": "The career path for data professionals often looks like this: Start as a Data Analyst. Short-term growth leads to Senior Data Analyst. Long-term, with skills in machine learning and statistics, one can transition to a Data Scientist or Analytics Manager.",
        "metadata": {"type": "career_roadmap", "field": "Data Science"},
    },
    {
        "id": "upskill-1",
        "content": "To advance in data analytics, learning cloud data platforms like AWS Redshift, Google BigQuery, or Azure Synapse Analytics is highly recommended. A certification like 'Google Professional Data Engineer' validates these skills.",
        "metadata": {"type": "upskilling", "field": "Data Science"},
    },
]
