import argparse
import os
import re
import sys
import tempfile
from typing import Optional
from typing import Sequence

from bs4 import BeautifulSoup
from gh_md_to_html import main as convert_md

if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
    import importlib_metadata
    import importlib_resources
else:  # pragma: no cover (<py38)
    import importlib.metadata as importlib_metadata
    import importlib.resources as importlib_resources


def _remove_newline_from_code(html: str) -> str:
    html = re.sub(r'<code>(\s)+', '<code>', html)
    html = re.sub(r'(\s)+</code>', '</code>', html)
    return html


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog='gh-md-to-moodle')
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {importlib_metadata.version("gh_md_to_moodle")}',
    )
    parser.add_argument(
        'origin',
        type=str,
        help='markdown file to be converted',
    )
    parser.add_argument(
        'destination',
        type=str,
        help='path to output directory',
    )
    args = parser.parse_args(argv)

    # convert the markdown
    # pass this output to a temporary dir
    with tempfile.TemporaryDirectory() as tmpdir:
        convert_md(md_origin=args.origin, destination=tmpdir, css_paths=tmpdir)
        raw_html = os.path.join(
            tmpdir,
            re.sub(r'\.md$', '.html', os.path.basename(args.origin)),
        )
        with open(raw_html) as f:
            html_str = f.read()
    add_style_js = importlib_resources.read_text('resources', 'add_style.js')
    contents = (
        f'<script>{add_style_js}</script>'
        f'<div class="code-container">{html_str}</div>'
    )
    soup = BeautifulSoup(contents, 'html.parser')
    pretty_html = soup.prettify()
    # remove newlines form code tag
    pretty_html = _remove_newline_from_code(pretty_html)
    with open(args.destination, 'w') as f:
        f.write(pretty_html)
    return 0


if __name__ == '__main__':
    exit(main())
