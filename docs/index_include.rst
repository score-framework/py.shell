.. module:: score.shell
.. role:: confkey
.. role:: confdefault

***********
score.shell
***********

This module provides a quick python shell where your project is initialized.

Quickstart
==========

Just install the module and you're good to go:

.. code-block:: console

    $ score shell
    Python 3.4.3 (default, Jan  8 2016, 11:18:01) 
    [GCC 5.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> type(score)
    <class 'score.init.initializer.ConfiguredScore'>

If you want other environment variables in your shell, you will need to
register callback functions in your configuration file to add them at startup:

.. code-block:: ini

    [shell]
    callbacks = pyth.to.my.custom.init_shell_env

.. code-block:: python

    def init_shell_env(env):
        import random
        lines = [
            "I'm, afraid we're fresh out of that, sir.",
            "I'm afraid we never have that at the end of the week, sir, we get it fresh on Monday.",
            "Ah! It's beeeen on order, sir, for two weeks. Was expecting it this morning.",
            "Normally, sir, yes. Today the van broke down.",
            "The cat's eaten it.",
            "Well, we don't get much call for it around here, sir.",
            "I'll have a look, sir ... nnnnnnnnnnnnnnnno.",
        ]
        env['get_cheese'] = lambda cheese: random.choice(lines)

.. code-block:: console

    $ score shell
    Python 3.4.3 (default, Jan  8 2016, 11:18:01) 
    [GCC 5.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> get_cheese('Red Leicester')
    "I'm afraid we never have that at the end of the week, sir, we get it fresh on Monday."

You can also use ipython or bpython if you want:

.. code-block:: ini

    [shell]
    backend = bpython

Configuration
=============

.. autofunction:: score.shell.init

Details
=======

Backend
-------

A *backend*, in this context, is a :class:`score.shell.Shell` instance. This
module comes with some shell backend pre-installed, but you can add your own by
subclassing :class:`Shell <score.shell.Shell>` and providing the path to your
class as backend:

.. code-block:: ini

    [shell]
    backend = path.to.my.custom_shell

API
===

Configuration
-------------

.. autofunction:: score.shell.init

.. autoclass:: score.shell.ConfiguredShellModule()

    .. attribute:: backend

        The :class:`score.shell.Shell` instance the module was configured with.

    .. attribute:: callbacks

        The `list` of resolved `callback` objects to use for constructing the
        shell environment.

.. autoclass:: score.shell.Shell()

    .. automethod:: spawn

    .. automethod:: _is_available

    .. automethod:: _install

    .. automethod:: _spawn
