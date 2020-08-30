import os
import sys
import six

WINDOWS_MAGIC_PREFIX = u'\\\\?\\'

# Taken from beets github. Thank you for this blog post beets team!
# https://beets.io/blog/paths.html
def _fsencoding():
    """Get the system's filesystem encoding. On Windows, this is always
    UTF-8 (not MBCS).
    """
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    if encoding == 'mbcs':
        # On Windows, a broken encoding known to Python as "MBCS" is
        # used for the filesystem. However, we only use the Unicode API
        # for Windows paths, so the encoding is actually immaterial so
        # we can avoid dealing with this nastiness. We arbitrarily
        # choose UTF-8.
        encoding = 'utf-8'
    return encoding

def displayable_path(path, separator=u'; '):
    """Attempts to decode a bytestring path to a unicode object for the
    purpose of displaying it to the user. If the `path` argument is a
    list or a tuple, the elements are joined with `separator`.
    """
    if isinstance(path, (list, tuple)):
        return separator.join(displayable_path(p) for p in path)
    elif isinstance(path, six.text_type):
        return path
    elif not isinstance(path, bytes):
        # A non-string object: just get its unicode representation.
        return six.text_type(path)

    try:
        return path.decode(_fsencoding(), 'ignore')
    except (UnicodeError, LookupError):
        return path.decode('utf-8', 'ignore')

# Taken from beets github. Thank you for this blog post beets team!
# https://beets.io/blog/paths.html
def bytestring_path(path):
    """Given a path, which is either a bytes or a unicode, returns a str
    path (ensuring that we never deal with Unicode pathnames).
    """
    # Pass through bytestrings.
    if isinstance(path, bytes):
        return path

    # On Windows, remove the magic prefix added by `syspath`. This makes
    # ``bytestring_path(syspath(X)) == X``, i.e., we can safely
    # round-trip through `syspath`.
    if os.path.__name__ == 'ntpath' and path.startswith(WINDOWS_MAGIC_PREFIX):
        path = path[len(WINDOWS_MAGIC_PREFIX):]

    # Try to encode with default encodings, but fall back to utf-8.
    try:
        return path.encode(_fsencoding())
    except (UnicodeError, LookupError):
        return path.encode('utf-8')

# Taken from beets github. Thank you for this blog post beets team!
# https://beets.io/blog/paths.html
def syspath(path, prefix=True):
    """Convert a path for use by the operating system. In particular,
    paths on Windows must receive a magic prefix and must be converted
    to Unicode before they are sent to the OS. To disable the magic
    prefix on Windows, set `prefix` to False---but only do this if you
    *really* know what you're doing.
    """
    # Don't do anything if we're not on windows
    if os.path.__name__ != 'ntpath':
        return path

    if not isinstance(path, six.text_type):
        # Beets currently represents Windows paths internally with UTF-8
        # arbitrarily. But earlier versions used MBCS because it is
        # reported as the FS encoding by Windows. Try both.
        try:
            path = path.decode('utf-8')
        except UnicodeError:
            # The encoding should always be MBCS, Windows' broken
            # Unicode representation.
            encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
            path = path.decode(encoding, 'replace')

    # Add the magic prefix if it isn't already there.
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247.aspx
    if prefix and not path.startswith(WINDOWS_MAGIC_PREFIX):
        if path.startswith(u'\\\\'):
            # UNC path. Final path should look like \\?\UNC\...
            path = u'UNC' + path[1:]
        path = WINDOWS_MAGIC_PREFIX + path

    return path