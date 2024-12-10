from datetime import datetime, timezone, timedelta

from moy_nalog.methods.method import BaseMethod


class TestDateToLocalISO:
    instance = BaseMethod("nothing")
    method = instance._format_date_to_local_iso

    def test_current_date(self):
        assert self.method(datetime.now())

    def test_special_date(self):
        # check on ISO 6801
        # https://ru.wikipedia.org/wiki/ISO_8601

        assert self.method(datetime(2024, 10, 3)) == "2024-10-03T23:59:59+05:00"
        assert self.method(datetime(2022, 3, 10)) == "2022-03-10T23:59:59+05:00"

    def test_date_unique(self):
        for _ in range(100):
            date = datetime.now().replace(microsecond=0)
            string_date = self.method(date)
            # Currently
            # if method get datetime object, then
            # datetime object formatting ->
            # hours=23, minutes=59, seconds=59
            # with timezone
            assert date.replace(
                hour=23,
                minute=59,
                second=59,
                tzinfo=timezone(timedelta(seconds=18000)),
            ) == datetime.fromisoformat(string_date)
        for _ in range(100):
            date = datetime.now().replace(microsecond=0)
            string_date = self.method()
            assert date.astimezone() == datetime.fromisoformat(string_date)
