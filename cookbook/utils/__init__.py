import os
import sys
import six

WINDOWS_MAGIC_PREFIX = u'\\\\?\\'

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