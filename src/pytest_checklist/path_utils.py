from pathlib import Path

INIT_FNAME = "__init__.py"


def find_top_level_module_dir(dirpath: Path) -> Path | None:
    """Search up for a directory not containing __init__.py."""

    dirpath = dirpath.resolve()

    # first figure out if this is a module containing directory
    if not (dirpath / INIT_FNAME).exists():

        # check one level down to see if any directory below has
        # __init__.py in them, which makes this a search path

        is_search_dir = False
        for subdir in dirpath.iterdir():

            if (subdir / INIT_FNAME).exists():
                is_search_dir = True
                break

        if is_search_dir:
            return dirpath

        # if not then this is not a search path and you won't find one
        # either
        else:

            return None

    # otherwise we go up to find it
    else:

        # search the current directory first
        for parent in [dirpath] + list(dirpath.parents):
            if not (parent / INIT_FNAME).exists():
                return parent

    return None
