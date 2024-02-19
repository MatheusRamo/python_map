from flask import Flask, render_template_string
import pandas as pd
import folium

app = Flask(__name__)


@app.route("/")
def components():

    df = pd.read_csv('dados_prismas.csv')
    # Converta a coluna 'Data' para o tipo de data
    df['Data'] = pd.to_datetime(df['Data'],  format='%d/%m/%Y')
    print(df['Data'])
    df = df.sort_values('Data')

    # Crie um mapa centrado na média de suas coordenadas
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=17, tiles = None)
    folium.TileLayer(tiles = "cartodbpositron").add_to(m)
    folium.TileLayer(tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                    name = "Imagem Satélite").add_to(m)

    folium.LayerControl().add_to(m)

    datas_unicas = []
    for data in df['Data'].unique():
        datas_unicas.append(data.date())

    # Adicione um marcador para cada prisma
    for prisma in df['Prisma'].unique():
        df_prisma = df[df['Prisma'] == prisma]

        # Use a última localização disponível para o marcador
        location = df_prisma.iloc[-1][['Latitude', 'Longitude']]
        datas_scrool = " "

        # for data in datas_unicas:
        #     datas_scrool += f"""
        #                 <div style="display: inline-block; width:150px; height: 20px; margin: 10px; border: 1px solid black;padding: 10px;">
        #                     {data}
        #                 </div> 
        #         """
            

        # Crie uma string HTML com as diferenças de elevação para cada dia
        html = '<div style="white-space: nowrap; overflow-x: auto;">' + datas_scrool + '</div>' + '<h3>' + prisma + '</h3>'
        for i, row in df_prisma.iterrows():
            html += f"""
            <h4> Data:  { str(row['Data'].date())} </h4>
            <ul>
                <li><b>N:</b> {str(round(row['Norte'], 5))} </li>
                <li><b>E:</b> {str(round(row['Leste'], 5))}  </li>
                <li><b>Elevação:</b> {str(round(row['Elevacao'], 5))} </li>
            </ul>
            """
        iframe = folium.IFrame(html=html, width=500, height=500)
        popup = folium.Popup(iframe, max_width=500)
        # Adicione o marcador ao mapa
        folium.Marker(location, popup=popup).add_to(m)






    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )


if __name__ == "__main__":
    app.run(debug=True)