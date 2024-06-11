# FC Style Guide
Unless specifically stated, FC follows the standard set out in [PEP 8](https://peps.python.org/pep-0008/#introduction).

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
Type hints are always preferred, they make coding quicker at very little cost. The C# dev in me loves them, however, they can get in the way, use your best judgement here.

## Specifics
### Classes
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