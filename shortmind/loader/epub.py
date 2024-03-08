import os
import pickle
import string
import sys
from copy import copy
from pathlib import Path

from bs4 import BeautifulSoup as bs
from bs4 import Tag
from bs4.element import NavigableString
from ebooklib import ITEM_DOCUMENT, epub
from rich import print
from tqdm import tqdm
import re
from shortmind.loader.base import BaseBookLoader

url_pattern = r"(http[s]?://|www\.)+(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"


def is_text_link(text):
    return bool(re.compile(url_pattern).match(text.strip()))



class EPUBBookLoader(BaseBookLoader):
    def __init__(
        self,
        epub_name,
    ):
        self.exclude_filelist = ""
        self.only_filelist = ""
        self.epub_name = epub_name
        self.exclude_translate_tags = "sup"
        self.trans_taglist = "p".split(",")
        def _write_items_patch(obj):
            for item in obj.book.get_items():
                if isinstance(item, epub.EpubNcx):
                    obj.out.writestr(
                        "%s/%s" % (obj.book.FOLDER_NAME,
                                   item.file_name), obj._get_ncx()
                    )
                elif isinstance(item, epub.EpubNav):
                    obj.out.writestr(
                        "%s/%s" % (obj.book.FOLDER_NAME, item.file_name),
                        obj._get_nav(item),
                    )
                elif item.manifest:
                    obj.out.writestr(
                        "%s/%s" % (obj.book.FOLDER_NAME,
                                   item.file_name), item.content
                    )
                else:
                    obj.out.writestr("%s" % item.file_name, item.content)

        def _check_deprecated(obj):
            pass
        epub.EpubWriter._write_items = _write_items_patch
        epub.EpubReader._check_deprecated = _check_deprecated
        try:
            self.origin_book = epub.read_epub(self.epub_name)
        except Exception:
            # tricky monkey patch for #71 if you don't know why please check the issue and ignore this
            # when upstream change will TODO fix this
            def _load_spine(obj):
                spine = obj.container.find(
                    "{%s}%s" % (epub.NAMESPACES["OPF"], "spine"))

                obj.book.spine = [
                    (t.get("idref"), t.get("linear", "yes")) for t in spine
                ]
                obj.book.set_direction(
                    spine.get("page-progression-direction", None))

            epub.EpubReader._load_spine = _load_spine
            self.origin_book = epub.read_epub(self.epub_name)
            
    def filter_nest_list(self, p_list, trans_taglist):
        filtered_list = [p for p in p_list if not self.has_nest_child(p, trans_taglist)]
        return filtered_list
    
    def has_nest_child(self, element, trans_taglist):
        if isinstance(element, Tag):
            for child in element.children:
                if child.name in trans_taglist:
                    return True
                if self.has_nest_child(child, trans_taglist):
                    return True
        return False
    
    def _extract_paragraph(self, p):
        for p_exclude in self.exclude_translate_tags.split(","):
            # for issue #280
            if type(p) == NavigableString:
                continue
            for pt in p.find_all(p_exclude):
                pt.extract()
        return p
    
    @staticmethod
    def _is_special_text(text):
        return (
            text.isdigit()
            or text.isspace()
            or is_text_link(text)
            or all(char in string.punctuation for char in text)
        )

    def process_item(self, item):
        soup = bs(item.content, "html.parser")
        p_list = soup.findAll(["div", "p"])

        p_list = self.filter_nest_list(p_list, self.trans_taglist)

        text_list = []
        for p in p_list:
            if not p.text or self._is_special_text(p.text):
                continue
            new_p = self._extract_paragraph(copy(p))
            text_list.append(new_p.text)

        if soup:
            item.content = soup.encode()
        return text_list

    def list_items(self):
        results = []
        for item in self.origin_book.get_items_of_type(ITEM_DOCUMENT):
            results.append(self.process_item(item))
        return results
