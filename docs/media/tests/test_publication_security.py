"""Regression probes for optional publication tools; run with Python -I -B."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
MEDIA = ROOT / 'docs/media'
PYTHON = sys.executable


def run_script(name, *args):
    return subprocess.run([PYTHON, '-I', '-B', str(MEDIA / name), *(str(x) for x in args)],
                          text=True, capture_output=True)


def load_builder():
    spec = importlib.util.spec_from_file_location('paper_builder_security_test', MEDIA / 'build_white_paper.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='systemx-publication-security-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_planted_sibling_import_is_not_executed(self):
        for script in ('build_white_paper.py', 'build_white_paper_legacy.py',
                       'narrate_white_paper.py', 'verify_white_paper_example.py'):
            with self.subTest(script=script):
                directory = self.root / script.replace('.py', '')
                directory.mkdir()
                marker = directory / 'executed'
                (directory / 'argparse.py').write_text(
                    'from pathlib import Path\nPath('+repr(str(marker))+').write_text("executed")\n')
                shutil.copy2(MEDIA / script, directory / script)
                result = subprocess.run([PYTHON, str(directory / script), '--help'],
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(marker.exists())

    def test_current_paper_and_links(self):
        output = self.root / 'draft.pdf'
        result = run_script('build_white_paper.py', '--output', output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.read_bytes().startswith(b'%PDF-'))
        builder = load_builder()
        self.assertIn('<link', builder.inline('[citation](https://example.org)'))
        self.assertIn('<link', builder.inline('[section](#contents)'))
        self.assertIn('href="https://example.org/?a=1&amp;b=2"',
                      builder.inline('[query](https://example.org/?a=1&b=2)'))
        for scheme in ('file:///etc/passwd', 'javascript:alert%281%29', 'data:text/plain,hi',
                       'https://', 'https://user@example.org/', 'https://example.org\\@other.test/',
                       'https://example.org:invalid/'):
            with self.subTest(scheme=scheme), self.assertRaises(ValueError):
                builder.inline('[bad](' + scheme + ')')
        with self.assertRaises(ValueError):
            builder.https_url('https://example.org/\n/other')
        config = json.loads((MEDIA / 'publication-template.json').read_text())
        config['links'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            builder.configure(config)

    def test_published_edition_is_not_overwritten(self):
        published = ROOT / '.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.pdf'
        before = published.read_bytes()
        result = run_script('build_white_paper.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Published edition path is reserved', result.stderr)
        self.assertEqual(published.read_bytes(), before)

    def test_missing_published_path_is_also_reserved(self):
        builder = load_builder()
        mock_repo = self.root / 'mock-repo'
        published = mock_repo / '.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.pdf'
        published.parent.mkdir(parents=True)
        source = self.root / 'draft.md'
        source.write_text('## Front\n### Abstract\nDraft.\n## Section\nContent.\n')
        with patch.object(builder, 'ROOT', mock_repo), patch.object(
                sys, 'argv', ['build_white_paper.py', '--source', str(source),
                              '--output', str(published)]):
            with self.assertRaisesRegex(ValueError, 'Published edition path is reserved'):
                builder.main()
        self.assertFalse(published.exists())

    def test_symlinked_figure_root_is_rejected(self):
        builder = load_builder()
        white_paper = self.root / 'MEDIA/White-Paper'
        white_paper.mkdir(parents=True)
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'private.jpg').write_bytes(b'not a public figure')
        (self.root / 'MEDIA/Infographics').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            builder.content('![private](../Infographics/private.jpg)', white_paper / 'paper.md')

    def test_symlinked_figure_ancestor_is_rejected(self):
        builder = load_builder()
        real_media = self.root / 'real-media'
        (real_media / 'White-Paper').mkdir(parents=True)
        (real_media / 'Infographics').mkdir()
        (real_media / 'Infographics/private.jpg').write_bytes(b'not a public figure')
        linked_media = self.root / 'linked-media'
        linked_media.symlink_to(real_media, target_is_directory=True)
        with self.assertRaises(OSError):
            builder.content('![private](../Infographics/private.jpg)',
                            linked_media / 'White-Paper/paper.md')

    def test_output_directory_ancestor_symlink_is_rejected(self):
        builder = load_builder()
        real_dir = self.root / 'real-output'
        real_dir.mkdir()
        linked_dir = self.root / 'linked-output'
        linked_dir.symlink_to(real_dir, target_is_directory=True)
        with self.assertRaises(OSError):
            builder.open_directory(linked_dir)

    def test_parent_swap_cannot_redirect_pdf(self):
        builder = load_builder()
        parent = self.root / 'output'
        parent.mkdir()
        victim = self.root / 'victim'
        victim.mkdir()
        sentinel = victim / 'paper.pdf'
        sentinel.write_text('KEEP')
        original_build = builder.build

        def swap_then_build(source, output):
            parent.rename(self.root / 'moved-output')
            parent.symlink_to(victim, target_is_directory=True)
            original_build(source, output)

        with patch.object(builder, 'build', side_effect=swap_then_build), patch.object(
                sys, 'argv', ['build_white_paper.py', '--output', str(parent / 'paper.pdf')]):
            with self.assertRaisesRegex(RuntimeError, 'Output directory changed'):
                builder.main()
        self.assertEqual(sentinel.read_text(), 'KEEP')
        self.assertFalse((self.root / 'moved-output/paper.pdf').exists())

    def test_legacy_output_does_not_truncate_source_alias(self):
        source = self.root / 'old.md'
        source.write_text('## Front\n### Abstract\nA local paper.\n## Section\nA local section.\n')
        original = source.read_bytes()
        alias = self.root / 'alias.pdf'
        os.link(source, alias)
        result = run_script('build_white_paper_legacy.py', '--source', source,
                            '--output', alias)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(alias.read_bytes(), original)
        alias.unlink()
        alias.write_text('OLD')
        alias.chmod(0o600)
        result = run_script('build_white_paper_legacy.py', '--source', source,
                            '--output', alias)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(alias.read_bytes().startswith(b'%PDF-'))
        self.assertEqual(stat.S_IMODE(alias.stat().st_mode), 0o600)
        source.write_text('## Front\n### Abstract\n[bad](file:///etc/passwd)\n'
                          '## Section\nA local section.\n')
        bad_output = self.root / 'bad-legacy.pdf'
        result = run_script('build_white_paper_legacy.py', '--source', source,
                            '--output', bad_output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Paper links must use a valid HTTPS URL', result.stderr)
        self.assertFalse(bad_output.exists())

    def test_text_outputs_do_not_follow_aliases(self):
        source = self.root / 'edition-1.1.md'
        source.write_text('Edition 1.1 | archived\n## Front\nA historical paper.\n')
        original = source.read_bytes()
        hardlink = self.root / 'reading.txt'
        os.link(source, hardlink)
        result = run_script('narrate_white_paper.py', hardlink, '--source', source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source.read_bytes(), original)
        self.assertNotEqual(hardlink.read_bytes(), original)
        victim = self.root / 'victim.txt'
        victim.write_text('KEEP')
        link = self.root / 'linked-reading.txt'
        link.symlink_to(victim)
        result = run_script('narrate_white_paper.py', link, '--source', source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(victim.read_text(), 'KEEP')
        example_victim = self.root / 'example-victim.json'
        example_victim.write_text('KEEP')
        example_link = self.root / 'linked-example.json'
        example_link.symlink_to(example_victim)
        result = run_script('verify_white_paper_example.py', '--output', example_link)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(example_victim.read_text(), 'KEEP')
        normal = self.root / 'example.json'
        result = run_script('verify_white_paper_example.py', '--output', normal)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(normal.read_text())['passed'])


if __name__ == '__main__':
    unittest.main()
