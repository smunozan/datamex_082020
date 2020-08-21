def index_page(link):
    try:
        print("1")
        resp = requests.get(link)
        print("2")
        sopa = bs(resp.content, "html.parser")
        filename = slugify(link)
        with open(f"wikipedia/{filename}.html", 'wb') as f:
            f.write(sopa.encode(formatter=None))
        return link
    except:
        print("3")
        pass
        return "error"