from src.collectors.api_collector import APICollector
def collect(cfg): return APICollector().jsonplaceholder(cfg)
