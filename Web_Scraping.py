import string
from urllib2 import urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

class BCSScraper():
    def __init__(self, year=2013):
        self.soup = self.get_soup(year)
        self._punctuation = self.get_punctuation()

    def get_punctuation(self):
        punctuation = set(string.punctuation)
        punctuation.remove('.')
        return punctuation

    def _strip_punct(self, text):
        return ''.join(char for char in text if char not in self._punctuation) 

    def get_soup(self, year):
        bcs_string = 'http://espn.go.com/college-football/bcs/_/year/{year}'
        content = urlopen(bcs_string.format(year=year)).read()
        soup = BeautifulSoup(content)
        return soup

    def scrape(self):
        data_info = self.get_data()
        df = self.make_df(*data_info)
        df.sort_index(level='rk', inplace=True)
        return df

    def get_data(self):
        first_column_level = self.get_first_column_level()
        second_column_level = self.get_second_column_level()
        table_data = self.get_table_data()
        return first_column_level, second_column_level, table_data

    def get_first_column_level(self):
        def format_header(col_header):
             return self._strip_punct(col_header.text).replace(' ', '_').lower() 
        num_cols = lambda col_header: range(int(col_header.attrs['colspan']))
        col_one_css = 'tr.stathead td'
        cols_one_stuff = self.soup.select(col_one_css)
        first_column_level = [format_header(col_header)
                              for col_header in cols_one_stuff[1:]
                              for _ in num_cols(col_header)]
        return first_column_level

    def get_second_column_level(self):
        format_col = lambda col: self._strip_punct(col.text).lower()
        col_two_css = 'tr.colhead td'
        cols_two_stuff = self.soup.select(col_two_css)
        second_column_level = [format_col(col) for col in cols_two_stuff]
        return second_column_level

    def get_table_data(self):
        row_types = ('even', 'odd')
        table_data = [row for row_type in row_types
                          for row in self.get_rows_data(row_type)]
        return table_data
        
    def get_rows_data(self, rows_type):
        get_row_data = lambda row: [self._strip_punct(col.text) for col in row]
        rows_css = 'table tr.{odd_even}row'
        rows = self.soup.select(rows_css.format(odd_even=rows_type))
        rows_data = (get_row_data(row) for row in rows)
        return rows_data

    def make_df(self, first_column_level, second_column_level, table_data):
        df_index_names, second_column_level = second_column_level[:2], second_column_level[2:]
        column_tuples = zip(first_column_level, second_column_level)
        column_index = pd.MultiIndex.from_tuples(column_tuples)
        np_table_data = np.array(table_data)
        df_index, np_table_data = np_table_data[:, :2], np_table_data[:, 2:]
        tuple_index = [(int(row[0]), row[1]) for row in df_index]
        row_index = pd.MultiIndex.from_tuples(tuple_index, names=df_index_names) 
        df = pd.DataFrame(np_table_data, index=row_index, columns=column_index)
        return df


if __name__ == '__main__':
    bcss = BCSScraper()
    bsc_df = bcss.scrape()
