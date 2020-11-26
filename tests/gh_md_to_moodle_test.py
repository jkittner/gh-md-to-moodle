import os

import pytest

from gh_md_to_moodle import _remove_newline_from_code
from gh_md_to_moodle import main


@pytest.fixture()
def md_dummy():
    def _create_dummy_file(contents):
        with open('testing.md', 'w') as f:
            f.write(contents)
    return _create_dummy_file


def test_argparse_shows_help_no_args():
    with pytest.raises(SystemExit):
        main(['--help'])


@pytest.mark.parametrize(
    ('content', 'exp'),
    (
        pytest.param(
            '', '''\
<script>
 var stylesheet =
  "https://github.githubassets.com/assets/gist-embed-52b3348036dbd45f4ab76e44de42ebc4.css";
var head = document.getElementsByTagName("head")[0];
var link = document.createElement("link");
link.rel = "stylesheet";
link.href = stylesheet;
head.appendChild(link);
// add custom css to make syntax-hl bigger font-size
var css = `
    .highlight {
        font-size: 1rem !important;
    }
    .box-body {
        padding: 1rem !important;
    }
    .code-container {
        width: 100%;
        padding-right: 15px;
        padding-left: 15px;
        margin-right: auto;
        margin-left: auto;
        max-width: 1140px;
    }
    code {
        color: #e83e8c;
        word-wrap: break-word;
    }`;
var style = document.createElement("style");
head.appendChild(style);
style.appendChild(document.createTextNode(css));
</script>''', id='js file contents are present',
        ),
        pytest.param(
            '# this is a h1!',
            'this is a h1!\n        </h1>',
            id='h1',
        ),
        pytest.param(
            '## this is a h2!',
            'this is a h2!\n        </h2>',
            id='h2',
        ),
        pytest.param(
            '- this\n- is\n- a\n- list',
            '''\
        <ul>
         <li>
          this
         </li>
         <li>
          is
         </li>
         <li>
          a
         </li>
         <li>
          list
         </li>
        </ul>''',
            id='list',
        ),
        pytest.param(
            'this is normal text',
            '<p>\n         this is normal text\n        </p>',
            id='normal_text',
        ),
        pytest.param(
            '```py\ndef func():\n    ...\n```',
            '''\
        <div class="highlight highlight-source-python">
         <pre><span class="pl-k">def</span> <span class="pl-en">func</span>():
    ...</pre>
        </div>''',
            id='code_block',
        ),
        pytest.param(
            '--------',
            '<hr/>\n       </article>',
            id='horizontal_rule',
        ),
        pytest.param(
            '# header with `inline_code`!',
            '<code>inline_code</code>',
            id='inline_code',
        ),
    ),
)
def test_convert_md_contains(content, exp, tmpdir, md_dummy):
    with tmpdir.as_cwd():
        md_dummy(content)
        args = ['testing.md', 'test.html']
        main(args)
        with open('test.html') as f:  # also checks that file exists
            contents = f.read()

    assert exp in contents


@pytest.mark.parametrize(
    ('code', 'exp'),
    (
        pytest.param(
            '<code>\n  foo\n   </code>',
            '<code>foo</code>',
            id='newlines_rm',
        ),
        pytest.param(
            '\n<code>\n  foo\n   </code>\n',
            '\n<code>foo</code>\n',
            id='newlines_kept_end_ws_stripped',
        ),
    ),
)
def test_remove_newline_from_code_tag(code, exp):
    new_code = _remove_newline_from_code(code)
    print(code)
    print(new_code)
    assert new_code == exp


def test_css_folder_is_not_created(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        md_dummy('# foo')
        args = ['testing.md', 'test.html']
        main(args)
        contents = os.listdir(tmpdir)
        assert 'github-markdown-css' not in contents
