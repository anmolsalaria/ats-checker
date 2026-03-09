"""Advanced suggestion engine (Feature 12).

Produces high-quality, actionable suggestions based on:
- Skill-gap per category
- Missing keywords
- Resume sections
- Score tiers
- Bullet-point analysis
- Impact statement count
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Generates actionable improvement suggestions."""

    CATEGORY_ADVICE: dict[str, str] = {
        "languages": (
            "Add more programming languages relevant to the role. "
            "List them explicitly in a Skills section."
        ),
        "frameworks": (
            "Include frameworks mentioned in the job description "
            "(e.g., React, Django, Spring, Node.js)."
        ),
        "databases": (
            "Highlight database experience. Mention specific databases "
            "(PostgreSQL, MongoDB, Redis) and query-optimisation work."
        ),
        "cloud": (
            "Add cloud platform experience (AWS, Azure, GCP). "
            "Mention specific services like S3, EC2, Lambda, or Cloud Functions."
        ),
        "devops": (
            "Include DevOps and CI/CD experience. Mention Docker, Kubernetes, "
            "Jenkins, GitHub Actions, Terraform, or similar tools."
        ),
        "tools": (
            "List developer tools you use daily (Git, Postman, VS Code, Linux). "
            "These are easy wins for ATS keyword matching."
        ),
        "data_ml": (
            "Mention data and ML tools relevant to the role "
            "(pandas, TensorFlow, scikit-learn, Spark, Tableau)."
        ),
        "concepts": (
            "Reference software-engineering concepts from the JD "
            "(REST APIs, microservices, system design, Agile, TDD)."
        ),
    }

    @staticmethod
    def generate_suggestions(
        missing_keywords: list[str],
        resume_sections: dict[str, bool],
        ats_score: int,
        skill_gap: dict | None = None,
        impact_count: int = 0,
        bullet_quality_score: int = 100,
        detected_role: str = "Software Engineer",
    ) -> list[str]:
        suggestions: list[str] = []

        # ---- 1. Category-specific skill-gap suggestions ----
        if skill_gap:
            for cat, info in skill_gap.items():
                ms = info.get("missing_skills", [])
                if ms:
                    advice = SuggestionEngine.CATEGORY_ADVICE.get(cat, "")
                    if advice:
                        suggestions.append(
                            f"{advice} Missing: {', '.join(ms[:5])}."
                        )

        # ---- 2. Top missing keywords ----
        if missing_keywords and len(missing_keywords) > 2:
            top = missing_keywords[:6]
            suggestions.append(
                f"Add these high-priority keywords to your resume: "
                f"{', '.join(top)}. Weave them naturally into your experience "
                f"and skills sections."
            )

        # ---- 3. Section suggestions ----
        if not resume_sections.get("summary"):
            suggestions.append(
                "Add a Professional Summary at the top of your resume. "
                "This helps recruiters and ATS parsers quickly identify "
                "your profile."
            )

        if not resume_sections.get("skills"):
            suggestions.append(
                "Add a dedicated Skills section listing technologies, tools, "
                "and competencies. This is one of the highest-impact ATS sections."
            )

        if not resume_sections.get("projects"):
            suggestions.append(
                "Add a Projects section to showcase hands-on work, "
                "especially personal or open-source projects."
            )

        if not resume_sections.get("certifications"):
            suggestions.append(
                "Consider adding a Certifications section (e.g., AWS Certified, "
                "Google Cloud Associate, PMP). Certifications significantly "
                "boost ATS scores for many roles."
            )

        # ---- 4. Quantified-achievement guidance ----
        if impact_count < 2:
            suggestions.append(
                'Add quantified achievements (e.g., '
                '"Improved API response time by 40%", '
                '"Reduced deployment time from 2 hours to 15 minutes"). '
                "Metrics make your resume more compelling to both ATS and humans."
            )

        # ---- 5. Bullet quality suggestions ----
        if bullet_quality_score < 40:
            suggestions.append(
                "Improve your bullet points: start each with a strong action verb "
                "(Built, Developed, Optimized), mention the specific technology, "
                "and include a quantified result."
            )
        elif bullet_quality_score < 60:
            suggestions.append(
                "Some bullet points lack impact. Ensure each one follows the "
                "pattern: [Action Verb] + [Technology] + [Quantified Result]."
            )

        # ---- 6. Score-tier advice ----
        if ats_score < 40:
            suggestions.append(
                "Your resume has low alignment with this job description. "
                "Consider tailoring it specifically for this role by "
                "mirroring the language and keywords from the job posting."
            )
        elif ats_score < 60:
            suggestions.append(
                "Your resume partially matches the job description. "
                "Focus on incorporating the missing keywords "
                "in context within your experience bullets."
            )
        elif ats_score < 80:
            suggestions.append(
                "Good alignment. Fine-tune by incorporating a few more "
                "missing keywords and strengthening quantified achievements."
            )

        # ---- 7. Role-specific advice ----
        if "Machine Learning" in detected_role or "Data" in detected_role:
            suggestions.append(
                f"Targeting '{detected_role}': emphasize ML/data projects, "
                "model metrics (accuracy, F1), and tools (TensorFlow, PyTorch, "
                "pandas, SQL)."
            )
        elif "DevOps" in detected_role or "Cloud" in detected_role:
            suggestions.append(
                f"Targeting '{detected_role}': highlight infrastructure "
                "projects, uptime improvements, CI/CD pipelines, and "
                "cloud cost optimisations."
            )

        # Deduplicate (preserve order)
        seen: set[str] = set()
        unique: list[str] = []
        for s in suggestions:
            key = s[:60]
            if key not in seen:
                seen.add(key)
                unique.append(s)

        return unique

    @staticmethod
    def generate_strength_suggestions(
        weaknesses: list[str],
        resume_sections: dict[str, bool],
        impact_count: int = 0,
        bullet_quality_score: int = 100,
    ) -> list[str]:
        """Suggestions for the no-JD resume-strength mode (Feature 8)."""
        suggestions: list[str] = []

        for w in weaknesses:
            suggestions.append(f"Weakness identified: {w}.")

        if impact_count < 2:
            suggestions.append(
                'Add measurable achievements (e.g., '
                '"Reduced infrastructure costs by 30%", '
                '"Served 10K daily active users").'
            )

        if bullet_quality_score < 50:
            suggestions.append(
                "Strengthen your bullet points: use strong action verbs, "
                "mention technologies, and add quantified results."
            )

        if not resume_sections.get("summary"):
            suggestions.append(
                "Start with a concise Professional Summary to give "
                "recruiters an immediate snapshot of your strengths."
            )

        return suggestions
