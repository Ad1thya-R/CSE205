
CC=cc
ALLOWED=libc_start|stdin|stdout|fgets|fputs|putchar|puts|strcmp|strncmp|strtok|dyld_stub_binder

calc: calc.c
	$(CC) -o $@ -Wall $<

test_all: test.py test_cf.txt test_parsehex.txt test_printbin.txt test_parsebin.txt calc
	python3 test.py

test_printbin: test.py test_printbin.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_print_binary 

test_from_binary_string: test.py test_parsebin.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_from_binary_string

test_print_hexadecimal: test.py test_printbin.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_print_hexadecimal

test_from_hexadecimal_string: test.py test_parsehex.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_from_hexadecimal_string

test_is_negative: test.py test_printbin.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_is_negative

test_condition_codes: test.py test_cf.txt calc
	python3 test.py --stop_at_first_failure --print_output_when_fail --only_condition_codes

check: calc
	@F="$(shell nm $< | sed -ne 's/^.*U _//p' | egrep -v '$(ALLOWED)')"; \
	  if [ -n "$$F" ]; \
	  then echo "illegal functions: $$F";\
	  else echo "check for illegal passed";\
	  fi

clean:
	@rm -f calc test[0-9]*.log
