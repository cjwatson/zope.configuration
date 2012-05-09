##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test configuration machinery.
"""
import unittest

class _Catchable(object):
    # Mixin for classes which need to make assertions about the exception
    # instance.
    def assertRaises(self, excClass, callableObj, *args, **kwargs):
        # Morph stdlib version to return the raised exception
        try:
            callableObj(*args, **kwargs)
        except excClass as exc:
            return exc
        if hasattr(excClass,'__name__'):
            excName = excClass.__name__
        else:
            excName = str(excClass)
        raise self.failureException("%s not raised" % excName)


class ConfigurationContextTests(_Catchable,
                                unittest.TestCase,
                               ):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationContext
        return ConfigurationContext
    
    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_resolve_blank(self):
        c = self._makeOne()
        self.assertRaises(ValueError, c.resolve, '')
        self.assertRaises(ValueError, c.resolve, '   ')

    def test_resolve_dot(self):
        c = self._makeOne()
        package = c.package = object()
        self.assertTrue(c.resolve('.') is package)

    def test_resolve_trailing_dot_in_resolve(self):
        #Dotted names are no longer allowed to end in dots
        c = self._makeOne()
        self.assertRaises(ValueError, c.resolve, 'zope.')

    def test_resolve_builtin(self):
        c = self._makeOne()
        self.assertTrue(c.resolve('str') is str)

    def test_resolve_single_non_builtin(self):
        import os
        c = self._makeOne()
        self.assertTrue(c.resolve('os') is os)

    def test_resolve_relative_miss_no_package(self):
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        c.package = None
        self.assertRaises(ConfigurationError, c.resolve, '.nonesuch')

    def test_resolve_relative_miss_w_package_too_many_dots(self):
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        package = c.package = FauxPackage()
        package.__name__ = 'one.dot'
        self.assertRaises(ConfigurationError, c.resolve, '....nonesuch')

    def test_resolve_bad_dotted_last_import(self):
        # Import error caused by a bad last component in the dotted name.
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        exc = self.assertRaises(ConfigurationError,
                          c.resolve, 'zope.configuration.tests.nosuch')
        self.assertTrue('ImportError' in str(exc))

    def test_resolve_bad_dotted_import(self):
        # Import error caused by a totally wrong dotted name.
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        exc = self.assertRaises(ConfigurationError, 
                          c.resolve, 'zope.configuration.nosuch.noreally')
        self.assertTrue('ImportError' in str(exc))

    def test_resolve_bad_sub_last_import(self):
        #Import error caused by a bad sub import inside the referenced
        #dotted name. Here we keep the standard traceback.
        import sys
        c = self._makeOne()
        self.assertRaises(ImportError,
                          c.resolve, 'zope.configuration.tests.victim')
        #Cleanup:
        for name in ('zope.configuration.tests.victim',
                     'zope.configuration.tests.bad'):
           if name in sys.modules:
               del sys.modules[name]

    def test_resolve_bad_sub_import(self):
        #Import error caused by a bad sub import inside part of the referenced
        #dotted name. Here we keep the standard traceback.
        import sys
        c = self._makeOne()
        self.assertRaises(ImportError, 
                          c.resolve, 'zope.configuration.tests.victim.nosuch')
        #Cleanup:
        for name in ('zope.configuration.tests.victim',
                     'zope.configuration.tests.bad'):
           if name in sys.modules:
               del sys.modules[name]

    def test_path_w_absolute_filename(self):
        c = self._makeOne()
        self.assertEqual(c.path('/path/to/somewhere'), '/path/to/somewhere')

    def test_path_w_relative_filename_w_basepath(self):
        c = self._makeOne()
        c.basepath = '/path/to'
        self.assertEqual(c.path('somewhere'), '/path/to/somewhere')

    def test_path_w_relative_filename_wo_basepath_wo_package(self):
        import os
        c = self._makeOne()
        c.package = None
        self.assertEqual(c.path('somewhere'),
                         os.path.join(os.getcwd(), 'somewhere'))

    def test_path_wo_basepath_w_package_having_file(self):
        #Path must always return an absolute path.
        import os
        class stub:
            __file__ = os.path.join('relative', 'path')
        c = self._makeOne()
        c.package = stub()
        self.assertTrue(os.path.isabs(c.path('y/z')))

    def test_path_wo_basepath_w_package_having_no_file_but_path(self):
        #Determine package path using __path__ if __file__ isn't available.
        # (i.e. namespace package installed with
        #--single-version-externally-managed)
        import os
        class stub:
            __path__ = [os.path.join('relative', 'path')]
        c = self._makeOne()
        c.package = stub()
        os.path.isabs(c.path('y/z'))

    def test_checkDuplicate_miss(self):
        c = self._makeOne()
        c.checkDuplicate('/path') # doesn't raise
        self.assertEqual(list(c._seen_files), ['/path'])

    def test_checkDuplicate_hit(self):
        from zope.configuration.exceptions import ConfigurationError
        c = self._makeOne()
        c.checkDuplicate('/path')
        self.assertRaises(ConfigurationError, c.checkDuplicate, '/path')
        self.assertEqual(list(c._seen_files), ['/path'])

    def test_processFile_miss(self):
        c = self._makeOne()
        self.assertEqual(c.processFile('/path'), True)
        self.assertEqual(list(c._seen_files), ['/path'])

    def test_processFile_hit(self):
        c = self._makeOne()
        c.processFile('/path')
        self.assertEqual(c.processFile('/path'), False)
        self.assertEqual(list(c._seen_files), ['/path'])

    def test_action_defaults_no_info_no_includepath(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR)
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], None)
        self.assertEqual(info['args'], ())
        self.assertEqual(info['kw'], {})
        self.assertEqual(info['includepath'], ())
        self.assertEqual(info['info'], '')
        self.assertEqual(info['order'], 0)

    def test_action_defaults_w_info_w_includepath(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.info = 'INFO' # normally provided by subclass
        c.includepath = ('a', 'b') # normally provided by subclass
        c.action(DISCRIMINATOR)
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], None)
        self.assertEqual(info['args'], ())
        self.assertEqual(info['kw'], {})
        self.assertEqual(info['order'], 0)
        self.assertEqual(info['includepath'], ('a', 'b'))
        self.assertEqual(info['info'], 'INFO')

    def test_action_explicit_no_extra(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        ARGS = (12, 'z')
        KW = {'one': 1}
        INCLUDE_PATH = ('p', 'q/r')
        INFO = 'INFO'
        def _callable():
            pass
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR,
                 _callable,
                 ARGS,
                 KW,
                 42,
                 INCLUDE_PATH,
                 INFO,
                )
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], _callable)
        self.assertEqual(info['args'], ARGS)
        self.assertEqual(info['kw'], KW)
        self.assertEqual(info['order'], 42)
        self.assertEqual(info['includepath'], INCLUDE_PATH)
        self.assertEqual(info['info'], INFO)

    def test_action_explicit_w_extra(self):
        DISCRIMINATOR = ('a', ('b',), 0)
        ARGS = (12, 'z')
        KW = {'one': 1}
        INCLUDE_PATH = ('p', 'q/r')
        INFO = 'INFO'
        def _callable():
            pass
        c = self._makeOne()
        c.actions = [] # normally provided by subclass
        c.action(DISCRIMINATOR,
                 _callable,
                 ARGS,
                 KW,
                 42,
                 INCLUDE_PATH,
                 INFO,
                 foo='bar',
                 baz=17,
                )
        self.assertEqual(len(c.actions), 1)
        info = c.actions[0]
        self.assertEqual(info['discriminator'], DISCRIMINATOR)
        self.assertEqual(info['callable'], _callable)
        self.assertEqual(info['args'], ARGS)
        self.assertEqual(info['kw'], KW)
        self.assertEqual(info['order'], 42)
        self.assertEqual(info['includepath'], INCLUDE_PATH)
        self.assertEqual(info['info'], INFO)
        self.assertEqual(info['foo'], 'bar')
        self.assertEqual(info['baz'], 17)

    def test_hasFeature_miss(self):
        c = self._makeOne()
        self.assertFalse(c.hasFeature('nonesuch'))

    def test_hasFeature_hit(self):
        c = self._makeOne()
        c._features.add('a.feature')
        self.assertTrue(c.hasFeature('a.feature'))

    def test_provideFeature(self):
        c = self._makeOne()
        c.provideFeature('a.feature')
        self.assertTrue(c.hasFeature('a.feature'))


class ConfigurationAdapterRegistryTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationAdapterRegistry
        return ConfigurationAdapterRegistry
    
    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        reg = self._makeOne()
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory():
            pass
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        self.assertEqual(len(reg._registry), 1)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _factory)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register_replacement(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory():
            pass
        def _rival():
            pass
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        reg.register(IFoo, (NS, NAME), _rival)
        self.assertEqual(len(reg._registry), 1)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _rival)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_register_new_name(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        NAME2 = 'other'
        def _factory():
            pass
        def _rival():
            pass
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        reg.register(IFoo, (NS, NAME2), _rival)
        self.assertEqual(len(reg._registry), 2)
        areg = reg._registry[(NS, NAME)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _factory)
        areg = reg._registry[(NS, NAME2)]
        self.assertTrue(areg.lookup1(IFoo, Interface) is _rival)
        self.assertEqual(len(reg._docRegistry), 0)

    def test_document_non_string_name(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        HANDLER = object()
        INFO = 'INFO'
        PARENT = object()
        reg = self._makeOne()
        reg.document((NS, NAME), ISchema, IUsedIn, HANDLER, INFO, PARENT)
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 1)
        name, schema, used_in, handler, info, parent = reg._docRegistry[0]
        self.assertEqual(name, (NS, NAME))
        self.assertEqual(schema, ISchema)
        self.assertEqual(used_in, IUsedIn)
        self.assertEqual(info, INFO)
        self.assertEqual(parent, PARENT)

    def test_document_w_string_name(self):
        from zope.interface import Interface
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        NAME = 'testing'
        HANDLER = object()
        INFO = 'INFO'
        PARENT = object()
        reg = self._makeOne()
        reg.document(NAME, ISchema, IUsedIn, HANDLER, INFO, PARENT)
        self.assertEqual(len(reg._registry), 0)
        self.assertEqual(len(reg._docRegistry), 1)
        name, schema, used_in, handler, info, parent = reg._docRegistry[0]
        self.assertEqual(name, ('', NAME))
        self.assertEqual(schema, ISchema)
        self.assertEqual(used_in, IUsedIn)
        self.assertEqual(info, INFO)
        self.assertEqual(parent, PARENT)

    def test_factory_miss(self):
        from zope.configuration.exceptions import ConfigurationError
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = object()
        reg = self._makeOne()
        self.assertRaises(ConfigurationError, reg.factory, context, (NS, NAME))

    def test_factory_hit_on_fqn(self):
        from zope.interface import Interface
        from zope.interface import implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Context(object):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = Context()
        def _factory():
            pass
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        self.assertEqual(reg.factory(context, (NS, NAME)), _factory)

    def test_factory_miss_on_fqn_hit_on_bare_name(self):
        from zope.interface import Interface
        from zope.interface import implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Context(object):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = Context()
        def _factory():
            pass
        reg = self._makeOne()
        reg.register(IFoo, NAME, _factory)
        self.assertEqual(reg.factory(context, (NS, NAME)), _factory)

    def test_factory_hit_on_fqn_lookup_fails(self):
        from zope.interface import Interface
        from zope.configuration.exceptions import ConfigurationError
        class IFoo(Interface):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        context = object() # doesn't provide IFoo
        def _factory():
            pass
        reg = self._makeOne()
        reg.register(IFoo, (NS, NAME), _factory)
        self.assertRaises(ConfigurationError, reg.factory, context, (NS, NAME))


class ConfigurationMachineTests(_Catchable,
                                unittest.TestCase,
                               ):

    def _getTargetClass(self):
        from zope.configuration.config import ConfigurationMachine
        return ConfigurationMachine
    
    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_IConfigurationContext(self):
        from zope.interface.verify import verifyClass
        from zope.configuration.interfaces import IConfigurationContext
        verifyClass(IConfigurationContext, self._getTargetClass())

    def test_instance_conforms_to_IConfigurationContext(self):
        from zope.interface.verify import verifyObject
        from zope.configuration.interfaces import IConfigurationContext
        verifyObject(IConfigurationContext, self._makeOne())

    def test_ctor(self):
        from zope.configuration.config import RootStackItem
        from zope.configuration.config import metans
        cm = self._makeOne()
        self.assertEqual(cm.package, None)
        self.assertEqual(cm.basepath, None)
        self.assertEqual(cm.includepath, ())
        self.assertEqual(cm.info, '')
        self.assertEqual(len(cm.actions), 0)
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertTrue(isinstance(root, RootStackItem))
        self.assertTrue(root.context is cm)
        self.assertEqual(len(cm.i18n_strings), 0)
        # Check bootstrapped meta:*.
        self.assertTrue((metans, 'directive') in cm._registry)
        self.assertTrue((metans, 'directives') in cm._registry)
        self.assertTrue((metans, 'complexDirective') in cm._registry)
        self.assertTrue((metans, 'groupingDirective') in cm._registry)
        self.assertTrue((metans, 'provides') in cm._registry)
        self.assertTrue((metans, 'subdirective') in cm._registry)

    def test_begin_w___data_and_kw(self):
        from zope.configuration.config import IConfigurationContext
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        def _factory(context, data, info):
            pass
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        self.assertRaises(TypeError,
                          cm.begin, (NS, NAME), {'foo': 'bar'}, baz='bam')

    def test_begin_w___data_no_kw(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        def _handler(*args, **kw):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm.begin((NS, NAME), {'name': 'testing',
                                  'schema': ISchema,
                                  'usedIn': IUsedIn,
                                  'handler': _handler,
                                 }, 'INFO')
        self.assertEqual(len(cm.stack), 2)
        root = cm.stack[0]
        self.assertTrue(isinstance(root, RootStackItem))
        nested = cm.stack[1]
        self.assertTrue(nested is item)
        self.assertEqual(_called_with,
                        [(cm, {'name': 'testing',
                               'schema': ISchema,
                               'usedIn': IUsedIn,
                               'handler': _handler,
                              }, 'INFO')])

    def test_begin_wo___data_w_kw(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        def _handler(*args, **kw):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = object()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm.begin((NS, NAME), None, 'INFO',
                  name='testing',
                  schema=ISchema,
                  usedIn=IUsedIn,
                  handler=_handler,
                )
        self.assertEqual(len(cm.stack), 2)
        root = cm.stack[0]
        self.assertTrue(isinstance(root, RootStackItem))
        nested = cm.stack[1]
        self.assertTrue(nested is item)
        self.assertEqual(_called_with,
                        [(cm, {'name': 'testing',
                               'schema': ISchema,
                               'usedIn': IUsedIn,
                               'handler': _handler,
                              }, 'INFO')])

    def test_end(self):
        from zope.configuration.config import RootStackItem
        class FauxItem(object):
            _finished = False
            def finish(self):
                self._finished = True
        cm = self._makeOne()
        item = FauxItem()
        cm.stack.append(item)
        cm.end()
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertTrue(isinstance(root, RootStackItem))
        self.assertTrue(item._finished)

    def test___call__(self):
        from zope.interface import Interface
        from zope.configuration.config import IConfigurationContext
        from zope.configuration.config import RootStackItem
        class ISchema(Interface):
            pass
        class IUsedIn(Interface):
            pass
        class FauxItem(object):
            _finished = False
            def finish(self):
                self._finished = True
        def _handler(*args, **kw):
            pass
        NS = 'http://namespace.example.com/'
        NAME = 'testing'
        _called_with = []
        item = FauxItem()
        def _factory(context, data, info):
            _called_with.append((context, data, info))
            return item
        cm = self._makeOne()
        cm.register(IConfigurationContext, (NS, NAME), _factory)
        cm((NS, NAME), 'INFO',
            name='testing',
            schema=ISchema,
            usedIn=IUsedIn,
            handler=_handler,
           )
        self.assertEqual(len(cm.stack), 1)
        root = cm.stack[0]
        self.assertTrue(isinstance(root, RootStackItem))
        self.assertEqual(_called_with,
                        [(cm, {'name': 'testing',
                               'schema': ISchema,
                               'usedIn': IUsedIn,
                               'handler': _handler,
                              }, 'INFO')])
        self.assertTrue(item._finished)

    def test_getInfo_only_root_default(self):
        cm = self._makeOne()
        self.assertEqual(cm.getInfo(), '')

    def test_getInfo_only_root(self):
        cm = self._makeOne()
        cm.info = 'INFO'
        self.assertEqual(cm.getInfo(), 'INFO')

    def test_getInfo_w_item(self):
        class FauxItem(object):
            info = 'FAUX'
            def __init__(self):
                self.context = self
        cm = self._makeOne()
        cm.stack.append(FauxItem())
        self.assertEqual(cm.getInfo(), 'FAUX')

    def test_setInfo_only_root(self):
        cm = self._makeOne()
        cm.setInfo('INFO')
        self.assertEqual(cm.info, 'INFO')

    def test_setInfo_w_item(self):
        class FauxItem(object):
            info = 'FAUX'
            def __init__(self):
                self.context = self
        cm = self._makeOne()
        item = FauxItem()
        cm.stack.append(item)
        cm.setInfo('UPDATED')
        self.assertEqual(item.info, 'UPDATED')

    def test_execute_actions_empty(self):
        cm = self._makeOne()
        cm.execute_actions() # noop

    def test_execute_actions_wo_errors(self):
        _called_with = {}
        def _a1(*args, **kw):
            _called_with.setdefault('_a1', []).append((args, kw))
        def _a2(*args, **kw):
            _called_with.setdefault('_a2', []).append((args, kw))
        cm = self._makeOne()
        cm.action(None, None) # will be skipped
        cm.action(None, _a1, ('a', 0), {'foo': 'bar'}, 4)
        cm.action(None, _a2, ('a', 1), {'foo': 'baz'}, 3)
        cm.action(None, _a1, ('b', 2), {'foo': 'qux'}, 2)
        cm.execute_actions()
        self.assertEqual(_called_with['_a1'],
                        [(('b', 2), {'foo': 'qux'}),
                         (('a', 0), {'foo': 'bar'}),
                        ])
        self.assertEqual(_called_with['_a2'],
                        [(('a', 1), {'foo': 'baz'}),
                        ])

    def test_execute_actions_w_errors_w_testing(self):
        def _err(*args, **kw):
            raise ValueError('XXX')
        cm = self._makeOne()
        cm.action(None, _err)
        exc = self.assertRaises(ValueError, cm.execute_actions, testing=True)
        self.assertEqual(str(exc), 'XXX')

    def test_execute_actions_w_errors_wo_testing(self):
        from zope.configuration.config import ConfigurationExecutionError
        def _err(*args, **kw):
            raise ValueError('XXX')
        cm = self._makeOne()
        cm.info = 'INFO'
        cm.action(None, _err)
        exc = self.assertRaises(ConfigurationExecutionError,
                                cm.execute_actions)
        self.assertEqual(str(exc),
                         "<type 'exceptions.ValueError'>: XXX\n  in:\n  INFO")

    def test_keyword_handling(self):
        from zope.configuration.config import metans
        from zope.configuration.tests.directives import f
        from zope.configuration._compat import b
        from zope.configuration._compat import u
        machine = self._makeOne()
        ns = "http://www.zope.org/testing"

        #Register some test directives, starting with a grouping directive
        # that sets a package:

        machine((metans, "groupingDirective"),
                 name="package", namespace=ns,
                 schema="zope.configuration.tests.directives.IPackaged",
                 handler="zope.configuration.tests.directives.Packaged",
                )

        # set the package:
        machine.begin((ns, "package"),
                       package="zope.configuration.tests.directives",
                      )

        #Which makes it easier to define the other directives:
        machine((metans, "directive"),
                namespace=ns, name="k",
                schema=".Ik", handler=".k")

        machine((ns, "k"), "yee ha",
                **{"for": u("f"), "class": u("c"), "x": u("x")})

        self.assertEqual(len(machine.actions), 1)
        self.assertEqual(machine.actions[0],
                         {'args': (b('f'), b('c'), b('x')),
                          'callable': f,
                          'discriminator': ('k', b('f')),
                          'includepath': (),
                          'info': 'yee ha',
                          'kw': {},
                          'order': 0,
                         })

    #TODO: coverage


class FauxPackage(object):
    pass


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ConfigurationContextTests),
        unittest.makeSuite(ConfigurationAdapterRegistryTests),
        unittest.makeSuite(ConfigurationMachineTests),
        ))
