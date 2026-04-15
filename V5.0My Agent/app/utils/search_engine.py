from models.search.google_search import GoogleSearch

class SearchEngine:
    def __init__(self):
        self.engine = GoogleSearch()
    
    def search(self, query):
        return self.engine.search(query)


