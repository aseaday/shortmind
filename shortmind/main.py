from shortmind.loader.epub import EPUBBookLoader

if __name__ == "__main__":
    epub = EPUBBookLoader("test.epub")
    items = epub.list_items()
    print(items)
