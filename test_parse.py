from parse.base_parser import BaseParsingService

class Dummy(BaseParsingService):
    def parse_row(self, line): pass
    def build_report(self, rows, raw_text, lines): pass

d = Dummy()
print(d.extract_times("08:50 03:37"))
print(d.extract_times("08:25 03:52"))
print(d.extract_times("01:04 10:00"))
