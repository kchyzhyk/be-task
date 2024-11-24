from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(name='add_styles')
def add_styles(value):
    if not value:
        return value
    
    soup = BeautifulSoup(value, 'html.parser')
    
    section = soup.find('section')
    if section:
        section['class'] = section.get('class', []) + ['strux_view_table', 'col-span-2']
    
    # Adding styles to the header
    header = soup.find('header')
    if header:
        header['class'] = header.get('class', []) + ['strux_view_header', 'grid', 'grid-cols-5', 'gap-2', 'p-2', 'text-center', 'font-semibold']
        header_cells_to_remove = header.find_all('div', id=['energy_rate_adj_title', 'energy_rate_sell_title'])
        for header_cell in header_cells_to_remove:
            header_cell.decompose()
    rows = soup.find_all('div', class_='strux_view_row')
    
    for row_number, row in enumerate(rows, start=1):
        row['class'] = row.get('class', []) + ['grid', 'gap-2', 'p-2', 'text-center']
        row['id'] = f'row_{row_number}'
        remaining_cells = row.find_all('div', class_='strux_view_cell')
        remaining_cells = remaining_cells[:5]
        for extra_cell in row.find_all('div', class_='strux_view_cell')[5:]:
            extra_cell.decompose()
        row['class'] = row.get('class', []) + ['grid', f'grid-cols-{len(remaining_cells)}', 'gap-2', 'p-2', 'text-center']
        
        header_cells = header.find_all('div', class_='tier_col')
        for col_number, cell in enumerate(remaining_cells, start=1):
            cell['class'] = cell.get('class', []) + ['border', 'border-gray-300', 'p-2']
            header_cell = header_cells[col_number - 1]
            header_content = header_cell.get_text(strip=True)
            cell['id'] = f'{header_content}{col_number}{row_number}'
    
    return str(soup)
