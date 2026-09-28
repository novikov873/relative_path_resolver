import os


class DifferentRootError(ValueError):
    """Raised when two paths have no common ancestor.

    On POSIX this means the paths do not share the same root (e.g. /a vs /b
    is fine — they share / — but /a and C:\\b would not, though that mix is
    only reachable via explicit construction). We raise rather than silently
    producing a long ../.. chain because a silent result across roots is the
    kind of bug that ships to production unnoticed.
    """


def _split(path):
    """Split a normalized path into a tuple of components.

    We normalize via os.path.normpath so that redundant separators, '.' and
    '..' are collapsed before comparison. normpath also strips trailing
    slashes, which means '/a/' and '/a' compare equal — that is the
    behaviour we want.
    """
    normalized = os.path.normpath(path)
    head, tail = os.path.split(normalized)
    parts = []
    if tail:
        parts.append(tail)
    while head and head not in (os.sep, os.curdir):
        head, tail = os.path.split(head)
        if tail:
            parts.append(tail)
        if head == os.sep:
            break
    parts.reverse()
    root = _root(path)
    if root:
        parts = [root.rstrip(os.sep)] + parts
    return tuple(parts)


def _root(path):
    """Return the root component of a path, or '' if it is relative."""
    drive, rest = os.path.splitdrive(path)
    if drive:
        return drive + os.sep
    if path.startswith(os.sep):
        return os.sep
    return ""


def common_ancestor(from_dir, to_dir):
    """Return the shared ancestor directory of two paths.

    Returns an empty string if the paths have no shared ancestor (different
    roots on the same platform, or both relative with no common prefix
    component).
    """
    if _root(from_dir) != _root(to_dir):
        return ""
    a = _split(from_dir)
    b = _split(to_dir)
    common = []
    for x, y in zip(a, b):
        if x == y:
            common.append(x)
        else:
            break
    if not common:
        return ""
    if common == ['']:
        return ""
    return os.sep.join(common)


def relative_path(from_dir, to_dir):
    """Compute the shortest relative path from *from_dir* to *to_dir*.

    Both arguments are treated as directories. The result uses '..' to climb
    out of *from_dir* and then descends into *to_dir*.

    Raises DifferentRootError if the paths do not share a root.

    Examples (POSIX)::

        relative_path('/a/b', '/a')      == '..'
        relative_path('/a/b', '/a/c')    == '../c'
        relative_path('/a', '/a/b/c')    == 'b/c'
        relative_path('/a/b', '/a/b')    == '.'
    """
    if _root(from_dir) != _root(to_dir):
        raise DifferentRootError(
            "Paths {!r} and {!r} have different roots".format(from_dir, to_dir)
        )

    a = _split(from_dir)
    b = _split(to_dir)

    i = 0
    for x, y in zip(a, b):
        if x == y:
            i += 1
        else:
            break

    up = len(a) - i
    down = b[i:]

    if up == 0 and not down:
        return "."

    pieces = [".."] * up + list(down)
    return os.path.join(*pieces) if pieces else "."
