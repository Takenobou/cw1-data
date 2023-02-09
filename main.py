import numpy as np
import pandas as pd


class RainFallRecord:
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

            self.name = datapath[:-4]

            self.year = self.df['year'] = self.df['year'].astype(int)
            self.month = self.df['month'] = self.df['month'].astype(int)
            self.rain = self.df['rain'] = self.df['rain'].astype(float)

        except FileNotFoundError:
            print(f'File: {datapath} does not exist')

    def average(self, start_month, end_month, year):
        selection_df = self.df.loc[(self.year == year) &
                                   (self.month >= start_month) &
                                   (self.month <= end_month)]
        rain_list = list(map(float, selection_df['rain'].values.tolist()))
        average = np.average(rain_list)

        return f'The average rainfall in {self.name} in {year} between months {start_month} and {end_month}: {average}'

    def rainfall(self, month, year):
        rainfall = self.df.loc[(self.month == month) & (self.year == year), 'rain']

        return f'The rainfall in {self.name} for month {month} in {year} is {rainfall.values[0]}mm'

    def delete(self, month, year):
        self.df.loc[(self.year == year) & (self.month == month), 'rain'] = np.nan
        return f'The rainfall value in {self.name} for month {month} in {year} has been deleted'

    def insert(self, month, year, rainfall):
        index = self.df.index[(self.df["year"] == year) & (self.df["month"] == month)].tolist()
        if index:
            self.df.loc[index[0], "rain"] = rainfall
        else:
            new_row = pd.DataFrame({'year': [year], 'month': [month], 'rain': [rainfall]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)

        return f'The rainfall in {self.name} for month {month} in {year} is {rainfall}mm'

    def insert_quarter(self, quarter, year, rain_list):
        quarters = {'winter': 1,
                    'spring': 4,
                    'summer': 7,
                    'autumn': 10}
        month = quarters[quarter]

        index = self.df.index[(self.df["year"] == year) & (self.df["month"] == month)].tolist()
        if index:
            index = index[0]
            for i in range(3):
                self.df.loc[(index + i), "rain"] = rain_list[i]
        else:
            for i in range(3):
                new_row = pd.DataFrame({'year': [year], 'month': [month], 'rain': [rain_list[i]]})
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                month = month + 1

        rain_string = ('mm, '.join(map(str, rain_list)))
        return f'Added the rainfall values {rain_string}mm in {self.name} for the {quarter} quarter in {year}'


class Archive:
    def __init__(self, file_name):
        self.file_name = file_name
        self.archive_name = f'{self.file_name[:-4]}_archive.csv'

    def insert(self, record):
        with open(self.archive_name, 'a') as f:
            record.df.to_csv(f, mode='a', header=not f.tell(), index=False, lineterminator='\n')

    def delete(self, record):
        archive_df = pd.read_csv(self.archive_name)
        merged = archive_df.merge(record.df, on='year', how='inner')
        archive_df = archive_df[~archive_df['year'].isin(merged['year'])]
        archive_df.to_csv(self.archive_name, index=False, lineterminator='\n')

    def sma(self, city, start_year, end_year, k):
        df = pd.read_csv(city)
        df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        df['SMA'] = df['rain'].rolling(k).mean()
        df = df[df['SMA'].notnull()]
        values = [float(val) for val in [val[0] for val in df[['SMA']].values.tolist()]]
        return f'The {k} SMA of rainfall in {city[:-12]} between {start_year} and {end_year}: {values}'


class Driver:
    def __init__(self, city1, city2, city3):
        self.city_list = [city1, city2, city3]
        self.archive_list = [f'{city1[:-4]}_archive.csv',
                             f'{city2[:-4]}_archive.csv',
                             f'{city3[:-4]}_archive.csv']
        self.city_record_list = [RainFallRecord(city1), RainFallRecord(city2), RainFallRecord(city3)]

    def task1(self):
        average_list = []
        for i in self.city_record_list:
            average_list.append(i.average(1, 12, 1941))

        return_string = ('\n'.join(map(str, average_list)))
        return f'{return_string}'

    def task2(self):
        return_list = []
        for i in self.city_record_list:
            return_list.append(i.rainfall(1, 1941))
            return_list.append(i.delete(1, 1941))
            return_list.append(i.insert(1, 1941, 97.1))
            return_list.append(i.insert_quarter('spring', 1941, [19.2, 34.6, 12.5]))

        return_string = ('\n'.join(map(str, return_list)))
        return f'{return_string}'

    def task3(self):
        return_list = []

        for i in range(len(self.city_list)):
            rain_archive = Archive(self.city_list[i])
            rain_archive.insert(self.city_record_list[i])
            rain_archive.delete(self.city_record_list[i])
            rain_archive.insert(self.city_record_list[i])
            return_list.append(rain_archive.sma(self.archive_list[i], 1950, 1951, 6))

        return_string = ('\n'.join(map(str, return_list)))
        return f'{return_string}'


def main():
    city1 = 'Aberporth.csv'
    city2 = 'Armagh.csv'
    city3 = 'Oxford.csv'

    print(Driver(city1, city2, city3).task1())
    print(Driver(city1, city2, city3).task2())
    print(Driver(city1, city2, city3).task3())


if __name__ == '__main__':
    main()
