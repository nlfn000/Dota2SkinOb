def find_by_class(soup, class_name):
    return soup.find(attrs={'class': class_name})


def find_all_by_class(soup, class_name):
    return soup.findAll(attrs={'class': class_name})

