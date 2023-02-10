import os
import numpy as np
import pandas as pd


class RainFallRecord:
    def __init__(self, data_path):
        # Takes a file path as an argument and loads the data into a pandas DataFrame.
        # The data is cleaned up and transformed to a more usable format,
        # reaming columns for the year, month, and rainfall amount.
        # The file name without the extension is stored as the name attribute.
        # The year and month columns are cast to integers, and the rain column is cast to a float.

        try:
            self.df = pd.read_csv(data_path)
            self.df = self.df.T.reset_index().T.reset_index(drop=True)
            self.df.drop(self.df.columns[[2, 3, 4, 6]], axis='columns', inplace=True)
            self.df.dropna(how='any', inplace=True)
            self.df.columns = ['year', 'month', 'rain']
            self.df.replace({'rain': {'[^0-9.]': ''}}, regex=True)
            self.df = self.df.apply(lambda x: pd.to_numeric(x, errors='coerce'))
            self.df = self.df[pd.to_numeric(self.df['year'], errors='coerce').notnull()]
            self.df.reset_index(drop=True, inplace=True)

            self.name = data_path[:-4]

            self.year = self.df['year'] = self.df['year'].astype(int)
            self.month = self.df['month'] = self.df['month'].astype(int)
            self.rain = self.df['rain'] = self.df['rain'].astype(float)

        except FileNotFoundError:
            print(f'File: {data_path} does not exist')

    # returns the average rainfall in a given range of months in a specified year.
    def average(self, start_month, end_month, year):
        try:
            selection_df = self.df.loc[(self.year == year) &
                                       (self.month >= start_month) &
                                       (self.month <= end_month)]
            rain_list = list(map(float, selection_df['rain'].values.tolist()))
            average = np.average(rain_list)
            return f'The average rainfall in {self.name} in {year} between months {start_month} and {end_month}: {average}'
        except Exception as e:
            raise Exception(f"Input error: {e}")

    #  returns the rainfall amount for a specific month and year.
    def rainfall(self, month, year):
        try:
            rainfall = self.df.loc[(self.month == month) & (self.year == year), 'rain']
            if rainfall.empty:
                return f'Error: No rainfall data found for month {month} in year {year} in {self.name}'

            return f'The rainfall in {self.name} for month {month} in {year} is {rainfall.values[0]}mm'
        except Exception as e:
            raise Exception(f"Input error: {e}")

    # deletes the rainfall amount for a specific month and year.
    def delete(self, month, year):
        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValueError("Invalid value for month. It should be an integer between 1 and 12.")
        if not isinstance(year, int) or year < 0:
            raise ValueError("Invalid value for year. It should be a positive integer.")

        mask = (self.df['year'] == year) & (self.df['month'] == month)
        if not mask.any():
            raise ValueError(f"No data found for month {month} and year {year} in {self.name}.")

        self.df.loc[mask, 'rain'] = np.nan
        return f'The rainfall value in {self.name} for month {month} in {year} has been deleted'

    #  inserts or updates the rainfall amount for a specific month and year.
    def insert(self, month, year, rainfall):
        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValueError("Invalid value for month. It should be an integer between 1 and 12.")
        if not isinstance(year, int) or year < 0:
            raise ValueError("Invalid value for year. It should be a positive integer.")
        if not isinstance(rainfall, (int, float)) or rainfall < 0:
            raise ValueError("Invalid value for rainfall. It should be a non-negative number.")

        index = self.df.index[(self.df["year"] == year) & (self.df["month"] == month)].tolist()
        if index:
            self.df.loc[index[0], "rain"] = rainfall
        else:
            new_row = pd.DataFrame({'year': [year], 'month': [month], 'rain': [rainfall]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)

        return f'The rainfall in {self.name} for month {month} in {year} is {rainfall}mm'

    #  inserts or updates the rainfall amounts for a whole quarter (three months) in a specified year.
    def insert_quarter(self, quarter, year, rain_list):
        if quarter not in ['winter', 'spring', 'summer', 'autumn']:
            raise ValueError("Invalid value for quarter. It should be one of 'winter', 'spring', 'summer', 'autumn'.")
        if not isinstance(year, int) or year < 0:
            raise ValueError("Invalid value for year. It should be a positive integer.")
        if not isinstance(rain_list, list) or len(rain_list) != 3:
            raise ValueError("Invalid value for rain_list. It should be a list of 3 non-negative numbers.")
        for r in rain_list:
            if not isinstance(r, (int, float)) or r < 0:
                raise ValueError("Invalid value for rainfall. It should be a non-negative number.")

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


# task3
class Archive:
    # initializes the file name, creates the archive file name,
    # and creates an instance of the RainFallRecord class using the file name.
    def __init__(self, file_name):
        if not file_name.endswith(".csv"):
            raise ValueError("Invalid file name. It should be a .csv file.")
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File '{file_name}' does not exist.")

        self.file_name = file_name
        self.archive_name = f'{self.file_name[:-4]}_archive.csv'
        self.record = RainFallRecord(self.file_name)

    # writes or appending the data stored in the record's data frame to the archive file
    def insert(self):
        try:
            with open(self.archive_name, 'a') as f:
                self.record.df.to_csv(f, mode='a', header=not f.tell(), index=False, lineterminator='\n')
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.archive_name}' does not exist.")
        except Exception as e:
            raise Exception(f"An error occurred while writing to the file: {e}")

    # deletes the data in the archive file that matches the record's data frame
    def delete(self):
        try:
            archive_df = pd.read_csv(self.archive_name)
            merged = archive_df.merge(self.record.df, on='year', how='inner')
            archive_df = archive_df[~archive_df['year'].isin(merged['year'])]
            archive_df.to_csv(self.archive_name, index=False, lineterminator='\n')
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.archive_name}' does not exist.")
        except Exception as e:
            raise Exception(f"An error occurred while reading or writing to the file: {e}")

    # calculates the simple moving average of rainfall for a city between a start and end year, for a given window size
    def sma(self, city, start_year, end_year, k):
        try:
            df = pd.read_csv(city)
        except FileNotFoundError:
            return f'Error: The file {city} does not exist'

        df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        df['SMA'] = df['rain'].rolling(k).mean()
        df = df[df['SMA'].notnull()]
        values = [float(val) for val in [val[0] for val in df[['SMA']].values.tolist()]]
        return f'The {k} SMA of rainfall in {city[:-12]} between {start_year} and {end_year}: {values}'


class Driver:
    def __init__(self, city_list):
        self.city_list = city_list
        self.city_record_list = []
        self.archive_list = []

        for i in city_list:
            self.archive_list.append(f'{i[:-4]}_archive.csv')
            self.city_record_list.append(RainFallRecord(i))

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
            rain_archive.insert()
            rain_archive.delete()
            rain_archive.insert()
            return_list.append(rain_archive.sma(self.archive_list[i], 1950, 1951, 6))

        return_string = ('\n'.join(map(str, return_list)))
        return f'{return_string}'


def main():
    city1 = 'Aberporth.csv'
    city2 = 'Armagh.csv'
    city3 = 'Oxford.csv'

    city_list = [city1, city2, city3]

    print(Driver(city_list).task1())
    print(Driver(city_list).task2())
    print(Driver(city_list).task3())


if __name__ == '__main__':
    main()
