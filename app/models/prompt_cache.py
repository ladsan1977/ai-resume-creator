class PromptCache:
    def __init__(self):
        self.cache = {}
    
    def get_cached_prompt(self, key):
        return self.cache.get(key)
    
    def add_to_cache(self, key, prompt):
        self.cache[key] = prompt