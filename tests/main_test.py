import os
from unittest import mock

import pytest

import gh_md_to_moodle.main
from gh_md_to_moodle.main import _remove_newline_from_code
from gh_md_to_moodle.main import main


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
    assert new_code == exp


def test_css_folder_is_not_created(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        md_dummy('# foo')
        args = ['testing.md', 'test.html']
        main(args)
        contents = os.listdir(tmpdir)
        assert 'github-markdown-css' not in contents


def test_single_img_with_link(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        link = 'https://i.fluffy.cc/KT532NcD7QsGgd6zTXsbQsm6lX7sMrCD.png'
        md_dummy(f'![alt_text]({link})')
        args = ['testing.md', 'test.html']
        main(args)
        with open('test.html') as f:  # also checks that file exists
            contents = f.read()
        assert f'<a href="{link}" rel="nofollow" target="_blank">' in contents
        assert (
            f'<img alt="alt_text" data-canonical-src="{link}" src="{link}" '
            'style="max-width:100%; max-height: 480px;"/>'
        ) in contents


def test_multiple_img_with_link(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        link_a = 'https://i.fluffy.cc/KT532NcD7QsGgd6zTXsbQsm6lX7sMrCD.png'
        link_b = 'https://i.fluffy.cc/9dgJNxvRbHXjlTvDM3cC74NTpkqqN468.png'
        md_dummy(
            f'![alt_text]({link_a})\n\n'
            f'![alt_text]({link_b})',
        )
        args = ['testing.md', 'test.html']
        main(args)
        with open('test.html') as f:  # also checks that file exists
            contents = f.read()

        # first link
        assert (
            f'<a href="{link_a}" rel="nofollow" target="_blank">'
        ) in contents
        assert (
            f'<img alt="alt_text" data-canonical-src="{link_a}" src="{link_a}"'
            ' style="max-width:100%; max-height: 480px;"/>'
        ) in contents

        # second link
        assert (
            f'<a href="{link_b}" rel="nofollow" target="_blank">'
        ) in contents
        assert (
            f'<img alt="alt_text" data-canonical-src="{link_b}" src="{link_b}"'
            ' style="max-width:100%; max-height: 480px;"/>'
        ) in contents


def test_regular_links_are_not_converted(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        link_a = 'https://i.fluffy.cc/KT532NcD7QsGgd6zTXsbQsm6lX7sMrCD.png'
        link_b = 'https://i.fluffy.cc/9dgJNxvRbHXjlTvDM3cC74NTpkqqN468.png'
        md_dummy(
            f'[this is a link]({link_a})\n\n'
            f'![alt_text]({link_b})',
        )
        args = ['testing.md', 'test.html']
        main(args)
        with open('test.html') as f:  # also checks that file exists
            contents = f.read()

        # regular link
        assert f'<a href="{link_a}" rel="nofollow">this is a link</a>'

        # image
        assert (
            f'<a href="{link_b}" rel="nofollow" target="_blank">'
        ) in contents
        assert (
            f'<img alt="alt_text" data-canonical-src="{link_b}" src="{link_b}"'
            ' style="max-width:100%; max-height: 480px;"/>'
        ) in contents


def test_local_imgs(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        # mock an image file
        img_dir = 'local/img'
        os.makedirs(img_dir, exist_ok=True)
        link = f'{img_dir}/test.png'
        with open(link, 'w') as f:
            f.write('foo')

        md_dummy(f'![alt_text]({link})')
        args = ['testing.md', 'test.html']
        main(args)
        with open('test.html') as f:  # also checks that file exists
            contents = f.read()
        assert (
            f'<a href="{link}" rel="noopener noreferrer" target="_blank">'
        ) in contents
        assert (
            f'<img alt="alt_text" data-canonical-src="{link}" src="{link}" '
            'style="max-width:100%;"/>'
        ) in contents


def test_rate_limit_exceeded(tmpdir, md_dummy):
    with tmpdir.as_cwd():
        md_dummy('# test')
        mock_return = (
            '{"message":"API rate limit exceeded for 188.101.86.189. '
            '(But here\'s the good news: Authenticated requests get a '
            'higher rate limit. Check out the documentation for more '
            'details.)","documentation_url":'
            '"https://docs.github.com/rest/overview/resources-in-the-rest'
            '-api#rate-limiting"}'
        )
        with mock.patch.object(
            gh_md_to_moodle.main,
            'BeautifulSoup',
            return_value=mock_return,
        ):
            args = ['testing.md', 'test.html']
            with pytest.raises(Exception) as exc:
                main(args)
        assert exc.value.args[0] == 'API limit exceeded. Wait a few minutes'
