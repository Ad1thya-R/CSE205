import sys
import os
import argparse
import logging
import tempfile
from threading import Timer
from subprocess import Popen, PIPE, check_output, run, STDOUT
import re
import tempfile


import functools

MASK_BIN=0x1
MASK_HEX=0x2
MASK_UNSIGNED=0x4
MASK_SIGNED=0x8
MASK_FLAGS=0x10

MASK_ALL = MASK_BIN | MASK_HEX | MASK_UNSIGNED | MASK_SIGNED | MASK_FLAGS

tests_list = [
  ("test_printbin.txt", MASK_BIN,      "Checking the correctness of print_binary"),
  ("test_parsebin.txt", MASK_UNSIGNED, "Checking correctness of from_binary_string"),
  ("test_printbin.txt", MASK_HEX,      "Checking the correctness of print_hexadecimal"),
  ("test_parsehex.txt", MASK_UNSIGNED, "Checking correctness of from_hexadecimal_string"),
  ("test_parsebin.txt", MASK_SIGNED, "Checking correctness of is_negative"),
  ("test_cf.txt", MASK_FLAGS, "Checking correctness of print_condition_codes"),
]

class CmdRes:
  def __init__(self, cmd):
    self.cmd = cmd
    self.out_lines = []
    self.numbers = []

    self.cf = None
    self.zf = None
    self.sf = None
    self.of = None

  def add_line(self, l):
    self.out_lines.append(l)

  def add_numbers(self, binary, hexa, unsigned, signed):
    data = (binary, hexa, unsigned, signed)
    self.numbers.append(data)

  def set_cf(self, value):
    self.cf = value

  def set_zf(self, value):
    self.zf = value

  def set_sf(self, value):
    self.sf = value

  def set_of(self, value):
    self.of = value

  def __eq_num(self, other_cmd, num):
    return (
      len(self.numbers) == len(other_cmd.numbers) and
      functools.reduce(lambda acc,y: acc and y[0][num].lower() == y[1][num].lower(),
                       zip(self.numbers,other_cmd.numbers), True)
    )


  def eq_bin(self, other_cmd):
    return self.__eq_num(other_cmd, 0)

  def eq_hex(self, other_cmd):
    return self.__eq_num(other_cmd, 1)

  def eq_unsigned(self, other_cmd):
    return self.__eq_num(other_cmd, 2)

  def eq_signed(self, other_cmd):
    return self.__eq_num(other_cmd, 3)

  def eq_flags(self, other_cmd):
    return (
      self.cf == other_cmd.cf and
      self.zf == other_cmd.zf and
      self.sf == other_cmd.sf and
      self.of == other_cmd.of
    )

    return self.__eq_num(other_cmd, 3)



def parse_output(output, test_case):
  ignore=["Welcome to calc","ciao"]
  re_prompt_txt = "[\s]*([0-9]+) > ([a-zA-Z0-9\s\_\+><\-\*\^\|&!\(\)\_ ]+)"
  re_prompt = re.compile(re_prompt_txt)

  # 0b0010_1010    0x (unsigned: 42, signed: 42)
  re_bin_txt = "[\s]*0b([0-1_]*)[\s]+0x([0-9a-fA-F_]*)[\s]*\(unsigned: ([0-9]+), signed: ([\-0-9]+)\)"
  re_bin = re.compile(re_bin_txt)

  re_bin_txt = "[\s]*0b([0-1_]*)[\s]+0x([0-9a-fA-F_]*)[\s]*\(unsigned: ([0-9]+), signed: ([\-0-9]+)\)"
  re_bin = re.compile(re_bin_txt)

  re_flag_txt = "[\s]*([CFSO]F)[\s]*=[\s]*([0-1]*)"
  re_flag = re.compile(re_flag_txt)



  def is_number(re_bin, string):
    res = re_bin.match(string)
    if res:
      return (True, (res.group(1),res.group(2),res.group(3),res.group(4)))
    else:
      return (False, None)

  cmds= []
  cmd = None

  for l in output.splitlines():
    l = l.strip()
    if (not l):
      continue
    for i in ignore:
      if l.startswith(i):
        continue

    new_prompt = re_prompt.match(l)
    if new_prompt:
      if not cmd is None:
        cmds.append(cmd)
      cmd = CmdRes(new_prompt.group(2)) #
    elif (not cmd is None):
      cmd.add_line(l)

      # number
      (res, numbers) = is_number(re_bin, l)
      if (res):
        cmd.add_numbers(numbers[0],numbers[1],numbers[2],numbers[3])

      # FLAG
      if (l.startswith("CF") | l.startswith("ZF") |
          l.startswith("SF") | l.startswith("OF")):
        res = re_flag.match(l)
        if (res):
          flag = res.group(1)
          val =  res.group(2)

          if (flag == "CF"): cmd.set_cf(val)
          if (flag == "ZF"): cmd.set_zf(val)
          if (flag == "SF"): cmd.set_sf(val)
          if (flag == "OF"): cmd.set_of(val)


  if (not cmd is None):
    cmds.append(cmd)

  return cmds

def print_cmds(expected,result,
               mask = MASK_ALL,
               print_full_output=False, print_when_fail=False,
               stop_at_first=False,
               out=sys.stdout):
  all_pass = True

  if (len(expected) != len(result)):
    raise Exception("Script error: found %d instead of %d commands! (this should not happen, contact your instructor)" % (len(result), len(expected)))

  for exp,res in zip(expected, result):
    if (exp.cmd != res.cmd):
      raise Exception("Script error: found the command %s instead of %s! (this should not happen, contact your instructor)" % (res.cmd, exp.cmd))

    is_test_pass = (
      ( (not (mask & MASK_BIN)) or exp.eq_bin(res)) and
      ( (not (mask & MASK_HEX)) or exp.eq_hex(res)) and
      ( (not (mask & MASK_UNSIGNED)) or exp.eq_unsigned(res)) and
      ( (not (mask & MASK_SIGNED)) or exp.eq_signed(res)) and
      ( (not (mask & MASK_FLAGS)) or exp.eq_flags(res))
    )

    extended_print = print_full_output or (print_when_fail and not is_test_pass)

    if extended_print:
      print("================================================================================", file=out)
      print(file=out)

    if (is_test_pass):
      print("PASS:", exp.cmd, file=out)
    else:
      print("FAIL:", exp.cmd, file=out)
      all_pass = False

    if extended_print:
      print("\nExpected result:", file=out)
      print("%s" % "\n".join(exp.out_lines), file=out)

      print("\nYour result:", file=out)
      print("%s" % "\n".join(res.out_lines), file=out)

    if (not is_test_pass and stop_at_first):
      break

  return all_pass


def run_test(calc, calcref, test_cases):
  test_input="%s\nquit\n" % "\n".join(test_cases)
  test_input = test_input.encode("UTF-8")

  result_ref = run(
    [calcref, "-e"],
    input=test_input,
    stdout=PIPE, stderr=PIPE)

  result = run(
    [calc, "-e"],
    input=test_input,
    stdout=PIPE, stderr=PIPE)

  out_str = result.stdout.decode("UTF-8")
  ref_str = result_ref.stdout.decode("UTF-8")

  outcmd = parse_output(out_str, "")
  outcmd_ref = parse_output(ref_str, "")


  return (out_str == ref_str, (outcmd_ref, outcmd))



def main():
  def error(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

  calcref = "calc-ref-exec"
  calc = "calc-exec"


  parser = argparse.ArgumentParser()
  parser.add_argument("--print_all_output",
                      dest='print_all_output', action='store_true',
                      help="Print all the output.")
  parser.add_argument("--print_output_when_fail",
                      dest='print_output_when_fail', action='store_true',
                      help="Print the computed output and the expected output when a command fail.")
  parser.add_argument("--stop_at_first_failure",
                      dest='stop_at_first_error', action='store_true',
                      help="Stop the test after the first failure.")

  parser.add_argument("--my_test",
                      dest='my_test',
                      help="Specify a file containing a set of commands to test.")


  parser.add_argument("--only_print_binary",
                      dest='only_print_binary', action='store_true',
                      help="Run the test for print_binary.")
  parser.add_argument("--only_from_binary_string",
                      dest='only_from_binary_string', action='store_true',
                      help="Run the test for from_binary_string.")
  parser.add_argument("--only_print_hexadecimal",
                      dest='only_print_hexadecimal', action='store_true',
                      help="Run the test for print_hexadecimal.")
  parser.add_argument("--only_from_hexadecimal_string",
                      dest='only_from_hexadecimal_string', action='store_true',
                      help="Run the test for from_hexadecimal_string.")
  parser.add_argument("--only_is_negative",
                      dest='only_is_negative', action='store_true',
                      help="Run the test for is_negative.")
  parser.add_argument("--only_condition_codes",
                      dest='only_condition_codes', action='store_true',
                      help="Run the test for print_condition_codes.")

  parser.add_argument("--calcref",
                      dest='calcref',
                      help="Path to calc-ref executable (if not in path).")
  parser.add_argument("--calc",
                      dest='calc',
                      help="Path to calc executable (if not in path).")


  args = parser.parse_args()

  stop_at_first = args.stop_at_first_error
  print_when_fail = args.print_output_when_fail
  print_all_output = args.print_all_output


  to_use = {
    calcref : "calc-ref",
    calc : "calc"
  }

  current_path = os.getcwd()
  print(current_path)
  if (args.calcref):
    to_use[calcref] = args.calcref
  else:
    to_use[calcref] = os.path.join(current_path, "calc-ref")

  if (args.calc):
    to_use[calc] = args.calc
  else:
    to_use[calc] = os.path.join(current_path, "calc")

  for key,fname in to_use.items():
    if (not os.path.isfile(fname)):
      error("Cannot find the file %s" % fname)

  tests_to_run = None
  if (args.only_print_binary):
    tests_to_run = [tests_list[0]]
  if (args.only_from_binary_string):
    tests_to_run = [tests_list[1]]
  if (args.only_print_hexadecimal):
    tests_to_run = [tests_list[2]]
  if (args.only_from_hexadecimal_string):
    tests_to_run = [tests_list[3]]
  if (args.only_is_negative):
    tests_to_run = [tests_list[4]]
  if (args.only_condition_codes):
    tests_to_run = [tests_list[5]]

  if (args.my_test):
    if (not os.path.isfile(args.my_test)):
      error("Cannot find the test file %s" % args.my_test)

    tests_to_run = [(args.my_test, MASK_ALL, "Checking the correctness for all the functions")]

  if tests_to_run is None:
    tests_to_run = tests_list

  for (testfile, mask, msg) in tests_to_run:
    with open(testfile, "r") as f:
      print("Running commands in %s: %s" % (testfile, msg))
      commands = [t for t in f.readlines()]

      (equal_output, output) = run_test(to_use[calc], to_use[calcref], commands)
      outcmb,outcmd_ref = output
      is_pass = print_cmds(outcmb, outcmd_ref,
                           mask,
                           print_all_output, print_when_fail, stop_at_first)


      if (not is_pass):
        print("\nRun the command: \"python3 test.py --print_output_when_fail "
              "--stop_at_first_failure\" to debug the mistake\n")

        if stop_at_first:
          sys.exit(1)

      print()

if __name__ == "__main__":
    main()

