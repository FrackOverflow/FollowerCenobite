# FC Style Guide
Unless specifically stated, FC follows the standard set out in [PEP 8](https://peps.python.org/pep-0008/#introduction).

## Linting
FC using flake8 for linting. The flake8 configuration in setupconfig has the following rules:
Ignore E501 - Lines must be <79 characters long

## General
### Naming
Methods & Functions:
- All methods and functions are in lowercase with name that describe their implementation
- Public API methods should have a name that describes their end result (instead of implementation)
- Private methods start with an underscore
- Public methods do not start with an underscore
- Function names should (usually) include a verb

Classes:
- All classes are named in camel case without exception.

Files:
- All File & Folder names are Capitalized with spaces removed
- All python & static json files are prefixed with FC_****.py

### Comments
The following items should **always have a docstring**:
- Class
- Public Method
- Function

The following items should **always have a descriptive comment**:
- Private method
- Class member variables
- Constants

Unless the implementation is particularly complex, the following **do not need a comment**:
- Dunder methods

### Type Hints
Type hints are preferred *where they make things more clear.* Especially for complex functionality where the type is unlikely to change.

However, type hints can get in the way of clean code: 
- Functions may be rewritten to return different types
- Functions may return different types by design (an issue that deserves its own section...) 
- Sometimes Python has already determined a return/arg type

You know you need to add a type hint when you get frustrated through repeated failures to access members w/ hints! Don't hestitate to remove unhelpful type hints, they should serve the developer.

### Constructors
**Constructors** should stack each argument on a seperate line:
```
def __init__(self,
             arg1,
             arg2,
             ...
             argn):
    # Implementation
```

### Line Length
Line length is not limited for this project. That doesn't mean you shouldn't ever wrap a line, but the usual 79 characters is crazy. Use your best judgement here.

### UI
FC supports dark and light mode, take this into consideration when designing UI.

#### Colors
Logo:
- Blue Gradient (\#0081FB to \#007ffa)

GUI:
- dark colors
- light colors