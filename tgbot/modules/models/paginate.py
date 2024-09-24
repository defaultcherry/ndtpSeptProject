from .users import Task

__all__ = ["paginate_pages"]


def paginate_pages(data: list[Task]) -> list[list[Task]]:
    pages = []
    data_per_page = 25
    for count, i in enumerate(data):
        if count % data_per_page == 0:
            pages.append([i])
        else:
            pages[count // data_per_page].append(i)
    return pages
