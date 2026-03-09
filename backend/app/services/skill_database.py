"""Curated technical-skill dictionary for ATS keyword matching (Feature 2).

Skills are grouped into categories so we can produce a per-category
skill-gap analysis and filter irrelevant tokens.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Category -> skill list
# ---------------------------------------------------------------------------
SKILL_CATEGORIES: dict[str, list[str]] = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "php", "scala",
        "r", "matlab", "perl", "lua", "haskell", "elixir", "dart",
        "objective-c", "shell", "bash", "powershell", "sql", "nosql",
        "html", "css", "sass", "less", "groovy", "clojure", "fortran",
        "cobol", "assembly", "solidity", "zig", "nim",
    ],
    "frameworks": [
        "react", "react.js", "angular", "vue", "vue.js", "next.js",
        "nextjs", "nuxt", "nuxt.js", "svelte", "sveltekit", "node.js",
        "nodejs", "express", "express.js", "django", "flask", "fastapi",
        "spring", "spring boot", "rails", "ruby on rails", ".net",
        "asp.net", "laravel", "symfony", "nestjs", "nest.js",
        "gatsby", "remix", "tailwindcss", "tailwind", "bootstrap",
        "material ui", "chakra ui", "jquery", "backbone.js",
        "react native", "flutter", "electron", "ionic", "xamarin",
        "blazor", "gin", "echo", "fiber", "actix", "rocket",
        "phoenix", "ktor", "micronaut", "quarkus", "hapi",
        "koa", "fastify", "starlette", "tornado",
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "dynamodb", "cassandra", "sqlite",
        "oracle", "mariadb", "couchdb", "neo4j", "firebase",
        "firestore", "supabase", "cockroachdb", "influxdb",
        "memcached", "mssql", "sql server", "arangodb",
        "clickhouse", "timescaledb", "fauna", "planetscale",
    ],
    "cloud": [
        "aws", "amazon web services", "azure", "gcp",
        "google cloud", "heroku", "digitalocean", "vercel",
        "netlify", "cloudflare", "lambda", "s3", "ec2",
        "ecs", "eks", "rds", "sqs", "sns", "cloudformation",
        "cloud run", "app engine", "bigquery", "cloud functions",
        "azure functions", "azure devops", "fargate",
        "api gateway", "step functions", "kinesis",
        "elastic beanstalk", "lightsail", "amplify",
    ],
    "devops": [
        "docker", "kubernetes", "k8s", "terraform", "ansible",
        "jenkins", "ci/cd", "github actions", "gitlab ci",
        "circleci", "travis ci", "argo cd", "helm",
        "prometheus", "grafana", "datadog", "new relic",
        "nginx", "apache", "caddy", "linux",
        "vagrant", "puppet", "chef", "packer",
        "pulumi", "argocd", "flux", "istio", "linkerd",
        "envoy", "consul", "vault", "sonarqube",
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket",
        "jira", "confluence", "notion", "trello", "asana",
        "postman", "insomnia", "swagger", "openapi",
        "figma", "sketch", "adobe xd",
        "webpack", "vite", "babel", "eslint", "prettier",
        "npm", "yarn", "pnpm", "pip", "poetry", "conda",
        "vs code", "intellij", "vim", "neovim",
        "sentry", "splunk", "kibana", "logstash",
        "slack", "linear", "clickup", "monday",
    ],
    "data_ml": [
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
        "jupyter", "colab", "mlflow", "kubeflow",
        "feature engineering", "model training",
        "reinforcement learning", "generative ai",
        "langchain", "llm", "rag", "fine-tuning",
        "stable diffusion", "gpt", "bert", "xgboost",
        "lightgbm", "catboost", "random forest",
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
        "domain driven design", "clean architecture",
        "solid principles", "mvc", "mvvm",
        "caching", "load balancing", "sharding",
        "replication", "message queue", "pub/sub",
        "distributed systems", "cap theorem",
        "concurrency", "multithreading", "async programming",
    ],
}

# ---------------------------------------------------------------------------
# Flat lookups (O(1) membership checks)
# ---------------------------------------------------------------------------
_SKILL_TO_CATEGORY: dict[str, str] = {}
_ALL_SKILLS: set[str] = set()

for _cat, _skills in SKILL_CATEGORIES.items():
    for _skill in _skills:
        _s = _skill.lower()
        _SKILL_TO_CATEGORY[_s] = _cat
        _ALL_SKILLS.add(_s)


def get_all_skills() -> set[str]:
    return _ALL_SKILLS.copy()


def get_skill_category(skill: str) -> str | None:
    return _SKILL_TO_CATEGORY.get(skill.lower())


def get_skills_in_category(category: str) -> list[str]:
    return SKILL_CATEGORIES.get(category, [])


# ---------------------------------------------------------------------------
# Soft skills
# ---------------------------------------------------------------------------
SOFT_SKILLS: set[str] = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "mentoring", "presentation", "negotiation",
    "project management", "stakeholder management", "strategic planning",
    "decision making", "conflict resolution", "analytical thinking",
    "interpersonal", "attention to detail", "multitasking",
    "organizational", "self-motivated", "initiative",
    "public speaking", "customer service", "cross-functional",
    "team building", "emotional intelligence", "delegation",
}

# ---------------------------------------------------------------------------
# Action verbs (Feature 5)
# ---------------------------------------------------------------------------
STRONG_ACTION_VERBS: set[str] = {
    "achieved", "administered", "advanced", "analyzed", "architected",
    "automated", "boosted", "built", "collaborated", "configured",
    "consolidated", "contributed", "coordinated", "created", "customized",
    "debugged", "decreased", "delivered", "deployed", "designed",
    "developed", "devised", "directed", "drove", "eliminated",
    "enabled", "engineered", "enhanced", "established", "evaluated",
    "executed", "expanded", "expedited", "facilitated", "formulated",
    "generated", "grew", "guided", "headed", "identified",
    "implemented", "improved", "increased", "initiated", "innovated",
    "integrated", "introduced", "launched", "led", "leveraged",
    "maintained", "managed", "maximized", "mentored", "migrated",
    "minimized", "modernized", "monitored", "negotiated", "operated",
    "optimized", "orchestrated", "organized", "overhauled", "owned",
    "partnered", "performed", "pioneered", "planned", "produced",
    "programmed", "promoted", "proposed", "prototyped", "provisioned",
    "published", "rebuilt", "recommended", "redesigned", "reduced",
    "refactored", "refined", "released", "remediated", "replaced",
    "resolved", "restructured", "revamped", "reviewed", "scaled",
    "secured", "simplified", "solved", "spearheaded", "standardized",
    "streamlined", "strengthened", "supervised", "surpassed",
    "tested", "trained", "transformed", "transitioned", "troubleshot",
    "unified", "upgraded", "utilized", "validated", "visualized",
}

WEAK_VERBS: set[str] = {
    "did", "made", "got", "went", "used", "had", "was",
    "worked", "helped", "assisted", "participated", "responsible",
    "involved", "handled", "dealt", "tasked", "supported",
}

# ---------------------------------------------------------------------------
# Role keywords for job-role detection (Feature 7)
# ---------------------------------------------------------------------------
ROLE_KEYWORDS: dict[str, list[str]] = {
    "Backend Engineer": [
        "backend", "server-side", "api", "rest api", "microservices",
        "database", "sql", "nosql", "python", "java", "go", "node.js",
        "fastapi", "django", "flask", "spring", "express",
    ],
    "Frontend Engineer": [
        "frontend", "front-end", "ui", "ux", "react", "angular", "vue",
        "javascript", "typescript", "html", "css", "tailwind",
        "responsive", "web application", "single page",
    ],
    "Full-Stack Developer": [
        "full-stack", "full stack", "fullstack", "frontend", "backend",
        "react", "node.js", "api", "database", "end-to-end",
    ],
    "Machine Learning Engineer": [
        "machine learning", "deep learning", "ml", "ai",
        "tensorflow", "pytorch", "model training", "neural network",
        "nlp", "computer vision", "data pipeline", "feature engineering",
    ],
    "Data Engineer": [
        "data engineering", "data pipeline", "etl", "data warehouse",
        "spark", "kafka", "airflow", "hadoop", "snowflake", "dbt",
        "bigquery", "data lake", "batch processing", "streaming",
    ],
    "Data Scientist": [
        "data science", "data analysis", "statistics", "machine learning",
        "pandas", "numpy", "visualization", "hypothesis testing",
        "a/b testing", "predictive modeling", "jupyter",
    ],
    "DevOps Engineer": [
        "devops", "ci/cd", "docker", "kubernetes", "terraform",
        "infrastructure", "deployment", "monitoring", "sre",
        "aws", "azure", "gcp", "linux", "automation",
    ],
    "Cloud Engineer": [
        "cloud", "aws", "azure", "gcp", "infrastructure",
        "cloud architecture", "serverless", "lambda", "ec2",
        "cloud migration", "iac", "terraform",
    ],
    "Mobile Developer": [
        "mobile", "ios", "android", "react native", "flutter",
        "swift", "kotlin", "mobile application", "app store",
    ],
    "Security Engineer": [
        "security", "cybersecurity", "penetration testing", "vulnerability",
        "encryption", "authentication", "oauth", "ssl", "firewall",
        "soc", "siem", "incident response",
    ],
    "QA Engineer": [
        "qa", "quality assurance", "testing", "test automation",
        "selenium", "cypress", "jest", "unit testing", "e2e testing",
        "test cases", "regression", "load testing",
    ],
    "Site Reliability Engineer": [
        "sre", "reliability", "monitoring", "incident", "on-call",
        "observability", "prometheus", "grafana", "alerting",
        "uptime", "latency", "error budget",
    ],
    "Software Engineer": [
        "software engineer", "software developer", "programming",
        "coding", "software development", "application development",
    ],
}

# ---------------------------------------------------------------------------
# Generic stopwords — must NEVER appear as extracted keywords
# ---------------------------------------------------------------------------
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
    "also", "well", "will", "may", "can", "need", "like",
    "want", "know", "take", "make", "come", "give",
    "look", "find", "think", "tell", "become", "leave",
    "feel", "seem", "show", "keep", "let", "begin",
    "world", "life", "head", "face", "change", "much",
    "able", "key", "top", "best", "real", "full",
    "sweat", "vibe", "flow", "massive", "highway", "highways",
}
