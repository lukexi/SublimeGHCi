import sublime, sublime_plugin
import subprocess, thread, os, os.path

#GHCi gives us lots of "Prelude|" lines when we give it multi-line input, so we clean these up
def cleanup_prelude(text):
    #first item minus the > at the beginning
    repeated_text = text.split("| ")[0].replace('>', '') + "| "
    return text.replace(repeated_text, "")

def is_literate(text):
    return text[0:2] == "> "

def remove_literate(text):
    if (is_literate(text)):
        return text[2:]
    return text

def filter_literate_text(text):
    if (not is_literate(text)):
        return text
    return '\n'.join(map(remove_literate, text.splitlines()))

#Turns top-level assignments (e.g. x = 5) into let statements to work with GHCi
def add_let_if_needed(text):
    keywords = ["let", "data", "type"]
    has_no_equals_sign = text.find("=") == -1
    begins_with_keyword = any([text.startswith(keyword) for keyword in keywords])
    if (has_no_equals_sign or begins_with_keyword):
        return text
    return "let " + text

#Group together lines with subsequent indented lines to determine what should be given to GHCi using multi-line mode and what to give with single-line mode
group_indented_sections_testcase = """\
do
    x <- return 1
    case x of
        1 -> print "hi"
    print "seven"
print "ham"
do
    x <- return 5
    print x
print "cheese"
print "whiz"
"""
def group_indented_sections(text):
    groups = []
    current_group = []
    for line in text.splitlines():
        if line[:1].isspace():
            current_group.append(line)
        else:
            if len(current_group):
                groups.append(current_group)
            current_group = [line]
    if len(current_group):
        groups.append(current_group)
    return groups

def ghci(text):
    sublime.run_command("ghci_interpret_text", {"text":text})

class GhciLoadModule(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        file_dir = os.path.dirname(file_name)
        ghci(":cd " + file_dir)
        ghci(":load " + quote_text(file_name) + " " + quote_text(documentation_helper_path()))
        ghci(":module +FindDocumentation")

def quote_text(text):
    return "\"" + text + "\""

class GhciCommand(sublime_plugin.TextCommand):
    def run_command_on_regions(self, command, quote=False):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                if quote:
                    text = quote_text(text)
                ghci(command+" "+text)

class GhciOpenModuleDocs(GhciCommand):
    def run(self, edit):
        self.run_command_on_regions("openDocsFor", quote=True)

class GhciBrowseModule(GhciCommand):
    def run(self, edit):
        self.run_command_on_regions(":browse")

class GhciPrintType(GhciCommand):
    def run(self, edit):
        self.run_command_on_regions(":type")

class GhciPrintInfo(GhciCommand):
    def run(self, edit):
        self.run_command_on_regions(":info")

class GhciInterpretRegions(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        print "hi"
        prepend = ""
        if (kwargs.has_key("prepend")):
            prepend = kwargs["prepend"]
        # for each region in the current view, run on either the region's selection or the line
        for region in self.view.sel():
            if not region.empty():
                # Get the selected text
                text = self.view.substr(region)
            else: # Get the text of the current line
                text = self.view.substr(self.view.line(region))
            self.tell_ghci_multiline(prepend + text)
    
    def tell_ghci_multiline(self, text):
        # Write to GHCi using multi-line syntax so we can support multiple lines
        text = filter_literate_text(text)
        grouped_lines = group_indented_sections(text)
        for line_group in grouped_lines:
            is_single_line = len(line_group) == 1
            line_group_with_let_if_needed = [add_let_if_needed(line_group[0])] + line_group[1:]
            if (is_single_line):
                self.tell_ghci(line_group_with_let_if_needed[0])
            else:
                map(self.tell_ghci, [":{"] + line_group_with_let_if_needed + [":}"])
    
    def tell_ghci(self, text):
        ghci(text)

def documentation_helper_path():
    return sublime.packages_path() + "/SublimeGHCi/" + "FindDocumentation.hs"

class GhciInterpretText(sublime_plugin.ApplicationCommand):
    def __init__(self):
        
        self.process = subprocess.Popen(["ghci", documentation_helper_path()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if self.process.stdout:
            thread.start_new_thread(self.read_stdout, ())

        if self.process.stderr:
            thread.start_new_thread(self.read_stderr, ())
        
        self.setup_prompt()
        
    def setup_prompt(self):
        self.tell_ghci(":set prompt >")
        # we force ghci to print something to keep it from buffering its first "Prelude>" output
        self.tell_ghci("print \"GHCi Ready.\"")
    
    def read_stdout(self):
        while True:
            print cleanup_prelude(self.process.stdout.readline())
            
    def read_stderr(self):
        while True:
            print cleanup_prelude(self.process.stderr.readline())
    
    def tell_ghci(self, text):
        ghci = self.process.stdin
        print text
        map(ghci.write, [text, '\n'])
    
    def run(self, text=""):
        self.tell_ghci(text)
