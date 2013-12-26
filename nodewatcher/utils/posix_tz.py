import os
import pytz


def get_posix_tz(zone):
    """
    Returns a timezone definition in POSIX TZ format. Raises ValueError
    when the timezone name is not valid.

    :param zone: Timezone name (for example 'Europe/Ljubljana')
    :return: POSIX TZ string or None if no data is available
    """

    try:
        with pytz.open_resource(zone) as tz:
            # Seek to the end of timezone datafile
            tz.seek(-2, os.SEEK_END)
            while tz.tell() > 0:
                # Scan bytes towards the front to discover the second to last newline
                c = tz.read(1)
                if c == '\n':
                    break
                tz.seek(-2, os.SEEK_CUR)

            return tz.readline().strip() or None
    except (IOError, ValueError):
        raise ValueError("Invalid timezone specified")
