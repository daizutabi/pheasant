import os

from mkdocs.commands.build import get_context
from mkdocs.config import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

import pheasant


def test_plugins_mkdocs():
    root = os.path.join(pheasant.__file__, "../../tests/docs")
    config_file = os.path.join(root, "mkdocs.yml")
    config_file = os.path.normpath(config_file)
    config = load_config(config_file)

    assert "pheasant" in config["plugins"]
    plugin = config["plugins"]["pheasant"]
    config = plugin.on_config(config)

    files = get_files(config)

    env = config["theme"].get_env()
    files.add_files_from_theme(env, config)
    files = plugin.on_files(files, config)

    nav = get_navigation(files, config)
    nav = plugin.on_nav(nav, config)
    assert len(files.documentation_pages()) == 1
    assert len(plugin.converter.pages) == 1

    for file in files.documentation_pages():
        page = file.page
        page.markdown = plugin.on_page_read_source(None, page)
        page.render(config, files)
        page.content = plugin.on_page_content(page.content, page)

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
