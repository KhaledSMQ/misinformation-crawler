import re
import arrow
import pendulum


def extract_datetime_string(date_string, date_format=None, timezone=False, simplified_formats=False):
    # Replace lower-case AM and PM with upper-case equivalents since pendulum
    # can only interpret upper-case
    if date_string:
        date_string = date_string.replace("am", "AM").replace("pm", "PM")

    # Huffington Post (sometimes) uses datetimes in the following format:
    # YYYY-MM-DD hh:mm:ss Z and sometimes the normal form with 'T' and no spaces
    # Here we convert the first to the second
    # so 2019-01-30 09:39:19 -0500 goes to 2019-01-30T09:39:19-0500
    if date_string:
        if re.search(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s[+-]\d{4}", date_string):
            date_string = date_string.replace(" -", "-").replace(" +", "+").replace(" ", "T")

    # Date strings with a shortened version of a month name followed by a dot need to be
    # in the correct format to be parsed correctly
    if date_string:
        for character_following_shortened_month in [',', '.', ' ']:
            date_string = date_string.replace('Sept' + character_following_shortened_month, 'Sep' + character_following_shortened_month)

    # Some sites have a large number of possible formats, in the site configs
    # which we reduce by removing characters from the date_string
    if simplified_formats:
        for separator_character in [',', '.', ' ']:
            date_string = date_string.replace(separator_character, '')

    # First try pendulum as it seems to have fewer bugs
    # Source: http://blog.eustace.io/please-stop-using-arrow.html
    _datetime = pendulum_datetime_extract(date_string, date_format)
    if not _datetime:
        # then try arrow as it can extract dates froom within longer non-date strings
        _datetime = arrow_datetime_extract(date_string, date_format)

    # If a datetime is successfully extracted, re-export as ISO-8601 string.
    # NOTE: Datetime objects generated by both arrow and pendulum support the format() method
    if _datetime:
        if timezone:
            return _datetime.format('YYYY-MM-DDTHH:mm:ssZ')
        return _datetime.format('YYYY-MM-DDTHH:mm:ss')
    return None


def pendulum_datetime_extract(date_string, date_format=None):
    # Attempt to extract the date using the specified format if provided
    try:
        if date_format:
            if "unix" in date_format:
                if "milliseconds" in date_format:
                    date_string = date_string[:-3]
                _datetime = pendulum.from_timestamp(int(date_string))
            else:
                _datetime = pendulum.from_format(date_string, date_format)
        else:
            # Assume ISO-8601
            _datetime = pendulum.parse(date_string)
    except (ValueError, TypeError, RuntimeError):
        _datetime = None
    return _datetime


def arrow_datetime_extract(date_string, date_format=None):
    _datetime = None
    # Some tricks to avoid some undesired outcomes:
    # (1) Arrow will match the first/last digits of a 4-digit year if passed a 2-digit year format
    #
    if date_format:
        # If 2-digit year at start or end of format string, first try to extract date with equivalent
        arrow_separators = ['-', '/', '.']
        if date_format[:2] == 'YY' and date_format[2] in arrow_separators:
            _datetime = arrow_datetime_extract(date_string, "YY{}".format(date_format))
        if not _datetime and date_format[-2:] == 'YY' and date_format[-3] in arrow_separators:
            _datetime = arrow_datetime_extract(date_string, "{}YY".format(date_format))

    if not _datetime:
        try:
            if date_format:
                _datetime = arrow.get(date_string, date_format)
            else:
                # Assume ISO-8601
                _datetime = arrow.get(date_string)
        except (ValueError, TypeError, RuntimeError):
            # If we fail to parse a datetime, return None
            _datetime = None
    return _datetime
