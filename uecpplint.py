import functools
import sys
import sysconfig
import unicodedata

try:
  #  -- pylint: disable=used-before-assignment
  unicode
except NameError:
  #  -- pylint: disable=redefined-builtin
  basestring = unicode = str


import cpplint


def hook_function(oldfunction, newfunction):
    """
    Hook a python function, simple assign in doesn't work.
    """
    # https://stackoverflow.com/questions/35758323/hook-python-module-function
    @functools.wraps(oldfunction)
    def run(*args, **kwargs):
        return newfunction(oldfunction, *args, **kwargs)
    return run

def replace_function(oldfunction, newfunction):
    """
    Hook a python function, simple assign in doesn't work.
    """
    # https://stackoverflow.com/questions/35758323/hook-python-module-function
    @functools.wraps(oldfunction)
    def run(*args, **kwargs):
        return newfunction(*args, **kwargs)
    return run

OldError = cpplint.Error

_SUPPRESSED_MESSAGES = [
    'Tab found; better to use spaces',
    'Missing space before {',
    '{ should almost always be at the end of the previous line',
    'should be indented +1 space inside class',
    'An else should appear on the same line as the preceding }',
    'At least two spaces is best between code and comments',
    '"virtual" is redundant since function is already declared as "override"',
]

def Error(old_error, filename, linenum, category, confidence, message):
    for supprss in _SUPPRESSED_MESSAGES:
        if supprss in message:
            return
    old_error(filename, linenum, category, confidence, message)


def GetLineWidth(line):
  """Determines the width of the line in column positions.

  Args:
    line: A string, which may be a Unicode string.

  Returns:
    The width of the line in column positions, accounting for Unicode
    combining characters and wide characters.
  """
  tab_size = 4
  width = 0
  for uc in unicodedata.normalize('NFC', line):
    if unicodedata.east_asian_width(uc) in ('W', 'F'):
      width += 2
    elif not unicodedata.combining(uc):
      if (sys.version_info.major, sys.version_info.minor) <= (3, 2):
        is_wide_build = sysconfig.get_config_var("Py_UNICODE_SIZE") >= 4
        is_low_surrogate = 0xDC00 <= ord(uc) <= 0xDFFF
        if not is_wide_build and is_low_surrogate:
          width -= 1
    elif uc == '\t':
      # Expand tabs to the next multiple of tab_size
      width += tab_size - (width % tab_size)
    else:
      width += 1
  return width


# cpplint._line_length = 120

cpplint.Error = hook_function(cpplint.Error, Error)
cpplint.GetLineWidth = replace_function(cpplint.GetLineWidth, GetLineWidth)


def main():
    cpplint.main()


if __name__ == '__main__':
    main()