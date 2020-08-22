def index_page(link):
    try:
        print("1")
        url = link
        print(url)
        resp = requests.get(url)
        print(resp)
        sopa = bs(resp.content, "html.parser")
        filename = slugify(url)
        with open(f"wikipedia/{filename}.html", 'wb') as f:
            f.write(sopa.encode(formatter=None))
        return link
    except:
        print("3")
        pass
        return "error"