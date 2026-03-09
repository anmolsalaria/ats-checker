"""Suggestion generation service for resume improvements."""

import logging

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Generates actionable improvement suggestions based on analysis results."""

    # Category-based suggestion templates
    KEYWORD_SUGGESTIONS = {
        "cloud": (
            "Add cloud platform experience (AWS, Azure, GCP). "
            "Include specific services you've used, such as S3, EC2, Lambda, "
            "or Cloud Functions."
        ),
        "containerization": (
            "Include containerization skills like Docker and Kubernetes. "
            "Mention orchestration tools and CI/CD pipeline experience."
        ),
        "database": (
            "Highlight database experience. Mention specific databases "
            "(PostgreSQL, MongoDB, Redis) and query optimization skills."
        ),
        "testing": (
            "Add testing methodologies — unit testing, integration testing, "
            "TDD, or BDD. Mention frameworks like Jest, PyTest, or JUnit."
        ),
        "devops": (
            "Include DevOps and CI/CD experience. Mention tools like "
            "Jenkins, GitHub Actions, GitLab CI, or Terraform."
        ),
        "agile": (
            "Mention Agile/Scrum experience. Include sprint planning, "
            "retrospectives, or tools like Jira and Confluence."
        ),
    }

    CATEGORY_KEYWORDS = {
        "cloud": {"aws", "azure", "gcp", "cloud", "lambda", "s3", "ec2"},
        "containerization": {"docker", "kubernetes", "k8s", "container", "helm"},
        "database": {"sql", "postgresql", "mysql", "mongodb", "redis", "database"},
        "testing": {"testing", "unit test", "tdd", "bdd", "pytest", "jest", "junit"},
        "devops": {"ci/cd", "jenkins", "terraform", "ansible", "devops", "github actions"},
        "agile": {"agile", "scrum", "sprint", "jira", "kanban"},
    }

    @staticmethod
    def generate_suggestions(
        missing_keywords: list[str],
        resume_sections: dict[str, bool],
        ats_score: int,
        skill_gap: dict | None = None,
    ) -> list[str]:
        """Generate improvement suggestions.

        Args:
            missing_keywords: Keywords not found in the resume.
            resume_sections: Detected sections in the resume.
            ats_score: Current ATS score.
            skill_gap: Skill gap analysis results.

        Returns:
            List of actionable suggestion strings.
        """
        suggestions: list[str] = []

        # 1. Missing keyword category suggestions
        missing_lower = {kw.lower() for kw in missing_keywords}
        suggested_categories: set[str] = set()

        for category, keywords in SuggestionEngine.CATEGORY_KEYWORDS.items():
            if keywords & missing_lower:
                suggested_categories.add(category)
                suggestions.append(SuggestionEngine.KEYWORD_SUGGESTIONS[category])

        # 2. Generic missing keyword suggestion
        if missing_keywords and len(missing_keywords) > 3:
            top_missing = missing_keywords[:5]
            suggestions.append(
                f"Add these high-priority keywords to your resume: "
                f"{', '.join(top_missing)}. Incorporate them naturally in your "
                f"experience and skills sections."
            )

        # 3. Resume section suggestions
        if not resume_sections.get("summary"):
            suggestions.append(
                "Add a professional summary or objective at the top of your resume. "
                "This helps recruiters quickly understand your profile and improves "
                "ATS keyword matching."
            )

        if not resume_sections.get("skills"):
            suggestions.append(
                "Add a dedicated 'Skills' section listing your technical and soft "
                "skills. This is one of the most important sections for ATS parsing."
            )

        if not resume_sections.get("projects"):
            suggestions.append(
                "Consider adding a 'Projects' section to showcase practical "
                "experience and relevant work beyond your job history."
            )

        if not resume_sections.get("certifications"):
            suggestions.append(
                "If you have relevant certifications, add a 'Certifications' "
                "section. Certifications can significantly boost ATS scores for "
                "roles that require them."
            )

        # 4. Score-based suggestions
        if ats_score < 40:
            suggestions.append(
                "Your resume has low alignment with this job description. "
                "Consider tailoring your resume specifically for this role by "
                "mirroring the language and keywords used in the job posting."
            )

        if ats_score < 60:
            suggestions.append(
                "Use measurable achievements with numbers and metrics "
                "(e.g., 'Reduced API response time by 40%' or "
                "'Managed a team of 5 engineers'). Quantified results "
                "make your resume more compelling."
            )

        # 5. Skill gap suggestions
        if skill_gap:
            tech_gap = skill_gap.get("technical", {})
            if tech_gap.get("missing", 0) > 0:
                missing_tech = tech_gap.get("keywords", [])
                if missing_tech:
                    suggestions.append(
                        f"Technical skill gap detected. Consider gaining experience "
                        f"with: {', '.join(missing_tech[:5])}."
                    )

            soft_gap = skill_gap.get("soft_skills", {})
            if soft_gap.get("missing", 0) > 0:
                missing_soft = soft_gap.get("keywords", [])
                if missing_soft:
                    suggestions.append(
                        f"Soft skills gap detected. Try incorporating these "
                        f"skills into your experience descriptions: "
                        f"{', '.join(missing_soft[:5])}."
                    )

        # 6. General best practices
        suggestions.append(
            "Use a clean, ATS-friendly format — avoid tables, images, "
            "headers/footers, and complex formatting. Stick to standard "
            "section headings."
        )

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique.append(s)

        return unique
