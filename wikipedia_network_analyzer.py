import wikipediaapi  # pip3 wikipedia-api
import csv
import sys
import requests

exclude = [
    "Wikipedia:",
    "File:",
    "Template:",
    "Template talk:",
    "Help:",
    "Category:",
    "Talk:",
    "Portal:",
    "Module:",
]

# convert dict of wiki links to list of link titles
def dl(node: dict):
    out = []
    for link in node:
        out.append(link)

    return out


# prune links to internal wikipedia pages such as editor discussions
def prune(node: list, exclude: list):
    hit = []
    for link in node:
        if any(ex in link for ex in exclude):
            hit.append(link)

    for link in hit:
        node.remove(link)

    return node


# return article creation date if available
def get_date_created(root: str):
    node = requests.get(
        f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvlimit=1&rvprop=timestamp&rvdir=newer&format=json&titles={root}"
    )
    # print(f"CODE: {node.status_code}")
    try:
        return list(node.json()["query"]["pages"].values())[0]["revisions"][0][
            "timestamp"
        ]
    except:
        return "NA"


# build a network of links starting from a given root node; return a list of edges
def crawl(root: str):
    global exclude

    crawled = []
    new_links = []
    edges = []

    node = prune(dl(wiki.page(root).links), exclude)
    edges.append((root, "", get_date_created(root)))

    # crawl the root node
    for link in node:
        print(f"{root} -> {link}")
        new_links.append(link)
        edges.append((root, link, get_date_created(link)))
    crawled.append(root)

    # crawl through all the links found in the root node
    for l in new_links:
        node = prune(dl(wiki.page(l).links), exclude)

        for link in node:
            print(f"{l} -> {link}")
            edges.append((l, link, get_date_created(link)))

        crawled.append(l)

    return edges


if __name__ == "__main__":

    # Wikipedia language
    wiki = wikipediaapi.Wikipedia("en")

    search_query = sys.argv[1]
    print(f"Searching: {search_query}")

    file_out_name = f'{search_query.replace(" ", "_")}_wiki_edges.csv'

    with open(file_out_name, "w", newline="") as csv_out:
        writer = csv.writer(csv_out, delimiter=",")

        # Write CSV header
        writer.writerow(["Source", "Target", "Target Creation Date"])

        # populate CSV
        for l in crawl(search_query):
            writer.writerow(l)
