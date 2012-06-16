import os
import sys
import imp
import argparse
from collections import OrderedDict


def getTasks(pakefile):
   items = pakefile.__dict__.viewitems()
   tasks = {name.split('_', 1)[1]: func for name, func in items \
            if name.startswith('task_')}

   return tasks


def getPakefile():
   assert os.path.exists('Pakefile'), 'Pakefile not found'
   pakefile = imp.load_source('Pakefile', os.path.abspath('Pakefile'))

   return (pakefile, getTasks(pakefile))


def buildArgParser(pakefile, task):
   parser = argparse.ArgumentParser(prog = 'pake ' + task)
   # Find the tasks option setter if there is one
   add_options = getattr(pakefile, 'options_'+task, None)
   if add_options is not None:
      # The task does take args so pass them in
      add_options(parser)

   return parser

def printTasks(pakefile, tasks):
   print "Tasks:"
   print "  " + "\n  ".join(tasks)


def parseOptions(pakefile, tasks):
   # Break passed args in to sub lists per supplied task
   # This allows for:
   #    test -w build --all
   # Where -w is only for test and --all is only for build
   args_per_task = OrderedDict()
   for arg in sys.argv[1:]:
      if arg in tasks:
         cur_task = arg
         args_per_task[arg] = []
      else:
         args_per_task[cur_task].append(arg)

   # Parse the args for each task providing nice failures and help text
   parsed_per_task = OrderedDict()
   for task, args in args_per_task.viewitems():
      # Get a parser that knows all of fields in question
      parser = buildArgParser(pakefile, task)

      # Store the options with the task
      # Even if no options were passed in the key must be set so that we
      # know the user selected this task
      parsed_per_task[task] = vars(parser.parse_args(args))

   return parsed_per_task


if __name__ == '__main__':
   pakefile, task_funcs = getPakefile()

   tasks = parseOptions(pakefile, task_funcs)

   if 0 == len(tasks):
      printTasks(pakefile, task_funcs.keys())
      exit(0)

   for task, args in tasks.viewitems():
      # Call the task with the supplied args
      getattr(pakefile, 'task_' + task)(args)
