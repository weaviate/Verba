import pytest
from wasabi import msg

from goldenverba.ingestion import preprocess_weaviate


@pytest.fixture(autouse=True)
def no_warnings(monkeypatch):
    monkeypatch.setattr(msg, "warn", lambda *args, **kwargs: None)


def test_document_filtering():
    # Test cases to assert
    test_cases = {
        "developers/weaviate/api/_category_.json": False,
        "developers/weaviate/_vectorization/vectorizer-comparisons.md": False,
        "developers/contributor-guide/weaviate-core/parsing-cross-refs.md": True,
        "developers/academy/standalone/index.md": True,
        "developers/_academy/standalone/index.md": False,
        "developers/academy/standalone/_index.md": False,
    }

    for document, expected_result in test_cases.items():
        assert preprocess_weaviate.document_filtering(document) == expected_result


def test_document_cleaning():
    # Test cases to assert
    test_cases = {
        """---
        title: Weaviate Clients
        sidebar_position: 0
        image: og/contributor-guide/weaviate-clients.jpg
        # tags: ['contributor-guide', 'clients']
        ---
        # Contributor guidelines""": "# Contributor guidelines",
        """:::note Vector spaces and Expore{}

        The `Explore` function is currently not available on Weaviate Cloud Services (WCS) instances, or others where it is likely that multiple vector spaces will exist.

        As WCS by default enables multiple inference-API modules and therefore multiple vector spaces, `Explore` is disabled by default by Weaviate.

        :::""": """
        The `Explore` function is currently not available on Weaviate Cloud Services (WCS) instances, or others where it is likely that multiple vector spaces will exist.

        As WCS by default enables multiple inference-API modules and therefore multiple vector spaces, `Explore` is disabled by default by Weaviate.
        """,
        "Meow": "Meow",
        """import GraphQLExploreVec from '/_includes/code/graphql.explore.vector.mdx';

        <GraphQLExploreVec/>

        The result might look like this:""": """The result might look like this:""",
    }

    for document, expected_result in test_cases.items():
        assert (
            preprocess_weaviate.document_cleaning(document).strip()
            == expected_result.strip()
        )
