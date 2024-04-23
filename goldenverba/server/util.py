from goldenverba.components.interfaces import Reader, Chunker, Embedder, Retriever, Generator
from goldenverba.verba_manager import VerbaManager


def setup_managers(
    manager, config_manager, readers, chunker, embedders, retrievers, generators
):
    if config_manager.get_reader() == "":
        for reader in readers:
            available = manager.check_verba_component(readers[reader])
            if available:
                manager.reader_set_reader(reader)
                config_manager.set_reader(reader)
                break
    else:
        if config_manager.get_reader() in readers:
            available = manager.check_verba_component(
                readers[config_manager.get_reader()]
            )
            if available:
                manager.reader_set_reader(config_manager.get_reader())
            else:
                for reader in readers:
                    available = manager.check_verba_component(readers[reader])
                    if available:
                        manager.reader_set_reader(reader)
                        config_manager.set_reader(reader)
                        break

    if config_manager.get_chunker() == "":
        for chunk in chunker:
            available = manager.check_verba_component(chunker[chunk])
            if available:
                manager.chunker_set_chunker(chunk)
                config_manager.set_chunker(chunk)
                break
    else:
        if config_manager.get_chunker() in chunker:
            available = manager.check_verba_component(
                chunker[config_manager.get_chunker()]
            )
            if available:
                manager.chunker_set_chunker(config_manager.get_chunker())
            else:
                for chunk in chunker:
                    available = manager.check_verba_component(chunker[chunk])
                    if available:
                        manager.chunker_set_chunker(chunk)
                        config_manager.set_chunker(chunk)
                        break

    if config_manager.get_embedder() == "":
        for embedder in embedders:
            available = manager.check_verba_component(embedders[embedder])
            if available:
                manager.embedder_set_embedder(embedder)
                config_manager.set_embedder(embedder)
                break
    else:
        if config_manager.get_embedder() in embedders:
            available = manager.check_verba_component(
                embedders[config_manager.get_embedder()]
            )
            if available:
                manager.embedder_set_embedder(config_manager.get_embedder())
            else:
                for embedder in embedders:
                    available = manager.check_verba_component(
                        embedders[embedder]
                    )
                    if available:
                        manager.embedder_set_embedder(embedder)
                        config_manager.set_embedder(embedder)
                        break

    if config_manager.get_retriever() == "":
        for retriever in retrievers:
            available = manager.check_verba_component(retrievers[retriever])
            if available:
                manager.retriever_set_retriever(retriever)
                config_manager.set_retriever(retriever)
                break
    else:
        if config_manager.get_retriever() in retrievers:
            available = manager.check_verba_component(
                retrievers[config_manager.get_retriever()]
            )
            if available:
                manager.retriever_set_retriever(config_manager.get_retriever())
            else:
                for retriever in retrievers:
                    available = manager.check_verba_component(
                        retrievers[retriever]
                    )
                    if available:
                        manager.retriever_set_retriever(retriever)
                        config_manager.set_retriever(retriever)
                        break

    if config_manager.get_generator() == "":
        for generator in generators:
            available = manager.check_verba_component(generators[generator])
            if available:
                manager.generator_set_generator(generator)
                config_manager.set_generator(generator)
                break
    else:
        if config_manager.get_generator() in generators:
            available = manager.check_verba_component(
                generators[config_manager.get_generator()]
            )
            if available:
                manager.generator_set_generator(config_manager.get_generator())
            else:
                for generator in generators:
                    available = manager.check_verba_component(
                        generators[generator]
                    )
                    if available:
                        manager.generator_set_generator(generator)
                        config_manager.set_generator(generator)
                        break


def create_reader_payload(manager, key: str, reader: Reader) -> dict:
    available, message = manager.check_verba_component(reader)
    return {
        "name": key,
        "description": reader.description,
        "input_form": reader.input_form,
        "available": available,
        "message": message,
    }


def create_chunker_payload(manager, key: str, chunker: Chunker) -> dict:
    available, message = manager.check_verba_component(chunker)

    return {
        "name": key,
        "description": chunker.description,
        "input_form": chunker.input_form,
        "units": chunker.default_units,
        "overlap": chunker.default_overlap,
        "available": available,
        "message": message,
    }


def create_embedder_payload(manager, key: str, embedder: Embedder) -> dict:
    available, message = manager.check_verba_component(embedder)

    return {
        "name": key,
        "description": embedder.description,
        "input_form": embedder.input_form,
        "available": available,
        "message": message,
    }


def create_retriever_payload(manager, key: str, retriever: Retriever) -> dict:
    available, message = manager.check_verba_component(retriever)

    return {
        "name": key,
        "description": retriever.description,
        "available": available,
        "message": message,
    }


def create_generator_payload(manager, key: str, generator: Generator) -> dict:
    available, message = manager.check_verba_component(generator)

    return {
        "name": key,
        "description": generator.description,
        "available": available,
        "message": message,
        "streamable": generator.streamable,
    }


def get_config(manager: VerbaManager) -> dict:

    available_environments = manager.environment_variables
    available_libraries = manager.installed_libraries

    readers = manager.reader_manager.get_readers()
    reader_config = {"components":{reader: readers[reader].get_meta(available_environments,available_libraries) for reader in readers}, "selected": manager.reader_manager.selected_reader}

    chunkers = manager.chunker_manager.get_chunkers()
    chunkers_config = {"components":{chunker: chunkers[chunker].get_meta(available_environments,available_libraries) for chunker in chunkers}, "selected": manager.chunker_manager.selected_chunker}

    embedders = manager.embedder_manager.get_embedders()
    embedder_config = {"components":{embedder: embedders[embedder].get_meta(available_environments,available_libraries) for embedder in embedders}, "selected": manager.embedder_manager.selected_embedder}

    retrievers = manager.retriever_manager.get_retrievers()
    retrievers_config = {"components":{retriever: retrievers[retriever].get_meta(available_environments,available_libraries) for retriever in retrievers}, "selected": manager.retriever_manager.selected_retriever}

    generators = manager.generator_manager.get_generators()
    generator_config = {"components":{generator: generators[generator].get_meta(available_environments,available_libraries) for generator in generators}, "selected": manager.generator_manager.selected_generator}

    return {"Reader": reader_config, "Chunker":chunkers_config, "Embedder":embedder_config, "Retriever":retrievers_config, "Generator": generator_config}


def set_config(manager: VerbaManager, config: dict):

    # Set Selected
    manager.reader_manager.set_reader(config.get("Reader",{}).get("selected",""))
    manager.chunker_manager.set_chunker(config.get("Chunker",{}).get("selected",""))
    manager.embedder_manager.set_embedder(config.get("Embedder",{}).get("selected",""))
    manager.retriever_manager.set_retriever(config.get("Retriever",{}).get("selected",""))
    manager.generator_manager.set_generator(config.get("Generator",{}).get("selected",""))

    # Set Config
    readers = manager.reader_manager.get_readers()
    for _reader in config.get("Reader",{}).get("components",{}):
        if _reader in readers:
            readers[_reader].set_config(config.get("Reader",{}).get("components",{}).get(_reader,{}).get("config",{}))

    chunkers = manager.chunker_manager.get_chunkers()
    for _chunker in config.get("Chunker",{}).get("components",{}):
        if _chunker in chunkers:
            chunkers[_chunker].set_config(config.get("Chunker",{}).get("components",{}).get(_chunker,{}).get("config",{}))

    embedders = manager.embedder_manager.get_embedders()
    for _embedder in config.get("Embedder",{}).get("components",{}):
        if _embedder in embedders:
            embedders[_embedder].set_config(config.get("Embedder",{}).get("components",{}).get(_chunker,{}).get("config",{}))

    retrievers = manager.retriever_manager.get_retrievers()
    for _retriever in config.get("Retriever",{}).get("components",{}):
        if _retriever in retrievers:
            retrievers[_retriever].set_config(config.get("Retriever",{}).get("components",{}).get(_chunker,{}).get("config",{}))

    generators = manager.generator_manager.get_generators()
    for _generator in config.get("Generator",{}).get("components",{}):
        if _generator in generators:
            generators[_generator].set_config(config.get("Generator",{}).get("components",{}).get(_chunker,{}).get("config",{}))



