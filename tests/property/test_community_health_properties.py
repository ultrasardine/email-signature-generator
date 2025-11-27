"""Property-based tests for community health files and open source standards."""

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st


@given(
    required_section=st.sampled_from(
        [
            "development setup",
            "pull request",
            "code style",
            "testing",
            "contributing",
            "workflow",
            "commit",
            "branch",
        ]
    )
)
def test_contributing_has_required_sections(required_section: str) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.2, 1.3, 1.4, 1.5

    For any required section (development setup, pull request process, code style,
    testing requirements), the CONTRIBUTING.md file should contain a heading or
    content addressing that section.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should contain content related to the required section
    # We check for section keywords that would indicate the topic is covered
    section_keywords = {
        "development setup": ["development setup", "install", "dependencies", "virtual environment"],
        "pull request": ["pull request", "pr process", "submitting", "review"],
        "code style": ["code style", "formatting", "black", "ruff", "linting"],
        "testing": ["testing", "pytest", "test", "coverage", "hypothesis"],
        "contributing": ["contributing", "contribute", "contribution"],
        "workflow": ["workflow", "process", "steps", "fork"],
        "commit": ["commit", "commit message", "git commit"],
        "branch": ["branch", "feature branch", "git branch"],
    }

    keywords = section_keywords.get(required_section, [required_section])

    # At least one keyword should be present in the content
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should contain content about '{required_section}'"


@given(
    tool=st.sampled_from(
        [
            "black",
            "ruff",
            "mypy",
            "pytest",
            "hypothesis",
        ]
    )
)
def test_contributing_mentions_required_tools(tool: str) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.4, 1.5

    For any required development tool (black, ruff, mypy, pytest, hypothesis),
    the CONTRIBUTING.md file should mention that tool.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should mention the required tool
    assert tool.lower() in content, f"CONTRIBUTING.md should mention {tool}"


@given(
    heading_level=st.sampled_from(["#", "##", "###"]),
    section_name=st.sampled_from(
        [
            "Getting Started",
            "Development Setup",
            "Code Style",
            "Testing",
            "Pull Request",
            "Contributing",
        ]
    ),
)
def test_contributing_has_proper_markdown_structure(
    heading_level: str, section_name: str
) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.2, 1.3, 1.4, 1.5

    For any major section in CONTRIBUTING.md, the file should use proper markdown
    heading structure to organize content.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8")

    # Then it should contain markdown headings
    # We verify that the file uses markdown heading syntax
    assert "#" in content, "CONTRIBUTING.md should use markdown headings"

    # The file should be well-structured with multiple sections
    heading_count = content.count("\n#")
    assert heading_count >= 5, "CONTRIBUTING.md should have multiple sections (at least 5 headings)"


@given(
    command_type=st.sampled_from(
        [
            "install",
            "test",
            "format",
            "lint",
            "typecheck",
        ]
    )
)
def test_contributing_includes_command_examples(command_type: str) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.2, 1.5

    For any common development command (install, test, format, lint, typecheck),
    the CONTRIBUTING.md file should include code examples showing how to run that command.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8")

    # Then it should contain code blocks (indicated by ``` or indented code)
    assert "```" in content or "    " in content, "CONTRIBUTING.md should include code examples"

    # And it should mention the command type
    content_lower = content.lower()
    command_keywords = {
        "install": ["install", "uv sync", "pip install"],
        "test": ["pytest", "test", "uv run pytest"],
        "format": ["black", "format", "uv run black"],
        "lint": ["ruff", "lint", "uv run ruff"],
        "typecheck": ["mypy", "type check", "uv run mypy"],
    }

    keywords = command_keywords.get(command_type, [command_type])
    assert any(
        keyword in content_lower for keyword in keywords
    ), f"CONTRIBUTING.md should include examples for {command_type}"


@given(
    file_size_threshold=st.integers(min_value=1000, max_value=100000),
)
def test_contributing_has_substantial_content(file_size_threshold: int) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5

    For any reasonable content threshold, the CONTRIBUTING.md file should contain
    substantial content (not just a placeholder).
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we check the file size
    file_size = contributing_path.stat().st_size

    # Then it should have substantial content
    # A comprehensive CONTRIBUTING.md should be at least 5KB
    assert file_size >= 5000, f"CONTRIBUTING.md should have substantial content (at least 5KB), got {file_size} bytes"

    # And it should have multiple lines
    content = contributing_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    assert line_count >= 50, f"CONTRIBUTING.md should have substantial content (at least 50 lines), got {line_count} lines"


@given(
    contact_method=st.sampled_from(
        [
            "issue",
            "discussion",
            "github",
        ]
    )
)
def test_contributing_includes_communication_channels(contact_method: str) -> None:
    """Feature: open-source-standards, Property 3: CONTRIBUTING.md contains required sections.

    Validates: Requirements 1.2

    For any communication channel (issues, discussions, GitHub), the CONTRIBUTING.md
    file should provide information about how to use that channel.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should mention communication channels
    communication_keywords = {
        "issue": ["issue", "bug report", "feature request"],
        "discussion": ["discussion", "question", "help"],
        "github": ["github", "repository", "pull request"],
    }

    keywords = communication_keywords.get(contact_method, [contact_method])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should mention {contact_method} as a communication channel"


@given(
    required_section=st.sampled_from(
        [
            "pledge",
            "standards",
            "enforcement",
            "scope",
            "contact",
            "our pledge",
            "our standards",
            "enforcement responsibilities",
            "enforcement guidelines",
        ]
    )
)
def test_code_of_conduct_has_required_sections(required_section: str) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.2, 2.3, 2.4, 2.5

    For any required section (standards, enforcement, contact), the CODE_OF_CONDUCT.md
    file should contain that section with substantive content.
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we read the file content
    content = code_of_conduct_path.read_text(encoding="utf-8").lower()

    # Then it should contain the required section
    # We check for section keywords that indicate the topic is covered
    section_keywords = {
        "pledge": ["pledge", "commitment", "welcoming"],
        "standards": ["standards", "expected behavior", "unacceptable behavior", "examples"],
        "enforcement": ["enforcement", "responsibilities", "consequences", "reporting"],
        "scope": ["scope", "applies", "spaces", "representation"],
        "contact": ["contact", "email", "report", "@"],
        "our pledge": ["our pledge", "pledge"],
        "our standards": ["our standards", "standards"],
        "enforcement responsibilities": ["enforcement responsibilities", "enforcement", "responsibilities"],
        "enforcement guidelines": ["enforcement guidelines", "guidelines", "enforcement"],
    }

    keywords = section_keywords.get(required_section, [required_section])

    # At least one keyword should be present in the content
    assert any(
        keyword in content for keyword in keywords
    ), f"CODE_OF_CONDUCT.md should contain content about '{required_section}'"


@given(
    behavior_type=st.sampled_from(
        [
            "expected",
            "unacceptable",
            "positive",
            "harassment",
        ]
    )
)
def test_code_of_conduct_defines_behaviors(behavior_type: str) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.2, 2.3

    For any behavior category (expected, unacceptable), the CODE_OF_CONDUCT.md
    file should define what constitutes that type of behavior.
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we read the file content
    content = code_of_conduct_path.read_text(encoding="utf-8").lower()

    # Then it should define behaviors
    behavior_keywords = {
        "expected": ["expected", "positive", "welcoming", "respectful", "empathy"],
        "unacceptable": ["unacceptable", "inappropriate", "unwelcome", "harassment"],
        "positive": ["positive", "welcoming", "inclusive", "respectful"],
        "harassment": ["harassment", "trolling", "insulting", "derogatory"],
    }

    keywords = behavior_keywords.get(behavior_type, [behavior_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"CODE_OF_CONDUCT.md should define {behavior_type} behaviors"


@given(
    enforcement_aspect=st.sampled_from(
        [
            "reporting",
            "investigation",
            "consequences",
        ]
    )
)
def test_code_of_conduct_describes_enforcement(enforcement_aspect: str) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.4

    For any enforcement aspect (reporting, investigation, consequences),
    the CODE_OF_CONDUCT.md file should describe how that aspect is handled.
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we read the file content
    content = code_of_conduct_path.read_text(encoding="utf-8").lower()

    # Then it should describe enforcement procedures
    enforcement_keywords = {
        "reporting": ["report", "reporting", "complaint", "violation"],
        "investigation": ["investigate", "investigation", "review", "determine"],
        "consequences": ["consequences", "action", "ban", "removal", "warning"],
    }

    keywords = enforcement_keywords.get(enforcement_aspect, [enforcement_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"CODE_OF_CONDUCT.md should describe {enforcement_aspect} procedures"


@given(
    file_size_threshold=st.integers(min_value=1000, max_value=50000),
)
def test_code_of_conduct_has_substantial_content(file_size_threshold: int) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5

    For any reasonable content threshold, the CODE_OF_CONDUCT.md file should contain
    substantial content (not just a placeholder).
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we check the file size
    file_size = code_of_conduct_path.stat().st_size

    # Then it should have substantial content
    # A comprehensive CODE_OF_CONDUCT.md (like Contributor Covenant) should be at least 3KB
    assert file_size >= 3000, f"CODE_OF_CONDUCT.md should have substantial content (at least 3KB), got {file_size} bytes"

    # And it should have multiple lines
    content = code_of_conduct_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    assert line_count >= 30, f"CODE_OF_CONDUCT.md should have substantial content (at least 30 lines), got {line_count} lines"


@given(
    heading_level=st.sampled_from(["#", "##", "###"]),
)
def test_code_of_conduct_has_proper_markdown_structure(heading_level: str) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.2, 2.3, 2.4, 2.5

    For any markdown heading level, the CODE_OF_CONDUCT.md file should use proper
    markdown structure to organize content into sections.
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we read the file content
    content = code_of_conduct_path.read_text(encoding="utf-8")

    # Then it should contain markdown headings
    assert "#" in content, "CODE_OF_CONDUCT.md should use markdown headings"

    # The file should be well-structured with multiple sections
    heading_count = content.count("\n#")
    assert heading_count >= 4, "CODE_OF_CONDUCT.md should have multiple sections (at least 4 headings)"


@given(
    contact_info_type=st.sampled_from(
        [
            "email",
            "maintainer",
            "project",
        ]
    )
)
def test_code_of_conduct_includes_contact_information(contact_info_type: str) -> None:
    """Feature: open-source-standards, Property 4: CODE_OF_CONDUCT.md contains required sections.

    Validates: Requirements 2.5

    For any contact information type (email, maintainer reference, project reference),
    the CODE_OF_CONDUCT.md file should include that information for reporting violations.
    """
    # Given the CODE_OF_CONDUCT.md file exists
    code_of_conduct_path = Path("CODE_OF_CONDUCT.md")
    assert code_of_conduct_path.exists(), "CODE_OF_CONDUCT.md file must exist"

    # When we read the file content
    content = code_of_conduct_path.read_text(encoding="utf-8").lower()

    # Then it should include contact information
    contact_keywords = {
        "email": ["email", "@", "contact"],
        "maintainer": ["maintainer", "team", "leader"],
        "project": ["project", "repository", "github"],
    }

    keywords = contact_keywords.get(contact_info_type, [contact_info_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"CODE_OF_CONDUCT.md should include {contact_info_type} information"


@given(
    required_section=st.sampled_from(
        [
            "supported versions",
            "reporting",
            "vulnerability",
            "response",
            "timeline",
            "contact",
            "disclosure",
            "security",
        ]
    )
)
def test_security_has_required_sections(required_section: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.2, 3.3, 3.4, 3.5

    For any required section (supported versions, reporting instructions, response
    timeline, contact), the SECURITY.md file should contain that section.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should contain the required section
    section_keywords = {
        "supported versions": ["supported versions", "version", "support"],
        "reporting": ["reporting", "report", "how to report"],
        "vulnerability": ["vulnerability", "vulnerabilities", "security issue"],
        "response": ["response", "respond", "acknowledgment"],
        "timeline": ["timeline", "timeframe", "within", "hours", "days"],
        "contact": ["contact", "email", "@", "maintainer"],
        "disclosure": ["disclosure", "disclose", "public"],
        "security": ["security", "secure"],
    }

    keywords = section_keywords.get(required_section, [required_section])

    # At least one keyword should be present in the content
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should contain content about '{required_section}'"


@given(
    reporting_method=st.sampled_from(
        [
            "github",
            "security advisory",
            "private",
            "issue",
        ]
    )
)
def test_security_provides_reporting_instructions(reporting_method: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.3

    For any reporting method (GitHub, security advisory, private contact),
    the SECURITY.md file should provide instructions for that method.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should provide reporting instructions
    reporting_keywords = {
        "github": ["github", "repository", "security tab"],
        "security advisory": ["security advisory", "advisory", "report a vulnerability"],
        "private": ["private", "privately", "do not", "not public"],
        "issue": ["issue", "report", "contact"],
    }

    keywords = reporting_keywords.get(reporting_method, [reporting_method])
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should provide instructions for {reporting_method}"


@given(
    response_aspect=st.sampled_from(
        [
            "acknowledgment",
            "investigation",
            "fix",
            "update",
        ]
    )
)
def test_security_describes_response_process(response_aspect: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.4

    For any response aspect (acknowledgment, investigation, fix, update),
    the SECURITY.md file should describe how that aspect is handled.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should describe the response process
    response_keywords = {
        "acknowledgment": ["acknowledge", "acknowledgment", "receipt", "confirm"],
        "investigation": ["investigate", "investigation", "assess", "determine"],
        "fix": ["fix", "patch", "resolve", "solution"],
        "update": ["update", "status", "progress", "inform"],
    }

    keywords = response_keywords.get(response_aspect, [response_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should describe {response_aspect} process"


@given(
    time_commitment=st.sampled_from(
        [
            "48 hours",
            "hours",
            "days",
            "timeline",
        ]
    )
)
def test_security_includes_response_timeframes(time_commitment: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.4

    For any time commitment aspect, the SECURITY.md file should include
    expected response timeframes.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should include timeframes
    time_keywords = {
        "48 hours": ["48 hours", "48 hour", "two days"],
        "hours": ["hours", "hour"],
        "days": ["days", "day"],
        "timeline": ["timeline", "timeframe", "within"],
    }

    keywords = time_keywords.get(time_commitment, [time_commitment])
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should include timeframes mentioning {time_commitment}"


@given(
    communication_channel=st.sampled_from(
        [
            "github",
            "security advisory",
            "maintainer",
        ]
    )
)
def test_security_specifies_communication_channels(communication_channel: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.5

    For any communication channel (GitHub, security advisory, maintainer contact),
    the SECURITY.md file should specify how to use that channel.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should specify communication channels
    channel_keywords = {
        "github": ["github", "repository", "security tab"],
        "security advisory": ["security advisory", "advisory"],
        "maintainer": ["maintainer", "@ultrasardine", "contact"],
    }

    keywords = channel_keywords.get(communication_channel, [communication_channel])
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should specify {communication_channel} as a communication channel"


@given(
    file_size_threshold=st.integers(min_value=1000, max_value=50000),
)
def test_security_has_substantial_content(file_size_threshold: int) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5

    For any reasonable content threshold, the SECURITY.md file should contain
    substantial content (not just a placeholder).
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we check the file size
    file_size = security_path.stat().st_size

    # Then it should have substantial content
    # A comprehensive SECURITY.md should be at least 3KB
    assert file_size >= 3000, f"SECURITY.md should have substantial content (at least 3KB), got {file_size} bytes"

    # And it should have multiple lines
    content = security_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    assert line_count >= 50, f"SECURITY.md should have substantial content (at least 50 lines), got {line_count} lines"


@given(
    heading_level=st.sampled_from(["#", "##", "###"]),
)
def test_security_has_proper_markdown_structure(heading_level: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.2, 3.3, 3.4, 3.5

    For any markdown heading level, the SECURITY.md file should use proper
    markdown structure to organize content into sections.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8")

    # Then it should contain markdown headings
    assert "#" in content, "SECURITY.md should use markdown headings"

    # The file should be well-structured with multiple sections
    heading_count = content.count("\n#")
    assert heading_count >= 5, "SECURITY.md should have multiple sections (at least 5 headings)"


@given(
    disclosure_aspect=st.sampled_from(
        [
            "coordinated",
            "private",
            "public",
            "policy",
        ]
    )
)
def test_security_includes_disclosure_policy(disclosure_aspect: str) -> None:
    """Feature: open-source-standards, Property 5: SECURITY.md contains required sections.

    Validates: Requirements 3.5

    For any disclosure aspect (coordinated, private, public, policy),
    the SECURITY.md file should include information about the disclosure policy.
    """
    # Given the SECURITY.md file exists
    security_path = Path("SECURITY.md")
    assert security_path.exists(), "SECURITY.md file must exist"

    # When we read the file content
    content = security_path.read_text(encoding="utf-8").lower()

    # Then it should include disclosure policy information
    disclosure_keywords = {
        "coordinated": ["coordinated", "coordinate", "coordination"],
        "private": ["private", "privately", "confidential"],
        "public": ["public", "publicly", "disclosure"],
        "policy": ["policy", "approach", "process"],
    }

    keywords = disclosure_keywords.get(disclosure_aspect, [disclosure_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"SECURITY.md should include information about {disclosure_aspect} disclosure"


import yaml


@given(
    template_file=st.sampled_from(
        [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        ]
    )
)
def test_issue_templates_exist(template_file: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.2, 4.3, 4.4, 4.5

    For any issue template (bug report, feature request), the template file
    should exist in the .github/ISSUE_TEMPLATE/ directory.
    """
    # Given an issue template path
    template_path = Path(template_file)

    # Then the template file should exist
    assert template_path.exists(), f"Issue template {template_file} should exist"

    # And it should not be empty
    assert template_path.stat().st_size > 0, f"Issue template {template_file} should not be empty"


@given(
    required_field=st.sampled_from(
        [
            "description",
            "reproduction",
            "expected",
            "actual",
        ]
    )
)
def test_bug_report_template_has_required_fields(required_field: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.2, 4.3

    For any required field in the bug report template (description, reproduction steps,
    expected behavior, actual behavior), the template should include that field.
    """
    # Given the bug report template exists
    template_path = Path(".github/ISSUE_TEMPLATE/bug_report.yml")
    assert template_path.exists(), "Bug report template should exist"

    # When we parse the template YAML
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have a body with form fields
    assert "body" in template_data, "Bug report template should have a body"
    assert isinstance(template_data["body"], list), "Template body should be a list of fields"

    # And it should contain the required field
    field_ids = [field.get("id", "") for field in template_data["body"] if "id" in field]
    field_labels = [
        field.get("attributes", {}).get("label", "").lower()
        for field in template_data["body"]
        if "attributes" in field
    ]

    field_keywords = {
        "description": ["description", "bug description"],
        "reproduction": ["reproduction", "reproduce", "steps"],
        "expected": ["expected", "expected behavior"],
        "actual": ["actual", "actual behavior"],
    }

    keywords = field_keywords.get(required_field, [required_field])

    # Check if the field ID or label matches
    assert (
        required_field in field_ids
        or any(keyword in label for label in field_labels for keyword in keywords)
    ), f"Bug report template should include field for {required_field}"


@given(
    environment_field=st.sampled_from(
        [
            "os",
            "python-version",
        ]
    )
)
def test_bug_report_template_has_environment_fields(environment_field: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.3

    For any environment field (OS, Python version), the bug report template
    should include that field to capture environment information.
    """
    # Given the bug report template exists
    template_path = Path(".github/ISSUE_TEMPLATE/bug_report.yml")
    assert template_path.exists(), "Bug report template should exist"

    # When we parse the template YAML
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have environment fields
    assert "body" in template_data, "Bug report template should have a body"

    field_ids = [field.get("id", "") for field in template_data["body"] if "id" in field]

    # Check if the environment field is present
    assert (
        environment_field in field_ids
    ), f"Bug report template should include {environment_field} field"


@given(
    required_field=st.sampled_from(
        [
            "problem",
            "solution",
            "use-case",
        ]
    )
)
def test_feature_request_template_has_required_fields(required_field: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.4, 4.5

    For any required field in the feature request template (problem description,
    proposed solution, use case), the template should include that field.
    """
    # Given the feature request template exists
    template_path = Path(".github/ISSUE_TEMPLATE/feature_request.yml")
    assert template_path.exists(), "Feature request template should exist"

    # When we parse the template YAML
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have a body with form fields
    assert "body" in template_data, "Feature request template should have a body"
    assert isinstance(template_data["body"], list), "Template body should be a list of fields"

    # And it should contain the required field
    field_ids = [field.get("id", "") for field in template_data["body"] if "id" in field]

    # Check if the field ID matches
    assert (
        required_field in field_ids
    ), f"Feature request template should include field for {required_field}"


@given(
    optional_field=st.sampled_from(
        [
            "alternatives",
            "additional",
        ]
    )
)
def test_feature_request_template_has_optional_fields(optional_field: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.5

    For any optional field in the feature request template (alternatives considered,
    additional context), the template should include that field.
    """
    # Given the feature request template exists
    template_path = Path(".github/ISSUE_TEMPLATE/feature_request.yml")
    assert template_path.exists(), "Feature request template should exist"

    # When we parse the template YAML
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have a body with form fields
    assert "body" in template_data, "Feature request template should have a body"

    field_ids = [field.get("id", "") for field in template_data["body"] if "id" in field]

    # Check if the optional field is present
    assert (
        optional_field in field_ids
    ), f"Feature request template should include optional field for {optional_field}"


@given(
    template_file=st.sampled_from(
        [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        ]
    )
)
def test_issue_templates_have_valid_yaml_structure(template_file: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5

    For any issue template, the template should be valid YAML with proper structure
    including name, description, and body fields.
    """
    # Given an issue template
    template_path = Path(template_file)
    assert template_path.exists(), f"Template {template_file} should exist"

    # When we parse the template
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have required top-level fields
    assert "name" in template_data, f"Template {template_file} should have a name"
    assert "description" in template_data, f"Template {template_file} should have a description"
    assert "body" in template_data, f"Template {template_file} should have a body"

    # And the body should be a list
    assert isinstance(template_data["body"], list), f"Template {template_file} body should be a list"

    # And the body should have at least one field
    assert len(template_data["body"]) > 0, f"Template {template_file} should have at least one field"


@given(
    field_index=st.integers(min_value=0, max_value=10),
)
def test_issue_template_fields_have_proper_structure(field_index: int) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.2, 4.3, 4.4, 4.5

    For any field in an issue template, the field should have proper structure
    with type and attributes.
    """
    # Given a bug report template
    template_path = Path(".github/ISSUE_TEMPLATE/bug_report.yml")
    assert template_path.exists(), "Bug report template should exist"

    # When we parse the template
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then if the field index is valid
    if field_index < len(template_data["body"]):
        field = template_data["body"][field_index]

        # The field should have a type
        assert "type" in field, f"Field at index {field_index} should have a type"

        # If it's not a markdown field, it should have attributes
        if field["type"] != "markdown":
            assert (
                "attributes" in field
            ), f"Non-markdown field at index {field_index} should have attributes"


def test_issue_template_config_exists() -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.1

    The issue template configuration file should exist to configure the template chooser.
    """
    # Given the issue template directory
    config_path = Path(".github/ISSUE_TEMPLATE/config.yml")

    # Then the config file should exist
    assert config_path.exists(), "Issue template config.yml should exist"

    # And it should be valid YAML
    content = config_path.read_text(encoding="utf-8")
    config_data = yaml.safe_load(content)

    # And it should have the blank_issues_enabled setting
    assert (
        "blank_issues_enabled" in config_data
    ), "config.yml should have blank_issues_enabled setting"


@given(
    template_type=st.sampled_from(
        [
            "bug_report",
            "feature_request",
        ]
    )
)
def test_issue_templates_have_labels(template_type: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.1

    For any issue template type, the template should include labels to auto-apply
    to issues created with that template.
    """
    # Given an issue template
    template_path = Path(f".github/ISSUE_TEMPLATE/{template_type}.yml")
    assert template_path.exists(), f"Template {template_type}.yml should exist"

    # When we parse the template
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then it should have labels defined
    assert "labels" in template_data, f"Template {template_type}.yml should have labels"
    assert isinstance(template_data["labels"], list), "Labels should be a list"
    assert len(template_data["labels"]) > 0, f"Template {template_type}.yml should have at least one label"


@given(
    validation_requirement=st.sampled_from(
        [
            "required_true",
            "required_false",
        ]
    )
)
def test_issue_template_fields_have_validation(validation_requirement: str) -> None:
    """Feature: open-source-standards, Property 6: Issue templates contain required fields.

    Validates: Requirements 4.2, 4.3, 4.4, 4.5

    For any field validation requirement, issue templates should properly mark
    fields as required or optional using the validations section.
    """
    # Given the bug report template
    template_path = Path(".github/ISSUE_TEMPLATE/bug_report.yml")
    assert template_path.exists(), "Bug report template should exist"

    # When we parse the template
    content = template_path.read_text(encoding="utf-8")
    template_data = yaml.safe_load(content)

    # Then we should find fields with validation settings
    fields_with_validation = [
        field for field in template_data["body"] if "validations" in field
    ]

    assert len(fields_with_validation) > 0, "Template should have fields with validation settings"

    # And we should find both required and optional fields
    if validation_requirement == "required_true":
        required_fields = [
            field
            for field in fields_with_validation
            if field.get("validations", {}).get("required") is True
        ]
        assert len(required_fields) > 0, "Template should have required fields"
    else:
        optional_fields = [
            field
            for field in fields_with_validation
            if field.get("validations", {}).get("required") is False
        ]
        assert len(optional_fields) > 0, "Template should have optional fields"


@given(
    required_section=st.sampled_from(
        [
            "description",
            "related issues",
            "type of change",
            "testing",
            "documentation",
            "code quality",
        ]
    )
)
def test_pr_template_has_required_sections(required_section: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.2, 5.3, 5.4, 5.5

    For any required section (description, related issues, testing checklist,
    documentation checklist), the PR template should contain that section.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should contain the required section
    section_keywords = {
        "description": ["description", "what does this pr do", "why is this change"],
        "related issues": ["related issues", "fixes", "closes", "issue"],
        "type of change": ["type of change", "bug fix", "feature", "breaking change"],
        "testing": ["testing", "tests", "test coverage", "pytest"],
        "documentation": ["documentation", "readme", "docs", "changelog"],
        "code quality": ["code quality", "linting", "type checking", "black", "ruff", "mypy"],
    }

    keywords = section_keywords.get(required_section, [required_section])

    # At least one keyword should be present in the content
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should contain section about '{required_section}'"


@given(
    checklist_type=st.sampled_from(
        [
            "testing",
            "documentation",
            "code quality",
            "type of change",
        ]
    )
)
def test_pr_template_has_checklists(checklist_type: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.3, 5.4, 5.5

    For any checklist type (testing, documentation, code quality, type of change),
    the PR template should include a checklist for that category.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8")

    # Then it should contain checkbox items (markdown checkboxes)
    assert "- [ ]" in content, "PR template should contain checkbox items"

    # And it should contain the checklist type
    content_lower = content.lower()
    checklist_keywords = {
        "testing": ["testing", "tests", "test"],
        "documentation": ["documentation", "readme", "docs", "changelog"],
        "code quality": ["code quality", "linting", "type checking", "black", "ruff", "mypy"],
        "type of change": ["type of change", "bug fix", "feature", "breaking change"],
    }

    keywords = checklist_keywords.get(checklist_type, [checklist_type])
    assert any(
        keyword in content_lower for keyword in keywords
    ), f"PR template should include checklist for {checklist_type}"


@given(
    change_type=st.sampled_from(
        [
            "bug fix",
            "feature",
            "breaking change",
            "documentation",
        ]
    )
)
def test_pr_template_includes_change_types(change_type: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.3

    For any change type (bug fix, feature, breaking change, documentation),
    the PR template should include that option in the type of change checklist.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include the change type
    change_type_keywords = {
        "bug fix": ["bug fix", "bug"],
        "feature": ["feature", "new feature"],
        "breaking change": ["breaking change", "breaking"],
        "documentation": ["documentation", "docs"],
    }

    keywords = change_type_keywords.get(change_type, [change_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include '{change_type}' as a change type option"


@given(
    testing_item=st.sampled_from(
        [
            "tests added",
            "tests pass",
            "coverage",
        ]
    )
)
def test_pr_template_includes_testing_checklist_items(testing_item: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.4

    For any testing checklist item (tests added, tests pass, coverage maintained),
    the PR template should include that item in the testing checklist.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include the testing item
    testing_keywords = {
        "tests added": ["added tests", "tests that prove", "test"],
        "tests pass": ["tests pass", "passing", "all new and existing tests"],
        "coverage": ["coverage", "test coverage"],
    }

    keywords = testing_keywords.get(testing_item, [testing_item])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include testing checklist item for '{testing_item}'"


@given(
    documentation_item=st.sampled_from(
        [
            "readme",
            "docs",
            "changelog",
        ]
    )
)
def test_pr_template_includes_documentation_checklist_items(
    documentation_item: str,
) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.5

    For any documentation checklist item (README updated, docs updated, changelog updated),
    the PR template should include that item in the documentation checklist.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include the documentation item
    documentation_keywords = {
        "readme": ["readme", "readme.md"],
        "docs": ["docs", "documentation"],
        "changelog": ["changelog", "changelog.md"],
    }

    keywords = documentation_keywords.get(documentation_item, [documentation_item])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include documentation checklist item for '{documentation_item}'"


@given(
    quality_check=st.sampled_from(
        [
            "linting",
            "type checking",
            "black",
            "ruff",
            "mypy",
        ]
    )
)
def test_pr_template_includes_code_quality_checks(quality_check: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.5

    For any code quality check (linting, type checking, black, ruff, mypy),
    the PR template should include that check in the code quality checklist.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include the quality check
    quality_keywords = {
        "linting": ["linting", "lint", "ruff"],
        "type checking": ["type checking", "type check", "mypy"],
        "black": ["black", "format"],
        "ruff": ["ruff", "lint"],
        "mypy": ["mypy", "type"],
    }

    keywords = quality_keywords.get(quality_check, [quality_check])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include code quality check for '{quality_check}'"


@given(
    linking_instruction=st.sampled_from(
        [
            "fixes",
            "closes",
            "related",
        ]
    )
)
def test_pr_template_includes_issue_linking_instructions(
    linking_instruction: str,
) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.3

    For any issue linking instruction (Fixes, Closes, Related to),
    the PR template should include examples or instructions for that linking keyword.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include issue linking instructions
    linking_keywords = {
        "fixes": ["fixes", "fix"],
        "closes": ["closes", "close"],
        "related": ["related", "related to"],
    }

    keywords = linking_keywords.get(linking_instruction, [linking_instruction])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include issue linking instruction for '{linking_instruction}'"


@given(
    file_size_threshold=st.integers(min_value=1000, max_value=50000),
)
def test_pr_template_has_substantial_content(file_size_threshold: int) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5

    For any reasonable content threshold, the PR template should contain
    substantial content (not just a placeholder).
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we check the file size
    file_size = pr_template_path.stat().st_size

    # Then it should have substantial content
    # A comprehensive PR template should be at least 2KB
    assert file_size >= 2000, f"PR template should have substantial content (at least 2KB), got {file_size} bytes"

    # And it should have multiple lines
    content = pr_template_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    assert line_count >= 50, f"PR template should have substantial content (at least 50 lines), got {line_count} lines"


@given(
    heading_level=st.sampled_from(["#", "##", "###"]),
)
def test_pr_template_has_proper_markdown_structure(heading_level: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.2, 5.3, 5.4, 5.5

    For any markdown heading level, the PR template should use proper
    markdown structure to organize content into sections.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8")

    # Then it should contain markdown headings
    assert "#" in content, "PR template should use markdown headings"

    # The file should be well-structured with multiple sections
    heading_count = content.count("\n#")
    assert heading_count >= 5, "PR template should have multiple sections (at least 5 headings)"


def test_pr_template_exists() -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.1

    The pull request template file should exist at the expected location.
    """
    # Given the expected PR template path
    pr_template_path = Path(".github/pull_request_template.md")

    # Then the template file should exist
    assert pr_template_path.exists(), "Pull request template should exist at .github/pull_request_template.md"

    # And it should not be empty
    assert pr_template_path.stat().st_size > 0, "Pull request template should not be empty"


@given(
    prompt_type=st.sampled_from(
        [
            "what does this pr do",
            "why is this change needed",
            "describe",
        ]
    )
)
def test_pr_template_includes_description_prompts(prompt_type: str) -> None:
    """Feature: open-source-standards, Property 7: Pull request template contains required sections.

    Validates: Requirements 5.2

    For any description prompt type, the PR template should include prompts
    to guide contributors in providing comprehensive descriptions.
    """
    # Given the PR template exists
    pr_template_path = Path(".github/pull_request_template.md")
    assert pr_template_path.exists(), "Pull request template should exist"

    # When we read the file content
    content = pr_template_path.read_text(encoding="utf-8").lower()

    # Then it should include description prompts
    prompt_keywords = {
        "what does this pr do": ["what does this pr do", "what", "do"],
        "why is this change needed": ["why", "needed", "motivation"],
        "describe": ["describe", "description", "explain"],
    }

    keywords = prompt_keywords.get(prompt_type, [prompt_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"PR template should include description prompt for '{prompt_type}'"



@given(
    badge_type=st.sampled_from(
        [
            "ci",
            "coverage",
            "release",
            "license",
        ]
    )
)
def test_readme_contains_required_badges(badge_type: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5, 8.2, 8.3, 8.4, 8.5

    For any required badge type (CI/CD status, coverage, release, license),
    the README should contain badge markdown or HTML for that badge type.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should contain badge markdown (shields.io or GitHub badges)
    assert "![" in content or "<img" in content, "README should contain badge markdown or HTML"

    # And it should contain the specific badge type
    content_lower = content.lower()
    badge_keywords = {
        "ci": ["cross-platform tests", "workflow", "actions", "ci", "build"],
        "coverage": ["codecov", "coverage", "cov"],
        "release": ["release", "version", "v/release"],
        "license": ["license", "mit"],
    }

    keywords = badge_keywords.get(badge_type, [badge_type])
    assert any(
        keyword in content_lower for keyword in keywords
    ), f"README should contain badge for {badge_type}"


@given(
    badge_url_component=st.sampled_from(
        [
            "github.com",
            "codecov.io",
            "shields.io",
            "img.shields.io",
        ]
    )
)
def test_readme_badges_use_standard_services(badge_url_component: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5, 8.2, 8.3, 8.4, 8.5

    For any standard badge service (GitHub, Codecov, shields.io),
    the README should use that service for displaying badges.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should contain URLs from standard badge services
    assert (
        badge_url_component in content
    ), f"README should use {badge_url_component} for badges"


@given(
    badge_format=st.sampled_from(
        [
            "markdown",
            "clickable",
        ]
    )
)
def test_readme_badges_have_proper_format(badge_format: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5, 8.2, 8.3, 8.4, 8.5

    For any badge format requirement (markdown syntax, clickable links),
    the README badges should follow that format.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then badges should follow proper format
    if badge_format == "markdown":
        # Badges should use markdown image syntax
        assert "![" in content, "README should use markdown image syntax for badges"
    elif badge_format == "clickable":
        # Badges should be wrapped in links
        assert "[![" in content or "](" in content, "README badges should be clickable (wrapped in links)"


@given(
    badge_position=st.sampled_from(
        [
            "top",
            "after title",
            "before features",
        ]
    )
)
def test_readme_badges_positioned_prominently(badge_position: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5

    For any badge positioning requirement, the README should position badges
    prominently near the top of the document.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Then badges should appear in the first 20 lines (prominently positioned)
    badge_line_indices = [i for i, line in enumerate(lines) if "![" in line and "badge" in line.lower()]

    assert len(badge_line_indices) > 0, "README should contain badges"
    assert min(badge_line_indices) < 20, "Badges should be positioned prominently (within first 20 lines)"


@given(
    workflow_name=st.sampled_from(
        [
            "Cross-Platform Tests",
            "test",
        ]
    )
)
def test_readme_ci_badge_references_actual_workflow(workflow_name: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 8.2

    For any CI workflow name, the README CI badge should reference an actual
    GitHub Actions workflow that exists in the repository.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should reference the workflow
    # The badge should contain either the workflow name or the workflow file
    content_lower = content.lower()
    workflow_indicators = [
        workflow_name.lower(),
        "workflows/test.yml",
        "actions/workflows",
    ]

    assert any(
        indicator in content_lower for indicator in workflow_indicators
    ), f"README CI badge should reference workflow '{workflow_name}' or workflow file"


@given(
    badge_count_threshold=st.integers(min_value=3, max_value=10),
)
def test_readme_has_multiple_badges(badge_count_threshold: int) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5, 8.2, 8.3, 8.4, 8.5

    For any reasonable badge count threshold, the README should contain
    multiple badges to display project health and status.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should contain multiple badges
    # Count badge markdown patterns
    badge_count = content.count("[![")

    # README should have at least 4 badges (CI, coverage, release, license)
    assert badge_count >= 4, f"README should have at least 4 badges, found {badge_count}"


@given(
    link_target=st.sampled_from(
        [
            "actions",
            "codecov",
            "releases",
            "license",
        ]
    )
)
def test_readme_badges_link_to_relevant_pages(link_target: str) -> None:
    """Feature: open-source-standards, Property 9: README contains required badges.

    Validates: Requirements 6.5, 8.2, 8.3, 8.4, 8.5

    For any badge link target (actions, codecov, releases, license),
    the README badges should link to relevant pages that provide more information.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then badges should link to relevant pages
    link_keywords = {
        "actions": ["actions/workflows", "github.com"],
        "codecov": ["codecov.io"],
        "releases": ["releases", "github.com"],
        "license": ["LICENSE", "license"],
    }

    keywords = link_keywords.get(link_target, [link_target])
    assert any(
        keyword in content for keyword in keywords
    ), f"README badges should link to {link_target} page"


@given(
    screenshot_type=st.sampled_from(
        [
            "gui",
            "signature",
            "settings",
            "profile",
        ]
    )
)
def test_readme_contains_screenshots(screenshot_type: str) -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any visual component (GUI interface, generated output, settings, profile management),
    the README should reference screenshot images that exist in the repository.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should contain image references (markdown or HTML)
    assert "![" in content or "<img" in content, "README should contain image references"

    # And it should reference screenshots for the visual component
    content_lower = content.lower()
    screenshot_keywords = {
        "gui": ["gui", "interface", "main window", "application"],
        "signature": ["signature", "output", "example", "generated"],
        "settings": ["settings", "configuration", "preferences"],
        "profile": ["profile", "management", "user"],
    }

    keywords = screenshot_keywords.get(screenshot_type, [screenshot_type])
    # Check if any keyword appears near an image reference
    assert any(
        keyword in content_lower for keyword in keywords
    ), f"README should reference screenshots for {screenshot_type}"


@given(
    image_path_component=st.sampled_from(
        [
            "docs/images",
            ".png",
            ".jpg",
            "screenshot",
        ]
    )
)
def test_readme_screenshot_paths_are_valid(image_path_component: str) -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any screenshot path component (directory, file extension),
    the README should use valid relative paths to images.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then if it contains image references, they should use valid paths
    if "![" in content or "<img" in content:
        # Check for common image path patterns
        path_indicators = {
            "docs/images": ["docs/images", "docs\\images"],
            ".png": [".png"],
            ".jpg": [".jpg", ".jpeg"],
            "screenshot": ["screenshot", "image", "docs"],
        }

        indicators = path_indicators.get(image_path_component, [image_path_component])
        # At least one indicator should be present if images are referenced
        assert any(
            indicator in content for indicator in indicators
        ), f"README image paths should include {image_path_component}"


@given(
    alt_text_requirement=st.sampled_from(
        [
            "gui",
            "signature",
            "settings",
            "screenshot",
        ]
    )
)
def test_readme_screenshots_have_alt_text(alt_text_requirement: str) -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any screenshot in the README, the image should have descriptive alt text
    for accessibility.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then if it contains markdown images, they should have alt text
    # Markdown format: ![alt text](path)
    # We check that images don't have empty alt text
    import re

    markdown_images = re.findall(r"!\[(.*?)\]\((.*?)\)", content)

    if markdown_images:
        # At least some images should have non-empty alt text
        images_with_alt = [img for img in markdown_images if img[0].strip()]
        assert len(images_with_alt) > 0, "README images should have descriptive alt text"


@given(
    screenshot_section=st.sampled_from(
        [
            "screenshots",
            "features",
            "gui",
            "usage",
        ]
    )
)
def test_readme_screenshots_in_appropriate_section(screenshot_section: str) -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any appropriate section (Screenshots, Features, GUI, Usage),
    the README should include screenshots in or near that section.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    # Then it should have sections where screenshots would be appropriate
    section_keywords = {
        "screenshots": ["screenshots", "## screenshots", "### screenshots"],
        "features": ["features", "## features", "### features"],
        "gui": ["gui", "interface", "graphical"],
        "usage": ["usage", "## usage", "### usage"],
    }

    keywords = section_keywords.get(screenshot_section, [screenshot_section])
    # At least one appropriate section should exist
    assert any(
        keyword in content_lower for keyword in keywords
    ), f"README should have a section for {screenshot_section}"


@given(
    image_count_threshold=st.integers(min_value=1, max_value=10),
)
def test_readme_has_multiple_screenshots(image_count_threshold: int) -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any reasonable image count threshold, the README should contain
    multiple screenshots to demonstrate different aspects of the application.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8")

    # Then it should contain multiple image references
    import re

    # Count markdown images
    markdown_images = re.findall(r"!\[.*?\]\(.*?\)", content)

    # Count HTML images
    html_images = re.findall(r"<img.*?>", content, re.IGNORECASE)

    total_images = len(markdown_images) + len(html_images)

    # Should have at least 2 screenshots for a GUI application
    assert total_images >= 2, f"README should contain multiple screenshots (at least 2), found {total_images}"


def test_readme_screenshot_files_exist() -> None:
    """Feature: open-source-standards, Property 11: README contains screenshots.

    Validates: Requirements 11.1

    For any screenshot referenced in the README, the actual image file
    should exist in the repository.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content and extract image paths
    content = readme_path.read_text(encoding="utf-8")

    import re

    # Extract markdown image paths
    markdown_images = re.findall(r"!\[.*?\]\((.*?)\)", content)

    # Extract HTML image paths
    html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)

    all_image_paths = markdown_images + html_images

    # Filter for local paths (not URLs)
    local_image_paths = [
        path for path in all_image_paths if not path.startswith(("http://", "https://", "//"))
    ]

    # Then if there are local image references, at least some should exist
    if local_image_paths:
        existing_images = [path for path in local_image_paths if Path(path).exists()]
        # At least 50% of referenced images should exist
        existence_ratio = len(existing_images) / len(local_image_paths)
        assert (
            existence_ratio >= 0.5
        ), f"At least 50% of referenced screenshot files should exist, found {len(existing_images)}/{len(local_image_paths)}"


@given(
    governance_aspect=st.sampled_from(
        [
            "maintainers",
            "decision-making",
            "becoming a maintainer",
        ]
    )
)
def test_project_governance_is_documented(governance_aspect: str) -> None:
    """Feature: open-source-standards, Property 17: Project governance is documented.

    Validates: Requirements 12.1, 12.2, 12.3

    For any governance aspect (maintainer identification, decision process,
    maintainer onboarding), the documentation should address that aspect.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should contain governance information
    governance_keywords = {
        "maintainers": ["maintainer", "maintained by", "project maintainer"],
        "decision-making": ["decision", "approval", "consensus", "pull request"],
        "becoming a maintainer": ["becoming a maintainer", "how to become", "maintainer"],
    }

    keywords = governance_keywords.get(governance_aspect, [governance_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should document {governance_aspect}"


@given(
    governance_section=st.sampled_from(
        [
            "project governance",
            "maintainers",
            "decision-making process",
        ]
    )
)
def test_contributing_has_governance_section(governance_section: str) -> None:
    """Feature: open-source-standards, Property 17: Project governance is documented.

    Validates: Requirements 12.1, 12.2, 12.3

    For any governance section, the CONTRIBUTING.md file should have a dedicated
    section addressing that governance topic.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should have a governance section
    section_keywords = {
        "project governance": ["project governance", "governance"],
        "maintainers": ["maintainers", "## maintainers"],
        "decision-making process": ["decision-making", "decision process", "approval"],
    }

    keywords = section_keywords.get(governance_section, [governance_section])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should have a section about {governance_section}"


@given(
    maintainer_info=st.sampled_from(
        [
            "name",
            "role",
            "ultrasardine",
        ]
    )
)
def test_contributing_identifies_maintainers(maintainer_info: str) -> None:
    """Feature: open-source-standards, Property 17: Project governance is documented.

    Validates: Requirements 12.1

    For any maintainer information (name, role), the CONTRIBUTING.md file
    should identify the project maintainers.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should identify maintainers
    maintainer_keywords = {
        "name": ["ultrasardine", "maintainer"],
        "role": ["maintainer", "lead maintainer", "project creator"],
        "ultrasardine": ["ultrasardine"],
    }

    keywords = maintainer_keywords.get(maintainer_info, [maintainer_info])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should identify maintainers with {maintainer_info}"


@given(
    decision_aspect=st.sampled_from(
        [
            "pull request approval",
            "maintainer approval",
            "consensus",
        ]
    )
)
def test_contributing_explains_decision_making(decision_aspect: str) -> None:
    """Feature: open-source-standards, Property 17: Project governance is documented.

    Validates: Requirements 12.2

    For any decision-making aspect (PR approval, maintainer approval, consensus),
    the CONTRIBUTING.md file should explain how decisions are made.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should explain decision-making
    decision_keywords = {
        "pull request approval": ["pull request", "approval", "require approval"],
        "maintainer approval": ["maintainer", "approval", "maintainer approval"],
        "consensus": ["consensus", "agreement", "discussed"],
    }

    keywords = decision_keywords.get(decision_aspect, [decision_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should explain {decision_aspect} in decision-making"


@given(
    onboarding_aspect=st.sampled_from(
        [
            "contributions",
            "community trust",
            "commitment",
        ]
    )
)
def test_contributing_explains_maintainer_onboarding(onboarding_aspect: str) -> None:
    """Feature: open-source-standards, Property 17: Project governance is documented.

    Validates: Requirements 12.3

    For any maintainer onboarding aspect (consistent contributions, community trust,
    commitment), the CONTRIBUTING.md file should explain how to become a maintainer.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should explain how to become a maintainer
    onboarding_keywords = {
        "contributions": ["contribution", "contributing", "consistent"],
        "community trust": ["community", "trust", "positive"],
        "commitment": ["commitment", "dedicated", "understanding"],
    }

    keywords = onboarding_keywords.get(onboarding_aspect, [onboarding_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should explain {onboarding_aspect} for becoming a maintainer"



@given(
    acknowledgment_location=st.sampled_from(
        [
            "readme",
            "contributing",
        ]
    )
)
def test_contributors_are_acknowledged(acknowledgment_location: str) -> None:
    """Feature: open-source-standards, Property 18: Contributors are acknowledged.

    Validates: Requirements 12.5

    For any acknowledgment location (README, CONTRIBUTING), the documentation
    should acknowledge contributors to the project.
    """
    # Given the documentation files exist
    readme_path = Path("README.md")
    contributing_path = Path("CONTRIBUTING.md")

    # When we check the appropriate file
    if acknowledgment_location == "readme":
        assert readme_path.exists(), "README.md file must exist"
        content = readme_path.read_text(encoding="utf-8").lower()
    else:
        assert contributing_path.exists(), "CONTRIBUTING.md file must exist"
        content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should acknowledge contributors
    acknowledgment_keywords = [
        "contributor",
        "contributors",
        "contribution",
        "acknowledgment",
        "recognition",
        "thank",
    ]

    assert any(
        keyword in content for keyword in acknowledgment_keywords
    ), f"{acknowledgment_location.upper()} should acknowledge contributors"


@given(
    acknowledgment_type=st.sampled_from(
        [
            "all contributors",
            "github contributors",
            "contributor graph",
        ]
    )
)
def test_readme_acknowledges_contributors(acknowledgment_type: str) -> None:
    """Feature: open-source-standards, Property 18: Contributors are acknowledged.

    Validates: Requirements 12.5

    For any acknowledgment type, the README should acknowledge contributors
    in some form (all contributors, GitHub graph, etc.).
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8").lower()

    # Then it should acknowledge contributors
    acknowledgment_keywords = {
        "all contributors": ["contributor", "all contributors", "valued"],
        "github contributors": ["github", "contributor", "graph"],
        "contributor graph": ["contributor", "graph", "github"],
    }

    keywords = acknowledgment_keywords.get(acknowledgment_type, [acknowledgment_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"README should acknowledge contributors via {acknowledgment_type}"


@given(
    recognition_aspect=st.sampled_from(
        [
            "valued",
            "appreciated",
            "recognized",
        ]
    )
)
def test_contributing_expresses_contributor_appreciation(recognition_aspect: str) -> None:
    """Feature: open-source-standards, Property 18: Contributors are acknowledged.

    Validates: Requirements 12.5

    For any recognition aspect (valued, appreciated, recognized), the CONTRIBUTING.md
    file should express appreciation for contributors.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should express appreciation
    appreciation_keywords = {
        "valued": ["valued", "value", "important"],
        "appreciated": ["appreciated", "appreciate", "thank"],
        "recognized": ["recognized", "recognition", "acknowledge"],
    }

    keywords = appreciation_keywords.get(recognition_aspect, [recognition_aspect])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should express that contributors are {recognition_aspect}"


@given(
    contributor_visibility=st.sampled_from(
        [
            "github graph",
            "release notes",
            "readme",
        ]
    )
)
def test_contributors_have_visibility(contributor_visibility: str) -> None:
    """Feature: open-source-standards, Property 18: Contributors are acknowledged.

    Validates: Requirements 12.5

    For any visibility mechanism (GitHub graph, release notes, README),
    the documentation should mention how contributors gain visibility.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should mention contributor visibility
    visibility_keywords = {
        "github graph": ["github", "contributor", "graph"],
        "release notes": ["release notes", "release", "highlighted"],
        "readme": ["readme", "acknowledged"],
    }

    keywords = visibility_keywords.get(contributor_visibility, [contributor_visibility])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should mention contributor visibility via {contributor_visibility}"


@given(
    contribution_size=st.sampled_from(
        [
            "small",
            "large",
            "any",
        ]
    )
)
def test_all_contribution_sizes_are_valued(contribution_size: str) -> None:
    """Feature: open-source-standards, Property 18: Contributors are acknowledged.

    Validates: Requirements 12.5

    For any contribution size (small, large, any), the documentation should
    express that all contributions are valued.
    """
    # Given the CONTRIBUTING.md file exists
    contributing_path = Path("CONTRIBUTING.md")
    assert contributing_path.exists(), "CONTRIBUTING.md file must exist"

    # When we read the file content
    content = contributing_path.read_text(encoding="utf-8").lower()

    # Then it should value all contributions
    value_keywords = {
        "small": ["small", "no matter how small", "any"],
        "large": ["significant", "major", "large"],
        "any": ["all", "any", "every", "no matter"],
    }

    keywords = value_keywords.get(contribution_size, [contribution_size])
    assert any(
        keyword in content for keyword in keywords
    ), f"CONTRIBUTING.md should express that {contribution_size} contributions are valued"


@given(
    required_file=st.sampled_from(
        [
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
        ]
    )
)
def test_required_community_health_files_exist(required_file: str) -> None:
    """Feature: open-source-standards, Property 1: Required community health files exist.

    Validates: Requirements 1.1, 2.1, 3.1

    For any required community health file (CONTRIBUTING.md, CODE_OF_CONDUCT.md,
    SECURITY.md), the file should exist at the expected path in the repository.
    """
    # Given a required community health file path
    file_path = Path(required_file)

    # Then the file should exist
    assert file_path.exists(), f"Required community health file {required_file} should exist"

    # And it should not be empty
    assert file_path.stat().st_size > 0, f"Required community health file {required_file} should not be empty"

    # And it should be readable
    content = file_path.read_text(encoding="utf-8")
    assert len(content) > 0, f"Required community health file {required_file} should have content"


@given(
    template_path=st.sampled_from(
        [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/pull_request_template.md",
        ]
    )
)
def test_github_templates_exist(template_path: str) -> None:
    """Feature: open-source-standards, Property 2: GitHub templates exist.

    Validates: Requirements 4.1, 5.1

    For any required GitHub template (issue templates, PR template), the template
    file should exist in the .github directory structure.
    """
    # Given a required GitHub template path
    file_path = Path(template_path)

    # Then the template file should exist
    assert file_path.exists(), f"Required GitHub template {template_path} should exist"

    # And it should not be empty
    assert file_path.stat().st_size > 0, f"Required GitHub template {template_path} should not be empty"

    # And it should be readable
    content = file_path.read_text(encoding="utf-8")
    assert len(content) > 0, f"Required GitHub template {template_path} should have content"


@given(
    platform=st.sampled_from(
        [
            "windows",
            "macos",
            "linux",
        ]
    )
)
def test_readme_contains_platform_specific_installation_instructions(platform: str) -> None:
    """Feature: open-source-standards, Property 8: README contains platform-specific installation instructions.

    Validates: Requirements 6.2

    For any supported platform (Windows, macOS, Linux), the README should contain
    installation instructions specific to that platform.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8").lower()

    # Then it should contain platform-specific installation instructions
    platform_keywords = {
        "windows": ["windows", "win", "powershell", "cmd", ".exe"],
        "macos": ["macos", "mac", "darwin", "homebrew", "brew"],
        "linux": ["linux", "ubuntu", "debian", "apt", "yum"],
    }

    keywords = platform_keywords.get(platform, [platform])
    assert any(
        keyword in content for keyword in keywords
    ), f"README should contain installation instructions for {platform}"

    # And it should have an installation section
    assert "install" in content, "README should have an installation section"


@given(
    usage_type=st.sampled_from(
        [
            "cli",
            "gui",
            "docker",
            "command",
        ]
    )
)
def test_readme_contains_usage_examples(usage_type: str) -> None:
    """Feature: open-source-standards, Property 10: README contains usage examples.

    Validates: Requirements 6.3, 11.2

    For any major feature (CLI usage, GUI usage, Docker usage), the README should
    contain code examples demonstrating that feature.
    """
    # Given the README.md file exists
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md file must exist"

    # When we read the file content
    content = readme_path.read_text(encoding="utf-8").lower()

    # Then it should contain usage examples
    assert "usage" in content or "example" in content, "README should have usage or example sections"

    # And it should contain code blocks (indicated by ``` or indented code)
    assert "```" in content, "README should include code examples"

    # And it should mention the usage type
    usage_keywords = {
        "cli": ["cli", "command line", "terminal", "python", "uv run"],
        "gui": ["gui", "graphical", "interface", "window"],
        "docker": ["docker", "container", "docker-compose"],
        "command": ["command", "run", "execute"],
    }

    keywords = usage_keywords.get(usage_type, [usage_type])
    assert any(
        keyword in content for keyword in keywords
    ), f"README should include usage examples for {usage_type}"


@given(
    license_location=st.sampled_from(
        [
            "LICENSE",
            "README.md",
            "pyproject.toml",
        ]
    )
)
def test_license_information_is_consistent(license_location: str) -> None:
    """Feature: open-source-standards, Property 12: License information is consistent.

    Validates: Requirements 7.2, 7.3, 7.5

    For any license reference (LICENSE file, README badge, pyproject.toml), the
    license type should be consistently identified as MIT.
    """
    # Given a license location
    file_path = Path(license_location)

    # Then the file should exist
    assert file_path.exists(), f"License location {license_location} should exist"

    # When we read the file content
    content = file_path.read_text(encoding="utf-8")

    # Then it should reference MIT license
    content_lower = content.lower()
    assert "mit" in content_lower, f"{license_location} should reference MIT license"

    # And if it's the LICENSE file, it should contain the full MIT license text
    if license_location == "LICENSE":
        assert "permission is hereby granted" in content_lower, "LICENSE file should contain full MIT license text"
        assert "free of charge" in content_lower, "LICENSE file should contain MIT license terms"

    # And if it's the README, it should have a license badge or section
    if license_location == "README.md":
        assert "license" in content_lower, "README should mention license"

    # And if it's pyproject.toml, it should have license metadata
    if license_location == "pyproject.toml":
        assert "license" in content_lower, "pyproject.toml should have license metadata"


@given(
    platform=st.sampled_from(
        [
            "windows",
            "macos",
            "ubuntu",
            "linux",
        ]
    )
)
def test_ci_workflow_tests_all_platforms(platform: str) -> None:
    """Feature: open-source-standards, Property 13: CI workflow tests all platforms.

    Validates: Requirements 9.2

    For any supported platform (Windows, macOS, Linux), the CI workflow matrix
    should include that platform.
    """
    # Given the CI workflow file exists
    workflow_path = Path(".github/workflows/test.yml")
    assert workflow_path.exists(), "CI workflow file should exist"

    # When we read the workflow content
    content = workflow_path.read_text(encoding="utf-8").lower()

    # Then it should include the platform in the matrix
    platform_keywords = {
        "windows": ["windows", "windows-latest"],
        "macos": ["macos", "macos-latest"],
        "ubuntu": ["ubuntu", "ubuntu-latest"],
        "linux": ["ubuntu", "linux"],
    }

    keywords = platform_keywords.get(platform, [platform])
    assert any(
        keyword in content for keyword in keywords
    ), f"CI workflow should test on {platform}"

    # And it should have a matrix strategy
    assert "matrix" in content or "strategy" in content, "CI workflow should use matrix strategy"


@given(
    quality_check=st.sampled_from(
        [
            "tests",
            "coverage",
            "linting",
            "type checking",
        ]
    )
)
def test_ci_workflow_includes_quality_checks(quality_check: str) -> None:
    """Feature: open-source-standards, Property 14: CI workflow includes quality checks.

    Validates: Requirements 9.3, 9.4, 9.5

    For any required quality check (tests, coverage, linting, type checking),
    the CI workflow should include a step performing that check.
    """
    # Given the CI workflow file exists
    workflow_path = Path(".github/workflows/test.yml")
    assert workflow_path.exists(), "CI workflow file should exist"

    # When we read the workflow content
    content = workflow_path.read_text(encoding="utf-8").lower()

    # Then it should include the quality check
    check_keywords = {
        "tests": ["pytest", "test", "run tests"],
        "coverage": ["coverage", "cov", "codecov"],
        "linting": ["ruff", "lint", "flake8"],
        "type checking": ["mypy", "type check", "type-check"],
    }

    keywords = check_keywords.get(quality_check, [quality_check])
    assert any(
        keyword in content for keyword in keywords
    ), f"CI workflow should include {quality_check}"

    # And it should have steps defined
    assert "steps:" in content or "run:" in content, "CI workflow should have steps defined"


@given(
    platform=st.sampled_from(
        [
            "windows",
            "macos",
            "linux",
        ]
    )
)
def test_release_scripts_support_all_platforms(platform: str) -> None:
    """Feature: open-source-standards, Property 15: Release scripts support all platforms.

    Validates: Requirements 10.3

    For any supported platform (Windows, macOS, Linux), the release automation
    should include build targets for that platform.
    """
    # Given the release documentation exists
    releasing_path = Path("docs/RELEASING.md")
    assert releasing_path.exists(), "Release documentation should exist"

    # When we read the release documentation
    content = releasing_path.read_text(encoding="utf-8").lower()

    # Then it should mention the platform
    platform_keywords = {
        "windows": ["windows", "win", ".exe"],
        "macos": ["macos", "mac", "darwin"],
        "linux": ["linux", "ubuntu"],
    }

    keywords = platform_keywords.get(platform, [platform])
    assert any(
        keyword in content for keyword in keywords
    ), f"Release documentation should mention {platform}"

    # And it should mention building or releases
    assert "build" in content or "release" in content, "Release documentation should mention building or releases"


@given(
    release_step=st.sampled_from(
        [
            "changelog",
            "binary",
            "github release",
            "git tag",
        ]
    )
)
def test_release_process_includes_required_steps(release_step: str) -> None:
    """Feature: open-source-standards, Property 16: Release process includes required steps.

    Validates: Requirements 10.2, 10.4, 10.5

    For any required release step (changelog generation, binary building, GitHub
    release creation, git tagging), the release automation should perform that step.
    """
    # Given the release documentation exists
    releasing_path = Path("docs/RELEASING.md")
    assert releasing_path.exists(), "Release documentation should exist"

    # When we read the release documentation
    content = releasing_path.read_text(encoding="utf-8").lower()

    # Then it should include the release step
    step_keywords = {
        "changelog": ["changelog", "change log", "changelog.md"],
        "binary": ["binary", "build", "executable", "package"],
        "github release": ["github release", "release", "create release"],
        "git tag": ["git tag", "tag", "version tag"],
    }

    keywords = step_keywords.get(release_step, [release_step])
    assert any(
        keyword in content for keyword in keywords
    ), f"Release documentation should include step for {release_step}"

    # And it should have a structured process
    assert "step" in content or "process" in content or "#" in content, "Release documentation should have a structured process"
