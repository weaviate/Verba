from goldenverba.verba_manager import VerbaManager

import json
import os

from wasabi import msg  # type: ignore[import]

config_uuid = "e0adcc12-9bad-4588-8a1e-bab0af6ed485"


def setup_managers(manager):
    msg.info("Setting up components")
    config = load_config(manager)
    set_config(manager, config)


def get_config(manager: VerbaManager) -> dict:

    config = {}

    exists = manager.client.data_object.exists(
    config_uuid,
    class_name="VERBA_Config",
    )

    if exists:
        document = manager.client.data_object.get_by_id(
                config_uuid,
                class_name="VERBA_Config",
        )
        config = json.loads(document["properties"]["config"])

    setting_config = config.get("SETTING", {})

    available_environments = manager.environment_variables
    available_libraries = manager.installed_libraries

    readers = manager.reader_manager.get_readers()
    reader_config = {
        "components": {
            reader: readers[reader].get_meta(
                available_environments, available_libraries
            )
            for reader in readers
        },
        "selected": manager.reader_manager.selected_reader,
    }

    chunkers = manager.chunker_manager.get_chunkers()
    chunkers_config = {
        "components": {
            chunker: chunkers[chunker].get_meta(
                available_environments, available_libraries
            )
            for chunker in chunkers
        },
        "selected": manager.chunker_manager.selected_chunker,
    }

    embedders = manager.embedder_manager.get_embedders()
    embedder_config = {
        "components": {
            embedder: embedders[embedder].get_meta(
                available_environments, available_libraries
            )
            for embedder in embedders
        },
        "selected": manager.embedder_manager.selected_embedder,
    }

    retrievers = manager.retriever_manager.get_retrievers()
    retrievers_config = {
        "components": {
            retriever: retrievers[retriever].get_meta(
                available_environments, available_libraries
            )
            for retriever in retrievers
        },
        "selected": manager.retriever_manager.selected_retriever,
    }

    generators = manager.generator_manager.get_generators()
    generator_config = {
        "components": {
            generator: generators[generator].get_meta(
                available_environments, available_libraries
            )
            for generator in generators
        },
        "selected": manager.generator_manager.selected_generator,
    }

    return {
        "RAG": {
            "Reader": reader_config,
            "Chunker": chunkers_config,
            "Embedder": embedder_config,
            "Retriever": retrievers_config,
            "Generator": generator_config,
        },
        "SETTING": setting_config,
    }


def set_config(manager: VerbaManager, combined_config: dict):

    save_config(manager, combined_config)
    config = combined_config.get("RAG", {})

    selected_theme = combined_config.get("SETTING", {}).get("selectedTheme", "")
    enable_caching = (
        combined_config.get("SETTING", {})
        .get("themes", {})
        .get(selected_theme, {})
        .get("Chat", {})
        .get("settings", {})
        .get("caching", {})
        .get("checked", True)
    )
    if manager.enable_caching != enable_caching:
        msg.info(f"Changing Caching from {manager.enable_caching} to {enable_caching} ")
        manager.enable_caching = enable_caching

    # Set Selected
    manager.reader_manager.set_reader(config.get("Reader", {}).get("selected", ""))
    manager.chunker_manager.set_chunker(config.get("Chunker", {}).get("selected", ""))
    manager.embedder_manager.set_embedder(
        config.get("Embedder", {}).get("selected", "")
    )
    manager.retriever_manager.set_retriever(
        config.get("Retriever", {}).get("selected", "")
    )
    manager.generator_manager.set_generator(
        config.get("Generator", {}).get("selected", "")
    )

    # Set Config
    readers = manager.reader_manager.get_readers()
    for _reader in config.get("Reader", {}).get("components", {}):
        if _reader in readers:
            readers[_reader].set_config(
                config.get("Reader", {})
                .get("components", {})
                .get(_reader, {})
                .get("config", {})
            )

    chunkers = manager.chunker_manager.get_chunkers()
    for _chunker in config.get("Chunker", {}).get("components", {}):
        if _chunker in chunkers:
            chunkers[_chunker].set_config(
                config.get("Chunker", {})
                .get("components", {})
                .get(_chunker, {})
                .get("config", {})
            )

    embedders = manager.embedder_manager.get_embedders()
    for _embedder in config.get("Embedder", {}).get("components", {}):
        if _embedder in embedders:
            embedders[_embedder].set_config(
                config.get("Embedder", {})
                .get("components", {})
                .get(_chunker, {})
                .get("config", {})
            )

    retrievers = manager.retriever_manager.get_retrievers()
    for _retriever in config.get("Retriever", {}).get("components", {}):
        if _retriever in retrievers:
            retrievers[_retriever].set_config(
                config.get("Retriever", {})
                .get("components", {})
                .get(_chunker, {})
                .get("config", {})
            )

    generators = manager.generator_manager.get_generators()
    for _generator in config.get("Generator", {}).get("components", {}):
        if _generator in generators:
            generators[_generator].set_config(
                config.get("Generator", {})
                .get("components", {})
                .get(_chunker, {})
                .get("config", {})
            )


def save_config(manager: VerbaManager, config: dict):
    """Save config to file."""

    exists = manager.client.data_object.exists(
    config_uuid,
    class_name="VERBA_Config",
    )

    if exists:
        manager.client.data_object.delete(uuid=config_uuid, class_name="VERBA_Config")

    with manager.client.batch as batch:
        batch.batch_size = 1
        properties = {
            "config": json.dumps(config),
        }
        manager.client.batch.add_data_object(properties, "VERBA_Config", uuid=config_uuid)
        msg.good("Config Saved in Weaviate")


def load_config(manager):
    """Save config to file."""
    
    exists = manager.client.data_object.exists(
    config_uuid,
    class_name="VERBA_Config",
    )

    if exists:
        document = manager.client.data_object.get_by_id(
                config_uuid,
                class_name="VERBA_Config",
        )

        config = json.loads(document["properties"]["config"])
        msg.info("Retrieve Config From Weaviate")
        return config

    return get_config(manager)
