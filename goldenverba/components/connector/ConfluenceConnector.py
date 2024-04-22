from goldenverba.components.connector.AtlassianConnector import AtlassianConnector


class ConfluenceConnector(AtlassianConnector):
    def __init__(self, base_url, access_token):
        super().__init__(base_url, access_token, "/confluence")

    def getSpace(self, space):
        return self.getRessource(f"space/{space}")

    def getPage(self, page_id, *, params=None):
        return self.getRessource(f"content/{page_id}", params=params)

    def getChildren(self, page_id, *, params=None):
        return self.getRessource(f"content/{page_id}/child/page").get("results")
