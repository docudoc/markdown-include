# Markdown-Include

This is an extension to [Python-Markdown](https://pythonhosted.org/Markdown/) which provides an "include" function, similar to that found in LaTeX (and also the C pre-processor and Fortran).

It is based on the original [Markdown-Include](https://github.com/cmacmackin/markdown-include).


## Installation

This module can now be installed using ``pip``.

```
pip install git+https://github.com/docudoc/markdown-include.git#egg=markdown-include
```

## Usage
This module can be used in a program in the following way:

```python
import markdown
html = markdown.markdown(source, extensions=['markdown_include.include'])
```

The syntax for use within your Markdown files is ``{!filename!}``. This statement will be replaced by the contents of ``filename``.

Markdown-Include will work recursively, so any included files within ``filename`` will also be included. This replacement is done prior to any other Markdown processing, so any Markdown syntax that you want can be used within your included files.

By default, all file-names are evaluated relative to the location from which Markdown is being called. If you would like to change the directory relative to which paths are evaluated, then this can be done by specifying the extension setting ``base_path``.


## Configuration

The following settings can be specified when initialising the plugin.

- __base_path__: Default location from which to evaluate relative paths for the include statement. _(Default: the run-directory)_
- __encoding__: Encoding of the files used by the include statement. _(Default: utf-8.)_
- __inheritHeadingDepth__ : If true, increases headings on include file by amount of previous heading. Combiens with headingOffset   option, below. _(Default: False)_
- __headingOffset__: Increases heading depth by a specific ammount, in addition to the inheritHeadingDepth Option. _(Default: 0)_
- __throwException__: If the extension is unable to find an included file it will throw an exception. Default behavior is to print a warning continue parsing the file. _(Default: False)_
- __relativeIncludes__: When true, includes can use relative paths. _(Default: False)_ [TBD]


## Examples

An example of setting the base path and file encoding is given below:

```python
import markdown
from markdown_include.include import MarkdownInclude

# Markdown Extensions
markdown_include = MarkdownInclude(
    configs={'base_path':'/srv/content/', 'encoding': 'iso-8859-1'}
)
html = markdown.markdown(source, extensions=[markdown_include])
```

Included files can inherit the heading depth of the location ``inheritHeadingDepth``, as well as receive a specific offset, ``headingOffset``

For example, consider the  files
```markdown
Source file
# Heading Level 1 of main file

{!included_file.md!}

## Heading Level 2 of main file

{!included_file.md!}
```

and included_file.md

```markdown
# This heading will be one level deeper from the previous heading
More included file content.
End of included content.
```
Then running the script
```python
import markdown
from markdown_include.include import MarkdownInclude

# Markdown Extensions
markdown_include = MarkdownInclude(
    configs={'inheritHeadingDepth':True}
)
html = markdown.markdown(source, extensions=[markdown_include])
```
produces
```html
<p>Source file</p>
<h1>Heading Level 1 of main file</h1>
<h2>This heading will be one level deeper from the previous heading</h2>
<p>More included file content.</p>
<p>End of included content.</p>
<h2>Heading Level 2 of main file</h2>
<h3>This heading will be one level deeper from the previous heading</h3>
<p>More included file content.</p>
<p>End of included content.</p>
```


