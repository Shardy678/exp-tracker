from repos.categories_repo import list_categories_by_kind, insert_category, list_all_categories

def get_categories(kind: str) -> list[str]:
    return list_categories_by_kind(kind)

def get_all_categories() -> list[dict]:
    return list_all_categories()

def add_category(name: str, kind: str) -> None:
    insert_category(name, kind)