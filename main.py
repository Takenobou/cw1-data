import glob
import numpy as np
import pandas as pd


class RainFallRecord(object):
    def __init__(self, datapath):
        try:
            self.df = pd.read_csv(datapath)
            useless_cols = ['tmax', 'tmin', 'af', 'sun']
            self.df.drop(0, inplace=True)
            self.df.drop(useless_cols, inplace=True, axis=1)
            self.df.replace({'rain': {'[^0-9.]': ''}}, regex=True)
            self.df.reset_index(drop=True, inplace=True)
        except FileNotFoundError:
            print(f'File: {datapath} does not exist')

    def shape(self):
        return self.df.shape

    def average(self, start_month, end_month, year):
        selection_df = self.df.loc[(self.df['yyyy'] == year) &
                                   (self.df['mm'] >= start_month) &
                                   (self.df['mm'] <= end_month)]
        rain_list = list(map(float, selection_df['rain'].values.tolist()))
        average = np.average(rain_list)

        return average


def main():
    x = 0
    cities = glob.glob('cities/*csv')
    print("Select a city:")
    for city in cities:
        x = x + 1
        print(f"{x}: {city[:-4][7:]}")
    selection = cities[int(input("Enter number: ")) - 1]
    table = RainFallRecord(selection)
    print(table.average(1, 12, 1941))


if __name__ == '__main__':
    main()
