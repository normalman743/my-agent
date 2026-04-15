from models.search.google_search import GoogleSearch

class SearchEngine:
    def __init__(self):
        self.engine = GoogleSearch()
    
    def search(self, query):
        return self.engine.search(query)



# from models.search.bing_search import BingSearch
# from models.search.duckduckgo_search import DuckDuckGoSearch
# from models.search.google_search import GoogleSearch

# class SearchEngine:
#     def __init__(self, engine_type):
#         self.engine = self._initialize_engine(engine_type)
    
#     def _initialize_engine(self, engine_type):
#         if engine_type == 'bing':
#             return BingSearch()
#         elif engine_type == 'duckduckgo':
#             return DuckDuckGoSearch()
#         elif engine_type == 'google':
#             return GoogleSearch()
#         else:
#             raise ValueError("Unsupported search engine type")
    
#     def search(self, query):
#         return self.engine.search(query)
