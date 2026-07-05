-- ============================================================
-- Seed data (10 polls)
-- ============================================================

INSERT IGNORE INTO polls (id, question) VALUES
(1, 'Which container tool do you use most?'),
(2, 'Best way to learn Kubernetes?'),
(3, 'Preferred backend language?'),
(4, 'Best CI/CD tool?'),
(5, 'Which cloud provider do you use?'),
(6, 'What do you use for frontend development?'),
(7, 'Best database for production apps?'),
(8, 'Preferred Linux distribution?'),
(9, 'What do you use for monitoring?'),
(10, 'Best API style for microservices?');

INSERT IGNORE INTO poll_options (id, poll_id, option_text, votes) VALUES

-- Poll 1
(1, 1, 'Docker', 20),
(2, 1, 'Podman', 8),
(3, 1, 'containerd', 5),

-- Poll 2
(4, 2, 'kind / minikube practice', 25),
(5, 2, 'Official docs', 12),
(6, 2, 'YouTube tutorials', 18),

-- Poll 3
(7, 3, 'Python (FastAPI/Flask)', 22),
(8, 3, 'Node.js (Express)', 19),
(9, 3, 'Go (Gin/Fiber)', 27),
(10, 3, 'Java (Spring Boot)', 14),

-- Poll 4
(11, 4, 'Jenkins', 18),
(12, 4, 'GitHub Actions', 30),
(13, 4, 'GitLab CI', 12),
(14, 4, 'Argo CD', 10),

-- Poll 5
(15, 5, 'AWS', 35),
(16, 5, 'Azure', 20),
(17, 5, 'Google Cloud', 18),
(18, 5, 'On-prem', 7),

-- Poll 6
(19, 6, 'React', 40),
(20, 6, 'Vue', 15),
(21, 6, 'Angular', 12),
(22, 6, 'Svelte', 8),

-- Poll 7
(23, 7, 'PostgreSQL', 38),
(24, 7, 'MySQL', 25),
(25, 7, 'MongoDB', 22),
(26, 7, 'Redis', 10),

-- Poll 8
(27, 8, 'Ubuntu', 45),
(28, 8, 'Debian', 20),
(29, 8, 'CentOS / Rocky', 15),
(30, 8, 'Arch Linux', 12),

-- Poll 9
(31, 9, 'Prometheus + Grafana', 50),
(32, 9, 'ELK Stack', 22),
(33, 9, 'Datadog', 18),
(34, 9, 'New Relic', 10),

-- Poll 10
(35, 10, 'REST APIs', 42),
(36, 10, 'GraphQL', 20),
(37, 10, 'gRPC', 18),
(38, 10, 'WebSockets', 12);
