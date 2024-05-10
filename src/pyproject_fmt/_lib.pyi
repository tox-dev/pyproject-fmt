def format_toml(  # noqa: PLR0913
    content: str,
    *,
    column_width: int,
    indent: int,
    keep_full_version: bool,
    max_supported_python: tuple[int, int],
    min_supported_python: tuple[int, int],
) -> str: ...
