from h2o_wave import Q
from frontend.utils import clear_cards


async def page1(q: Q):
    q.page['sidebar'].value = '#page1'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(3):
        add_card(q, f'info{i}', cards.page1_card1)
    add_card(q, 'article', cards.page1_card4)

async def page2(q: Q):
    q.page['sidebar'].value = '#page2'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'chart1', cards.page2_card1)
    add_card(q, 'chart2', cards.page2_card2)
    add_card(q, 'table', cards.page2_card3)

async def page3(q: Q):
    q.page['sidebar'].value = '#page3'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
        add_card(q, f'item{i}', cards.page3_card1)

async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
    add_card(q, 'form', cards.page4_card1)
