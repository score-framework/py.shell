# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import click
from score.init import init, parse_list
from pprint import pprint


@click.command()
@click.argument('command', required=False)
@click.pass_context
def main(clickctx, command=None):
    """
    Allows operating on the project in a REPL.
    """
    conf = clickctx.obj['conf'].parse()
    if 'score.init' not in conf:
        conf['score.init'] = {}
    try:
        modules = parse_list(conf['score.init']['modules'])
    except KeyError:
        conf['score.init']['modules'] = 'score.shell'
    else:
        for module in modules:
            if module.startswith('score.shell'):
                break
        else:
            modules.append('score.shell')
            conf['score.init']['modules'] = '\n  ' + '\n  '.join(modules)
    score = init(conf)
    result = score.shell(command)
    if command and result is not None:
        pprint(result)


if __name__ == '__main__':
    import sys
    main(sys.argv)
