import json
from scholarly import scholarly
import pylcs

def load_json_bib(filename):
    """Requiring CSL Json export (from Zotero)."""
    with open(filename) as file:
        return json.load(file)

def get_json_bib_titles(json_bib: dict):
    """Get titles from CSL Json export (from Zotero) dictionary."""
    return [bib["title"].lower() for bib in json_bib]

def jaccard_similarity(str1, str2):
    set1, set2 = set(str1), set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def lcs_length(str1, str2):
    """Compute the harmonic mean of the length of the Longest Common Subsequence (LCS) between two strings."""
    lcs = pylcs.lcs_sequence_length(str1, str2)
    return lcs*2 / (len(str1)+len(str2)) # harmonic mean

def similarity_matrix_with_max(list1, list2, threshold=0.75, similarity=lcs_length):
    """Create a matrix of LCS lengths and return elements corresponding to max LCS in each row."""
    matrix = []
    max_pairs = []
    for str1 in list1:
        row = []
        for str2 in list2:
            row.append(similarity(str1, str2))
        matrix.append(row)
        # Find the index of the maximum element in the row
        row_max = max(row)
        max_index = row.index(row_max)
        # Append the corresponding elements of list1 and list2
        if row_max > threshold:
            max_pairs.append((str1, list2[max_index]))
        else:
            max_pairs.append((str1))
    return matrix, max_pairs

def get_new_titles_since_last_search(initial_search_titles: list, new_search_titles:list, threshold=0.75, similarity=lcs_length):
    """Compare two of titles (from different dates) and get the new titles. Compares titles based on LCS since they often have inconsistencies."""
    new_search_titles_lower = [t.lower() for t in new_search_titles]
    matrix, max_pairs = similarity_matrix_with_max(new_search_titles_lower, initial_search_titles, threshold, similarity=similarity)
    new_titles_since_last_search = [t for t in max_pairs if type(t) != tuple]
    return new_titles_since_last_search

def get_new_titles_since_last_search_from_json(initial_search_export_path: str, new_search_export_path: str, threshold=0.7, similarity=lcs_length):
    """Compare two json exports (from different dates) and get the new titles. Compares titles based on LCS since they often have inconsistencies. Requires CSL Json export (from Zotero)."""
    initial_search_titles = get_json_bib_titles(load_json_bib(initial_search_export_path))
    new_search_titles = get_json_bib_titles(load_json_bib(new_search_export_path))
    new_search_titles_lower = [t.lower() for t in new_search_titles]
    matrix, max_pairs = similarity_matrix_with_max(new_search_titles_lower, initial_search_titles, threshold, similarity=similarity)
    new_titles_since_last_search = [t for t in max_pairs if type(t) != tuple]
    return new_titles_since_last_search

def search_google_scholar(query):
    """Search Google Scholar for publications."""
    search_results = scholarly.search_pubs(query, patents=False, citations=False)
    publications = [res for res in search_results]
    print(len(publications), "publications found.")
    bibs = [pub["bib"] for pub in publications]
    titles = [bib["title"] for bib in bibs]
    return publications, bibs, titles