import fccWrapper as fcc

# ONE-TIME RETRIEVAL
# stations = fcc.station_getter()
# stations.to_csv('data/station-list.csv')
# station_detail = fcc.get_facility_detail(stations, ['ME'])
# station_detail.to_csv('data/all-station-detail.csv')

ref = fcc.create_ref()

fcc.get_public_files(ref)
