import sublime, sublime_plugin
import subprocess, thread, os

def cleanup_prelude(text):
    #first item minus the > at the beginning
    repeated_text = text.split("| ")[0].replace('>', '') + "| "
    return text.replace(repeated_text, "")

class ghci_interpret(sublime_plugin.ApplicationCommand):
    def __init__(self):
        print "HI!!!!!"
        self.process = subprocess.Popen(["ghci"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if self.process.stdout:
            thread.start_new_thread(self.read_stdout, ())

        if self.process.stderr:
            thread.start_new_thread(self.read_stderr, ())
        
        self.setup_prompt()
        
    def setup_prompt(self):
        self.process.stdin.write(":set prompt >")
        self.process.stdin.write('\n')
        # we force ghci to print something to keep it from buffering its first "Prelude>" output
        self.process.stdin.write("print \"GHCi Ready.\"")
        self.process.stdin.write('\n')
    
    def read_stdout(self):
        while True:
            print cleanup_prelude(self.process.stdout.readline())
            
    def read_stderr(self):
        while True:
            print cleanup_prelude(self.process.stderr.readline())
    
    def run(self):
        window = sublime.active_window()
        view = window.active_view()
        ghci = self.process.stdin
        for region in view.sel():
            if not region.empty():
                # Get the selected text
                text = view.substr(region)
                # Write to GHCi using multi-line syntax so we can support multiple lines
                map(ghci.write, [":{", '\n', text, '\n', ":}", '\n'])