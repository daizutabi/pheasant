import os

import pytest
from mkdocs.commands.build import get_context
from mkdocs.config import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

import pheasant


@pytest.fixture(scope="module")
def config_file():
    root = os.path.join(pheasant.__file__, "../../tests/docs")
    config_file = os.path.join(root, "mkdocs.yml")
    config_file = os.path.normpath(config_file)
    return config_file


@pytest.fixture(scope="module")
def config(config_file):
    config = load_config(config_file)
    plugin = config["plugins"]["pheasant"]
    config = plugin.on_config(config)
    return config


@pytest.fixture(scope="module")
def plugin(config):
    plugin = config["plugins"]["pheasant"]
    return plugin


@pytest.fixture(scope="module")
def env(config):
    env = config["theme"].get_env()
    return env


@pytest.fixture(scope="module")
def files(config, plugin, env):
    files = get_files(config)
    files.add_files_from_theme(env, config)
    files = plugin.on_files(files, config)
    return files


@pytest.fixture(scope="module")
def nav(config, plugin, files):
    nav = get_navigation(files, config)
    nav = plugin.on_nav(nav, config)
    return nav


def test_plugins_mkdocs_config_file(config_file):
    assert os.path.exists(config_file)


def test_plugins_mkdocs_config(config):
    assert "pheasant" in config["plugins"]


def test_plugins_mkdocs_plugin(plugin):
    assert "extra_css" in plugin.config
    assert "extra_javascript" in plugin.config


def test_plugins_mkdocs_files(files, plugin, nav):
    assert len(files.documentation_pages()) == 7


def test_plugins_mkdocs_page_render(files, plugin, config):
    for file in files.documentation_pages():
        page = file.page
        page.markdown = plugin.on_page_read_source(None, page)
        page.render(config, files)
        page.content = plugin.on_page_content(page.content, page)
        assert (
            '<span class="pheasant-header">' in page.content
            or "Skipped." in page.content
        )


def test_plugins_mkdocs_build(files, plugin, config, nav, env):
    for file in files.documentation_pages():
        page = file.page
        page.active = True
        context = get_context(nav, files, config, page)

        # Allow 'template:' override in md source files.
        if "template" in page.meta:
            template = env.get_template(page.meta["template"])
        else:
            template = env.get_template("main.html")
        output = template.render(context)
        output = plugin.on_post_page(output)
        assert "pheasant" in output

        page.active = False
