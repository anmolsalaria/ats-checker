"""Suggestion generation service — v2 (Feature 8).

Produces higher-quality, more actionable suggestions:
- Quantified-achievement guidance
- Category-aware missing-tech hints
- Resume-section recommendations
- Score-tier adaptive advice
"""

import logging

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Generates actionable improvement suggestions based on analysis results."""

    CATEGORY_ADVICE: dict[str, str] = {
        "languages": (
            "Add more programming languages relevant to the role. "
            "List them explicitly in a Skills section."
        ),
        "frameworks": (
            "Include frameworks mentioned in the job description — "
            "for example React, Django, Spring, or Node.js."
        ),
        "databases": (
            "Highlight database experience. Mention specific databases "
            "(PostgreSQL, MongoDB, Redis) and any query-optimisation work."
        ),
        "cloud": (
            "Add cloud platform experience (AWS, Azure, GCP). "
            "Mention specific services you have used, such as S3, EC2, Lambda, "
            "or Cloud Functions."
        ),
        "devops": (
            "Include DevOps and CI/CD experience. Mention Docker, Kubernetes, "
            "Jenkins, GitHub Actions, Terraform, or similar tools."
        ),
        "tools": (
            "List developer tools you use daily — Git, Postman, VS Code, "
            "Linux, etc. These are easy wins for ATS keyword matching."
        ),
        "data_and_ml": (
            "Mention data and ML tools relevant to the role — "
            "pandas, TensorFlow, scikit-learn, Spark, or Tableau."
        ),
        "concepts": (
            "Reference software-engineering concepts from the JD — "
            "REST APIs, microservices, system design, Agile, or TDD."
        ),
    }

    @staticmethod
    def generate_suggestions(
        missing_keywords: list[str],
        resume_sections: dict[str, bool],
        ats_score: int,
        skill_gap: dict | None = None,
        impact_count: int = 0,
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
                "This helps recruiters and ATS parsers quickly identify your profile."
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
                'Add quantified achievements — for example, '
                '"Improved API response time by 40%" or '
                '"Reduced deployment time from 2 hours to 15 minutes". '
                "Metrics make your resume more compelling to both ATS and humans."
            )

        # ---- 5. Score-tier advice ----
        if ats_score < 40:
            suggestions.append(
                "Your resume has low alignment with this job description. "
                "Consider tailoring it specifically for this role — "
                "mirror the language and keywords from the job posting."
            )
        elif ats_score < 60:
            suggestions.append(
                "Your resume partially matches the job description. "
                "Focus on the missing keywords and try to add them "
                "in context within your experience bullets."
            )
        elif ats_score < 80:
            suggestions.append(
                "Good alignment — fine-tune by incorporating a few more "
                "missing keywords and strengthening quantified achievements."
            )

        # ---- 6. Cloud / DevOps nudge ----
        if skill_gap:
            cloud_missing = skill_gap.get("cloud", {}).get("missing_skills", [])
            devops_missing = skill_gap.get("devops", {}).get("missing_skills", [])
            if cloud_missing and "cloud" not in [s[:5] for s in suggestions]:
                suggestions.append(
                    "Cloud skills are increasingly expected. "
                    f"Consider adding: {', '.join(cloud_missing[:3])}."
                )
            if devops_missing and "devops" not in [s[:6] for s in suggestions]:
                suggestions.append(
                    "DevOps experience is highly valued. "
                    f"Consider learning: {', '.join(devops_missing[:3])}."
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
    ) -> list[str]:
        """Suggestions for the no-JD resume-strength mode (Feature 6)."""
        suggestions: list[str] = []

        for w in weaknesses:
            suggestions.append(f"Weakness identified: {w}.")

        if impact_count < 2:
            suggestions.append(
                'Add measurable achievements — e.g., '
                '"Reduced infrastructure costs by 30%" or '
                '"Served 10K daily active users".'
            )

        if not resume_sections.get("summary"):
            suggestions.append(
                "Start with a concise Professional Summary to give "
                "recruiters an immediate snapshot of your strengths."
            )

        return suggestions
