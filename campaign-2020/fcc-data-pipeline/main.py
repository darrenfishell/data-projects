import fccWrapper as fcc

stations = fcc.station_getter()

station_detail = fcc.get_facility_detail(stations, ['ME'])

station_detail.to_csv('data/all-station-detail.csv')

