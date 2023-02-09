import numpy as np
import pandas as pd


class RainFallRecord(object):
    def __init__(self, datapath):
        try:
            self.df = pd.read_csv(datapath)
            self.df = self.df.T.reset_index().T.reset_index(drop=True)
            self.df.drop(self.df.columns[[2, 3, 4, 6]], axis='columns', inplace=True)
            self.df.dropna(how='any', inplace=True)
            self.df.columns = ['year', 'month', 'rain']
            self.df.replace({'rain': {'[^0-9.]': ''}}, regex=True)
            self.df = self.df.apply(lambda x: pd.to_numeric(x, errors='coerce'))
            self.df = self.df[pd.to_numeric(self.df['year'], errors='coerce').notnull()]
            self.df.reset_index(drop=True, inplace=True)
            self.name = datapath[7:][:-4]

            self.year = self.df['year'] = self.df['year'].astype(int)
            self.month = self.df['month'] = self.df['month'].astype(int)
            self.rain = self.df['rain'] = self.df['rain'].astype(float)

        except FileNotFoundError:
            print(f'File: {datapath} does not exist')

    def shape(self):
        return self.df.shape

    def first_rows(self, num=3):
        return self.df.head(num)

    def last_rows(self, num=3):
        return self.df.tail(num)

    def tostring(self):
        return self.df.to_string()

    def types(self):
        return self.df.dtypes

    def average(self, start_month, end_month, year):
        selection_df = self.df.loc[(self.year == year) &
                                   (self.month >= start_month) &
                                   (self.month <= end_month)]
        rain_list = list(map(float, selection_df['rain'].values.tolist()))
        average = np.average(rain_list)

        return f'The average rainfall: {average}'

    def rainfall(self, month, year):
        rainfall = self.df.loc[(self.month == month) & (self.year == year), 'rain']

        return f'The rainfall in {self.name} for month {month} in {year} is {rainfall.values[0]}mm'

    def delete(self, month, year):
        self.df.loc[(self.year == year) & (self.month == month), 'rain'] = np.nan
        return f'The rainfall value in {self.name} for month {month} in {year} has been deleted'

    def insert(self, month, year, rainfall):
        new_row = pd.DataFrame({'year': [year], 'month': [month], 'rain': [rainfall]})
        index = self.df.index[(self.df["year"] == year) & (self.df["month"] == month)].tolist()
        if index:
            self.df.loc[index[0], "rain"] = rainfall
        else:
            self.df = pd.concat([self.df, new_row], ignore_index=True)

        return f'The rainfall in {self.name} for month {month} in {year} is {rainfall}mm'

    def insert_quarter(self, quarter, year, rain_list):
        quarter_df = pd.DataFrame()
        quarters = {'winter': 1,
                    'spring': 4,
                    'summer': 7,
                    'autumn': 10,
                    }
        month = quarters[quarter]

        index = self.df.index[(self.df["year"] == year) & (self.df["month"] == month)].tolist()
        if index:
            index = index[0]
            for i in range(3):
                self.df.loc[(index+i), "rain"] = rain_list[i]
        else:
            print("index not found")
            self.df = pd.concat([self.df, quarter_df], ignore_index=True)

        rain_string = ('mm, '.join(map(str, rain_list)))
        return f'Added the rainfall values {rain_string}mm in {self.name} for the {quarter} quarter in {year}'


def main():
    city1 = RainFallRecord('cities/Aberporth.csv')
    print(city1.average(1, 12, 1941))
    print(city1.rainfall(1, 1941))
    print(city1.first_rows())
    print(city1.delete(1, 1941))
    print(city1.first_rows())
    print(city1.insert(1, 1941, 97.1))
    print(city1.first_rows(6))
    print(city1.insert_quarter('winter', 1941, [19.2, 34.6, 12.5]))
    print(city1.first_rows(9))


    # city2 = RainFallRecord('cities/Armagh.csv')
    # print(city2.average(1, 12, 1941))
    # print(city2.rainfall(1, 1941))
    # print(city2.first_rows())
    # print(city2.delete(1, 1941))
    # print(city2.first_rows())
    # print(city2.shape())
    # print(city2.insert(1, 1941, 97.1))
    # print(city2.first_rows())
    # print(city2.shape())
    # print(city2.types())
    #
    # city3 = RainFallRecord('cities/Oxford.csv')
    # print(city3.average(1, 12, 1941))
    # print(city3.rainfall(1, 1941))
    # print(city3.first_rows())
    # print(city3.delete(1, 1941))
    # print(city3.first_rows())
    # print(city3.shape())
    # print(city3.insert(1, 1941, 97.1))
    # print(city3.first_rows())
    # print(city3.shape())
    # print(city3.types())


if __name__ == '__main__':
    main()
