Changes
=======

4.1.1 (unreleased)
------------------

- Nothing changed yet.


4.1.0 (2017-04-26)
------------------

- Drop support for Python 2.6 and 3.2.

- Add support for Python 3.5 and 3.6.

- Fix the ``domain`` of MessageID fields to be a native string.
  Previously on Python 3 they were bytes, which meant that they
  couldn't be used to find translation utilities registered by
  zope.i18n. See `issue 17 <https://github.com/zopefoundation/zope.configuration/issues/17>`_.

4.0.3 (2014-03-19)
------------------

- Add explicit support for Python 3.4.

4.0.2 (2012-12-31)
------------------

- Flesh out PyPI Trove classifiers.

- Remove spurious declaration of 'test' dependency on ``zope.testing``.

4.0.1 (2012-11-21)
------------------

- Add support for Python 3.3.

- Remove the deprecated 'zope.configuration.stxdocs' script.
  and made the 'zope.configuration.tests.conditions' helper module
  (used in running Sphinx doctest snippets) Py3k compatible.
  https://bugs.launchpad.net/zope.configuration/+bug/1025390

4.0.0 (2012-05-16)
------------------

- Bring unit test coverage to 100%.

- Automate build of Sphinx HTML docs and running doctest snippets via tox.

- Drop hard testing dependency on ``zope.testing``.

- Add explicit support for PyPy.

- Add explicit support for Python 3.2.

- Drop explicit support for Python 2.4 / 2.5.

- Add support for continuous integration using ``tox`` and ``jenkins``.

- Add ``Sphinx`` documentation.

- Add ``setup.py docs`` alias (installs ``Sphinx`` and dependencies).

- Add ``setup.py dev`` alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).

3.8.1 (2012-05-05)
------------------

- Fix Python 2.4 backwards incompat (itemgetter used with multiple args);
  Python 2.4 now works (at least if you use zope.schema == 3.8.1).
  This is the last release which will support Python 2.4 or 2.5.

3.8.0 (2011-12-06)
------------------

- Change action structures from tuples to dictionaries to allow for action
  structure extensibility (merged chrism-dictactions branch).

3.7.4 (2011-04-03)
------------------

- Apply test fixes for Windows.

3.7.3 (2011-03-11)
------------------

- Correctly locate packages with a __path__ attribute but no
  __file__ attribute (such as namespace packages installed with setup.py
  install --single-version-externally-managed).

- Allow "info" and "includepath" to be passed optionally to context.action.

3.7.2 (2010-04-30)
------------------

- Prefer the standard libraries doctest module over zope.testing.doctest.

3.7.1 (2010-01-05)
------------------

- Jython support: use ``__builtin__`` module import rather than assuming
  ``__builtins__`` is available.

- Jython support: deal with the fact that the Jython SAX parser
  returns attribute sets that have an empty string indicating no
  namespace instead of ``None``.

- Allow ``setup.py test`` to run at least a subset of the tests that
  would be run when using the zope testrunner: ``setup.py test`` runs
  53 tests, while ``bin/test`` runs 156.

3.7.0 (2009-12-22)
------------------

- Adjust testing output to newer zope.schema.

- Prefer zope.testing.doctest over doctestunit.

3.6.0 (2009-04-01)
------------------

- Removed dependency of `zope.deprecation` package.

- Don't suppress deprecation warnings any more in 'zope.configuration'
  package level. This makes it more likely other packages will generate
  deprecation warnings now, which will allow us to remove more
  outdated ones.

- Don't fail when zope.testing is not installed.

- Added missing ``processFile`` method to ``IConfigurationContext``.
  It is already implemented in the mix-in class,
  ``zope.configuration.config.ConfigurationContext``, and used by
  implementations of ``include`` and ``exclude`` directives.

3.5.0 (2009-02-26)
------------------

- Added the ``exclude`` directive to standard directives. It was
  previously available via ``zc.configuration`` package and now it's
  merged into ``zope.configuration``.

- Changed package's mailing list address to zope-dev at zope.org,
  change "cheeseshop" to "pypi" in the package's url.

3.4.1 (2008-12-11)
------------------

- Use built-in 'set' type, rather than importin the 'sets' module,
  which is deprecated in Python 2.6.

- Added support to bootstrap on Jython.

3.4.0 (2007-10-02)
------------------

- Initial release as a standalone package.

Before 3.4.0
------------

This package was part of the Zope 3 distribution and did not have its own
CHANGES.txt. For earlier changes please refer to either our subversion log or
the CHANGES.txt of earlier Zope 3 releases.
