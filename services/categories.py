from repos.categories_repo import list_categories_by_kind, insert_category

def get_categories(kind: str) -> list[str]:
    return list_categories_by_kind(kind)

def add_category(name: str, kind: str) -> None:
    insert_category(name, kind)