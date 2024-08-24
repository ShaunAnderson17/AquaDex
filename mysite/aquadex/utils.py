import folium

def GenerateHeatMap(taxonKey, projection='3857', style='osm-bright', lng=5.4265362, lat=43.4200248, zoom=1):
    print(f"Generating HeatMap for taxonKey: {taxonKey}")  
    rasterTile = f'https://tile.gbif.org/{projection}/omt/{{z}}/{{x}}/{{y}}@1x.png?style={style}'
    prefix = 'https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png?'
    polygon = 'style=purpleHeat.point'
    polygonTile = f'{prefix}{polygon}&taxonKey={taxonKey}'

    print(f"Raster URL: {rasterTile}")
    print(f"Polygon URL: {polygonTile}")

    fmap = folium.Map(location=[lat, lng], zoom_start=zoom)

    folium.TileLayer(
        tiles=rasterTile,
        attr='Map data &#169; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    ).add_to(fmap)

    folium.TileLayer(
        tiles=polygonTile,
        attr='Data from <a href="https://www.gbif.org/">GBIF</a>',
    ).add_to(fmap)

    return fmap
