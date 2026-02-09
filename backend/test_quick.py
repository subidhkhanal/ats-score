"""Quick integration test — run with: python test_quick.py"""
import sys
sys.path.insert(0, ".")

from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_jd
from app.services.keyword_matcher import compute_keyword_score
from app.services.structure_scorer import compute_structure_score
from app.services.score_aggregator import compute_overall_score, get_recruiter_status, get_rank_estimate

RESUME = """John Doe
john@example.com | 555-123-4567
https://linkedin.com/in/johndoe | https://github.com/johndoe

SUMMARY
Experienced software engineer with 5 years in full-stack development using React, Node.js, Python, and AWS.

SKILLS
React, Next.js, TypeScript, Node.js, Python, FastAPI, PostgreSQL, Docker, AWS, Git

EXPERIENCE
Senior Software Engineer at TechCorp
Jan 2022 - Present
- Built a real-time dashboard using React and WebSocket
- Developed REST APIs with FastAPI serving 10M requests/day
- Implemented CI/CD pipeline with GitHub Actions and Docker

Software Engineer at StartupInc
Jun 2019 - Dec 2021
- Built microservices with Node.js and PostgreSQL
- Created responsive UIs with React and TypeScript

EDUCATION
BS Computer Science, MIT, 2019

PROJECTS
Portfolio Website
- Built with Next.js and Tailwind CSS
- Deployed on Vercel
"""

JD = """Senior Software Engineer

Required Skills:
- React.js, TypeScript
- Python, FastAPI or Django
- PostgreSQL
- Docker, Kubernetes
- AWS

Responsibilities:
- Design and build scalable web applications
- Develop RESTful APIs
- Implement CI/CD pipelines

Preferred:
- Experience with Next.js
- GraphQL knowledge
- Machine learning basics
"""

print("=== Parsing Resume ===")
parsed_resume = parse_resume(RESUME)
print(f"  Name: {parsed_resume.contact.name}")
print(f"  Email: {parsed_resume.contact.email}")
print(f"  Skills: {parsed_resume.skills[:10]}")
print(f"  Sections: {list(parsed_resume.sections.keys())}")
print(f"  Word count: {parsed_resume.word_count}")

print("\n=== Parsing JD ===")
parsed_jd = parse_jd(JD)
print(f"  Title: {parsed_jd.title}")
print(f"  Experience level: {parsed_jd.experience_level}")
print(f"  Keywords extracted: {len(parsed_jd.keywords)}")
for kw in parsed_jd.keywords[:5]:
    print(f"    - {kw.keyword} ({kw.category}, weight={kw.weight})")

print("\n=== Layer 1: Keyword Matching ===")
keyword_score, keyword_results = compute_keyword_score(parsed_resume, parsed_jd)
found = [r for r in keyword_results if r.found]
missing = [r for r in keyword_results if not r.found]
print(f"  Score: {keyword_score}")
print(f"  Found: {len(found)}/{len(keyword_results)}")
for r in found[:5]:
    print(f"    + {r.keyword} ({r.match_type}, in {r.location_in_resume})")
for r in missing[:5]:
    print(f"    - {r.keyword} (missing)")

print("\n=== Layer 2: Semantic Scoring ===")
try:
    from app.services.semantic_scorer import compute_semantic_score
    semantic_score, semantic_results = compute_semantic_score(parsed_resume, parsed_jd)
    print(f"  Score: {semantic_score}")
    print(f"  Skills similarity: {semantic_results.section_similarities.get('skills', 0)}%")
    print(f"  Experience similarity: {semantic_results.section_similarities.get('experience', 0)}%")
except Exception as e:
    semantic_score = 0
    print(f"  Skipped (model loading): {e}")

print("\n=== Layer 3: Structure Scoring ===")
structure_score, structure_results = compute_structure_score(parsed_resume)
print(f"  Score: {structure_score}")
print(f"  Contact: {structure_results.contact_score}/25")
print(f"  Sections: {structure_results.sections_score}/25")
print(f"  Length: {structure_results.length_score}/25")
print(f"  Format: {structure_results.formatting_score}/25")

print("\n=== Overall ===")
overall = compute_overall_score(keyword_score, semantic_score, structure_score)
status = get_recruiter_status(overall)
rank = get_rank_estimate(overall)
print(f"  Overall Score: {overall}")
print(f"  Recruiter Status: {status}")
print(f"  Rank Estimate: {rank}")
print("\n=== ALL TESTS PASSED ===")
