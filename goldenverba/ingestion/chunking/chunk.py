class Chunk:
    def __init__(
        self,
        text: str = "",
        doc_name: str = "",
        doc_type: str = "",
        doc_uuid: str = "",
        chunk_id: str = "",
    ):
        self._text = text
        self._doc_name = doc_name
        self._doc_type = doc_type
        self._doc_uuid = doc_uuid
        self._chunk_id = chunk_id

    @property
    def text(self):
        return self._text

    @property
    def text_no_overlap(self):
        return self._text_no_overlap

    @property
    def doc_name(self):
        return self._doc_name

    @property
    def doc_type(self):
        return self._doc_type

    @property
    def doc_uuid(self):
        return self._doc_uuid

    @property
    def chunk_id(self):
        return self._chunk_id
