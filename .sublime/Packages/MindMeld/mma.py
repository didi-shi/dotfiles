import sublime, sublime_plugin
import json
import re
try:
    # Using Python 2's urllib2
    from urllib2 import urlopen, Request
    
    def parse_query(url, query):
        try:
            payload = {"query": query, "dialogue_context": {}, "verbose": True}
            #req = Request(url, json.dumps(payload), {'Content-Type': 'application/json'})
            req = Request(url, json.dumps(payload), {'Content-Type': 'application/json'})
            f = urlopen(req)
            response = f.read()
            f.close()
            data = json.loads(response)
            return data
        except:
            return None

except ImportError:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    
    def parse_query(url, query):
        try:
            payload = {"query": query, "dialogue_context": {}, "verbose": True}
            req = Request(url, json.dumps(payload).encode('utf8'), {'Content-Type': 'application/json'})
            f = urlopen(req)
            response = f.read()
            f.close()
            data = json.loads(response.decode())
            return data
        except:
            return None

class AnnotateNonNumericCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # get text selection
        sels = self.view.sel()
        for sel in sels:
            old_str = self.view.substr(sel)
            new_str = old_str
            if len(old_str) > 0:
                if old_str[0] != '{':
                    new_str = '{' + old_str
                if old_str[-1] != '}':
                    new_str = new_str + '|}'
            self.view.replace(edit, sel, new_str)


class AnnotateNumericCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        for sel in sels:
            old_str = self.view.substr(sel)
            new_str = old_str
            if len(old_str) > 0:
                if old_str[0] != '[':
                    new_str = '[' + old_str
                if old_str[-1] != ']':
                    new_str = new_str + '|]'
            self.view.replace(edit, sel, new_str)

class UnannotateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for sel in self.view.sel():
            if sel.empty():
                # search backward for '{' or '['
                # search forward for ']' or '}'
                itr1 = sel.b
                itr2 = sel.b
                # assume no stand-alone numeric facets
                while itr1 >= 0:
                    if self.view.substr(itr1) == '{':
                        break;
                    itr1 -= 1
                while itr2 < self.view.size():
                    if self.view.substr(itr2) == '}':
                        break;
                    itr2 += 1
                span_entity = self.view.substr(sublime.Region(itr1, itr2+1))
                span_entity = re.sub('\{', '', span_entity)
                span_entity = re.sub('\[', '', span_entity)
                span_entity = re.sub('\|.*[\[\}]', '', span_entity)
                self.view.replace(edit, sublime.Region(itr1, itr2+1), span_entity)


class BootstrapCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # get entire text of current view
        text = sublime.Region(0, self.view.size())
        lines = self.view.split_by_newlines(text)
        # check if parse endpoint is available
        if len(lines) == 0:
            return
        # extra parse endpoint in the first line
        url = self.view.substr(lines[0]).strip()
        buffer = []
        for line in lines[1:]:
            # bootstrap each line
            # print(self.view.substr(line))
            data = parse_query(url, self.view.substr(line).strip())
            if data:
                parsed = data['parsed_query']['parsed-query'] + '\n'
                # self.view.replace(edit, line, parsed)
                buffer.append(parsed)
            else:
                buffer.append(self.view.substr(line).strip() + '\n')
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        for line in buffer:
            self.view.insert(edit, self.view.size(), line)


class ValidateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass


class MmaAutocomplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        # print locations[0]
        if not view.match_selector(locations[0],
                "source.mma"):
            return []
        # get current caret location
        pos = view.sel()[0].begin()
        if view.substr(pos-1) == '|':
            sugs = [('hello','hello'), ('world', 'world')]
            # print sugs
            return sugs
        else:
            return []