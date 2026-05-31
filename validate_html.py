from html.parser import HTMLParser
import sys

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        # Self-closing tags in HTML5
        self_closing = ["area", "base", "br", "col", "embed", "hr", "img", "input", 
                        "link", "meta", "param", "source", "track", "wbr"]
        if tag not in self_closing:
            self.tags.append(tag)

    def handle_endtag(self, tag):
        self_closing = ["area", "base", "br", "col", "embed", "hr", "img", "input", 
                        "link", "meta", "param", "source", "track", "wbr"]
        if tag in self_closing:
            return
        if not self.tags:
            self.errors.append(f"Unexpected closing tag: </{tag}> (no tags open)")
        elif self.tags[-1] == tag:
            self.tags.pop()
        else:
            # Check if this tag exists in the open tags stack
            if tag in self.tags:
                # Find matching tag index
                idx = len(self.tags) - 1 - self.tags[::-1].index(tag)
                unclosed = self.tags[idx+1:]
                self.errors.append(f"Improperly nested tags. Closed </{tag}> before closing: {', '.join([f'<{t}>' for t in unclosed])}")
                self.tags = self.tags[:idx]
            else:
                self.errors.append(f"Closing tag </{tag}> does not match current open tag <{self.tags[-1]}>")

def main():
    filepath = r"D:\Desktop\sql.html"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        validator = HTMLValidator()
        validator.feed(html_content)
        
        print("HTML Validation Results:")
        if validator.errors:
            print(f"Found {len(validator.errors)} errors:")
            for err in validator.errors[:20]:
                print(f"- {err}")
            if len(validator.errors) > 20:
                print("... and more errors")
            sys.exit(1)
        else:
            print("Structure is 100% valid. No open/mismatched HTML tags found!")
            
    except Exception as e:
        print(f"Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
