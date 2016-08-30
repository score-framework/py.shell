# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
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

import abc
from score.init import (
    ConfiguredModule, ConfigurationError, parse_list, parse_dotted_path)
import contextlib
import ast
import code


defaults = {
    'backend': 'python',
    'backend.autoinstall': True,
    'callbacks': [],
}


def init(confdict, ctx=None):
    """
    Initializes this module acoording to the :ref:`SCORE module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`backend` :confdefault:`python`
        The shell backend to use. You can use either of the shells prvided by
        this module ("python", "ipython" and "bpython") or a string, that will
        be resolved using :func:`score.init.parse_dotted_path`.

    :confkey:`backend.autoinstall` :confdefault:`True`
        Whether the given *backend* should be installed automatically, if it was
        not found.

    :confkey:`callbacks`
        A :func:`list <score.init.parse_list>` of :func:`dotted python paths
        <score.init.parse_dotted_path>` to functions that will be called before
        the shell is spawned. Every callback will receive a `dict` representing
        the variables that will be available in the shell. The callbacks are
        free to add further variables to this list.

    """
    conf = defaults.copy()
    conf.update(confdict)
    shell_cls = Shell.get(conf['backend'])
    if not shell_cls:
        shell_cls = parse_dotted_path(conf['backend'])
    backend = shell_cls(conf['backend.autoinstall'])
    callbacks = []
    for path in parse_list(conf['callbacks']):
        callback = parse_dotted_path(path)
        if not callable(callback):
            raise ConfigurationError('Given callback not callable: %s' % path)
        callbacks.append(callback)
    return ConfiguredShellModule(ctx, backend, callbacks)


class ConfiguredShellModule(ConfiguredModule):
    """
    This module's :class:`configuration class <score.init.ConfiguredModule>`.

    It also implements a `__call__()` method for evaluating arbitrary one-liners
    inside the shell environment and returning the result:

    >>> from score.init import init_from_file
    >>> score = init_from_file('path/to/your/config.file')
    >>> score.shell('1 + 1')
    2
    >>> score.shell('get_cheese("Stilton")')
    "I'll have a look, sir ... nnnnnnnnnnnnnnnno."

    It is also possible to use this feature without any command, in which case
    you will get an instance of the configured shell backend:

    >>> score.shell()
    Python 3.4.3 (default, Jan  8 2016, 11:18:01)
    [GCC 5.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> get_cheese('Red Leicester')
    "I'm, afraid we're fresh out of that, sir."
    >>> exit()
    >>> # we left the spawned shell and landed on the original shell
    >>> # (the one we called score.shell() on)
    """

    def __init__(self, ctx, backend, callbacks):
        import score.shell
        super().__init__(score.shell)
        self.ctx = ctx
        self.backend = backend
        self.callbacks = callbacks

    def _finalize(self, score):
        self.score = score

    def __call__(self, command=None):
        with self._create_env() as env:
            if not command:
                return self.backend.spawn(env)
            for node in ast.walk(ast.parse(command)):
                name = _extract_dotted_path(node)
                if not name:
                    continue
                try:
                    module = __import__(name)
                    if '.' not in name and name not in env:
                        env[name] = module
                except ImportError:
                    pass
            return eval(command, env)

    @contextlib.contextmanager
    def _create_env(self):
        env = {'score': self.score}
        try:
            if self.ctx:
                env['ctx'] = self.ctx.Context()
            for callback in self.callbacks:
                callback(env)
            yield env
            if self.ctx:
                env['ctx'].destroy()
        except Exception as e:
            if self.ctx:
                env['ctx'].destroy(e)
            raise e


def _extract_dotted_path(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return '%s.%s' % (_extract_dotted_path(node.value), node.attr)


class Shell(abc.ABC):
    """
    Abstract base class for shell backends.
    """

    @staticmethod
    def get(name):
        return {
            'python': PythonShell,
            'ipython': IPythonShell,
            'bpython': BPythonShell,
        }.get(name)

    def __init__(self, name, autoinstall):
        self.name = name
        self.autoinstall = autoinstall

    def spawn(self, env):
        """
        Creates an interactive instance of this shell, where all variables from
        given *env* are available. Performs possible auto-installation and
        passes the control to :meth:`_spawn` for the ractual work.
        """
        if not self._is_available():
            if not self.autoinstall:
                raise Exception("Configured shell `%s' not available"
                                % self.name)
            self._install()
        self._spawn(env)

    @abc.abstractmethod
    def _is_available(self):
        """
        Whether this shell is installed. Must return `True`, if this shell's
        :meth:`_spawn` could be called immediately or `False`, if it's
        :meth:`_install` needs to be invoked first.
        """
        pass

    @abc.abstractmethod
    def _install(self):
        """
        Installs this shell into the current virtual environment. The easiest
        implementation of this function is:

        .. code-block:: python

            import pip
            pip.main(['install', 'myshell'])
        """
        pass

    @abc.abstractmethod
    def _spawn(self, env):
        """
        Creates an interactive instance of this shell, where all variables from
        given *env* are available.
        """
        pass


class PythonShell(Shell):

    def __init__(self, autoinstall):
        Shell.__init__(self, 'python', autoinstall)

    def _is_available(self):
        return True

    def _install(self):
        assert False, 'Should not be here'

    def _spawn(self, env):
        code.interact(local=env)


class BPythonShell(Shell):

    def __init__(self, autoinstall):
        Shell.__init__(self, 'bpython', autoinstall)

    def _is_available(self):
        try:
            import bpython  # NOQA (suppress "unused import" warnings)
            return True
        except ImportError:
            return False

    def _install(self):
        import pip
        pip.main(['install', 'bpython'])

    def _spawn(self, env):
        import bpython
        bpython.embed(locals_=env)


class IPythonShell(Shell):

    def __init__(self, autoinstall):
        Shell.__init__(self, 'ipython', autoinstall)

    def _is_available(self):
        try:
            import IPython  # NOQA (suppress "unused import" warnings)
            return True
        except ImportError:
            return False

    def _install(self):
        import pip
        pip.main(['install', 'ipython'])

    def _spawn(self, env):
        import IPython
        IPython.embed(user_ns=env)
