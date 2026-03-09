"""Curated technical-skill dictionary for ATS keyword matching (Feature 2).

Skills are grouped into categories so we can produce a per-category
skill-gap analysis (Feature 5) and filter irrelevant tokens (Feature 1/4).
"""

SKILL_CATEGORIES: dict[str, list[str]] = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "php", "scala",
        "r", "matlab", "perl", "lua", "haskell", "elixir", "dart",
        "objective-c", "shell", "bash", "powershell", "sql", "nosql",
        "html", "css", "sass", "less",
    ],
    "frameworks": [
        "react", "react.js", "angular", "vue", "vue.js", "next.js",
        "nextjs", "nuxt", "nuxt.js", "svelte", "node.js", "nodejs",
        "express", "express.js", "django", "flask", "fastapi",
        "spring", "spring boot", "rails", "ruby on rails", ".net",
        "asp.net", "laravel", "symfony", "nestjs", "nest.js",
        "gatsby", "remix", "tailwindcss", "tailwind", "bootstrap",
        "material ui", "chakra ui", "jquery",
        "react native", "flutter", "electron",
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "dynamodb", "cassandra", "sqlite",
        "oracle", "mariadb", "couchdb", "neo4j", "firebase",
        "firestore", "supabase", "cockroachdb", "influxdb",
        "memcached", "mssql", "sql server",
    ],
    "cloud": [
        "aws", "amazon web services", "azure", "gcp",
        "google cloud", "heroku", "digitalocean", "vercel",
        "netlify", "cloudflare", "lambda", "s3", "ec2",
        "ecs", "eks", "rds", "sqs", "sns", "cloudformation",
        "cloud run", "app engine", "bigquery",
    ],
    "devops": [
        "docker", "kubernetes", "k8s", "terraform", "ansible",
        "jenkins", "ci/cd", "github actions", "gitlab ci",
        "circleci", "travis ci", "argo cd", "helm",
        "prometheus", "grafana", "datadog", "new relic",
        "nginx", "apache", "caddy", "linux",
        "vagrant", "puppet", "chef", "packer",
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket",
        "jira", "confluence", "notion", "trello",
        "postman", "insomnia", "swagger", "openapi",
        "figma", "sketch", "adobe xd",
        "webpack", "vite", "babel", "eslint", "prettier",
        "npm", "yarn", "pnpm", "pip", "poetry", "conda",
        "vs code", "intellij", "vim", "neovim",
        "sentry", "splunk", "kibana",
    ],
    "data_and_ml": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "keras",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn",
        "opencv", "hugging face", "transformers",
        "data engineering", "data science", "data analysis",
        "etl", "data pipeline", "airflow", "apache airflow",
        "hadoop", "spark", "apache spark", "kafka",
        "apache kafka", "dbt", "snowflake",
        "tableau", "power bi", "looker", "metabase",
        "jupyter", "colab",
    ],
    "concepts": [
        "rest", "rest api", "graphql", "grpc", "microservices",
        "api", "websocket", "oauth", "jwt", "ssl", "tls",
        "encryption", "cybersecurity", "penetration testing",
        "data structures", "algorithms", "system design",
        "design patterns", "oop", "functional programming",
        "unit testing", "integration testing", "e2e testing",
        "tdd", "bdd", "agile", "scrum", "kanban",
        "devops", "sre", "serverless", "event driven",
    ],
}

# Build a flat lookup → category mapping for O(1) membership checks
_SKILL_TO_CATEGORY: dict[str, str] = {}
_ALL_SKILLS: set[str] = set()

for _cat, _skills in SKILL_CATEGORIES.items():
    for _skill in _skills:
        _s = _skill.lower()
        _SKILL_TO_CATEGORY[_s] = _cat
        _ALL_SKILLS.add(_s)


def get_all_skills() -> set[str]:
    """Return the full set of known skills (lowercased)."""
    return _ALL_SKILLS.copy()


def get_skill_category(skill: str) -> str | None:
    """Return the category a skill belongs to, or None."""
    return _SKILL_TO_CATEGORY.get(skill.lower())


def get_skills_in_category(category: str) -> list[str]:
    """Return all skills for a given category."""
    return SKILL_CATEGORIES.get(category, [])


SOFT_SKILLS: set[str] = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "mentoring", "presentation", "negotiation",
    "project management", "stakeholder management", "strategic planning",
    "decision making", "conflict resolution", "analytical thinking",
    "interpersonal", "attention to detail", "multitasking",
    "organizational", "self-motivated", "initiative",
}

# Words that look like nouns/keywords but are meaningless for ATS
GENERIC_STOPWORDS: set[str] = {
    "work", "task", "tasks", "process", "processes", "ability",
    "abilities", "job", "role", "position", "company", "team",
    "the", "this", "that", "these", "those", "them",
    "year", "years", "month", "months", "day", "days",
    "time", "experience", "knowledge", "understanding",
    "responsibilities", "responsibility", "requirement",
    "requirements", "qualification", "qualifications",
    "candidate", "candidates", "opportunity", "opportunities",
    "environment", "environments", "solution", "solutions",
    "development", "management", "service", "services",
    "application", "applications", "system", "systems",
    "project", "projects", "information", "technology",
    "performance", "support", "business", "enterprise",
    "enterprises", "customer", "customers", "client", "clients",
    "industry", "field", "area", "level", "type",
    "group", "member", "members", "part", "result", "results",
    "way", "end", "number", "thing", "things", "case",
    "example", "examples", "use", "order", "value",
    "state", "set", "line", "point", "form", "base",
    "name", "place", "hand", "high", "good",
    "new", "first", "last", "long", "great", "little",
    "own", "old", "right", "big", "small", "large",
    "next", "early", "young", "important", "public",
    "strong", "excellent", "preferred", "plus", "bonus",
    "etc", "including", "related", "based", "must",
    "working", "looking", "using", "building", "creating",
    "developing", "maintaining", "managing", "leading",
    "providing", "ensuring", "implementing", "delivering",
    "minimum", "maximum", "equivalent", "similar",
}
