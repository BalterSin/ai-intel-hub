from ..config.config import Config

def get_retriever(retriever: str):
    """
    Gets the retriever
    Args:
        retriever (str): retriever name

    Returns:
        retriever: Retriever class

    """
    match retriever:

        case "tavily":
            from seres_researcher.search_tools import TavilySearch

            return TavilySearch
        case "ali_search":
            from seres_researcher.search_tools import AliSearch
            
            return AliSearch

        case _:
            return None


def get_retrievers(headers: dict[str, str], cfg: Config):
    """
    Determine which retriever(s) to use based on headers, config, or default.

    Args:
        headers (dict): The headers dictionary
        cfg (Config): The configuration object

    Returns:
        list: A list of retriever classes to be used for searching.
    """
    # Check headers first for multiple retrievers
    if headers.get("retrievers"):
        retrievers = headers.get("retrievers").split(",")
    # If not found, check headers for a single retriever
    elif headers.get("retriever"):
        retrievers = [headers.get("retriever")]
    # If not in headers, check config for multiple retrievers
    elif cfg.retrievers:
        retrievers = cfg.retrievers
    # If not found, check config for a single retriever
    elif cfg.retriever:
        retrievers = [cfg.retriever]
    # If still not set, use default retriever
    else:
        retrievers = [get_default_retriever().__name__]

    # Convert retriever names to actual retriever classes
    # Use get_default_retriever() as a fallback for any invalid retriever names
    return [get_retriever(r) or get_default_retriever() for r in retrievers]


def get_default_retriever():
    from seres_researcher.search_tools import TavilySearch

    return TavilySearch