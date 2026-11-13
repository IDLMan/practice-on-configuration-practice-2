"""Offline POM parsing and Maven source tests."""

from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from src.maven import MavenRepository, parse_pom

ROOT = Path(__file__).resolve().parents[1]


class MavenTests(TestCase):
    """Test XML extraction without invoking the Maven package manager."""

    def test_direct_dependencies(self) -> None:
        """Direct dependencies with XML namespaces are recognized."""
        deps = parse_pom(self.sample_pom(), "demo:app:1.0")
        self.assertEqual(deps, ("demo:core:1.0",))

    def test_optional_and_test_are_ignored(self) -> None:
        """Exclude Maven optional and test-scope edges."""
        xml = self.sample_pom().replace(
            b"</dependencies>",
            b"<dependency><groupId>x</groupId><artifactId>t</artifactId>"
            b"<version>1</version><scope>test</scope></dependency>"
            b"<dependency><groupId>x</groupId><artifactId>opt</artifactId>"
            b"<version>1</version><optional>true</optional></dependency>"
            b"</dependencies>",
        )
        self.assertEqual(parse_pom(xml, "demo:app:1.0"),
                         ("demo:core:1.0",))

    def test_invalid_xml(self) -> None:
        """Malformed Maven POMs cause informative errors."""
        with self.assertRaisesRegex(ValueError, "Invalid Maven"):
            parse_pom(b"<project>", "demo:app:1.0")

    def test_unresolved_variable(self) -> None:
        """Fail instead of inventing unavailable dependency versions."""
        xml = self.sample_pom().replace(b"${project.version}",
                                        b"${missing.version}")
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            parse_pom(xml, "demo:app:1.0")

    def test_download_and_cache(self) -> None:
        """Fetch Maven2 POM URLs only once for each package."""
        repo = MavenRepository("https://repo.example/maven2")
        with patch("src.maven.urlopen") as fetch:
            fetch.return_value.__enter__.return_value = BytesIO(
                self.sample_pom()
            )
            repo.dependencies("demo:app:1.0")
            repo.dependencies("demo:app:1.0")
        self.assertEqual(fetch.call_count, 1)

    def test_missing_remote_pom(self) -> None:
        """Report network errors as user-readable problems."""
        from urllib.error import URLError
        repo = MavenRepository("https://repo.example")
        with patch("src.maven.urlopen", side_effect=URLError("offline")):
            with self.assertRaisesRegex(ValueError, "Cannot fetch"):
                repo.dependencies("demo:app:1.0")


    def test_parent_dependency_management(self) -> None:
        """Inherited dependency versions resolve through parent POM."""
        repo = MavenRepository("https://repo.example/maven2")
        pom_root = ROOT / "fixtures/maven_repo"

        def fetch(request, timeout):
            """Read a Maven2 POM from an in-repository test fixture."""
            path = request.full_url.split("/maven2/")[-1]
            return BytesIO((pom_root / path).read_bytes())

        with patch("src.maven.urlopen", side_effect=fetch):
            deps = repo.dependencies("demo:app:1.0")
        self.assertEqual(deps, ("demo:core:1.0",))

    @staticmethod
    def sample_pom() -> bytes:
        """Small POM with a project property and default XML namespace."""
        return (
            b'<project xmlns="http://maven.apache.org/POM/4.0.0">'
            b"<modelVersion>4.0.0</modelVersion>"
            b"<dependencies><dependency><groupId>demo</groupId>"
            b"<artifactId>core</artifactId>"
            b"<version>${project.version}</version>"
            b"</dependency></dependencies></project>"
        )
