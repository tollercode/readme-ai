"""src/format.py
"""
import pandas as pd

import utils


def get_pkg_icons(path):
    """Get the package list from the json file.

    Args:
        path: The path of the json file.
        pkg_list: The list of packages.

    Returns:
        The package list.
    """
    contents = utils.read_json(path)
    icon_map = {}
    idx = 0
    while True:
        try:
            row = contents["icons"][idx]
            icon_map[row["name"].lower()] = row
        except:
            break
        idx += 1
    return icon_map


def create_header(path, pkg_list):
    """This function creates a header for a webpage.
    Args:
        icon_map (dict): A dictionary of icons.
        packages (list): A list of packages.
    Returns:
        str: A string of HTML.
    """
    header = ""
    icons = get_pkg_icons(path)
    pkg_list.append("python")
    pkg_list.append("github")
    for pkg in pkg_list:
        if pkg in icons:
            badge = icons[pkg.strip().lower()]["src"]
            header += f'<img src="{badge}">\n\t\t\t\t'
    return header


def create_html(badges, name, path):
    """This function creates an html file from a csv file.
    Args:
        icon (str): The icon to be used in the html file.
    Returns:
        str: The html file.
    """
    header = f"""
    <html>

    <body>
        <div>
            <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg"
                width="80">
            <h1>{name}</h1>
            <hr>
            <h3>Software and Packages</h3>
            <p>[description]</p>
            <p>
                {badges}
            </p>
        </div>
    """
    result = """
        <hr>
        <div>
            <h3>Overview</h3>
            <p>[description]</p>
            <hr>
            <h3>Prerequistes</h3>
            <p>[description]</p>
        </div>
        <hr>
        <div>
            <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-github-open.svg"
            width="80" />
            <h3>Repository Structure</h3>
            <p>[description]</p>
        </div>
        <hr>
        <div>
            <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-src-open.svg" 
            width="80" />
            <h3>Modules</h3>
    """
    closing_tags = """
        </div>
            <hr>
            <div>
                <h3>Roadmap</h3>
                <p>[description]</p>
            </div>
            <hr>
            <div>
                <h3>Licenses</h3>
                <p>[description]</p>
            </div>
            <hr>
        </body>
        </html>
    """

    prev_dir = None

    data = pd.read_csv(path)

    for i, j in data.iterrows():
        file = j[0].split("/")

        curr_dir = file[0]

        script = file[1]

        if prev_dir != curr_dir:
            tag = f"""<h3><i>{curr_dir.upper()}</i></h3>
            <dl>
                <dt><b><i>{script}</i></b></dt>
                <dd>{j[1]}</dd>
            </dl>
            """
        else:
            tag = f"""
            <dl>
                <dt><b><i>{script}</i></b></dt>
                <dd>{j[1]}</dd>
            </dl>
            """

        prev_dir = curr_dir

        result = f"{result}{tag}"

    return f"{header}{result}{closing_tags}"
