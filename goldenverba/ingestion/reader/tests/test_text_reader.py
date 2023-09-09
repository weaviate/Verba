from goldenverba.ingestion.reader.manager import ReaderManager


def test_text_reader():
    manager = ReaderManager()
    assert manager.set_reader("TextReader") == True

    documents = manager.load(["./data"])
    assert len(documents) == 3


def test_text_reader_file():
    manager = ReaderManager()
    assert manager.set_reader("TextReader") == True

    documents = manager.load(["./data/test.txt"])
    assert len(documents) == 1
    assert documents[0].text == "This is a test"


def test_text_reader_not_exist():
    manager = ReaderManager()
    assert manager.set_reader("TextReader") == True

    documents = manager.load(["./data/testtest.txt"])
    assert len(documents) == 0


def test_text_reader_json():
    manager = ReaderManager()
    assert manager.set_reader("TextReader") == True

    documents = manager.load(["./data/subfolder/test3.json"])
    assert len(documents) == 0


def test_text_reader_folder():
    manager = ReaderManager()
    assert manager.set_reader("TextReader") == True

    documents = manager.load(["./data/subfolder"])
    assert len(documents) == 2
