# Relative Path Resolver

Computes the shortest relative path from one directory to another, raising a clear error when the two paths share no common root.

## Usage

```python
from relative_path_resolver import relative_path, DifferentRootError

relative_path('/a/b', '/a/c')   # '../c'
relative_path('/a', '/a/b/c')   # 'b/c'
relative_path('/a/b', '/a/b')   # '.'

try:
    relative_path('/a', 'C:\\b')
except DifferentRootError:
    ...  # paths do not share a root
```

## Why

`os.path.relpath` exists in the standard library, but its behaviour across different roots is platform-dependent and produces results that are rarely what the caller intended. This library makes one explicit choice: if the two paths do not share a root, it raises `DifferentRootError` instead of returning a meaningless chain of `..` segments.

## Edge cases

- Both arguments are treated as directories. There is no special handling for file paths.
- Paths are normalized before comparison, so `/a/./b` and `/a/b` are equivalent, and trailing slashes are ignored.
- Relative paths (no leading separator) are considered to share a relative root; `relative_path('a/b', 'a/c')` returns `'../c'`.
