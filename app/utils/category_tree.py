from collections import defaultdict


def build_category_tree(categories):
    tree = defaultdict(list)

    for cat in categories:
        tree[cat.parent_category_id].append(cat)

    return tree


def build_full_path(category, lookup):
    path = []

    while category:
        path.append(category.name)

        parent_id = getattr(category, "parent_category_id", None)

        if parent_id is not None and parent_id in lookup:
            category = lookup[parent_id]
            continue

        category = getattr(category, "parent", None)

    return " > ".join(reversed(path))


def build_category_full_paths(categories):
    lookup = {
        category.category_id: category
        for category in categories
    }

    return {
        category.category_id: build_full_path(
            category,
            lookup,
        )
        for category in categories
    }