from scrapy import Item, Field
# from dataclass import dataclass

# @dataclass
class FacmsItem(Item):
    # keys: str = field(default_factory=list)
    key = Field()
    title = Field()
    author = Field()
    kind = Field()
    tag = Field()
    section = Field()
    date = Field()

    def __str__(self):
        return ''
