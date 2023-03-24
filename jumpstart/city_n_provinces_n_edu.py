import csv
import os
from pprint import pprint

csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv/canada_cities.csv')

with open(csv_file_path) as csvfile:
    reader = csv.DictReader(csvfile)
    CITY_CHOICES = []
    provinces = {}
    for row in reader:
        city = row['city']
        province_id = row['province_id']
        province_name = row['province_name']
        CITY_CHOICES.append((city, city))
        provinces[province_id] = province_name

    PROVINCE_CHOICES = sorted([(k, v) for k, v in provinces.items()])
    CITY_CHOICES = sorted(set(CITY_CHOICES))

    # pprint(CITY_CHOICES)

UNIVERSITY_CHOICES = [
    ('Algoma University', 'Algoma University'),
    ('Algonquin College', 'Algonquin College'),
    ('Brock University', 'Brock University'),
    ('Carleton University', 'Carleton University'),
    ('Centennial College', 'Centennial College'),
    ('Conestoga College', 'Conestoga College'),
    ('Confederation College', 'Confederation College'),
    ('Durham College', 'Durham College'),
    ('Fanshawe College', 'Fanshawe College'),
    ('Fleming College', 'Fleming College'),
    ('George Brown College', 'George Brown College'),
    ('Georgian College', 'Georgian College'),
    ('Humber College', 'Humber College'),
    ('Lakehead University', 'Lakehead University'),
    ('Laurentian University', 'Laurentian University'),
    ('Loyalist College', 'Loyalist College'),
    ('McMaster University', 'McMaster University'),
    ('Mohawk College', 'Mohawk College'),
    ('Niagara College', 'Niagara College'),
    ('Nipissing University', 'Nipissing University'),
    ('Northern College', 'Northern College'),
    ('OCAD University', 'OCAD University'),
    ('Ontario Tech University', 'Ontario Tech University'),
    ('Queen\'s University', 'Queen\'s University'),
    ('Ryerson University', 'Ryerson University'),
    ('Sault College', 'Sault College'),
    ('Seneca College', 'Seneca College'),
    ('Sheridan College', 'Sheridan College'),
    ('St. Clair College', 'St. Clair College'),
    ('St. Lawrence College', 'St. Lawrence College'),
    ('Trent University', 'Trent University'),
    ('University of Guelph', 'University of Guelph'),
    ('University of Ontario Institute of Technology', 'University of Ontario Institute of Technology'),
    ('University of Ottawa', 'University of Ottawa'),
    ('University of Toronto', 'University of Toronto'),
    ('University of Waterloo', 'University of Waterloo'),
    ('University of Windsor', 'University of Windsor'),
    ('Western University', 'Western University'),
    ('Wilfrid Laurier University', 'Wilfrid Laurier University'),
    ('York University', 'York University'),
]

EVENT_TIME_CHOICES = [('10:00', '10:00 AM'), ('11:00', '11:00 AM'), ('12:00', '12:00 PM'), ('13:00', '1:00 PM'),
                      ('14:00', '2:00 PM'), ('15:00', '3:00 PM'), ('16:00', '4:00 PM'), ('17:00', '5:00 PM'),
                      ('18:00', '6:00 PM'), ]
