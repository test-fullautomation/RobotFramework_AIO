# *******************************************************************************
#
# File: robot_res_2_py.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / Dec 2021.
#
# Description:
#   Tools for converting robotframework resource file to python dummy code file.
#
# History:
#
# 12.12.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
import argparse
import os
import abc
import string
import re
import ast
import inspect
from ast import *
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.model import ResourceFile
from robot.running.model import Import
from robot.running.namespace import Namespace
from robot.running.arguments.argumentmapper import DefaultValue
from robot.result.model import TestSuite
from robot.conf.settings import RobotSettings
from robot.variables.scopes import VariableScopes
from robot.output import Output


def FUNCTION_LOG(msg):
   """
   Function log.

   Args:

      msg: Message for function,

   Returns:
      None
   """
   stack = inspect.stack()
   try:
       locals_ = stack[1][0].f_locals
   finally:
       del stack
   locals_['log_r2p'] = R2PLog(msg)


class R2PLog:
   """
   Log handler for converting tool.
   """
   START_LOG = "%s[START] %s.."
   END_LOG = "%s[DONE] %s"
   FAIL_LOG = "%s[FAIL] %s"
   INFO_LOG = "%s[INFO] %s"
   ERROR_LOG = "%s[ERROR] %s"

   err_flag = False
   INDENTATION = "   "
   level = 0

   def __init__(self, function_job_msg):
      """
      Constructor for R2PLog class.

      Args:

         function_job_msg: Message when entering to a function.
      """
      self.msg = function_job_msg
      self.func_level = R2PLog.level
      print(R2PLog.START_LOG % (self.func_level * R2PLog.INDENTATION , self.msg))
      R2PLog.level += 1

   def __del__(self):
      """
      Destructor for R2PLog class.

      Returns:

         None
      """
      if not R2PLog.err_flag:
         print(R2PLog.END_LOG % (self.func_level * R2PLog.INDENTATION , self.msg))
      else:
         print(R2PLog.FAIL_LOG % (self.func_level * R2PLog.INDENTATION , self.msg))
         R2PLog.err_flag = False
      R2PLog.level -= 1

   @staticmethod
   def info(msg):
      print(R2PLog.INFO_LOG % (R2PLog.level * R2PLog.INDENTATION, msg))

   @staticmethod
   def error(msg):
      R2PLog.err_flag = True
      print(R2PLog.ERROR_LOG % (R2PLog.level * R2PLog.INDENTATION, msg))


class R2PException(Exception):
   pass

class GrammarSupportedAttribute:
   NAME = 'name'
   VALUE = 'value'
   DEFAULTS = 'defaults'
   TARGETS = 'targets'
   BODY = 'body'
   ARGS = 'args'



class GrammarAbstract(metaclass=abc.ABCMeta):
   """
   Python grammar class.
   """
   @abc.abstractmethod
   def generate(self):
      """
      Convert abstract grammar object to string.

      Returns:

         Python abstract grammar in string format.
      """
      pass


class PythonAbstractGrammar(GrammarAbstract, metaclass=abc.ABCMeta):
   """
   Class for handling python abstract grammar.
   """
   @abc.abstractproperty
   def template(self):
      return "abstract"

   def __init__(self, component):
      """
      Constructor for PythonAbstractGrammar class.
      Args:

         component: Children components.
      """
      self._component = component

   def get_template(self):
      """
      Get abstract grammar template for this instance.

      Returns:

         The abstract grammar template for this instance.
      """
      return self.template

   def get_comp_string(self):
      """
      Parse children components to string.

      Returns:

         Python abstract grammar in string format.
      """
      comp_str = ''
      if isinstance(self._component, list):
         for comp in self._component:
            comp_str += comp.generate()
            comp_str += ',\n'
         comp_str = comp_str[:-2]
      elif isinstance(self._component, str):
         comp_str = self._component
      elif isinstance(self._component, GrammarAbstract):
         comp_str = self._component.generate()
      return comp_str

   def generate(self):
      """
      Convert abstract grammar object to string.

      Returns:

         Python abstract grammar in string format.
      """
      res_str = self.get_template()
      comp_str = self.get_comp_string()

      if len([tup[1] for tup in string.Formatter().parse(self.get_template()) if tup[1] is not None]) > 0:
         res_str = self.get_template().format(comp_str)
      return res_str


class ModuleGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python module.

      Returns:

         The abstract grammar template for python module.
      """
      return "Module(\n \
      {0},\n \
      type_ignores=[])"


class ImportGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python import.

      Returns:

         The abstract grammar template for python import.
      """
      return "ImportFrom(\n \
      module='robot.api.deco',\n \
      names=[\n \
         alias(name='keyword'),\n \
         alias(name='library')],\n \
      level=0)"


class ClassGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python class.

      Returns:

         The abstract grammar template for python class.
      """
      return "ClassDef( \n\
      {0},\n\
      bases=[],\n\
      keywords=[],\n\
      decorator_list=[\n\
         Name(id='library', ctx=Load())])"


class FunctionGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python function.

      Returns:

         The abstract grammar template for python function.
      """
      return "FunctionDef(\n\
      {0},\n\
      decorator_list=[\n\
         Name(id='keyword', ctx=Load())])"


class BodyGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python body.

      Returns:

         The abstract grammar template for python body.
      """
      return "body=[{0}]"


class AssignGrammar(PythonAbstractGrammar):

   def __init__(self, name, value):
      self._name = name
      self._value = value

   @property
   def template(self):
      """
      Get abstract grammar template for python assign.

      Returns:

         The abstract grammar template for python assin.
      """
      return "Assign(\n\
      targets=[\n\
         Name(id='{0}', ctx=Store())],\n\
      value=Constant(value={1}))"

   def generate(self):
      return self.get_template().format(self._name, self._value)


class ReturnGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python return.

      Returns:

         The abstract grammar template for python return.
      """
      return " Return({0})"


class TupleGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python return.

      Returns:

         The abstract grammar template for python return.
      """
      return "Tuple(\
                                   elts=[\
                                       {0}],\
                                   ctx=Load())"


class FunctionArgsGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python function's arguments.

      Returns:

         The abstract grammar template for python function's arguments.
      """
      return "args=arguments(\n\
      posonlyargs=[],\n\
      {0},\n\
      kwonlyargs=[],\n\
      kw_defaults=[])"


class ArgsGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python arguments.

      Returns:

         The abstract grammar template for python arguments.
      """
      return "args=[{0}]"


class ArgGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python argument.

      Returns:

         The abstract grammar template for python argument.
      """
      return "arg(arg='{0}')"


class DefaultsGrammar(PythonAbstractGrammar):

   @property
   def template(self):
      """
      Get abstract grammar template for python default.

      Returns:

         The abstract grammar template for python default.
      """
      return "defaults=[{0}]"


class ExprGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python expression.

      Returns:

         The abstract grammar template for python expression.
      """
      return "Expr(value={0})"


class ConstantGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python constant.

      Returns:

         The abstract grammar template for python constant.
      """
      return "Constant(value={0})"


class NameGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python name.

      Returns:

         The abstract grammar template for python name.
      """
      return "Name(id='{0}', ctx=Load())"


class NameAttributeGrammar(PythonAbstractGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python name.

      Returns:

         The abstract grammar template for python name.
      """
      return "name='{0}'"


class AttributeGrammar(PythonAbstractGrammar):
   def __init__(self, name, component):
      self._name = name
      super(AttributeGrammar, self).__init__(component)

   @property
   def template(self):
      """
      Get abstract grammar template for python name.

      Returns:

         The abstract grammar template for python name.
      """
      return "%s={0}" % self._name


class AttributesGrammar(AttributeGrammar):
   @property
   def template(self):
      """
      Get abstract grammar template for python name.

      Returns:

         The abstract grammar template for python name.
      """
      return "%s=[{0}]" % self._name
   

class RobotRes2Py:
   """
   Class for converting robot framework resource to python dummy code.
   """
   ROBOT_VARIABLE_PATTERN = '\$\{([^\}]+)\}'
   INDENTATION = '    '
   CLASS_NAME_TEMPLATE = "'% slibrary_resource_dummy'"
   CLASS_DESC_TEMPLATE = "'\\n%s" % INDENTATION + "%s library resource dummy" + "\\n%s'" %INDENTATION
   DOCSTRING_TEMPLATE = "'\\n{0}{1}\\n{2}'"
   DUMMY_STR = 'dummy'
   SUPPORTED_EXT_TUPLE = ('.resource',)

   def __init__(self, robot_res_file, output_path, recursive=False):
      """
      Constructor for RobotRes2Py class.

      Args:

         robot_res_file: Path of the robot framework resource file to be converted.

         output_path: Output directory for the converted python file.
      """
      self.robot_resource = robot_res_file
      self.out_path = output_path
      self.robot_namespace = None
      self.recursive = recursive

   def get_robot_namespace_object(self):
      """
      Initialize the namespace for robot resource.

      Returns:
         The robot framework namespace for working with robot resource.
      """
      FUNCTION_LOG("Get namespace for the robot resource.")
      try:
         import_lib = self.robot_resource
         setting = RobotSettings({"output": None})
         setting._output_opts = []
         _variables = VariableScopes(setting)
         result = TestSuite()
         _output = Output(setting)
         resource = ResourceFile()
         if isinstance(import_lib, str):
            resource.imports.resource(import_lib)
         elif isinstance(import_lib, list):
            for lib in import_lib:
               lib = lib.replace("\\", '/')
               resource.imports.resource(lib)
         ns = Namespace(_variables, result, resource)
         ns.start_suite()
         EXECUTION_CONTEXTS.start_suite(result, ns, _output)
         ns.handle_imports()
         # ns._kw_store.get_runner("").
      except Exception as ex:
         R2PLog.error("Unable to get namespace for the robot resource. Exception: %s" % str(ex))
         raise R2PException()
      return ns


   def parse_robot_resource_2_py_grammar(self, robot_resource):
      """
      Parse robot resource to python module abstract grammar.

      Args:

         robot_resource: Robot resource object.

      Returns:

         Python module abstract grammar object.
      """
      # for robot_resource in robot_resources._items:
      FUNCTION_LOG("Parse robot resource '%s' to python module abstract grammar." % robot_resource.name)
      try:
         keyword_dict = robot_resource.handlers._normal._data
         py_func_grammar_list = []
         for kw_name, kw_value in keyword_dict.items():
            py_func_grammar_list.append(self.parse_robot_kw_2_func_grammar(kw_value))

         # Build the python class grammar
         py_class_grammar_name = AttributeGrammar(GrammarSupportedAttribute.NAME, RobotRes2Py.CLASS_NAME_TEMPLATE % robot_resource.name)
         py_class_grammar_docstrings = ExprGrammar(ConstantGrammar(RobotRes2Py.CLASS_DESC_TEMPLATE % robot_resource.name))
         py_class_grammar_robot_auto_keywords = AssignGrammar('ROBOT_AUTO_KEYWORDS', 'False')
         py_class_grammar_robot_library_version = AssignGrammar('ROBOT_LIBRARY_VERSION', "'0.1.0'")
         py_class_grammar_robot_library_scope = AssignGrammar('ROBOT_LIBRARY_SCOPE', "'GLOBAL'")
         py_class_grammar_body = BodyGrammar([py_class_grammar_docstrings,
                                              py_class_grammar_robot_auto_keywords,
                                              py_class_grammar_robot_library_version,
                                              py_class_grammar_robot_library_scope,
                                              *py_func_grammar_list])

         py_class_grammar = ClassGrammar([py_class_grammar_name, py_class_grammar_body])

         # Build the python class module
         py_module_grammar_import = ImportGrammar(None)
         py_module_grammar_body = BodyGrammar([py_module_grammar_import, py_class_grammar])
         py_module_grammar = ModuleGrammar(py_module_grammar_body)
      except Exception as ex:
         R2PLog.error("Unable to parse robot resource to python abstract grammar. Exception: %s" % str(ex))
         raise R2PException()
      return py_module_grammar

   def parse_robot_kw_2_func_grammar(self, kw_value):
      """
      Parse robot keyword to python function abstract grammar.

      Args:

         kw_value: Robot keyword object.

      Returns:

         Python function abstract grammar object.
      """
      FUNCTION_LOG("Parse robot keyword '%s' to python function abstract grammar." % kw_value._kw.name)
      try:
         # Parse input arguments of function
         py_arg_grammar_list = [ArgGrammar('self')]
         for kw_arg_name in kw_value.arguments.argument_names:
            py_arg_grammar_list.append(ArgGrammar(kw_arg_name))

         py_args_grammar = ArgsGrammar(py_arg_grammar_list)

         # Parse default values for input arguments.
         py_defaults_arg_grammar_list = []
         for default in kw_value.arguments.defaults.values():
            default_value = DefaultValue(default)
            parsed_value = default_value.resolve(self.robot_namespace.variables)
            if isinstance(parsed_value, str):
               parsed_value = self.add_quote_string(parsed_value)
            default_arg = str(parsed_value)
            py_defaults_arg_grammar_list.append(ConstantGrammar(default_arg))

         py_defaults_arg_grammar = DefaultsGrammar(py_defaults_arg_grammar_list)

         py_function_grammar_args = FunctionArgsGrammar([py_args_grammar, py_defaults_arg_grammar])
         py_function_grammar_name = AttributeGrammar(GrammarSupportedAttribute.NAME, self.add_quote_string(kw_value._kw.name))
         py_function_grammar_docs = ExprGrammar(ConstantGrammar(self.docs_format(kw_value.doc)))

         # Parse Return variables and Assign variables
         robot_return = kw_value.return_value
         py_function_grammar_assign_list = []
         py_return_var_name_grammar_list = []
         for ret in robot_return:
            var_name = self.remove_quote_dollar(ret)
            py_return_var_name_grammar = NameGrammar(var_name)
            py_return_var_name_grammar_list.append(py_return_var_name_grammar)
            py_function_grammar_assign_list.append(AssignGrammar(var_name, self.add_quote_string(RobotRes2Py.DUMMY_STR)))

         if len(py_return_var_name_grammar_list) > 1:
            tuple_grammar = TupleGrammar(py_return_var_name_grammar_list)
            value_grammar = AttributeGrammar(GrammarSupportedAttribute.VALUE, tuple_grammar)
         else:
            value_grammar = AttributeGrammar(GrammarSupportedAttribute.VALUE, py_return_var_name_grammar_list)
         py_function_grammar_return = ReturnGrammar(value_grammar)

         py_function_grammar_body = BodyGrammar([py_function_grammar_docs, *py_function_grammar_assign_list, py_function_grammar_return])

         py_function_grammar = FunctionGrammar([py_function_grammar_name, py_function_grammar_args, py_function_grammar_body])
      except Exception as ex:
         R2PLog.error("Unable to parse robot keyword to python abstract grammar. Exception: %s" % str(ex))
         raise R2PException()
      return py_function_grammar

   @staticmethod
   def convert_py_grammar_2_py_code(py_module_grammar):
      """
      Convert python abstract grammar to python code

      Args:

         py_module_grammar: Python abstract grammar object.

      Returns:

         Python code in string format.
      """
      try:
         module_grammar_str = py_module_grammar.generate()
         module_grammar_obj = eval(module_grammar_str)
         module_py_code_str = ast.unparse(ast.fix_missing_locations(module_grammar_obj))

      except Exception as ex:
         R2PLog.error("Unable to convert python grammar to python code. Exception: %s" % str(ex))
         raise R2PException()
      return module_py_code_str

   @staticmethod
   def get_list_of_resource_files(directory, recursive=False):
      """
      Get list of resource files from a directory.

      Args:

         directory: Directory contains resource files.

         recursive: Determine if it's required to search for Resources Files recursively into subdirectories.

      Returns:

         List of resource file.
      """
      resource_list = []
      if not recursive:
         resource_list.extend([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(RobotRes2Py.SUPPORTED_EXT_TUPLE)])
      else:
         list_dir = [os.path.join(directory, f) for f in os.listdir(directory)]
         for file in list_dir:
            if os.path.isfile(file) and file.endswith(RobotRes2Py.SUPPORTED_EXT_TUPLE):
               resource_list.append(file)
            elif os.path.isdir(file):
               list_dir.extend([os.path.join(file, f) for f in os.listdir(file)])
      return resource_list

   @staticmethod
   def add_quote_string(msg):
      """
      Add quote for string attribute.

      Args:
         msg: Message to be added quotes.

      Returns:

         String inside quotes.
      """
      return "'%s'" % msg

   @staticmethod
   def docs_format(docstring):
      return "'\\n{0}{1}\\n{2}'".format(RobotRes2Py.INDENTATION * 2,
                                        docstring.replace("\n", '\\n%s' % (RobotRes2Py.INDENTATION * 2)).replace("\\t", RobotRes2Py.INDENTATION),
                                        RobotRes2Py.INDENTATION * 2)

   @staticmethod
   def remove_quote_dollar(msg):
      return re.match(RobotRes2Py.ROBOT_VARIABLE_PATTERN, msg).groups()[0]

   def convert(self):
      """
      Convert robot framework resource file to python dummy file.

      Returns:

         None
      """
      FUNCTION_LOG("Convert robot framework resource to python dummy code...")
      try:
         if not os.path.isdir(self.robot_resource):
            R2PLog.info("+ Resource file: %s" % self.robot_resource)
         else:
            R2PLog.info("+ Resource directory: %s" % self.robot_resource)
            self.robot_resource = self.get_list_of_resource_files(self.robot_resource, self.recursive)
         R2PLog.info("+ Output directory: %s" % self.out_path)

         # Initialize robot environment
         self.robot_namespace = self.get_robot_namespace_object()
         resources = self.robot_namespace._kw_store.resources

         # Parse robot resource to python code
         for resource in resources._items:
            py_module_grammar = self.parse_robot_resource_2_py_grammar(resource)
            py_code = self.convert_py_grammar_2_py_code(py_module_grammar)

            if self.out_path:
               py_path = "%s/%s.py" % (self.out_path, resource.name)
            else:
               py_path = "%s.py" % resource.name

            f = open(py_path, "w")
            f.write(py_code)
            f.close()
      except Exception as ex:
         err_log = "Converting failure!!!"
         if not isinstance(ex, R2PException):
            err_log += " Exception: %s" % str(ex)

         R2PLog.error(err_log)


if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('-r', '--resource', type=str, help='The robot resource file/folder to be converted to python code.',  required=True)
   parser.add_argument('-o', '--out-dir', type=str, help='The output python folder path.', default="")
   parser.add_argument('-R', '--Recursive', help='Search for Resources Files recursively into subdirectories.', action='store_true')
   args = parser.parse_args()
   RobotRes2Py(args.resource, args.out_dir, args.Recursive).convert()


