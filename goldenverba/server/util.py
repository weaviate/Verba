def setup_managers(
    manager, config_manager, readers, chunker, embedders, retrievers, generators
):
    if config_manager.get_reader() == "":
        for reader in readers:
            available, message = manager.check_verba_component(readers[reader])
            if available:
                manager.reader_set_reader(reader)
                config_manager.set_reader(reader)
                break
    else:
        if config_manager.get_reader() in readers:
            available, message = manager.check_verba_component(
                readers[config_manager.get_reader()]
            )
            if available:
                manager.reader_set_reader(config_manager.get_reader())
            else:
                for reader in readers:
                    available, message = manager.check_verba_component(readers[reader])
                    if available:
                        manager.reader_set_reader(reader)
                        config_manager.set_reader(reader)
                        break

    if config_manager.get_chunker() == "":
        for chunk in chunker:
            available, message = manager.check_verba_component(chunker[chunk])
            if available:
                manager.chunker_set_chunker(chunk)
                config_manager.set_chunker(chunk)
                break
    else:
        if config_manager.get_chunker() in chunker:
            available, message = manager.check_verba_component(
                chunker[config_manager.get_chunker()]
            )
            if available:
                manager.chunker_set_chunker(config_manager.get_chunker())
            else:
                for chunk in chunker:
                    available, message = manager.check_verba_component(chunker[chunk])
                    if available:
                        manager.chunker_set_chunker(chunk)
                        config_manager.set_chunker(chunk)
                        break

    if config_manager.get_embedder() == "":
        for embedder in embedders:
            available, message = manager.check_verba_component(embedders[embedder])
            if available:
                manager.embedder_set_embedder(embedder)
                config_manager.set_embedder(embedder)
                break
    else:
        if config_manager.get_embedder() in embedders:
            available, message = manager.check_verba_component(
                embedders[config_manager.get_embedder()]
            )
            if available:
                manager.embedder_set_embedder(config_manager.get_embedder())
            else:
                for embedder in embedders:
                    available, message = manager.check_verba_component(
                        embedders[embedder]
                    )
                    if available:
                        manager.embedder_set_embedder(embedder)
                        config_manager.set_embedder(embedder)
                        break

    if config_manager.get_retriever() == "":
        for retriever in retrievers:
            available, message = manager.check_verba_component(retrievers[retriever])
            if available:
                manager.retriever_set_retriever(retriever)
                config_manager.set_retriever(retriever)
                break
    else:
        if config_manager.get_retriever() in retrievers:
            available, message = manager.check_verba_component(
                retrievers[config_manager.get_retriever()]
            )
            if available:
                manager.retriever_set_retriever(config_manager.get_retriever())
            else:
                for retriever in retrievers:
                    available, message = manager.check_verba_component(
                        retrievers[retriever]
                    )
                    if available:
                        manager.retriever_set_retriever(retriever)
                        config_manager.set_retriever(retriever)
                        break

    if config_manager.get_generator() == "":
        for generator in generators:
            available, message = manager.check_verba_component(generators[generator])
            if available:
                manager.generator_set_generator(generator)
                config_manager.set_generator(generator)
                break
    else:
        if config_manager.get_generator() in generators:
            available, message = manager.check_verba_component(
                generators[config_manager.get_generator()]
            )
            if available:
                manager.generator_set_generator(config_manager.get_generator())
            else:
                for generator in generators:
                    available, message = manager.check_verba_component(
                        generators[generator]
                    )
                    if available:
                        manager.generator_set_generator(generator)
                        config_manager.set_generator(generator)
                        break
