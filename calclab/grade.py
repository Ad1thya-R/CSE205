import os
import sys
import shutil
import tempfile
from distutils.dir_util import copy_tree
from subprocess import PIPE, run
import argparse

from io import StringIO
from string import Template
import functools

from test import (
  run_test, print_cmds,
  MASK_ALL,
  MASK_BIN,
  MASK_HEX,
  MASK_UNSIGNED,
  MASK_SIGNED,
  MASK_FLAGS,
  tests
)

# Set to true to keep the tmp folder when a failure (either in compiling or test) occurs
# The folder path is printed as output
NOT_CLEAN_TMP_IF_ERROR=True

class AllRes():
  def __init__(self):
    self.name_from_file = None
    self.name = None
    self.userid = None
    self.comp_res = None
    self.func_check_res = None
    self.q3 = None
    self.q4 = None
    self.q5 = None
    self.q6 = None
    self.q8 = None
    self.q9 = None

class OutRes:
  def __init__(self, success):
    self.success = success
    self.has_exception = False
    self.exception = False
    self.out = None
    pass


def prepare_working_dir(handin_path, student_file):
  working_dir = tempfile.mkdtemp()
  copy_tree(handin_path, working_dir)
  shutil.copy(student_file,
              os.path.join(working_dir, "calc.c"),
              )
  return working_dir


def check_illegal_functions(working_dir, log_file):
  print("Check illegal...")
  makefile_path = os.path.join(working_dir, "Makefile")

  result = run(
    ["make", "-f", makefile_path, "check", "-e"],
    stdout=PIPE, stderr=PIPE, cwd=working_dir)

  errstr = result.stderr.decode("UTF-8")
  log_file.write(result.stdout.decode("UTF-8"))
  log_file.write(errstr)

  if result.returncode != 0:
    print("CHECK ILLEGAL FUNCTION ERROR, returned %d" % result.returncode, file=log_file)
    res = OutRes(False)
    res.out = StringIO()
    res.out.write(errstr)
    return res

  outstr = result.stdout.decode("UTF-8")
  res = OutRes("check for illegal passed" in outstr)
  return res


def compile_calc(working_dir, log_file):
  print("compiling...")
  makefile_path = os.path.join(working_dir, "Makefile")

  result = run(
    ["make", "-f", makefile_path],
    stdout=PIPE, stderr=PIPE, cwd=working_dir)

  errstr = result.stderr.decode("UTF-8")
  log_file.write(result.stdout.decode("UTF-8"))
  log_file.write(errstr)

  if result.returncode != 0:
    print("COMPILATION ERROR, returned %d" % result.returncode, file=log_file)
    res = OutRes(False)
    res.out = StringIO()
    res.out.write(errstr)
    return res

  res = OutRes(True)
  return res

def read_name(working_dir):
  calc_file = os.path.join(working_dir, "calc.c")

  name = None
  userid = None

  with open(calc_file, "r") as f:
    for line in f.readlines():
      line = line.strip()
      if not line:
        continue

      if line.startswith("name:"):
        name = line[len("name:"):]
        name = name.strip()

      if line.startswith("userid:"):
        userid = line[len("userid:"):]
        userid = userid.strip()

  return (name,userid)


def test_res(working_dir, calc, calcref, test, log_file):
  (rel_testfile, mask, msg) = test

  try:
    testfile = os.path.join(working_dir, rel_testfile)
    with open(testfile, "r") as f:
      commands = [t for t in f.readlines()]

      (equal_output, output) = run_test(calc, calcref, commands)
      outcmb,outcmd_ref = output
      out_stream = StringIO()
      is_pass = print_cmds(outcmb, outcmd_ref,
                           mask,
                           False, True, False,
                           out_stream)

      out_stream.seek(0)
      log_file.write(out_stream.getvalue())

      res = OutRes(is_pass)
      res.out = out_stream
      return res

  except Exception as e:
    res = OutRes(False)
    res.has_exception = True
    res.exception = e
    return res


def test_submission(handin_path, log_file, student_file):
  # Prepare the working dir
  print("Processing %s" % student_file, file=log_file)

  all_res = AllRes()
  working_dir = prepare_working_dir(handin_path, student_file)

  try:
    # Compile
    print("Compilation...", file=log_file)
    all_res.comp_res = compile_calc(working_dir, log_file)
    if not all_res.comp_res.success:
      print("Failed compilation", file=log_file)
      return all_res

    (all_res.name, all_res.userid) = read_name(working_dir)

    # Check for illegal instructions
    print("Check functions...", file=log_file)
    all_res.func_check_res = check_illegal_functions(working_dir, log_file)
    if not all_res.func_check_res.success:
      return all_res

    calc = os.path.join(working_dir, "calc")
    calc_ref = os.path.join(working_dir, "calc-ref")

    # Test questions
    print("Q3...", file=log_file)
    all_res.q3 = test_res(working_dir, calc, calc_ref, tests[0], log_file)
    print("Q4...", file=log_file)
    all_res.q4 = test_res(working_dir, calc, calc_ref, tests[1], log_file)
    print("Q5...", file=log_file)
    all_res.q5 = test_res(working_dir, calc, calc_ref, tests[2], log_file)
    print("Q6...", file=log_file)
    all_res.q6 = test_res(working_dir, calc, calc_ref, tests[3], log_file)
    print("Q8...", file=log_file)
    all_res.q8 = test_res(working_dir, calc, calc_ref, tests[4], log_file)
    print("Q9...", file=log_file)
    all_res.q9 = test_res(working_dir, calc, calc_ref, tests[5], log_file)
  except Exception as e:
    print(e)
  finally:
    if (NOT_CLEAN_TMP_IF_ERROR and
        not ((not all_res.q3 is None) and all_res.q3.success and
             (not all_res.q4 is None) and all_res.q4.success and
             (not all_res.q5 is None) and all_res.q5.success and
             (not all_res.q6 is None) and all_res.q6.success and
             (not all_res.q8 is None) and all_res.q8.success and
             (not all_res.q9 is None) and all_res.q9.success)):
        print("%s: %s" % (all_res.name, working_dir))
    else:
        shutil.rmtree(working_dir)

  return all_res

def print_verbose_results(all_res, outstream):
  if (not all_res.comp_res.success):
    return
  return

def _extend(s, max_length):
  if len(s) < max_length:
    s = " " * (max_length - len(s)) + s
  else:
    return s
  return s

def print_score(all_res, outstream):
  scores = []
  if (not all_res.comp_res.success) or (not all_res.func_check_res.success):
    scores = [0,0,0,0,0,0]
  else:
    scores = [15 if all_res.q3.success else 0,
              15 if all_res.q4.success else 0,
               5 if all_res.q5.success else 0,
               5 if all_res.q6.success else 0,
               5 if all_res.q8.success else 0,
               5 if all_res.q9.success else 0]

  template_map = {
    "STUDENTNAME" : _extend(all_res.name_from_file if all_res.name is None else all_res.name,30),
    "Q3" : _extend("%d" % scores[0], 2),
    "Q4" : _extend("%d" % scores[1], 2),
    "Q5" : _extend("%d" % scores[2], 2),
    "Q6" : _extend("%d" % scores[3], 2),
    "Q8" : _extend("%d" % scores[4], 2),
    "Q9" : _extend("%d" % scores[5], 2),
    "TOTAL" : _extend("%d" % functools.reduce(lambda x, y: x+y, scores, 0),2)
  }

  template = """$STUDENTNAME $Q3 $Q4 $Q5 $Q6 $Q8 $Q9 $TOTAL"""

  res = Template(template).substitute(template_map)
  print(res, file=outstream)

def process_student_submission(handin_path,
                               out_path,
                               student_submission):
  pass

def main():
  IN_PATH = "/users/profs/2018/sergio.mover/2022/CSE205/calclab/grade/submissions" 
  OUT_PATH = "/users/profs/2018/sergio.mover/2022/CSE205/calclab/grade/results"
  HANDIN_PATH = "/users/profs/2018/sergio.mover/2022/CSE205/calclab-handin"

  parser = argparse.ArgumentParser()
  parser.add_argument("--submission-path",
                      dest='submission_path',
                      help="Path to a folder containing the submissions for all the students.")
  parser.add_argument("--out-path",
                      dest='out_path',
                      help="Path to the folder containing the output of the grading.")

  parser.add_argument("--handin-path",
                      dest='handin_path',
                      help="Path of the handin files as sent to students (used to compile the student solution.")

  args = parser.parse_args()

  def read_path(opt_value):
    if opt_value is None:
      print("Missing path!")
    path = os.path.abspath(opt_value)
    if not os.path.isdir(path):
      print("%s directory does not exist!" % path)
    return path
  in_path,out_path,handin_path = read_path(args.submission_path),read_path(args.out_path),read_path(args.handin_path)


  summary = open(os.path.join(out_path, "summary.txt"), "w")
  print(_extend("Name", 30),
        _extend("Q3",2),
        _extend("Q4",2),
        _extend("Q5",2),
        _extend("Q6",2),
        _extend("Q8",2),
        _extend("Q9",2),
        _extend("TOTAL",2), file=summary)
  files = os.listdir(in_path)
  files.sort()
  for submission in files:
    if not submission.endswith("-calc.c"):
      continue

    print("Processing... ", submission)

    prefix_name = os.path.basename(submission)[:-len("-calc.c")]
    log_file = open(os.path.join(out_path, "%s.log" % prefix_name), "w")
    res = test_submission(handin_path,
                          log_file,
                          os.path.join(in_path, submission))
    res.name_from_file = prefix_name
    print_score(res, summary)
    log_file.close()

if __name__ == "__main__":
  main()
