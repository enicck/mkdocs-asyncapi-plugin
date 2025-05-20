#!/usr/bin/env python3

import re
import subprocess
import mkdocs
import tempfile
import os


MARKER = re.compile(r"!!asyncapi(?: (?P<path>[^\s><&:]+))?(?P<params>(?: [^\s><&:]+=[^\s><&:]+)*)?!!")

plugin_params = ["template"]
class AsyncAPIPlugin(mkdocs.plugins.BasePlugin):
    def on_page_markdown(self, markdown, page, config, files):
        match = MARKER.search(markdown)

        if match is None:
            return markdown

        path = match.group("path")
        paramsStrings = match.group('params')
        params_dict = {}
        if paramsStrings:
            param_pairs = [p for p in paramsStrings.strip().split(' ') if p]
            params_dict = dict(p.split('=') for p in param_pairs)

        template = "@asyncapi/markdown-template@1.2.1"
        if "template" in paramsStrings:
            template = params_dict["template"]

        indir = "docs"
        fname = os.path.basename(path)
        fname = os.path.splitext(fname)[0]
        with tempfile.TemporaryDirectory() as outdir:
            infile = os.path.join(indir, path)
            args = [
                "asyncapi",
                "generate",
                "fromTemplate",
                infile,
                template,
                "--force-write",
                "-o",
                outdir,
                "-p", f"outFilename={fname}.md"
            ]

            if paramsStrings:
                for param in params_dict:
                    if param not in plugin_params:
                        args.extend(['-p', f'{param}={params_dict[param]}'])

            subprocess.run(
                args,
                check=True,
            )
            outfile = os.path.join(outdir, fname + ".md")
            with open(outfile) as f:
                generated = f.read()
                markdown = MARKER.sub(generated, markdown)
        return markdown
