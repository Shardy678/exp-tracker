from repos.categories_repo import list_categories_by_kind

def get_categories(kind: str) -> list[str]:
    return list_categories_by_kind(kind)
