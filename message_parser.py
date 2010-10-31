#!/usr/bin/env python

def parse(text):
    """
    This is what amounts to a simple lisp parser for turning the server's
    returned messages into an intermediate format that's easier to deal
    with than the raw (often poorly formatted) text.
    
    This parses generally, taking any lisp-like string and turning it into a
    list of nested lists, where each nesting (besides the outermost) indicates
    a parenthesized expression.  The outermost list is simply a container for
    holding multiple top-level parenthesized expressions. Ex: "(foo 1) (bar 2)"
    becomes [['foo', '1'], ['bar', '2']].
    """
    
    # make sure all of our parenthesis match
    if text.count("(") != text.count(")"):
        raise ValueError("Text has unmatching parenthesis!")
    
    # result acts as a stack that holds the strings grouped by nested parens
    result = []
    
    # the current level of indentation, used to append chars to correct level
    indent = 0
    
    # the non-indenting characters we find. these are kept in a buffer until
    # we indent or dedent, and then are added to the current indent level all
    # at once, for efficiency.
    s = []
    
    # whether we're currently in the middle of parsing a string
    in_string = False
    
    # the last character seen, None to begin with
    prev_c = None
    for c in text:
        # prevent parsing parens when inside a string (also ignores escaped
        # '"'s as well).
        if c == '"' and prev_c != "\\":
            in_string = not in_string
            s.append(c)
        
        # we only indent/dedent if not in the middle of parsing a string
        elif c == "(" and not in_string:
            # find current level of nesting
            cur = result
            for i in xrange(indent):
                cur = cur[-1]
            
            # add our buffered string onto the previous level, then clear it
            # for the next.
            if len(s) > 0:
                cur.append(''.join(s))
                s = []
            
            # append a new level of nesting to our list
            cur.append([])
            
            # increase the indent level so we can get back to this level
            indent += 1
        
        elif c == ")" and not in_string:
            # append remaining string buffer before dedenting
            if len(s) > 0:
                cur = result
                for i in xrange(indent):
                    cur = cur[-1]
                    
                # append our buffered string to the last level, then clear it
                cur.append(''.join(s))
                s = []
            
            # we finished with one level, so dedent back to the previous one
            indent -= 1
    
        # append non-space characters to the buffer list. spaces are delimiters
        # for expressions, hence are special.
        elif c != " ":
            # append the current string character to the buffer list.
            s.append(c)
        
        # we separate expressions by spaces
        elif c == " " and len(s) > 0:
            cur = result
            for i in xrange(indent):
                cur = cur[-1]
            
            # append our buffered string to the results
            cur.append(''.join(s))
            s = []
        
        # save the previous character. used to determine if c is escaped
        prev_c = c
    
    return result

if __name__ == "__main__":
    import sys
    
    # interactive mode if any args were specified
    if len(sys.argv) > 2:
           from pprint import pprint
           with open(sys.argv[1], 'r') as f:
               for line in f:
                   print "raw message:\n", line.strip()
                   print
                   print "parsed message:"
                   pprint(parse(line.strip()))
                   print "----"
                   raw_input()
                   print
    else:
        # just parse the message file
        with open(sys.argv[1], 'r') as f:
            for line in f:
                parse(line.strip())