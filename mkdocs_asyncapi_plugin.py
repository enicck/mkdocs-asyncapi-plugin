#!/usr/bin/env python3

import re
import subprocess
import mkdocs
import tempfile
import os


MARKER = re.compile(r"!!asyncapi(?: (?P<path>[^\s><&:]+))?!!")


class AsyncAPIPlugin(mkdocs.plugins.BasePlugin):
    def on_page_markdown(self, markdown, page, config, files):
        match = MARKER.search(markdown)

        if match is None:
            return markdown

        path = match.group("path")

        indir = "docs"
        fname = os.path.basename(path)
        fname = os.path.splitext(fname)[0]
        with tempfile.TemporaryDirectory() as outdir:
            infile = os.path.join(indir, path)
            subprocess.run(
                [
                    "asyncapi",
                    "generate",
                    "fromTemplate",
                    infile,
                    "@asyncapi/markdown-template@1.2.1",
                    "--force-write",
                    "-o",
                    outdir,
                    "-p", f"outFilename={fname}.md"
                ],
                check=True,
            )
            outfile = os.path.join(outdir, fname + ".md")
            with open(outfile) as f:
                generated = f.read()
                markdown = markdown.replace(match.group(0), generated)
        return markdown
