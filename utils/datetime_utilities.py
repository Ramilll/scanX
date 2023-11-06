import datetime


class DateTimeUtilities:
    @staticmethod
    def timestamp_to_datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def datetime_to_timestamp(dt):
        return int(dt.timestamp())

    @staticmethod
    def get_current_timestamp():
        return int(datetime.datetime.now().timestamp())

    @staticmethod
    def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
        return dt.strftime(format_str)

    @staticmethod
    def parse_datetime(date_string, format_str="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.strptime(date_string, format_str)
