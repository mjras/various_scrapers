#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, codecs, re
from boilerpipe.abstract import Boilerpipe
try:
    import htmlentitydefs
except ImportError: #Python3
    import html.entities as htmlentitydefs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

file_path = sys.argv[1]
extractor = sys.argv[2] if len(sys.argv) > 2 else "RegExp"

with open(file_path, 'r') as html_file:
    html_text = html_file.read()

if not isinstance(html_text, unicode):
    try:
        html_text_unicode = unicode(html_text, 'utf-8')
    except UnicodeDecodeError:
        try:
            html_text_unicode = unicode(html_text, 'iso-8859-1')
        except UnicodeDecodeError:
            try:
                html_text_unicode = unicode(html_text, 'cp1252')
            except UnicodeDecodeError as e:
                print "ERROR conv to unicode", e
else:
    html_text_unicode = html_text

if extractor.lower() != "regexp":
    try:
        bp = Boilerpipe(html_text_unicode)
        text = bp.extract(extractor)
    except Exception:
        try:
            bp = Boilerpipe(html_text)
            text = bp.extract(extractor)
        except Exception as e:
            sys.stderr.write("ERROR converting %s in unicode to extract text with BoilerPipe:\n%s\n" % (file_path, e))
    del bp
else:
    text = html_text_unicode

### Entity Nonsense from A. Swartz's html2text http://www.aaronsw.com/2002/html2text/html2text.py ###

def name2cp(k):
    if k == 'apos': return ord("'")
    if hasattr(htmlentitydefs, "name2codepoint"): # requires Python 2.3
        return htmlentitydefs.name2codepoint[k]
    else:
        k = htmlentitydefs.entitydefs[k]
        if k.startswith("&#") and k.endswith(";"): return int(k[2:-1]) # not in latin-1
        return ord(codecs.latin_1_decode(k)[0])

def charref(name):
    if name[0] in ['x','X']:
        c = int(name[1:], 16)
    else:
        c = int(name)
    try:
        return unichr(c)
    except NameError: #Python3
        return chr(c)

def entityref(c):
    try: name2cp(c)
    except KeyError: return "&" + c + ';'
    else:
        try:
            return unichr(name2cp(c))
        except NameError: #Python3
            return chr(name2cp(c))

def replaceEntities(s):
    s = s.group(1)
    if s[0] == "#": 
        return charref(s[1:])
    else: return entityref(s)

r_unescape = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")
def unescape(s):
    s = s.replace('&nbsp;', ' ')
    return r_unescape.sub(replaceEntities, s)

### End Entity Nonsense ###

re_clean_comments = re.compile(r'<!--.*?-->', re.I)
re_clean_javascript = re.compile(r'<script[^>]*/?>.*?</script>', re.I)
re_clean_style = re.compile(r'<style[^>]*/?>.*?</style>', re.I)
re_clean_balises = re.compile(r'<[/!]?\[?[a-z0-9\-]+[^>]*>', re.I)
re_clean_blanks = re.compile(r'[\s]+')
try:
    text = unescape(text)
    text = re_clean_blanks.sub(' ', text)
    text = re_clean_comments.sub(' ', text)
    text = re_clean_javascript.sub(' ', text)
    text = re_clean_style.sub(' ', text)
    text = re_clean_balises.sub(' ', text)
    text = re_clean_blanks.sub(' ', text).strip()
    pass
except:
    pass

print text

